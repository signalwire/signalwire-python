"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

A call, simulated in a test: the agent's tools, steps and state, without the
platform or a model.

``CallSimulator`` reads the agent's rendered SWML, as the platform would,
and plays the model's side: the test says what the caller says and which
tools the model calls. Each call is checked as the platform checks it: a
tool the current step doesn't offer doesn't run, and a gated tool runs only
when the test's gate callback lets it. A result's actions change the
simulated call: global data and ``semantic_state``, the step and context,
which functions are on, ``say``, and the end of the call.

It's an approximation of the platform, for testing your code's decisions.
It doesn't run a model, DataMap tools (give a stub), gather questions, or
the gates' decision model (give a callback).
"""

from __future__ import annotations

import copy
import json
import re
import time
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any

from signalwire.core.function_result import FunctionResult
from signalwire.core.semantic_gate import RESERVED_FUNCTION_NAMES
from signalwire.core.swaig_function import _resolve_awaitable
from signalwire.core.tool_middleware import CallNext

if TYPE_CHECKING:
    from signalwire.core.agent_base import AgentBase

#: A gate callback: ``gates(gate, simulator, args)`` returns True or a
#: probability at or above the gate's threshold to pass, False or one below it
#: to fail, or "unclear"
GateCallback = Callable[[dict[str, Any], "CallSimulator", dict[str, Any]], Any]

_NAVIGATION = ("next_step", "change_context")
_VARIABLE = re.compile(r"\$\{([A-Za-z0-9_.]+)\}")


class SimulatedCall:
    """What one tool call came to in the simulation."""

    def __init__(
        self,
        name: str,
        args: dict[str, Any],
        result: dict[str, Any],
        *,
        ran: bool,
        blocked_by: str | None = None,
    ) -> None:
        #: The tool's name
        self.name = name
        #: The arguments the model sent
        self.args = args
        #: The result, as the platform gets it
        self.result = result
        #: Whether the tool's handler (or stub) ran
        self.ran = ran
        #: Why it didn't: "step" for a tool the step doesn't offer, or the id
        #: of the gate that blocked it
        self.blocked_by = blocked_by

    @property
    def response(self) -> str:
        """The result's text: its response, or its tool_result."""
        response = self.result.get("response", "")
        if isinstance(response, dict):
            return str(response.get("tool_result", ""))
        return str(response)

    @property
    def tool_prompt(self) -> str | None:
        """The result's tool_prompt, if it has one."""
        response = self.result.get("response")
        return response.get("tool_prompt") if isinstance(response, dict) else None

    @property
    def actions(self) -> list[dict[str, Any]]:
        """The result's actions."""
        action = self.result.get("action", [])
        return action if isinstance(action, list) else [action]

    def __repr__(self) -> str:
        state = "ran" if self.ran else f"blocked by {self.blocked_by}"
        return f"<SimulatedCall {self.name} {state}: {self.response!r}>"


