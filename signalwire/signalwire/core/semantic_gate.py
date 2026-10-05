"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Semantic gates: natural-language preconditions on a SWAIG function.

A semantic gate is a yes/no question a decision model answers about the call
right before the platform dispatches the function. Every gate on the function
must pass for it to run. When one doesn't, the function isn't dispatched, and
the model gets that gate's ``on_fail`` output instead, as if a data_map had
returned it.

The platform refuses the whole function when any of its gates is invalid, so
the SDK checks gates by the platform's rules when a tool is defined, and
raises ValueError instead of sending a function the platform would drop.
"""

import json
import math
import re
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from signalwire.core.function_result import FunctionResult

# Phrases a function says, keyed by language code, "auto" (translated into the
# call's language on first use) or "default". An entry is a phrase, or a list
# of phrases, a wait script, spoken one at a time while the call is waiting.
FillerPhrases = Mapping[str, Sequence[str | Sequence[str]]]

# The platform's limits on a function's gates
MAX_GATES = 8
MAX_QUESTION_BYTES = 8192
MAX_CRITERIA_BYTES = 2048
MAX_ON_FAIL_BYTES = 8192

_GATE_KEYS = ("id", "question", "criteria", "threshold", "on_fail")
_GATE_ID = re.compile(r"[A-Za-z0-9_]{1,64}")

# Hooks the platform calls itself, the function OART intercepts by name, and
# the built-in function names: gates on any of them are refused
RESERVED_FUNCTION_NAMES = frozenset(
    {
        "startup_hook",
        "hangup_hook",
        "check_for_input",
        "end_call",
        "hangup",
        "check_time",
        "wait_for_user",
        "wait_seconds",
        "adjust_response_latency",
        "next_step",
        "change_context",
        "gather_submit",
        "get_visual_input",
        "get_ideal_strategy",
        "pause_conversation",
    }
)


class SemanticGate:
    """
    One semantic gate: a yes/no question about the call, and what the model
    gets when the answer isn't yes.

    The decision model sees the recent dialogue as ``conversation``, the
    call's ``global_data.semantic_state`` as ``semantic_state``, and the
    proposed call as ``proposed_function``. Write each question as one
    proposition and name what it's about with those field names, in
    backticks. The model reads literally and doesn't do arithmetic or compare
    dates, so put a computed result in ``semantic_state`` instead of asking
    for it.

    Example:
        SemanticGate(
            "Has the caller explicitly asked to cancel their account in "
            "`conversation`?",
            threshold=0.95,
            on_fail=FunctionResult(
                tool_result="cancel_account was not run.",
                tool_prompt="Ask the caller to confirm that they want to cancel.",
            ).update_global_data({"cancel_attempted": True}),
            true_means="The caller says they want to cancel.",
            false_means="The caller asked about cancelling, or said something else.",
            id="explicit_request",
        )
    """

    def __init__(
        self,
        question: str,
        threshold: float,
        on_fail: "str | FunctionResult | dict[str, Any]",
        *,
        id: str | None = None,
        true_means: str | None = None,
        false_means: str | None = None,
    ) -> None:
        """
        Args:
            question: The yes/no question, at most 8 KB. Its ``${...}``
                variables are expanded from the call's global data when the
                gate is checked; ``@{...}`` functions are not.
            threshold: The probability of yes, above 0 and at most 1, at or
                above which the gate passes. Thresholds are calibrated per
                decision model version.
            on_fail: What the model gets when this is the first gate that
                fails: the tool result text, a FunctionResult, or a data_map
                output dict. A FunctionResult's response and actions are used;
                its ``tool_prompt`` becomes a system message after the tool
                result in the text pipeline, which OpenAI Realtime agents
                don't use. The actions run as written, without template
                expansion.
            id: The gate's id, 1 to 64 letters, digits or underscores, unique
                within the function. Default ``gate_<n>``, 1-based.
            true_means: What yes means, at most 2 KB.
            false_means: What no means, at most 2 KB.

        Raises:
            ValueError: If ``on_fail`` has no response: a blocked call must
                never read as a success.
        """
        self.question = question
        self.threshold = threshold
        self.id = id
        self.criteria: dict[str, str] = {}
        if true_means is not None:
            self.criteria["true"] = true_means
        if false_means is not None:
            self.criteria["false"] = false_means
        self.on_fail: dict[str, Any] = _on_fail(on_fail)

    def to_dict(self) -> dict[str, Any]:
        """The gate as the platform reads it."""
        gate: dict[str, Any] = {}
        if self.id is not None:
            gate["id"] = self.id
        gate["question"] = self.question
        if self.criteria:
            gate["criteria"] = dict(self.criteria)
        gate["threshold"] = self.threshold
        gate["on_fail"] = json.loads(json.dumps(self.on_fail))
        return gate


def _on_fail(on_fail: "str | FunctionResult | dict[str, Any]") -> dict[str, Any]:
    """Build an on_fail output object from a string, FunctionResult or dict."""
    from signalwire.core.function_result import FunctionResult

    if isinstance(on_fail, dict):
        return on_fail
    response: Any
    if isinstance(on_fail, FunctionResult):
        response = on_fail.response
        actions = on_fail.action
        post_process = on_fail.post_process
    else:
        response, actions, post_process = on_fail, [], False
    # A blocked call must never read as a success, so the platform requires
    # the text; FunctionResult.to_dict() would fill in "Action completed."
    if not response:
        raise ValueError("on_fail needs a response saying the function didn't run")
    output: dict[str, Any] = {"response": response}
    if actions:
        output["action"] = actions
        if post_process:
            output["post_process"] = True
    return output


def _utf8_len(text: str) -> int:
    return len(text.encode("utf-8"))


# A member a lookup didn't find, as distinct from a JSON null
_MISSING = object()

# The two-character escapes cJSON prints; any other character below 0x20 is
# printed as \u00XX
_SHORT_ESCAPES = {
    '"': '\\"',
    "\\": "\\\\",
    "\b": "\\b",
    "\f": "\\f",
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
}


def _first_key(container: dict[str, Any], name: str) -> str | None:
    """The key cJSON_GetObjectItem() finds for ``name``: the first one equal to
    it without regard to ASCII case."""
    for key in container:
        if isinstance(key, str) and key.lower() == name and key.isascii():
            return key
    return None


def _item(container: dict[str, Any], name: str) -> Any:
    key = _first_key(container, name)
    return _MISSING if key is None else container[key]


def _cjson_text(value: Any) -> str:
    """``value`` as cJSON_PrintUnformatted() prints it in FreeSWITCH."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return "null"
        # A whole number is printed with %ld, any other with %lf
        return str(int(value)) if value.is_integer() else f"{value:f}"
    if isinstance(value, str):
        escaped = "".join(
            _SHORT_ESCAPES.get(c, f"\\u{ord(c):04x}" if ord(c) < 0x20 else c)
            for c in value
        )
        return f'"{escaped}"'
    if isinstance(value, dict):
        members = (f"{_cjson_text(str(k))}:{_cjson_text(v)}" for k, v in value.items())
        return "{" + ",".join(members) + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_cjson_text(v) for v in value) + "]"
    return _cjson_text(str(value))