class CallSimulator:
    """
    A simulated call to ``agent``, for tests.

    Example:
        sim = CallSimulator(agent, gates=lambda gate, sim, args: True)
        sim.caller("I'd like a large tea")
        assert sim.call("place_order", {"item": "tea"}).ran is False  # not offered yet
        sim.call("review_order", {"item": "large tea"})
        sim.caller("yes")
        assert sim.call("place_order").ran
        assert sim.step == "done"
    """

    def __init__(
        self,
        agent: AgentBase,
        *,
        call_id: str = "simulated-call",
        gates: GateCallback | None = None,
        stubs: Mapping[str, Callable[[dict[str, Any]], Any]] | None = None,
        global_data: Mapping[str, Any] | None = None,
    ) -> None:
        """
        Args:
            agent: The agent.
            call_id: The call's id, as the agent's tools see it.
            gates: The answer to each semantic gate, in place of the decision
                model. Without one, every gate passes.
            stubs: Results for tools that don't run locally, such as DataMap
                tools, by name: ``fn(args)`` returning a FunctionResult, a
                dict or text.
            global_data: Global data to start with, over the agent's own.
        """
        self.agent = agent
        self.call_id = call_id
        self._gates = gates
        self._stubs = dict(stubs or {})
        ai = _ai_verb(json.loads(agent._render_swml(call_id)))
        self.params: dict[str, Any] = copy.deepcopy(ai.get("params", {}))
        #: The call's global data
        self.global_data: dict[str, Any] = copy.deepcopy(ai.get("global_data", {}))
        self.global_data.update(copy.deepcopy(dict(global_data or {})))
        swaig = ai.get("SWAIG", {})
        self.functions: dict[str, dict[str, Any]] = {
            f["function"]: f for f in swaig.get("functions", []) if "function" in f
        }
        prompt = ai.get("prompt", {})
        self._contexts: dict[str, Any] = (
            prompt.get("contexts", {}) if isinstance(prompt, dict) else {}
        )
        #: The conversation so far, as call log entries
        self.call_log: list[dict[str, Any]] = []
        #: Whether a result ended the call
        self.ended = False
        #: The back_to_back_functions setting, as the last result left it
        self.chaining: bool | str = "forever"
        #: Whether a result asked the model to wait for the caller
        self.waiting_for_user = False
        #: Every tool call so far
        self.calls: list[SimulatedCall] = []
        self._toggled: dict[str, bool] = {}
        self._tool_calls = 0
        #: The current context and step, None without contexts
        self.context: str | None = None
        self.step: str | None = None
        self._step_functions: set[str] = set(self._tools())
        if self._contexts:
            first = (
                "default" if "default" in self._contexts else next(iter(self._contexts))
            )
            self._enter_context(first)

    # -- the conversation ------------------------------------------------

    def caller(self, text: str) -> CallSimulator:
        """The caller says ``text``."""
        self._log({"role": "user", "content": text})
        self.waiting_for_user = False
        return self

    def agent_says(self, text: str) -> CallSimulator:
        """The agent says ``text``, as the model's reply."""
        self._log({"role": "assistant", "content": text})
        return self

    @property
    def semantic_state(self) -> Any:
        """``global_data.semantic_state``, or None."""
        return self.global_data.get("semantic_state")

    def offered(self) -> list[str]:
        """The tools the model is offered now, as the current step allows."""
        offered = {
            name
            for name in self._step_functions
            if name in self.functions and self._toggled.get(name, True)
        }
        offered |= {
            name for name, on in self._toggled.items() if on and name in self.functions
        }
        step = self._step()
        if step and step.get("valid_steps"):
            offered.add("next_step")
        if self._valid_contexts():
            offered.add("change_context")
        return sorted(offered)

    # -- tool calls ------------------------------------------------------

    def call(self, name: str, args: Mapping[str, Any] | None = None) -> SimulatedCall:
        """
        The model calls ``name`` with ``args``.

        The call is checked as the platform checks it: a tool the current
        step doesn't offer, or one the platform doesn't know, doesn't run,
        and the model gets the platform's reply naming the tools it has. A
        gated tool runs only when every gate passes. Otherwise the tool's
        handler runs with a request like the platform's, and its result's
        actions change the call.

        Returns:
            What the call came to.

        Raises:
            RuntimeError: When the call has ended.
            ValueError: For a DataMap tool without a stub.
        """
        if self.ended:
            raise RuntimeError("the call has ended")
        args = dict(args or {})
        self._log(
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"function": {"name": name, "arguments": json.dumps(args)}}
                ],
            }
        )
        if name not in self.offered():
            outcome = SimulatedCall(
                name,
                args,
                {"response": self._unavailable(name)},
                ran=False,
                blocked_by="step",
            )
        elif name in _NAVIGATION:
            outcome = self._navigate(name, args)
        else:
            outcome = self._dispatch(name, args)
        self._log({"role": "tool", "content": outcome.response})
        self.calls.append(outcome)
        return outcome

    def replay(self, requests: Iterable[Mapping[str, Any]]) -> list[SimulatedCall]:
        """
        Run recorded tool requests against the agent again, as they came.

        Each request is a SWAIG request body, as ``RequestRecorder``
        records it, with its own call data; the simulated call's state isn't
        used or changed. Use it to check that changed code still gives the
        results it gave on real calls.

        Returns:
            What each request came to, in order.
        """
        outcomes = []
        for body in requests:
            name = str(body.get("function", ""))
            args = _arguments(body)
            result = _as_dict(
                _resolve_awaitable(
                    self.agent.on_function_call(name, args, copy.deepcopy(dict(body)))
                )
            )
            outcomes.append(SimulatedCall(name, args, result, ran=True))
        return outcomes

    # -- internals ---------------------------------------------------------

    def _dispatch(self, name: str, args: dict[str, Any]) -> SimulatedCall:
        definition = self.functions[name]
        blocked = self._check_gates(name, definition, args)
        if blocked is not None:
            return blocked
        if name in self._stubs:
            result = _as_dict(self._stubs[name](args))
        elif "data_map" in definition:
            raise ValueError(
                f"{name} is a DataMap tool, which runs on the platform; give a stub "
                "for it: CallSimulator(agent, stubs={...})"
            )
        else:
            result = _as_dict(
                _resolve_awaitable(
                    self.agent.on_function_call(name, args, self._request(name, args))
                )
            )
        self._apply(result)
        return SimulatedCall(name, args, result, ran=True)

    def _check_gates(
        self, name: str, definition: dict[str, Any], args: dict[str, Any]
    ) -> SimulatedCall | None:
        gates = definition.get("gates") or []
        unclear: dict[str, Any] | None = None
        for index, gate in enumerate(gates):
            answer = True if self._gates is None else self._gates(gate, self, args)
            gate_id = str(gate.get("id", f"gate_{index + 1}"))
            if answer == "unclear":
                unclear = unclear or {**gate, "id": gate_id}
                continue
            passed = (
                answer >= gate.get("threshold", 1)
                if isinstance(answer, (int, float)) and not isinstance(answer, bool)
                else bool(answer)
            )
            if not passed:
                return self._blocked(name, args, gate.get("on_fail", {}), gate_id)
        if unclear is not None:
            on_unclear = unclear.get("on_unclear") or {
                "response": f"{name} was not run. Ask the caller again."
            }
            return self._blocked(name, args, on_unclear, unclear["id"])
        return None

    def _blocked(
        self, name: str, args: dict[str, Any], output: dict[str, Any], gate_id: str
    ) -> SimulatedCall:
        result = _expand(
            copy.deepcopy(output), {"global_data": self.global_data, "args": args}
        )
        self._apply(result)
        return SimulatedCall(name, args, result, ran=False, blocked_by=gate_id)

    def _navigate(self, name: str, args: dict[str, Any]) -> SimulatedCall:
        if name == "next_step":
            requested = str(args.get("step", ""))
            valid = (self._step() or {}).get("valid_steps") or []
            target = self._following_step() if requested == "next" else requested
            if requested not in valid or target is None:
                return SimulatedCall(
                    name,
                    args,
                    {"response": f"{requested} is not a step you can go to."},
                    ran=False,
                    blocked_by="step",
                )
            self._enter_step(target)
            return SimulatedCall(
                name, args, {"response": f"Moved to step {target}."}, ran=True
            )
        target = str(args.get("context", ""))
        if target not in self._valid_contexts() or target not in self._contexts:
            return SimulatedCall(
                name,
                args,
                {"response": f"{target} is not a context you can go to."},
                ran=False,
                blocked_by="step",
            )
        self._enter_context(target)
        return SimulatedCall(
            name, args, {"response": f"Moved to context {target}."}, ran=True
        )

    def _request(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        self._tool_calls += 1
        request: dict[str, Any] = {
            "function": name,
            "argument": {"parsed": [args], "raw": json.dumps(args)},
            "call_id": self.call_id,
            "tool_call_id": f"{self.call_id}-tool-{self._tool_calls}",
            "global_data": copy.deepcopy(self.global_data),
            "content_type": "text/swaig",
            "version": "2.0",
        }
        if self.params.get("swaig_post_conversation"):
            request["call_log"] = copy.deepcopy(self.call_log)
            request["raw_call_log"] = copy.deepcopy(self.call_log)
        return request

    def _apply(self, result: dict[str, Any]) -> None:
        actions = result.get("action", [])
        for action in actions if isinstance(actions, list) else [actions]:
            if not isinstance(action, dict):
                continue
            for key, value in action.items():
                self._apply_one(key, value)

    def _apply_one(self, key: str, value: Any) -> None:
        if key == "say":
            self._log({"role": "assistant", "content": str(value)})
        elif key == "set_global_data" and isinstance(value, dict):
            self.global_data.update(copy.deepcopy(value))
        elif key == "unset_global_data":
            for name in [value] if isinstance(value, str) else list(value or []):
                self.global_data.pop(name, None)
        elif key == "change_step":
            self._enter_step(str(value))
        elif key == "change_context":
            self._enter_context(str(value))
        elif key == "toggle_functions" and isinstance(value, list):
            for toggle in value:
                if isinstance(toggle, dict) and "function" in toggle:
                    self._toggled[str(toggle["function"])] = bool(
                        toggle.get("active", True)
                    )
        elif key == "back_to_back_functions":
            self.chaining = value
        elif key == "wait_for_user":
            self.waiting_for_user = bool(value)
        elif key in ("hangup", "stop"):
            self.ended = True

    def _enter_context(self, name: str) -> None:
        if name not in self._contexts:
            raise ValueError(f"the agent has no context {name!r}")
        context = self._contexts[name]
        steps = context.get("steps", [])
        self.context = name
        self._step_functions = set(self._tools())
        initial = context.get("initial_step") or (steps[0]["name"] if steps else None)
        if initial:
            self._enter_step(str(initial))

    def _enter_step(self, name: str) -> None:
        if self.context is None:
            return
        step = self._find_step(name)
        if step is None:
            raise ValueError(f"context {self.context!r} has no step {name!r}")
        self.step = name
        functions = step.get("functions")
        if functions == "none" or functions == []:
            self._step_functions = set()
        elif isinstance(functions, list):
            self._step_functions = {str(f) for f in functions}
        # A step without a function list keeps the set before it

    def _step(self) -> dict[str, Any] | None:
        return self._find_step(self.step) if self.step else None

    def _find_step(self, name: str | None) -> dict[str, Any] | None:
        if self.context is None:
            return None
        for step in self._contexts[self.context].get("steps", []):
            if step.get("name") == name:
                return dict(step)
        return None

    def _following_step(self) -> str | None:
        if self.context is None:
            return None
        names = [s.get("name") for s in self._contexts[self.context].get("steps", [])]
        if self.step in names and names.index(self.step) + 1 < len(names):
            return str(names[names.index(self.step) + 1])
        return None

    def _valid_contexts(self) -> list[str]:
        step = self._step() or {}
        if step.get("valid_contexts") is not None:
            return list(step["valid_contexts"])
        if self.context is not None:
            return list(self._contexts[self.context].get("valid_contexts") or [])
        return []

    def _tools(self) -> list[str]:
        return [name for name in self.functions if name not in RESERVED_FUNCTION_NAMES]

    def _steps_offering(self, name: str) -> list[str]:
        if self.context is None:
            return []
        return [
            str(step.get("name"))
            for step in self._contexts[self.context].get("steps", [])
            if isinstance(step.get("functions"), list) and name in step["functions"]
        ]

    def _unavailable(self, name: str) -> str:
        """The platform's reply to a call of a tool it won't run now."""
        offered = self.offered()
        tools = ", ".join(offered)
        steps = ", ".join(self._steps_offering(name)) if name in self.functions else ""
        template = self.params.get("unavailable_function_response")
        if isinstance(template, str) and template:
            return (
                template.replace("${function}", name)
                .replace("${tools}", tools)
                .replace("${steps}", steps)
            )
        if name in self.functions:
            text = f"Nothing ran: {name} isn't available at this point in the call."
            if steps:
                text += f" The steps that offer it: {steps}."
        else:
            text = f"Nothing ran: there is no tool named {name}."
        if offered:
            return f"{text} The tools available now are: {tools}."
        return f"{text} No tools are available now."

    def _log(self, entry: dict[str, Any]) -> None:
        self.call_log.append({**entry, "timestamp": int(time.time() * 1_000_000)})


class RequestRecorder:
    """
    Tool middleware that records each tool request, for
    ``CallSimulator.replay``.

    Example:
        recorder = RequestRecorder("tool_requests.jsonl")
        agent.add_tool_middleware(recorder)
        ...
        CallSimulator(agent).replay(RequestRecorder.load("tool_requests.jsonl"))

    The requests carry what the caller said and the call's data: keep the
    file where you'd keep call recordings.
    """

    def __init__(self, path: str | Path | None = None, *, limit: int = 1000) -> None:
        """
        Args:
            path: A file to append each request to, one JSON object a line.
            limit: The most requests kept in ``requests``, newest kept.
        """
        self.path = Path(path) if path is not None else None
        self.limit = limit
        #: The requests recorded, oldest first
        self.requests: list[dict[str, Any]] = []

    def __call__(
        self,
        name: str,
        args: dict[str, Any],
        raw_data: dict[str, Any],
        call_next: CallNext,
    ) -> Any:
        request = copy.deepcopy(raw_data)
        request.setdefault("function", name)
        request.setdefault("argument", {"parsed": [args], "raw": json.dumps(args)})
        self.requests.append(request)
        del self.requests[: -self.limit]
        if self.path is not None:
            with self.path.open("a", encoding="utf-8") as out:
                out.write(json.dumps(request, default=str) + "\n")
        return call_next(args, raw_data)

    @staticmethod
    def load(path: str | Path) -> list[dict[str, Any]]:
        """The requests a recorder wrote to ``path``."""
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines if line.strip()]