def _check_text(value: Any) -> str:
    """Why a string in a gate can't reach the platform intact, or ''."""
    if isinstance(value, str):
        if "\x00" in value:
            # C reads a string up to its first NUL
            return "contains a NUL character, which the platform reads as the end of the text"
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            return "contains an unpaired surrogate, which isn't valid UTF-8"
        return ""
    if isinstance(value, dict):
        items: list[Any] = [*value.keys(), *value.values()]
    elif isinstance(value, (list, tuple)):
        items = list(value)
    else:
        return ""
    for item in items:
        why = _check_text(item)
        if why:
            return why
    return ""


def _check_on_fail(on_fail: Any) -> str:
    """Why the platform would refuse ``on_fail``, or an empty string.

    The platform finds ``response``, ``tool_result``, ``tool_prompt`` and
    ``action`` without regard to case, taking the first match.
    """
    if not isinstance(on_fail, dict):
        return "on_fail must be an object"
    response = _item(on_fail, "response")
    if isinstance(response, str):
        if not response:
            return "on_fail.response is empty"
    elif isinstance(response, dict):
        tool_result = _item(response, "tool_result")
        if not isinstance(tool_result, str) or not tool_result:
            return "on_fail.response.tool_result is missing or empty"
        tool_prompt = _item(response, "tool_prompt")
        if tool_prompt is not _MISSING and not isinstance(tool_prompt, str):
            return "on_fail.response.tool_prompt must be a string"
    else:
        return "on_fail.response is missing"
    action = _item(on_fail, "action")
    if action is not _MISSING and not isinstance(action, list):
        return "on_fail.action must be an array"
    # Measured as the platform measures it: cJSON's compact print, in bytes
    if _utf8_len(_cjson_text(on_fail)) > MAX_ON_FAIL_BYTES:
        return f"on_fail is larger than {MAX_ON_FAIL_BYTES} bytes"
    return ""


def _check_criteria(criteria: Any) -> str:
    """Why the platform would refuse ``criteria``, or an empty string."""
    if not isinstance(criteria, dict) or not criteria:
        return "criteria must be an object with true and/or false"
    for key, value in criteria.items():
        if key not in ("true", "false"):
            return (
                f"criteria has an unknown key '{key}'; only true and false are allowed"
            )
        if not isinstance(value, str) or not value:
            return f"criteria.{key} must be a non-empty string"
        if _utf8_len(value) > MAX_CRITERIA_BYTES:
            return f"criteria.{key} is longer than {MAX_CRITERIA_BYTES} bytes"
    return ""