def _ai_verb(swml: dict[str, Any]) -> dict[str, Any]:
    for verb in swml.get("sections", {}).get("main", []):
        if isinstance(verb, dict) and "ai" in verb:
            ai: dict[str, Any] = verb["ai"]
            return ai
    raise ValueError("the agent's SWML has no ai verb")


def _arguments(body: Mapping[str, Any]) -> dict[str, Any]:
    argument = body.get("argument")
    if isinstance(argument, dict):
        parsed = argument.get("parsed")
        if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
            return dict(parsed[0])
        raw = argument.get("raw")
        if isinstance(raw, str) and raw:
            try:
                loaded = json.loads(raw)
            except ValueError:
                return {}
            return loaded if isinstance(loaded, dict) else {}
    return {}


def _as_dict(result: Any) -> dict[str, Any]:
    if isinstance(result, FunctionResult):
        return result.to_dict()
    if isinstance(result, dict):
        return result
    return {"response": str(result)}


def _expand(value: Any, data: dict[str, Any]) -> Any:
    """``${...}`` variables in a gate's output, from the call's data, as the
    platform expands them once; a variable it can't find is left as it is."""
    if isinstance(value, str):

        def lookup(match: re.Match[str]) -> str:
            found: Any = data
            for part in match.group(1).split("."):
                if not isinstance(found, dict) or part not in found:
                    return match.group(0)
                found = found[part]
            return found if isinstance(found, str) else json.dumps(found)

        return _VARIABLE.sub(lookup, value)
    if isinstance(value, dict):
        return {k: _expand(v, data) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand(v, data) for v in value]
    return value