def _check_gate(gate: Any) -> str:
    """Why the platform would refuse one gate, or an empty string."""
    if not isinstance(gate, dict):
        return "must be an object"
    for key in gate:
        if key not in _GATE_KEYS:
            return f"unknown key '{key}'"
    why = _check_text(gate)
    if why:
        return why
    question = gate.get("question")
    if not isinstance(question, str) or not question:
        return "question is missing or empty"
    if _utf8_len(question) > MAX_QUESTION_BYTES:
        return f"question is longer than {MAX_QUESTION_BYTES} bytes"
    threshold = gate.get("threshold")
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not 0 < threshold <= 1
    ):
        return "threshold must be a number above 0 and at most 1"
    if "on_fail" not in gate:
        return "on_fail is missing"
    why = _check_on_fail(gate["on_fail"])
    if why:
        return why
    if "criteria" in gate:
        why = _check_criteria(gate["criteria"])
        if why:
            return why
    if "id" in gate:
        gate_id = gate["id"]
        if not isinstance(gate_id, str) or not _GATE_ID.fullmatch(gate_id):
            return "id must be 1 to 64 letters, digits or underscores"
    return ""


def gate_definitions(
    gates: Sequence["SemanticGate | dict[str, Any]"], function: str
) -> list[dict[str, Any]]:
    """
    Return a function's gates as the platform reads them.

    Args:
        gates: SemanticGate objects or gate dicts, 1 to 8.
        function: The function's name.

    Raises:
        ValueError: For anything that would make the platform refuse the
            function, with the platform's reason.
    """
    if function in RESERVED_FUNCTION_NAMES:
        raise ValueError(
            f"gates are not supported on {function}, a hook or built-in function name"
        )
    if isinstance(gates, (str, bytes, dict)) or not isinstance(gates, Sequence):
        raise ValueError(f"{function}: gates must be a list")
    if not 1 <= len(gates) <= MAX_GATES:
        raise ValueError(
            f"{function}: gates must hold 1 to {MAX_GATES} gates, not {len(gates)}"
        )
    definitions: list[dict[str, Any]] = []
    ids: list[str] = []
    for index, gate in enumerate(gates):
        definition = gate.to_dict() if isinstance(gate, SemanticGate) else gate
        why = _check_gate(definition)
        if why:
            raise ValueError(f"{function}: gate {index + 1}: {why}")
        gate_id = definition.get("id", f"gate_{index + 1}")
        if gate_id in ids:
            raise ValueError(
                f"{function}: gate {index + 1}: id '{gate_id}' is already used by "
                f"gate {ids.index(gate_id) + 1}"
            )
        ids.append(gate_id)
        definitions.append(json.loads(json.dumps(definition)))
    return definitions


def apply_gate_fields(
    fields: dict[str, Any], function: str, *, definition: bool = False
) -> None:
    """
    Check and normalize ``gates`` and ``gate_fillers`` in a function's fields.

    Its ``gates`` become the dicts the platform reads. The platform finds
    both keys without regard to case, taking the first match, so a raw
    definition's ``Gates`` is checked as its gates.

    Args:
        fields: A function definition, or the extra fields of one.
        function: The function's name.
        definition: True when ``fields`` is a whole function definition sent
            as written, such as a DataMap's or a raw dict. Then ``gates:
            None`` is refused, as the platform refuses the function for a
            JSON null, and a gated function needs a description. Otherwise
            None means no gates, as keyword arguments do.

    Raises:
        ValueError: For gates the platform would refuse, or ``gate_fillers``
            on a function without gates, which the platform ignores.
    """
    gates_key = _first_key(fields, "gates") if definition else "gates"
    gated = False
    if gates_key is not None and gates_key in fields:
        if fields[gates_key] is None and not definition:
            del fields[gates_key]
        else:
            fields[gates_key] = gate_definitions(fields[gates_key], function)
            gated = True
    if gated and definition:
        # The platform reads purpose, then description; any string counts
        purpose = _item(fields, "purpose")
        if not isinstance(purpose, str) and not isinstance(
            _item(fields, "description"), str
        ):
            raise ValueError(
                f"{function}: a gated function needs a description; the platform "
                "refuses it without one"
            )
    fillers_key = _first_key(fields, "gate_fillers") if definition else "gate_fillers"
    if fillers_key is None or fillers_key not in fields:
        return
    gate_fillers = fields[fillers_key]
    if gate_fillers is None:
        # The platform reads only the first match and ignores a null one, so
        # every spelling goes: removing only the first would expose another
        for key in [
            k for k in fields if isinstance(k, str) and k.lower() == "gate_fillers"
        ]:
            del fields[key]
        return
    if not gated:
        raise ValueError(
            f"{function}: gate_fillers needs gates; the platform ignores them on a "
            "function without gates"
        )
    if not isinstance(gate_fillers, Mapping):
        raise ValueError(
            f"{function}: gate_fillers must map a language code, 'auto' or "
            "'default' to a list of phrases"
        )
