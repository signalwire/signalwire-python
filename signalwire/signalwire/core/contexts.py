"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Contexts and Steps System for SignalWire Agents

This module provides an alternative to traditional POM-based prompts by allowing
agents to be defined as structured contexts with sequential steps. Each step
contains its own prompt, completion criteria, and function restrictions.

The SDK's installed documentation covers this module: run
``sw-pydocs contexts``, or ``sw-pydocs`` for the index.
"""

import re
import warnings
from collections.abc import Iterable
from typing import Optional, Any

from signalwire.core.logging_config import get_logger

_logger = get_logger("contexts")

MAX_CONTEXTS = 50
MAX_STEPS_PER_CONTEXT = 100


#: Valid values for a step's or context's ``history`` visibility mode.
#:
#: ``keep``     nothing is cleared — every prior step's instructions *and*
#:              dialogue stay in the model's context.
#: ``default``  prior step instructions are hidden; the dialogue is kept.
#: ``hide``     prior instructions hidden **and** the prior dialogue pulled
#:              out of the model's context. The only way back in is an
#:              explicit ``${step_history.*}`` reference in the new prompt.
#: ``isolate``  like ``hide``, but only while the agent is in this step: the
#:              earlier dialogue returns when the step is left, and the
#:              earlier step instructions stay cleared.
#: ``spoken``   prior instructions hidden, and every earlier tool call, tool
#:              result and turn-scoped system note (tool_prompts and the like)
#:              pulled out for the rest of the call; every spoken turn, the
#:              caller's and the agent's, stays.
HISTORY_MODES = ("keep", "default", "hide", "isolate", "spoken")


#: The most digits an expected answer can name
MAX_EXPECTED_DIGITS = 64
_EXPECTED_ANSWER_KEYS = frozenset({"digits", "min_digits", "max_digits"})


def expected_answer(
    digits: int | None = None,
    *,
    min_digits: int | None = None,
    max_digits: int | None = None,
) -> dict[str, int]:
    """Build and check an ``expected_answer`` value.

    Returns ``{"digits": N}`` for an exact count, or
    ``{"min_digits": a, "max_digits": b}`` for a range, with a at most b and each
    count from 1 to 64. The platform logs and ignores any other shape, so this
    function rejects one with ``ValueError`` instead. Pass the result to
    ``Step.set_expected_answer`` or to the ``expected_answer`` argument of
    ``Step.add_gather_question``.

    Args:
        digits: The exact number of digits. Do not combine with ``min_digits`` or
            ``max_digits``.
        min_digits: The fewest digits. Needs ``max_digits`` as well.
        max_digits: The most digits. Needs ``min_digits`` as well.

    Returns:
        A dict with the key ``digits``, or with the keys ``min_digits`` and
        ``max_digits``.

    Raises:
        ValueError: If a count is not a whole number from 1 to 64, if ``digits``
            is combined with ``min_digits`` or ``max_digits``, if only one of
            ``min_digits`` and ``max_digits`` is given, or if ``min_digits`` is
            greater than ``max_digits``.

    Example:
        ```python
        expected_answer(5)                         # {"digits": 5}
        expected_answer(min_digits=4, max_digits=6)
        ```
    """

    def count(name: str, value: Any) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not (1 <= value <= MAX_EXPECTED_DIGITS)
        ):
            raise ValueError(
                f"{name} must be a whole number from 1 to {MAX_EXPECTED_DIGITS}, "
                f"got {value!r}"
            )
        return value

    if digits is not None:
        if min_digits is not None or max_digits is not None:
            raise ValueError(
                "expected_answer takes digits, or min_digits and max_digits, not both"
            )
        return {"digits": count("digits", digits)}
    if min_digits is None or max_digits is None:
        raise ValueError(
            "expected_answer needs digits, or both min_digits and max_digits"
        )
    low, high = count("min_digits", min_digits), count("max_digits", max_digits)
    if low > high:
        raise ValueError(f"min_digits ({low}) must be at most max_digits ({high})")
    return {"min_digits": low, "max_digits": high}


def _check_expected_answer(value: Any) -> dict[str, int]:
    """A given expected_answer dict, checked by the platform's rules."""
    if not isinstance(value, dict) or not value or set(value) - _EXPECTED_ANSWER_KEYS:
        raise ValueError(
            'expected_answer must be {"digits": N} or '
            '{"min_digits": a, "max_digits": b}'
        )
    return expected_answer(**value)


def _validate_history(mode: str) -> str:
    if mode not in HISTORY_MODES:
        raise ValueError(f"history must be one of {HISTORY_MODES}, got {mode!r}")
    return mode


class GatherQuestion:
    """Represent a single question in a ``gather_info`` configuration.

    Each question defines a key for storing the answer, the question text, and
    optional type, confirmation and per-question settings. You rarely create one
    directly: ``Step.add_gather_question()`` and ``GatherInfo.add_question()``
    build it for you.
    """

    def __init__(
        self,
        key: str,
        question: str,
        type: str = "string",
        confirm: bool = False,
        prompt: str | None = None,
        functions: list[str] | None = None,
        isolated: bool | None = None,
        expected_answer: dict[str, int] | None = None,
    ):
        """Create a gather question.

        Args:
            key: Key name for storing the answer in ``global_data``. Must be unique
                within a single ``GatherInfo`` configuration.
            question: The question text to present to the user.
            type: JSON schema type for the answer: ``"string"`` (free-form text),
                ``"integer"`` (whole number), ``"number"`` (numeric value) or
                ``"boolean"`` (yes or no). Defaults to ``"string"``.
            confirm: When True, the model must read the answer back and get the
                user's confirmation before submitting it. Defaults to False.
            prompt: Extra instruction text for this question, such as additional
                context for asking or validating it.
            functions: Names of SWAIG functions to make available while this question
                is active, such as a lookup function that validates an account
                number.
            isolated: Overrides the ``isolated`` default of the gather for this one
                question. None (the default) inherits the gather's setting.
            expected_answer: The number of digits the answer has, as a dict:
                ``{"digits": 5}`` or ``{"min_digits": 4, "max_digits": 6}``. While
                this question is asked, it replaces the step's expected answer.

        Raises:
            ValueError: If ``expected_answer`` is not a valid expected answer. See
                the module function ``expected_answer``.
        """
        self.key = key
        self.question = question
        self.type = type
        self.confirm = confirm
        self.prompt = prompt
        self.functions = functions
        # Tri-state: None means "inherit the gather_info default"
        self.isolated = isolated
        # While this question is asked, it replaces the step's expected answer
        self.expected_answer = (
            None if expected_answer is None else _check_expected_answer(expected_answer)
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the question to a dictionary for SWML generation.

        Fields that hold their default value are omitted from the output.
        ``isolated`` is emitted whenever it is set, even when False, so that it can
        override an isolated gather.

        Returns:
            A dict with ``key`` and ``question``, plus ``type``, ``confirm``,
            ``prompt``, ``functions``, ``isolated`` and ``expected_answer`` when they
            are set.
        """
        d: dict[str, Any] = {"key": self.key, "question": self.question}
        if self.type != "string":
            d["type"] = self.type
        if self.confirm:
            d["confirm"] = True
        if self.prompt:
            d["prompt"] = self.prompt
        if self.functions:
            d["functions"] = self.functions
        # Emitted even when False, so it can override an isolated gather
        if self.isolated is not None:
            d["isolated"] = self.isolated
        if self.expected_answer is not None:
            d["expected_answer"] = dict(self.expected_answer)
        return d


class GatherInfo:
    """Collect several pieces of information in one step with ``gather_info``.

    The gather system presents its questions one at a time by re-injecting the
    step's instructions for each question, so it produces zero ``tool_call`` and
    ``tool_result`` entries in the history the model sees. Answers are stored in
    ``global_data`` and later steps or tools can read them.

    You normally configure it through ``Step.set_gather_info()`` and
    ``Step.add_gather_question()`` rather than creating it directly.

    Example:
        ```python
        gather = GatherInfo(output_key="patient_info", completion_action="next_step")
        gather.add_question("dob", "What is your date of birth?", confirm=True)
        gather.add_question("allergies", "Do you have any allergies?")
        ```
    """

    def __init__(
        self,
        output_key: str | None = None,
        completion_action: str | None = None,
        prompt: str | None = None,
        isolated: bool = False,
    ):
        """Create a gather configuration.

        Args:
            output_key: Key in ``global_data`` under which to nest all answers. When
                None, answers are stored at the top level of ``global_data`` under
                each question's ``key``.
            completion_action: Where to go after all questions are answered. None
                returns to normal step mode, ``"next_step"`` advances to the next
                sequential step, and a step name jumps to that step.
            prompt: Preamble text injected once when entering the gather step, giving
                the model personality and context for asking the questions.
            isolated: Default for every question. When True, a question is asked with
                the sibling questions and answers hidden from the model. A question's
                own ``isolated`` overrides it. Defaults to False.
        """
        self._questions: list[GatherQuestion] = []
        self._output_key = output_key
        self._completion_action = completion_action
        self._prompt = prompt
        self._isolated = isolated

    def add_question(self, key: str, question: str, **kwargs: Any) -> "GatherInfo":
        """Add a question to gather.

        Args:
            key: Key name for storing the answer in ``global_data``.
            question: The question text to ask.
            **kwargs: Optional fields passed to ``GatherQuestion``: ``type``,
                ``confirm``, ``prompt``, ``functions``, ``isolated`` and
                ``expected_answer``.

        Returns:
            This GatherInfo, for chaining.

        Example:
            ```python
            gather = GatherInfo()
            gather.add_question("zip", "What is your ZIP code?", type="string")
            ```
        """
        q = GatherQuestion(
            key=key,
            question=question,
            type=kwargs.get("type", "string"),
            confirm=kwargs.get("confirm", False),
            prompt=kwargs.get("prompt"),
            functions=kwargs.get("functions"),
            isolated=kwargs.get("isolated"),
            expected_answer=kwargs.get("expected_answer"),
        )
        self._questions.append(q)
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert the gather configuration to a dictionary for SWML generation.

        Returns:
            A dict with ``questions`` (a list of question dicts), plus ``prompt``,
            ``output_key``, ``completion_action`` and ``isolated`` when they are set.

        Raises:
            ValueError: If no questions have been added.
        """
        if not self._questions:
            raise ValueError("gather_info must have at least one question")
        d: dict[str, Any] = {"questions": [q.to_dict() for q in self._questions]}
        if self._prompt:
            d["prompt"] = self._prompt
        if self._output_key:
            d["output_key"] = self._output_key
        if self._completion_action:
            d["completion_action"] = self._completion_action
        if self._isolated:
            d["isolated"] = True
        return d


class Step:
    """A single phase within a context.

    A step has its own prompt text, completion criteria, available functions and
    navigation rules. The AI advances through steps as their criteria are met.
    You create steps by calling ``Context.add_step()``. Every setter returns the
    step itself, so calls chain.

    Example:
        ```python
        ctx = agent.define_contexts().add_context("default")
        step = ctx.add_step("collect_info")
        step.add_section("Task", "Collect the caller's account information.")
        step.add_bullets("Required Information", [
            "Full legal name",
            "Account number (10 digits)",
            "Reason for calling",
        ])
        step.set_step_criteria("All three items collected and confirmed.")
        step.set_valid_steps(["next"])
        ctx.add_step("done").set_text("Thank the caller.")
        ```
    """

    def __init__(self, name: str):
        """Create a step.

        Args:
            name: Step name. Must be unique within the parent context.
        """
        self.name = name
        self._text: str | None = None
        self._step_criteria: str | None = None
        self._functions: str | list[str] | None = None
        self._valid_steps: list[str] | None = None
        self._valid_contexts: list[str] | None = None

        # POM-style sections for rich prompts
        self._sections: list[dict[str, Any]] = []

        # Gather info configuration
        self._gather_info: GatherInfo | None = None

        # Step behavior flags
        self._end: bool = False
        self._skip_user_turn: bool = False
        self._skip_to_next_step: bool = False

        # Visibility of everything that came before this step
        self._history: str | None = None

        # The recognizer's hint for a number the caller is asked for
        self._expected_answer: dict[str, int] | None = None

        # Reset object for context switching from steps
        self._reset_system_prompt: str | None = None
        self._reset_user_prompt: str | None = None
        self._reset_consolidate: bool = False
        self._reset_full_reset: bool = False

    def set_text(self, text: str) -> "Step":
        """Set the step's prompt text directly.

        Cannot be combined with ``add_section()`` or ``add_bullets()``: use one
        approach or the other.

        The platform expands the text's variables, such as
        ``${global_data.order_total}``, when the step is entered, and
        current releases expand it again before a request whenever a value
        it reads has changed. Earlier releases, and a realtime model, keep
        the values from entry: there, return
        ``FunctionResult.refresh_step(name)`` after a later
        ``update_global_data`` to enter the step again with the new values.

        Args:
            text: Plain-text prompt instructions for this step.

        Returns:
            This Step, for chaining.

        Raises:
            ValueError: If POM sections were already added with ``add_section()`` or
                ``add_bullets()``.

        Example:
            ```python
            step = ctx.add_step("greeting")
            step.set_text("Welcome the caller and ask how you can help.")
            ```
        """
        if self._sections:
            raise ValueError(
                "Cannot use set_text() when POM sections have been added. Use one approach or the other."
            )
        self._text = text
        return self

    def add_section(self, title: str, body: str) -> "Step":
        """Add a POM section to the step.

        Cannot be combined with ``set_text()``. The section is rendered as a
        Markdown ``##`` heading followed by the body.

        Args:
            title: Section heading.
            body: Section body text.

        Returns:
            This Step, for chaining.

        Raises:
            ValueError: If ``set_text()`` was already used on this step.

        Example:
            ```python
            step = ctx.add_step("collect_info")
            step.add_section("Task", "Collect the caller's account information.")
            step.add_section("Guidelines", "Be polite and patient.")
            ```
        """
        if self._text is not None:
            raise ValueError(
                "Cannot add POM sections when set_text() has been used. Use one approach or the other."
            )
        self._sections.append({"title": title, "body": body})
        return self

    def add_bullets(self, title: str, bullets: list[str]) -> "Step":
        """Add a POM section with bullet points to the step.

        Cannot be combined with ``set_text()``.

        Args:
            title: Section heading.
            bullets: List of bullet point strings.

        Returns:
            This Step, for chaining.

        Raises:
            ValueError: If ``set_text()`` was already used on this step.

        Example:
            ```python
            step = ctx.add_step("collect_info")
            step.add_bullets("Required Information", [
                "Full legal name",
                "Account number (10 digits)",
                "Reason for calling",
            ])
            ```
        """
        if self._text is not None:
            raise ValueError(
                "Cannot add POM sections when set_text() has been used. Use one approach or the other."
            )
        self._sections.append({"title": title, "bullets": bullets})
        return self

    def set_step_criteria(self, criteria: str) -> "Step":
        """Set the criteria for determining when this step is complete.

        The AI evaluates this description against the conversation state to decide
        whether to advance.

        Be specific. Write "Customer has provided their full name AND phone number"
        rather than "Information collected". Include failure conditions when
        appropriate: "Verified OR after 3 failed attempts".

        Args:
            criteria: Natural-language description of the completion conditions.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            step = ctx.add_step("verify_identity")
            step.set_text("Verify the caller's identity.")
            step.set_step_criteria(
                "Customer gave their account number, or 3 verification attempts failed."
            )
            ```
        """
        self._step_criteria = criteria
        return self

    def set_functions(self, functions: str | list[str]) -> "Step":
        """Set which non-internal functions are callable while this step is active.

        IMPORTANT — keep the per-step active set small:
            LLM tool selection accuracy degrades noticeably once the
            per-call tool list grows past ~7-8 entries. Symptoms: the model
            has the right tool available, the user's request clearly matches
            it, but the model doesn't call it (or calls a near-neighbor
            instead). Same prompt may pass on rerun. This is the LLM's
            native tool-selection behavior — not something the SDK can fix.

            Mitigations:
              - Whitelist only the tools the current step actually needs.
                A 4-tool step is more reliable than a 12-tool step.
              - Split a busy step into two narrower steps so the relevant
                tools are partitioned by phase of the conversation.
              - Remember that `next_step` and `change_context` are
                auto-injected when valid_steps / valid_contexts are set —
                they count against the budget too. Don't list them in
                `functions`; the runtime adds them separately.

        IMPORTANT — inheritance behavior:
            If you do NOT call this method, the step inherits whichever function
            set was active on the previous step (or the previous context's last
            step). The server-side runtime only resets the active set when a
            step explicitly declares its `functions` field. This is by design,
            but it is the most common source of bugs in multi-step agents:
            forgetting set_functions() on a later step lets the previous step's
            tools leak through.

            Best practice: call set_functions() explicitly on every step that
            should have a different toolset than the previous one.

        Args:
            functions: One of:
                - List[str]  — whitelist of function names allowed in this step.
                              Functions not in the list become inactive.
                - []         — explicit disable-all (no user functions callable).
                - "none"     — synonym for [], same effect.

        Internal functions (`startup_hook`, `hangup_hook`, `check_for_input`,
        `summarize_conversation`, `gather_submit`, `get_ideal_strategy`) are
        ALWAYS protected and cannot be deactivated by this whitelist.

        The native navigation tools `next_step` and `change_context` are
        injected automatically when valid_steps / valid_contexts is set; they
        are not affected by this list and do not need to appear in it.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            step.set_functions(["lookup_account", "check_balance"])  # whitelist
            step.set_functions([])                                   # disable all
            step.set_functions("none")                               # disable all (alt)
            ```
        """
        self._functions = functions
        return self

    def set_valid_steps(self, steps: list[str]) -> "Step":
        """Set which steps can be navigated to from this step.

        Navigation from a step is controlled with ``set_valid_steps()`` and
        ``set_valid_contexts()``. A step's list takes precedence over the
        context-level list set with ``Context.set_valid_steps()``.
        ``ContextBuilder.validate()`` rejects a name that is not a step in the same
        context.

        Args:
            steps: Step names within the same context. Include ``"next"`` to allow
                sequential advancement to the next step in order.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            step = ctx.add_step("collect_info")
            step.set_text("Collect the caller's information.")
            step.set_valid_steps(["process_request", "escalate"])
            ctx.add_step("process_request").set_text("Process the request.")
            ctx.add_step("escalate").set_text("Escalate to a human agent.")
            ```
        """
        self._valid_steps = steps
        return self

    def set_valid_contexts(self, contexts: list[str]) -> "Step":
        """Set which contexts can be navigated to from this step.

        Overrides any context-level ``Context.set_valid_contexts()`` for this step.
        ``ContextBuilder.validate()`` rejects a name that is not a context in the
        builder.

        Args:
            contexts: Context names reachable from this step.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            step = ctx.add_step("transfer")
            step.set_text("Transfer the caller to the right department.")
            step.set_valid_contexts(["billing", "support"])
            ```
        """
        self._valid_contexts = contexts
        return self

    def set_end(self, end: bool) -> "Step":
        """Mark this step as terminal for the step flow.

        IMPORTANT: `end=True` does NOT end the conversation or hang up the
        call. It exits step mode entirely after this step executes — clearing
        the steps list, current step index, valid_steps, and valid_contexts.
        The agent keeps running, but operates only under the base system
        prompt and the context-level prompt; no more step instructions are
        injected and no more `next_step` tool is offered.

        To actually end the call, call a hangup tool or define a hangup_hook.

        Combine with `set_reset_*()` if you also want to reset/consolidate
        the conversation when this step exits.

        Args:
            end: True to exit step mode after this step.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            farewell = ctx.add_step("farewell")
            farewell.set_text("Thank you for calling. Goodbye!")
            farewell.set_end(True)
            ```
        """
        self._end = end
        return self

    def set_skip_user_turn(self, skip: bool) -> "Step":
        """Set whether to skip waiting for user input after this step.

        When True, the AI proceeds immediately without waiting for the caller to
        speak.

        Args:
            skip: True to skip the user turn after this step.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            intro = ctx.add_step("intro")
            intro.set_text("Introduce yourself and begin the intake process.")
            intro.set_skip_user_turn(True)
            ```
        """
        self._skip_user_turn = skip
        return self

    def set_skip_to_next_step(self, skip: bool) -> "Step":
        """Set whether to automatically advance to the next step.

        This works only together with `set_skip_user_turn(True)`: when the
        agent skips the caller's turn after this step, it also moves on to the
        next step in order, without waiting for the model to call `next_step`.
        On its own it has no effect.

        Args:
            skip: True to advance to the next step automatically.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            preamble = ctx.add_step("preamble")
            preamble.set_text("Read the disclaimer to the caller.")
            preamble.set_skip_user_turn(True)
            preamble.set_skip_to_next_step(True)
            ctx.add_step("main").set_text("Help the caller with their request.")
            ```
        """
        self._skip_to_next_step = skip
        return self

    def set_history(self, history: str) -> "Step":
        r"""Control what the model still sees when this step is entered.

        A step's mode overrides the context-level default set with
        ``Context.set_history()``.

        The mode applies when the step's instructions are injected, before
        the next request to the model, and governs everything before it. The
        exchange that entered the step stays under "hide", "isolate" and
        "spoken", as the step's start: the call whose action changed the step,
        its result, notes and say. A post_process action's change, which runs
        after the model's reply, keeps its call and everything stored from it
        on, the reply included. A change by next_step keeps nothing; platform
        releases before this keep nothing under "hide" and "isolate". An end
        step, or one with a reset, takes no history pass: steps end there.
        The mode doesn't affect this step's own turns, which accumulate fresh.
        Nothing is deleted: the call log keeps every message.

        Args:
            history: One of:
                - "keep": clear nothing. Every prior step's instructions and
                  dialogue stay visible to the model.
                - "default": hide the prior step *instructions*, keep the
                  user/assistant dialogue. This is the default when unset.
                - "hide": hide the prior instructions *and* pull the prior
                  dialogue out of the model's context. Pair it with a
                  ``${step_history.*}`` reference in this step's text to choose
                  exactly what comes back.
                - "isolate": like "hide" (the earlier dialogue leaves the
                  model's context and the earlier step instructions are
                  cleared), but only while the agent is in this step. When
                  the agent leaves it, the earlier dialogue comes back and
                  this step's own turns stay; the earlier instructions stay
                  cleared, and what an earlier "hide" step hid stays hidden.
                  Entering the step again isolates it again. Use it for a
                  step that must see nothing else, such as one that reads
                  back a confirmation. A platform without isolate treats it
                  as "default".
                - "spoken": keep the conversation, drop the work. Earlier step
                  instructions are cleared, and every earlier tool call, tool
                  result and turn-scoped system note (tool_prompts, ai-msg
                  injections, a gather's preamble) leaves the model's context
                  for the rest of the call. Every spoken turn stays: the
                  caller's, the agent's replies and ``say`` actions. An
                  assistant turn that spoke and called a tool keeps its words.
                  Use it at a stage boundary where the caller's earlier
                  requests must stay but the finished stage's tool results
                  shouldn't. A platform without spoken treats it as
                  "default", which keeps the tool exchanges.

        Raises:
            ValueError: if history is not one of these modes.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            ctx.add_step("collect_trip").set_text("Ask where the caller is going.")
            ctx.add_step("confirm_trip").set_history("hide").set_text(
                "Previously: ${step_history.prev.summary}\n\nConfirm the booking."
            )
            ```
        """
        self._history = _validate_history(history)
        return self

    def set_gather_info(
        self,
        output_key: str | None = None,
        completion_action: str | None = None,
        prompt: str | None = None,
        isolated: bool = False,
    ) -> "Step":
        """Enable info gathering for this step.

        Questions are presented one at a time via dynamic step instruction
        re-injection, producing zero ``tool_call`` and ``tool_result`` entries in the
        history the model sees. After calling this, use ``add_gather_question()`` to
        define the questions. Answers are stored in ``global_data``.

        Args:
            output_key: Key in global_data to store answers under (default: top-level)
            completion_action: Where to go when all questions are answered. Can be:
                - "next_step" to auto-advance to the next sequential step
                - A specific step name (e.g. "process_results") to jump to that step
                - None (default) to return to normal step mode after gathering
                The target must be valid: "next_step" requires a following step,
                and named steps must exist in the same context.
            prompt: Preamble text injected once when entering the gather step, giving
                the model personality/context for why it is asking these questions
            isolated: Default for every question in this gather. When True, a
                question is asked with the sibling Q&A hidden from the model, so
                it must ask rather than derive the answer from an earlier one.
                A question's own ``isolated`` overrides this. The hidden turns
                remain in the call log.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            intake = ctx.add_step("intake")
            intake.set_text("Collect patient information.")
            intake.set_gather_info(
                output_key="patient_info",
                completion_action="next_step",
                prompt="Be friendly and professional.",
            )
            intake.add_gather_question("full_name", "What is your full name?")
            ctx.add_step("review").set_text("Review the information collected.")
            ```
        """
        self._gather_info = GatherInfo(
            output_key=output_key,
            completion_action=completion_action,
            prompt=prompt,
            isolated=isolated,
        )
        return self

    def add_gather_question(
        self,
        key: str,
        question: str,
        type: str = "string",
        confirm: bool = False,
        prompt: str | None = None,
        functions: list[str] | None = None,
        isolated: bool | None = None,
        expected_answer: dict[str, int] | None = None,
    ) -> "Step":
        """Add a question to this step's gather_info configuration.

        ``set_gather_info()`` must be called before this method.

        IMPORTANT — gather mode locks function access:
            While the model is asking gather questions, the runtime forcibly
            deactivates ALL of the step's other functions. The only callable
            tools during a gather question are:

              - `gather_submit` (the native answer-submission tool)
              - Whatever names you list in this question's `functions` arg

            `next_step` and `change_context` are also filtered out — the model
            cannot navigate away until the gather completes. This is by design:
            it forces a tight ask → submit → next-question loop.

            If a question needs to call out to a tool (e.g. validate an email,
            geocode a ZIP), list that tool name in this question's `functions`.
            Functions listed here are active ONLY for this question.

        Args:
            key: Key name for storing the answer in global_data.
            question: The question text the model is instructed to ask.
            type: JSON schema type for the answer ("string", "integer",
                "number", "boolean"). Default: "string".
            confirm: If True, the model must read the answer back and obtain
                explicit user confirmation before submitting (the gather_submit
                schema gains a required `confirmed_by_user` parameter).
            prompt: Extra instruction text appended after the question.
            functions: Names of functions to unlock for this question only.
                These are activated on top of `gather_submit`. All other step
                functions remain locked out.
            isolated: Override the gather's ``isolated`` default for this one
                question. True hides the sibling Q&A while this question is
                asked; False keeps it visible even in an isolated gather.
                None (default) inherits the gather's setting.
            expected_answer: The number of digits the answer has, for the
                recognizer, as ``set_expected_answer`` takes it:
                ``{"digits": 5}`` or ``{"min_digits": 4, "max_digits": 6}``
                (``expected_answer()`` builds one). While this question is
                asked, it replaces the step's.

        Returns:
            This Step, for chaining.

        Raises:
            ValueError: If ``set_gather_info()`` has not been called first, or if
                ``expected_answer`` is not a valid expected answer.

        Example:
            ```python
            intake = ctx.add_step("intake")
            intake.set_text("Collect patient information.")
            intake.set_gather_info(output_key="patient_info")
            intake.add_gather_question("full_name", "Full name?", confirm=True)
            intake.add_gather_question(
                "insurance_id",
                "What is your insurance ID number?",
                functions=["verify_insurance"],
            )
            ctx.add_step("review").set_text("Review the information collected.")
            ```
        """
        if self._gather_info is None:
            raise ValueError("Must call set_gather_info() before add_gather_question()")
        self._gather_info.add_question(
            key=key,
            question=question,
            type=type,
            confirm=confirm,
            prompt=prompt,
            functions=functions,
            isolated=isolated,
            expected_answer=expected_answer,
        )
        return self

    def set_expected_answer(
        self,
        digits: int | None = None,
        *,
        min_digits: int | None = None,
        max_digits: int | None = None,
    ) -> "Step":
        """Tell the recognizer how many digits the caller's answer in this step
        has, such as a ZIP code or a PIN.

        The recognizer ends its wait for a number once the caller has said
        that many digits. A gather question's own expected answer replaces
        this while that question is asked. Pass ``digits`` for an exact count, or
        ``min_digits`` and ``max_digits`` for a range, each from 1 to 64.

        Args:
            digits: The exact number of digits.
            min_digits: The fewest digits, with ``max_digits``.
            max_digits: The most digits, with ``min_digits``.

        Returns:
            This Step, for chaining.

        Raises:
            ValueError: For a count or combination the platform would ignore.

        Example:
            ```python
            ctx.add_step("zip").set_text("Ask for the ZIP code.").set_expected_answer(5)
            ctx.add_step("pin").set_text("Ask for the PIN.").set_expected_answer(
                min_digits=4, max_digits=6
            )
            ```
        """
        self._expected_answer = expected_answer(
            digits, min_digits=min_digits, max_digits=max_digits
        )
        return self

    def clear_sections(self) -> "Step":
        """Remove all POM sections and direct text from this step.

        Lets the step be repopulated with new content, with either ``set_text()`` or
        the section methods.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            step = ctx.add_step("collect_info")
            step.add_section("Task", "Original instructions.")
            step.clear_sections()
            step.add_section("Task", "Updated instructions for this step.")
            ```
        """
        self._sections = []
        self._text = None
        return self

    def set_reset_system_prompt(self, system_prompt: str) -> "Step":
        """Set the system prompt this step's reset loads.

        A step with any reset setting is terminal: when the call enters it,
        the platform runs the reset in place of the step's text, and step
        mode ends there. Use it for a step that hands the call over to a new
        prompt.

        Args:
            system_prompt: New system prompt for the reset to load.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            transfer = ctx.add_step("transfer")
            transfer.set_text("Transfer the caller to billing.")
            transfer.set_reset_system_prompt(
                "You are now a billing specialist. Help with the invoice."
            )
            ```
        """
        self._reset_system_prompt = system_prompt
        return self

    def set_reset_user_prompt(self, user_prompt: str) -> "Step":
        """Set the user message this step's reset adds.

        A step with any reset setting is terminal: when the call enters it,
        the platform runs the reset in place of the step's text, and step
        mode ends there. Use it for a step that hands the call over to a new
        prompt.

        Args:
            user_prompt: User message for the reset to add.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            transfer = ctx.add_step("transfer")
            transfer.set_text("Transfer the caller to billing.")
            transfer.set_reset_user_prompt(
                "The customer needs help with their most recent invoice."
            )
            ```
        """
        self._reset_user_prompt = user_prompt
        return self

    def set_reset_consolidate(self, consolidate: bool) -> "Step":
        """Set whether this step's reset consolidates the conversation into a
        summary.

        A step with any reset setting is terminal: when the call enters it,
        the platform runs the reset in place of the step's text, and step
        mode ends there. Use it for a step that hands the call over to a new
        prompt.

        Args:
            consolidate: True to consolidate the previous conversation into a
                summary.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            transfer = ctx.add_step("transfer")
            transfer.set_text("Transfer the caller to billing.")
            transfer.set_reset_consolidate(True)
            ```
        """
        self._reset_consolidate = consolidate
        return self

    def set_reset_full_reset(self, full_reset: bool) -> "Step":
        """Set whether this step's reset replaces the system prompt, seeded with
        the consolidated summary, rather than adding to it.

        A step with any reset setting is terminal: when the call enters it,
        the platform runs the reset in place of the step's text, and step
        mode ends there. Use it for a step that hands the call over to a new
        prompt.

        Args:
            full_reset: True to replace the system prompt, seeded with the
                consolidated summary, rather than add to it.

        Returns:
            This Step, for chaining.

        Example:
            ```python
            transfer = ctx.add_step("transfer")
            transfer.set_text("Transfer the caller to billing.")
            transfer.set_reset_full_reset(True)
            ```
        """
        self._reset_full_reset = full_reset
        return self

    def _render_text(self) -> str:
        """Render the step's prompt text"""
        if self._text is not None:
            return self._text

        if not self._sections:
            raise ValueError(f"Step '{self.name}' has no text or POM sections defined")

        # Convert POM sections to markdown
        markdown_parts = []
        for section in self._sections:
            if "bullets" in section:
                markdown_parts.append(f"## {section['title']}")
                markdown_parts.extend(f"- {bullet}" for bullet in section["bullets"])
            else:
                markdown_parts.append(f"## {section['title']}")
                markdown_parts.append(section["body"])
            markdown_parts.append("")  # Add spacing

        return "\n".join(markdown_parts).strip()

    def to_dict(self) -> dict[str, Any]:
        """Convert the step to a dictionary for SWML generation.

        Returns:
            A dict with ``name`` and ``text`` (the rendered prompt), plus any of
            ``step_criteria``, ``functions``, ``valid_steps``, ``valid_contexts``,
            ``end``, ``skip_user_turn``, ``skip_to_next_step``, ``history``,
            ``expected_answer``, ``reset`` and ``gather_info`` that were set.

        Raises:
            ValueError: If the step has neither text nor POM sections.
        """
        step_dict: dict[str, Any] = {"name": self.name, "text": self._render_text()}

        if self._step_criteria:
            step_dict["step_criteria"] = self._step_criteria

        if self._functions is not None:
            step_dict["functions"] = self._functions

        if self._valid_steps is not None:
            step_dict["valid_steps"] = self._valid_steps

        if self._valid_contexts is not None:
            step_dict["valid_contexts"] = self._valid_contexts

        if self._end:
            step_dict["end"] = True

        if self._skip_user_turn:
            step_dict["skip_user_turn"] = True

        if self._skip_to_next_step:
            step_dict["skip_to_next_step"] = True

        if self._history is not None:
            step_dict["history"] = self._history

        if self._expected_answer is not None:
            step_dict["expected_answer"] = dict(self._expected_answer)

        # Add reset object if any reset parameters are set
        reset_obj: dict[str, Any] = {}
        if self._reset_system_prompt is not None:
            reset_obj["system_prompt"] = self._reset_system_prompt
        if self._reset_user_prompt is not None:
            reset_obj["user_prompt"] = self._reset_user_prompt
        if self._reset_consolidate:
            reset_obj["consolidate"] = self._reset_consolidate
        if self._reset_full_reset:
            reset_obj["full_reset"] = self._reset_full_reset

        if reset_obj:
            step_dict["reset"] = reset_obj

        if self._gather_info is not None:
            step_dict["gather_info"] = self._gather_info.to_dict()

        return step_dict


class Context:
    """A named conversation mode containing an ordered list of steps.

    A context is a distinct mode of the conversation, such as "sales", "support"
    or "billing". It holds an ordered sequence of ``Step`` objects and
    configures its own prompt, system prompt, fillers and navigation rules. You
    get one by calling ``ContextBuilder.add_context()`` or
    ``ContextBuilder.get_context()``. When a builder holds a single context, that
    context must be named ``"default"``.

    Conversation history across context switches
    --------------------------------------------
    By default (`isolated=False`), switching from one context to another
    via `change_context` PRESERVES the entire conversation history. The
    user's prior turns and the model's prior responses remain visible
    on the next LLM call. The only thing that changes is which step
    instructions get injected.

    A common confusion: "the AI re-asked for information the user already
    gave." If you see this, history loss is almost never the cause —
    history is preserved unless you set `isolated=True`. The real cause
    is usually one of:

      - The destination step's `text` literally tells the model to ask
        ("Ask the user for their account number"). The model follows
        instructions; rephrase to "Confirm the user's account number"
        or have the step instructions check global_data first.
      - The relevant info was never extracted into global_data, so
        ${var} expansion has nothing to inject and the step prompt
        looks generic. Add a webhook that captures the field.
      - You explicitly called `set_isolated(True)` on the destination
        context. Isolated contexts wipe the conversation array on entry.
        Pair with `set_consolidate(True)` if you want a summary instead.

    See Context.set_isolated() for the wipe semantics, and the SDK's
    FunctionResult.swml_change_step / swml_change_context docstrings
    for how to communicate transition intent through tool response text
    and global_data.

    Example:
        ```python
        contexts = agent.define_contexts()
        main = contexts.add_context("default")
        main.add_step("menu").set_text("Ask whether the caller needs support.")
        main.set_valid_contexts(["support"])

        support = contexts.add_context("support")
        support.set_system_prompt("You are a patient technical support engineer.")
        support.add_enter_filler("en-US", ["Let me connect you with support..."])
        support.set_valid_contexts(["default"])
        support.add_step(
            "diagnose",
            task="Understand the customer's issue.",
            criteria="Issue is clearly identified",
            valid_steps=["next"],
        )
        support.add_step("farewell").set_text("Thank the caller.").set_end(True)
        ```
    """

    def __init__(self, name: str):
        """Create a context.

        Args:
            name: Unique context name. When the builder holds a single context, it
                must be ``"default"``.
        """
        self.name = name
        self._steps: dict[str, Step] = {}
        self._step_order: list[str] = []
        self._valid_contexts: list[str] | None = None
        self._valid_steps: list[str] | None = None
        self._initial_step: str | None = None

        # Context entry parameters
        self._post_prompt: str | None = None
        self._system_prompt: str | None = None
        self._system_prompt_sections: list[
            dict[str, Any]
        ] = []  # For POM-style system prompts
        self._consolidate: bool = False
        self._full_reset: bool = False
        self._user_prompt: str | None = None
        self._isolated: bool = False

        # Context prompt (separate from system_prompt)
        self._prompt_text: str | None = None
        self._prompt_sections: list[dict[str, Any]] = []

        # Context fillers
        self._enter_fillers: dict[str, list[str]] | None = None
        self._exit_fillers: dict[str, list[str]] | None = None

        # Default visibility mode for the steps in this context
        self._history: str | None = None

    def add_step(
        self,
        name: str,
        *,
        task: str | None = None,
        bullets: list[str] | None = None,
        criteria: str | None = None,
        functions: str | list[str] | None = None,
        valid_steps: list[str] | None = None,
    ) -> Step:
        """Add a new step to this context.

        When called with only ``name`` the returned Step can be configured
        with the usual method-chaining API. When the optional keyword
        arguments are supplied the step is fully configured in one call.

        Args:
            name: Step name (must be unique within the context).
            task: Text for the "Task" section (equivalent to
                ``step.add_section("Task", task)``).
            bullets: List of bullet strings for the "Process" section
                (equivalent to ``step.add_bullets("Process", bullets)``).
                Requires *task* to also be set.
            criteria: Step-completion criteria (equivalent to
                ``step.set_step_criteria(criteria)``).
            functions: Tool names the step may call, or ``"none"``
                (equivalent to ``step.set_functions(functions)``).
            valid_steps: Names of steps the agent may transition to
                (equivalent to ``step.set_valid_steps(valid_steps)``).

        Returns:
            The new Step, for optional further chaining.

        Raises:
            ValueError: If a step with this name already exists in the context, or
                the context already holds 100 steps.

        Example:
            ```python
            ctx = agent.define_contexts().add_context("default")
            ctx.add_step(
                "get_name",
                task="Ask for the customer's full name.",
                criteria="Customer has provided their full name",
                valid_steps=["get_email"],
            )
            ctx.add_step("get_email").set_text("Ask for the customer's email address.")
            ```
        """
        if name in self._steps:
            raise ValueError(f"Step '{name}' already exists in context '{self.name}'")

        if len(self._steps) >= MAX_STEPS_PER_CONTEXT:
            raise ValueError(
                f"Maximum steps per context ({MAX_STEPS_PER_CONTEXT}) exceeded"
            )

        step = Step(name)
        self._steps[name] = step
        self._step_order.append(name)

        if task is not None:
            step.add_section("Task", task)
        if bullets is not None:
            step.add_bullets("Process", bullets)
        if criteria is not None:
            step.set_step_criteria(criteria)
        if functions is not None:
            step.set_functions(functions)
        if valid_steps is not None:
            step.set_valid_steps(valid_steps)

        return step

    def get_step(self, name: str) -> Optional["Step"]:
        """Get an existing step by name for inspection or modification.

        Args:
            name: Step name to look up.

        Returns:
            The Step if found, None otherwise.

        Example:
            ```python
            ctx.add_step("collect_info").set_text("Collect the account information.")
            step = ctx.get_step("collect_info")
            if step is not None:
                step.set_functions(["verify_identity"])
            ```
        """
        return self._steps.get(name)

    def remove_step(self, name: str) -> "Context":
        """Remove a step from this context entirely.

        Does nothing if the context has no step with this name.

        Args:
            name: Name of the step to remove.

        Returns:
            This Context, for chaining.

        Example:
            ```python
            ctx.add_step("obsolete_step").set_text("No longer needed.")
            ctx.remove_step("obsolete_step")
            ```
        """
        if name in self._steps:
            del self._steps[name]
            self._step_order = [s for s in self._step_order if s != name]
        return self

    def move_step(self, name: str, position: int) -> "Context":
        """Move an existing step to a specific position in the step order.

        Args:
            name: Name of the step to move.
            position: Target index in the step order. ``0`` places the step first.

        Returns:
            This Context, for chaining.

        Raises:
            ValueError: If the context has no step with this name.

        Example:
            ```python
            ctx.add_step("collect_info").set_text("Collect the caller's information.")
            ctx.add_step("confirm").set_text("Confirm the details with the caller.")
            ctx.move_step("confirm", 0)
            ```
        """
        if name not in self._steps:
            raise ValueError(f"Step '{name}' not found in context '{self.name}'")
        self._step_order.remove(name)
        self._step_order.insert(position, name)
        return self

    def set_valid_contexts(self, contexts: list[str]) -> "Context":
        """Set which contexts can be navigated to from this context.

        Acts as a context-level default. A step's own ``Step.set_valid_contexts()``
        overrides it for that step. ``ContextBuilder.validate()`` rejects a name that
        is not a context in the builder.

        Args:
            contexts: Context names reachable from this context.

        Returns:
            This Context, for chaining.

        Example:
            ```python
            support = agent.define_contexts().add_context("support")
            support.set_valid_contexts(["default", "billing"])
            ```
        """
        self._valid_contexts = contexts
        return self

    def set_valid_steps(self, steps: list[str]) -> "Context":
        """Set which steps can be navigated to from any step in this context.

        Acts as a context-level default. A step's own ``Step.set_valid_steps()``
        takes precedence when set. ``ContextBuilder.validate()`` rejects a name that
        is not a step in this context, other than ``"next"``.

        Args:
            steps: Step names. Include ``"next"`` to allow sequential advancement.

        Returns:
            This Context, for chaining.

        Example:
            ```python
            ctx = agent.define_contexts().add_context("default")
            ctx.set_valid_steps(["next", "cancel"])
            ctx.add_step("greet").set_text("Welcome the caller.")
            ctx.add_step("cancel").set_text("Cancel the process and say goodbye.")
            ```
        """
        self._valid_steps = steps
        return self

    def set_initial_step(self, step_name: str) -> "Context":
        """Set which step the context starts on when entered.

        By default, a context starts on its first step (index 0). If the
        context has a preamble step that should only run on first entry
        (e.g. a greeting), later entries via ``change_context`` can skip
        it by setting ``initial_step`` to the name of the step to start
        from instead.

        ``initial_step`` is honoured both at conversation creation (when
        the context is first activated) and when switching to this context
        via ``change_context`` during the conversation.

        Args:
            step_name: Name of the step to start on. Must exist in this
                context's step list; validated by ContextBuilder.validate().

        Returns:
            This Context, for chaining.

        Example:
            ```python
            ctx = agent.define_contexts().add_context("default")
            ctx.add_step("greeting").set_text("Welcome!")
            ctx.add_step("triage").set_text("What do you need help with?")
            ctx.set_initial_step("triage")  # skip greeting on re-entry
            ```
        """
        self._initial_step = step_name
        return self

    def set_post_prompt(self, post_prompt: str) -> "Context":
        """Set a post-prompt override for this context.

        Overrides the post-prompt text while this context is active.

        Args:
            post_prompt: Post-prompt text to use when this context is active.

        Returns:
            This Context, for chaining.

        Example:
            ```python
            billing = agent.define_contexts().add_context("default")
            billing.set_post_prompt("Summarize the billing issue and resolution.")
            ```
        """
        self._post_prompt = post_prompt
        return self

    def set_system_prompt(self, system_prompt: str) -> "Context":
        """Set a system prompt that takes effect when this context is entered.

        Setting a system prompt triggers a context reset when the context is entered.
        Cannot be combined with ``add_system_section()`` or ``add_system_bullets()``.

        Args:
            system_prompt: New system prompt for this context.

        Returns:
            This Context, for chaining.

        Raises:
            ValueError: If system prompt sections were already added with
                ``add_system_section()`` or ``add_system_bullets()``.

        Example:
            ```python
            support = agent.define_contexts().add_context("default")
            support.set_system_prompt("You are a patient technical support engineer.")
            ```
        """
        if self._system_prompt_sections:
            raise ValueError(
                "Cannot use set_system_prompt() when POM sections have been added for system prompt. Use one approach or the other."
            )
        self._system_prompt = system_prompt
        return self

    def set_consolidate(self, consolidate: bool) -> "Context":
        """Set whether to consolidate conversation history when entering this context.

        When True, the platform summarizes the previous conversation instead of
        carrying it over in full, which reduces token usage while preserving key
        information. It takes effect only together with a system prompt (see
        ``set_system_prompt()``).

        Args:
            consolidate: True to consolidate the previous conversation on entry.

        Returns:
            This Context, for chaining.

        Example:
            ```python
            support = agent.define_contexts().add_context("default")
            support.set_consolidate(True)
            support.set_system_prompt("You are a patient technical support engineer.")
            ```
        """
        self._consolidate = consolidate
        return self

    def set_full_reset(self, full_reset: bool) -> "Context":
        """Set whether to do a full reset when entering this context.

        When True, the system prompt is completely replaced rather than having
        additional instructions injected. It takes effect only together with a system
        prompt (see ``set_system_prompt()``).

        Args:
            full_reset: True to replace the system prompt on entry, False to inject
                instead.

        Returns:
            This Context, for chaining.

        Example:
            ```python
            escalation = agent.define_contexts().add_context("default")
            escalation.set_full_reset(True)
            escalation.set_system_prompt("You are a senior escalation specialist.")
            ```
        """
        self._full_reset = full_reset
        return self

    def set_user_prompt(self, user_prompt: str) -> "Context":
        """Set a user message to inject when entering this context.

        Useful for triggering the AI to speak first after a context switch. It takes
        effect only together with a system prompt (see ``set_system_prompt()``).

        Args:
            user_prompt: User message to inject on entry.

        Returns:
            This Context, for chaining.

        Example:
            ```python
            sales = agent.define_contexts().add_context("default")
            sales.set_system_prompt("You are a friendly sales representative.")
            sales.set_user_prompt("I'd like to learn about your products.")
            ```
        """
        self._user_prompt = user_prompt
        return self

    def set_history(self, history: str) -> "Context":
        """Set the default visibility mode for every step in this context.

        A step's own ``set_history()`` overrides this. See ``Step.set_history``
        for what each mode does.

        Args:
            history: One of ``"keep"``, ``"default"``, ``"hide"``, ``"isolate"`` or
                ``"spoken"``.

        Returns:
            This Context, for chaining.

        Raises:
            ValueError: If ``history`` is not one of these modes.

        Example:
            ```python
            ctx = agent.define_contexts().add_context("default").set_history("hide")
            ctx.add_step("greet").set_text("Greet the caller.")
            ctx.add_step("help").set_text("Previously: ${step_history.prev.summary}.")
            ```
        """
        self._history = _validate_history(history)
        return self

    def set_isolated(self, isolated: bool) -> "Context":
        """Mark this context as isolated — entering it wipes conversation history.

        When `isolated=True` and the context is entered via change_context,
        the runtime calls ai_conversation_restart(), which drops every
        conversation entry but the first, the base system prompt. The model
        starts fresh with the base prompt and the new context's step
        instructions, with no memory of prior turns.

        EXCEPTION — `reset` overrides the wipe:
            If the context also has a `reset` configuration (set via the
            Step.set_reset_*() methods on a step that switches into this
            context, or via set_consolidate() / set_full_reset() on the
            context itself), the wipe is skipped in favor of the reset
            behavior. Use `reset` with `consolidate=True` to summarize prior
            history into a single message instead of dropping it entirely.

        Use cases:
            - Switching to a sensitive billing flow that should not see
              prior small-talk
            - Handing off to a different agent persona
            - Resetting after a long off-topic detour

        Args:
            isolated: True to wipe conversation history on context entry
                (subject to the reset exception above).

        Returns:
            This Context, for chaining.

        Example:
            ```python
            secure = agent.define_contexts().add_context("default")
            secure.set_isolated(True)
            secure.add_step("verify").set_text("Ask for the caller's account PIN.")
            ```
        """
        self._isolated = isolated
        return self

    def add_system_section(self, title: str, body: str) -> "Context":
        """Add a POM section to the system prompt.

        Cannot be combined with ``set_system_prompt()``.

        Args:
            title: Section heading.
            body: Section body text.

        Returns:
            This Context, for chaining.

        Raises:
            ValueError: If ``set_system_prompt()`` was already used on this context.

        Example:
            ```python
            billing = agent.define_contexts().add_context("default")
            billing.add_system_section("Role", "You are a billing specialist.")
            billing.add_system_section("Tone", "Be professional and empathetic.")
            ```
        """
        if self._system_prompt is not None:
            raise ValueError(
                "Cannot add POM sections for system prompt when set_system_prompt() has been used. Use one approach or the other."
            )
        self._system_prompt_sections.append({"title": title, "body": body})
        return self

    def add_system_bullets(self, title: str, bullets: list[str]) -> "Context":
        """Add a POM section with bullet points to the system prompt.

        Cannot be combined with ``set_system_prompt()``.

        Args:
            title: Section heading.
            bullets: List of bullet point strings.

        Returns:
            This Context, for chaining.

        Raises:
            ValueError: If ``set_system_prompt()`` was already used on this context.

        Example:
            ```python
            support = agent.define_contexts().add_context("default")
            support.add_system_bullets("Guidelines", [
                "Verify identity before making changes",
                "Offer to escalate if the issue is unresolved after 5 minutes",
            ])
            ```
        """
        if self._system_prompt is not None:
            raise ValueError(
                "Cannot add POM sections for system prompt when set_system_prompt() has been used. Use one approach or the other."
            )
        self._system_prompt_sections.append({"title": title, "bullets": bullets})
        return self

    def set_prompt(self, prompt: str) -> "Context":
        """Set the context's prompt text directly.

        Cannot be combined with ``add_section()`` or ``add_bullets()``.

        Args:
            prompt: Plain-text prompt for this context.

        Returns:
            This Context, for chaining.

        Raises:
            ValueError: If POM sections were already added with ``add_section()`` or
                ``add_bullets()``.

        Example:
            ```python
            ctx = agent.define_contexts().add_context("default")
            ctx.set_prompt("You handle billing inquiries. Be concise and accurate.")
            ```
        """
        if self._prompt_sections:
            raise ValueError(
                "Cannot use set_prompt() when POM sections have been added. Use one approach or the other."
            )
        self._prompt_text = prompt
        return self

    def add_section(self, title: str, body: str) -> "Context":
        """Add a POM section to the context prompt.

        Cannot be combined with ``set_prompt()``.

        Args:
            title: Section heading.
            body: Section body text.

        Returns:
            This Context, for chaining.

        Raises:
            ValueError: If ``set_prompt()`` was already used on this context.

        Example:
            ```python
            ctx = agent.define_contexts().add_context("default")
            ctx.add_section("Role", "You are a billing specialist.")
            ctx.add_section("Guidelines", "Always verify account ownership first.")
            ```
        """
        if self._prompt_text is not None:
            raise ValueError(
                "Cannot add POM sections when set_prompt() has been used. Use one approach or the other."
            )
        self._prompt_sections.append({"title": title, "body": body})
        return self

    def add_bullets(self, title: str, bullets: list[str]) -> "Context":
        """Add a POM section with bullet points to the context prompt.

        Cannot be combined with ``set_prompt()``.

        Args:
            title: Section heading.
            bullets: List of bullet point strings.

        Returns:
            This Context, for chaining.

        Raises:
            ValueError: If ``set_prompt()`` was already used on this context.

        Example:
            ```python
            ctx = agent.define_contexts().add_context("default")
            ctx.add_bullets("Rules", [
                "Never share account numbers with the caller",
                "Always confirm changes before applying",
            ])
            ```
        """
        if self._prompt_text is not None:
            raise ValueError(
                "Cannot add POM sections when set_prompt() has been used. Use one approach or the other."
            )
        self._prompt_sections.append({"title": title, "bullets": bullets})
        return self

    def set_enter_fillers(self, enter_fillers: dict[str, list[str]]) -> "Context":
        """Set all enter fillers at once.

        Fillers are short phrases the AI says when entering a context, giving the
        caller a natural transition. An empty value, or one that is not a dict, is
        ignored.

        Args:
            enter_fillers: Dictionary mapping language codes (or ``"default"``) to
                lists of filler phrases.

        Returns:
            This Context, for chaining.

        Example:
            ```python
            support = agent.define_contexts().add_context("default")
            support.set_enter_fillers({
                "en-US": ["Let me transfer you...", "One moment please..."],
                "es": ["Un momento por favor..."],
            })
            ```
        """
        if enter_fillers and isinstance(enter_fillers, dict):
            self._enter_fillers = enter_fillers
        return self

    def set_exit_fillers(self, exit_fillers: dict[str, list[str]]) -> "Context":
        """Set all exit fillers at once.

        Exit fillers are phrases the AI says when it navigates away from this
        context. An empty value, or one that is not a dict, is ignored.

        Args:
            exit_fillers: Dictionary mapping language codes (or ``"default"``) to
                lists of filler phrases.

        Returns:
            This Context, for chaining.

        Example:
            ```python
            support = agent.define_contexts().add_context("default")
            support.set_exit_fillers({
                "en-US": ["Thank you for contacting support.", "Glad I could help."],
                "default": ["Thank you."],
            })
            ```
        """
        if exit_fillers and isinstance(exit_fillers, dict):
            self._exit_fillers = exit_fillers
        return self

    def add_enter_filler(self, language_code: str, fillers: list[str]) -> "Context":
        """Add enter fillers for a specific language.

        Replaces any fillers already set for that language. Does nothing if
        ``language_code`` or ``fillers`` is empty.

        Args:
            language_code: Language code, such as ``"en-US"`` or ``"es"``, or
                ``"default"`` for a catch-all.
            fillers: List of filler phrases for entering this context.

        Returns:
            This Context, for chaining.

        Example:
            ```python
            support = agent.define_contexts().add_context("default")
            support.add_enter_filler("en-US", [
                "Let me connect you with support...",
                "Transferring you now...",
            ])
            ```
        """
        if language_code and fillers and isinstance(fillers, list):
            if self._enter_fillers is None:
                self._enter_fillers = {}
            self._enter_fillers[language_code] = fillers
        return self

    def add_exit_filler(self, language_code: str, fillers: list[str]) -> "Context":
        """Add exit fillers for a specific language.

        Replaces any fillers already set for that language. Does nothing if
        ``language_code`` or ``fillers`` is empty.

        Args:
            language_code: Language code, such as ``"en-US"`` or ``"es"``, or
                ``"default"`` for a catch-all.
            fillers: List of filler phrases for exiting this context.

        Returns:
            This Context, for chaining.

        Example:
            ```python
            support = agent.define_contexts().add_context("default")
            support.add_exit_filler("en-US", [
                "Thank you for contacting support.",
                "Glad I could help.",
            ])
            ```
        """
        if language_code and fillers and isinstance(fillers, list):
            if self._exit_fillers is None:
                self._exit_fillers = {}
            self._exit_fillers[language_code] = fillers
        return self

    def _render_prompt(self) -> str | None:
        """Render the context's prompt text"""
        if self._prompt_text is not None:
            return self._prompt_text

        if not self._prompt_sections:
            return None

        # Convert POM sections to markdown
        markdown_parts = []
        for section in self._prompt_sections:
            if "bullets" in section:
                markdown_parts.append(f"## {section['title']}")
                markdown_parts.extend(f"- {bullet}" for bullet in section["bullets"])
            else:
                markdown_parts.append(f"## {section['title']}")
                markdown_parts.append(section["body"])
            markdown_parts.append("")  # Add spacing

        return "\n".join(markdown_parts).strip()

    def _render_system_prompt(self) -> str | None:
        """Render the system prompt text"""
        if self._system_prompt is not None:
            return self._system_prompt

        if not self._system_prompt_sections:
            return None

        # Convert POM sections to markdown
        markdown_parts = []
        for section in self._system_prompt_sections:
            if "bullets" in section:
                markdown_parts.append(f"## {section['title']}")
                markdown_parts.extend(f"- {bullet}" for bullet in section["bullets"])
            else:
                markdown_parts.append(f"## {section['title']}")
                markdown_parts.append(section["body"])
            markdown_parts.append("")  # Add spacing

        return "\n".join(markdown_parts).strip()

    def to_dict(self) -> dict[str, Any]:
        """Convert the context to a dictionary for SWML generation.

        Returns:
            A dict with ``steps`` (a list of step dicts in order), plus any of
            ``valid_contexts``, ``valid_steps``, ``initial_step``, ``post_prompt``,
            ``system_prompt``, ``consolidate``, ``full_reset``, ``user_prompt``,
            ``isolated``, ``pom`` or ``prompt``, ``enter_fillers``, ``exit_fillers``
            and ``history`` that were set.

        Raises:
            ValueError: If the context has no steps, or a step has neither text nor
                POM sections.
        """
        if not self._steps:
            raise ValueError(f"Context '{self.name}' has no steps defined")

        context_dict: dict[str, Any] = {
            "steps": [self._steps[name].to_dict() for name in self._step_order]
        }

        if self._valid_contexts is not None:
            context_dict["valid_contexts"] = self._valid_contexts

        if self._valid_steps is not None:
            context_dict["valid_steps"] = self._valid_steps

        if self._initial_step is not None:
            context_dict["initial_step"] = self._initial_step

        # Add context entry parameters
        if self._post_prompt is not None:
            context_dict["post_prompt"] = self._post_prompt

        rendered_system_prompt = self._render_system_prompt()
        if rendered_system_prompt is not None:
            context_dict["system_prompt"] = rendered_system_prompt

        if self._consolidate:
            context_dict["consolidate"] = self._consolidate

        if self._full_reset:
            context_dict["full_reset"] = self._full_reset

        if self._user_prompt is not None:
            context_dict["user_prompt"] = self._user_prompt

        if self._isolated:
            context_dict["isolated"] = self._isolated

        # Add context prompt - use POM structure if sections exist, otherwise use string
        if self._prompt_sections:
            # Use structured POM format
            context_dict["pom"] = self._prompt_sections
        elif self._prompt_text is not None:
            # Use string format
            context_dict["prompt"] = self._prompt_text

        # Add enter and exit fillers if defined
        if self._enter_fillers is not None:
            context_dict["enter_fillers"] = self._enter_fillers

        if self._exit_fillers is not None:
            context_dict["exit_fillers"] = self._exit_fillers

        if self._history is not None:
            context_dict["history"] = self._history

        return context_dict


#: Reserved tool names auto-injected by the runtime when contexts/steps are
#: present. User-defined SWAIG tools must not collide with these names.
RESERVED_NATIVE_TOOL_NAMES = frozenset(
    {
        "next_step",
        "change_context",
        "gather_submit",
    }
)


class ContextBuilder:
    r"""Builder for multi-step, multi-context AI agent workflows.

    A ContextBuilder owns one or more Contexts; each Context owns an ordered
    list of Steps. Only one context and one step is active at a time. Per
    chat turn, the runtime injects the current step's instructions as a
    system message, then asks the LLM for a response.

    Native tools auto-injected by the runtime
    -----------------------------------------
    When a step (or its enclosing context) declares `valid_steps` or
    `valid_contexts`, the runtime auto-injects two native tools so the model
    can navigate the flow:

      - ``next_step(step: enum)``        — present when valid_steps is set
      - ``change_context(context: enum)`` — present when valid_contexts is set

    Their `enum` schemas are rewritten when a step loads, to match whatever
    valid_steps / valid_contexts apply to that step. You do NOT need
    to define these tools yourself; they appear automatically.

    A third native tool — ``gather_submit`` — is injected during gather_info
    questioning (see Step.set_gather_info / add_gather_question).

    These three names — ``next_step``, ``change_context``, ``gather_submit``
    — are reserved. ContextBuilder.validate() will reject any agent that
    defines a SWAIG tool with one of these names.

    Function whitelisting (Step.set_functions)
    ------------------------------------------
    Each step may declare a `functions` whitelist. The whitelist is applied
    in-memory at the start of each LLM turn. CRITICALLY: if a step does NOT
    declare a `functions` field, it INHERITS the previous step's active set.
    See Step.set_functions() for details and examples.

    Validation
    ----------
    Call validate() (or to_dict(), which calls it) to check that:

      - At least one context is defined
      - A single context must be named "default"
      - Every context has at least one step
      - valid_steps references resolve to real step names (or "next")
      - valid_contexts references resolve to real context names
      - gather_info questions are non-empty and have unique keys
      - gather_info completion_action targets a reachable step
      - No user-defined SWAIG tool collides with a reserved native name

    Limits:
        A builder holds at most 50 contexts, and a context at most 100 steps.

    Note:
        You rarely create a ContextBuilder directly. Call
        ``agent.define_contexts()``, which creates the builder and wires it into
        SWML generation. The builder validates the whole context tree when the
        SWML document is rendered.

    Example:
        ```python
        contexts = agent.define_contexts()
        order = contexts.add_context("default")
        order.add_step("get_item") \
            .set_text("Ask what item they want to order.") \
            .set_step_criteria("Customer has specified an item") \
            .set_valid_steps(["get_quantity"])
        order.add_step("get_quantity") \
            .set_text("Ask how many they want.") \
            .set_valid_steps(["confirm"])
        order.add_step("confirm") \
            .set_text("Confirm the order details and thank them.") \
            .set_end(True)
        ```
    """

    def __init__(self, agent: Any) -> None:
        """Create a builder.

        Args:
            agent: The agent that owns these contexts, or None. It is used to check
                tool names when validating. Normally ``AgentBase.define_contexts()``
                creates the builder, so you do not call this directly.
        """
        self._agent = agent
        self._contexts: dict[str, Context] = {}
        self._context_order: list[str] = []
        # Design warnings already reported, so a render on every request
        # doesn't repeat them. The agent's set is used when there is one: a
        # per-request copy deep-copies this builder, but shares the agent's
        # attributes
        self._warned_here: set[tuple[str, ...]] = set()

    def reset(self) -> "ContextBuilder":
        """Remove all contexts, returning the builder to its initial state.

        Use this in a dynamic config callback when you need to rebuild
        contexts from scratch for a specific request — e.g. skipping a
        greeting context on transfers.

        For convenience at the agent level, ``AgentBase.reset_contexts()`` wraps
        ``define_contexts().reset()``.

        Returns:
            This ContextBuilder, for chaining.

        Example:
            ```python
            def on_dynamic_config(query, body, headers, agent):
                if query.get("transfer"):
                    agent.define_contexts().reset()
                    ctx = agent.define_contexts().add_context("default")
                    ctx.add_step("route").set_text("Route the caller.")
            ```
        """
        self._contexts.clear()
        self._context_order.clear()
        return self

    def add_context(self, name: str) -> Context:
        """Add a new context and return it.

        A builder with a single context must name it ``"default"``, or validation
        fails. A builder with several contexts can use any names.

        Args:
            name: Unique context name.

        Returns:
            The new Context, ready for adding steps.

        Raises:
            ValueError: If a context with this name already exists, or the builder
                already holds 50 contexts.

        Example:
            ```python
            contexts = agent.define_contexts()
            main = contexts.add_context("default")
            sales = contexts.add_context("sales")
            main.add_step("menu").set_text("Ask whether the caller needs sales.")
            main.set_valid_contexts(["sales"])
            sales.add_step("qualify").set_text("Understand what product they want.")
            ```
        """
        if name in self._contexts:
            raise ValueError(f"Context '{name}' already exists")

        if len(self._contexts) >= MAX_CONTEXTS:
            raise ValueError(f"Maximum number of contexts ({MAX_CONTEXTS}) exceeded")

        context = Context(name)
        self._contexts[name] = context
        self._context_order.append(name)
        return context

    def get_context(self, name: str) -> Context | None:
        """Get an existing context by name for inspection or modification.

        Args:
            name: Context name.

        Returns:
            The Context if found, None otherwise.

        Example:
            ```python
            contexts = agent.define_contexts()
            contexts.add_context("default")
            ctx = contexts.get_context("default")
            ```
        """
        return self._contexts.get(name)

    def validate(self) -> None:
        """Validate the whole context configuration tree.

        Called automatically when the SWML document is rendered (``to_dict()`` calls
        it), but you can call it yourself to catch errors early.

        Checks performed:

        - At least one context exists.
        - A single context is named ``"default"``.
        - Every context has at least one step.
        - Every context's ``initial_step``, when set, names a step in that context.
        - Every step-level ``valid_steps`` entry names a step in the same context
          (the special value ``"next"`` is always allowed).
        - Every context-level and step-level ``valid_contexts`` entry names a context
          in the builder.
        - Every ``gather_info`` has at least one question, no duplicate question
          keys, and a valid ``completion_action``: ``"next_step"`` needs a step after
          it, and any other value must name a step in the same context.
        - When the builder is attached to an agent, no user-defined tool shares a
          name with a reserved native tool (``next_step``, ``change_context``,
          ``gather_submit``).
        - When the builder is attached to an agent, every name a step passes to
          ``set_functions([...])`` is a registered SWAIG tool or a reserved native
          tool. ``"none"`` and ``[]`` mean disable all and are never treated as
          references.

        It also logs design warnings, without raising, for settings that do not do
        what they read as, such as a tool no step offers, a tool named in a step that
        does not offer it, and reset settings that have no effect.

        Returns:
            None. Raises ``ValueError`` when validation fails.

        Raises:
            ValueError: If any check above fails. The message names the context,
                step or tool at fault.

        Example:
            ```python
            contexts = agent.define_contexts()
            ctx = contexts.add_context("default")
            ctx.add_step("greet").set_text("Hello!")
            try:
                contexts.validate()
            except ValueError as e:
                print(f"Invalid context config: {e}")
            ```
        """
        if not self._contexts:
            raise ValueError("At least one context must be defined")

        # If only one context, it must be named "default"
        if len(self._contexts) == 1:
            context_name = next(iter(self._contexts.keys()))
            if context_name != "default":
                raise ValueError(
                    "When using a single context, it must be named 'default'"
                )

        # Validate each context has at least one step
        for context_name, context in self._contexts.items():
            if not context._steps:
                raise ValueError(
                    f"Context '{context_name}' must have at least one step"
                )

        # Validate initial_step references a real step in the context
        for context_name, context in self._contexts.items():
            if (
                context._initial_step is not None
                and context._initial_step not in context._steps
            ):
                available = sorted(context._steps.keys())
                raise ValueError(
                    f"Context '{context_name}' has initial_step='{context._initial_step}' "
                    f"but that step does not exist. Available steps: {available}"
                )

        # Validate step references in valid_steps
        for context_name, context in self._contexts.items():
            for step_name, step in context._steps.items():
                if step._valid_steps:
                    for valid_step in step._valid_steps:
                        if valid_step != "next" and valid_step not in context._steps:
                            raise ValueError(
                                f"Step '{step_name}' in context '{context_name}' "
                                f"references unknown step '{valid_step}'"
                            )

        # Validate context references in valid_contexts (context-level)
        for context_name, context in self._contexts.items():
            if context._valid_contexts:
                for valid_context in context._valid_contexts:
                    if valid_context not in self._contexts:
                        raise ValueError(
                            f"Context '{context_name}' references unknown context '{valid_context}'"
                        )

        # Validate context references in valid_contexts (step-level)
        for context_name, context in self._contexts.items():
            for step_name, step in context._steps.items():
                if hasattr(step, "_valid_contexts") and step._valid_contexts:
                    for valid_context in step._valid_contexts:
                        if valid_context not in self._contexts:
                            raise ValueError(
                                f"Step '{step_name}' in context '{context_name}' "
                                f"references unknown context '{valid_context}'"
                            )

        # Validate gather_info configurations
        for context_name, context in self._contexts.items():
            for step_name, step in context._steps.items():
                if step._gather_info is not None:
                    if not step._gather_info._questions:
                        raise ValueError(
                            f"Step '{step_name}' in context '{context_name}' "
                            f"has gather_info with no questions"
                        )
                    keys_seen = set()
                    for q in step._gather_info._questions:
                        if q.key in keys_seen:
                            raise ValueError(
                                f"Step '{step_name}' in context '{context_name}' "
                                f"has duplicate gather_info question key '{q.key}'"
                            )
                        keys_seen.add(q.key)

                    # Validate completion_action references a reachable step
                    action = step._gather_info._completion_action
                    if action is not None:
                        if action == "next_step":
                            # "next_step" requires a subsequent step in the order
                            step_idx = context._step_order.index(step_name)
                            if step_idx >= len(context._step_order) - 1:
                                raise ValueError(
                                    f"Step '{step_name}' in context '{context_name}' "
                                    f"has gather_info completion_action='next_step' "
                                    f"but it is the last step in the context. Either "
                                    f"(1) add another step after '{step_name}', "
                                    f"(2) set completion_action to the name of an "
                                    f"existing step in this context to jump to it, or "
                                    f"(3) set completion_action=None (default) to stay "
                                    f"in '{step_name}' after gathering completes."
                                )
                        elif action not in context._steps:
                            available = sorted(context._steps.keys())
                            raise ValueError(
                                f"Step '{step_name}' in context '{context_name}' "
                                f"has gather_info completion_action='{action}' "
                                f"but '{action}' is not a step in this context. "
                                f"Valid options: 'next_step' (advance to the next "
                                f"sequential step), None (stay in the current step), "
                                f"or one of {available}."
                            )

        # Validate that user-defined tools do not collide with reserved native
        # tool names. The runtime auto-injects next_step / change_context /
        # gather_submit when contexts/steps are present, so user tools sharing
        # those names would never be called.
        if self._agent is not None:
            tool_registry = getattr(self._agent, "_tool_registry", None)
            registered = (
                getattr(tool_registry, "_swaig_functions", None)
                if tool_registry
                else None
            )
            # Only run the collision check against a real dict — test mocks
            # pass Mock() instances and we don't want to misinterpret them.
            if isinstance(registered, dict) and registered:
                colliding = sorted(set(registered.keys()) & RESERVED_NATIVE_TOOL_NAMES)
                if colliding:
                    raise ValueError(
                        f"Tool name(s) {colliding} collide with reserved native "
                        f"tools auto-injected by contexts/steps. The names "
                        f"{sorted(RESERVED_NATIVE_TOOL_NAMES)} are reserved and "
                        f"cannot be used for user-defined SWAIG tools when "
                        f"contexts/steps are in use. Rename your tool(s) to "
                        f"avoid the collision."
                    )

            # Validate step set_functions([...]) whitelists against the known
            # tool universe. A step that whitelists a function which is neither
            # a registered SWAIG tool nor a reserved native tool is a DANGLING
            # reference: it renders a step whose active-function set silently
            # points at nothing (r5 F3 — get_datetime vs get_current_time).
            # Only enforce when a real registry is present; a contexts builder
            # with no agent (or a mock registry) cannot know the tool universe,
            # so we must not red a valid document there.
            if isinstance(registered, dict):
                known_functions = set(registered.keys()) | RESERVED_NATIVE_TOOL_NAMES
                for context_name, context in self._contexts.items():
                    for step_name, step in context._steps.items():
                        funcs = step._functions
                        # "none" and [] are explicit disable-all — not lists of
                        # references to resolve.
                        if not isinstance(funcs, list):
                            continue
                        for fn in funcs:
                            if fn not in known_functions:
                                available = sorted(known_functions)
                                raise ValueError(
                                    f"Step '{step_name}' in context "
                                    f"'{context_name}' whitelists function "
                                    f"'{fn}' via set_functions(), but no such "
                                    f"SWAIG tool is registered on the agent and "
                                    f"it is not a reserved native tool. This "
                                    f"would emit a dangling function reference. "
                                    f"Register the tool (define_tool / a skill) "
                                    f"or remove it from the step. Available: "
                                    f"{available}"
                                )

                self._warn_unoffered_tools(registered)
                self._warn_tool_mentions(registered)

        self._warn_inert_resets()

    def steps_offering(self, function: str) -> list[tuple[str, str]]:
        """
        The steps whose function list offers ``function``, as
        ``(context, step)`` pairs in order, including a gather question's
        functions.

        A step without ``set_functions()`` keeps whatever was active before
        it, so it isn't counted: what it offers depends on the step the call
        came from. The platform's reply to a call of a tool the current step
        doesn't offer names the same steps.

        Args:
            function: The function's name.

        Returns:
            The (context name, step name) pairs, empty when no step lists it.
        """
        return [
            (context_name, step_name)
            for context_name in self._context_order
            for step_name, step in self._contexts[context_name]._steps.items()
            if _step_offers(step, function)
        ]

    def _warn_unoffered_tools(self, registered: dict[str, Any]) -> None:
        """Log, once per tool, a tool that no step can offer: when every step
        lists its functions and none lists it, the model never gets it,
        unless a function result turns it on."""
        from signalwire.core.semantic_gate import RESERVED_FUNCTION_NAMES

        steps = [step for c in self._contexts.values() for step in c._steps.values()]
        if not steps or any(step._functions is None for step in steps):
            return
        for name in registered:
            if (
                ("unoffered", name) in self._warned()
                or name in RESERVED_FUNCTION_NAMES
                or name in RESERVED_NATIVE_TOOL_NAMES
                or self.steps_offering(name)
            ):
                continue
            self._warned().add(("unoffered", name))
            _design_warning(
                "tool_offered_by_no_step",
                f"no step offers the tool {name!r}: every step lists its "
                "functions and none lists it, so the model never gets it unless "
                "a function result turns it on (toggle_functions). Add it to the "
                "steps that need it.",
                function=name,
            )

    def _warned(self) -> set[tuple[str, ...]]:
        """The design warnings already reported: the agent's, shared with its
        per-request copies, or this builder's own without an agent."""
        shared = getattr(self._agent, "_design_warnings_seen", None)
        return shared if isinstance(shared, set) else self._warned_here

    def _warn_inert_resets(self) -> None:
        """Log, once each, reset settings that don't do what they read as: a
        step with a reset is terminal, so its text never runs; and a
        context's consolidate, full_reset and user_prompt act only with a
        system_prompt, whose presence runs the context's reset."""
        for context_name in self._context_order:
            context = self._contexts[context_name]
            unused = [
                name
                for name, value in (
                    ("consolidate", context._consolidate),
                    ("full_reset", context._full_reset),
                    ("user_prompt", context._user_prompt),
                )
                if value
            ]
            has_system_prompt = bool(
                context._system_prompt or context._system_prompt_sections
            )
            key: tuple[str, ...] = ("context", context_name)
            if unused and not has_system_prompt and key not in self._warned():
                self._warned().add(key)
                _design_warning(
                    "context_reset_without_system_prompt",
                    f"context {context_name!r} sets {', '.join(unused)} without a "
                    "system_prompt: the platform runs a context's reset only when "
                    "it has one, so these do nothing. Add set_system_prompt().",
                    context=context_name,
                    settings=unused,
                )
            for step_name, step in context._steps.items():
                key = ("step", context_name, step_name)
                if key in self._warned() or not (
                    step._reset_system_prompt is not None
                    or step._reset_user_prompt is not None
                    or step._reset_consolidate
                    or step._reset_full_reset
                ):
                    continue
                self._warned().add(key)
                _design_warning(
                    "step_reset_is_terminal",
                    f"step {step_name!r} in context {context_name!r} has a reset, "
                    "so it's terminal: the platform runs the reset in place of its "
                    "text, and step mode ends there.",
                    context=context_name,
                    step=step_name,
                )

    def _warn_tool_mentions(self, registered: dict[str, Any]) -> None:
        """Log, once each, a registered tool named where the step doesn't
        offer it: in its text, its criteria, its context's prompt (which goes
        before every step's text), a gather question, or a gate's output on
        one of its tools. The model reads the name and may call a tool it
        doesn't have. A step without a function list is skipped: what it
        offers depends on the step before it."""
        from signalwire.core.semantic_gate import RESERVED_FUNCTION_NAMES

        tools = [
            name
            for name in registered
            if name not in RESERVED_FUNCTION_NAMES
            and name not in RESERVED_NATIVE_TOOL_NAMES
        ]
        if not tools:
            return
        for context_name in self._context_order:
            context = self._contexts[context_name]
            prompt = context._render_prompt()
            for step_name, step in context._steps.items():
                if not isinstance(step._functions, list) and step._functions not in (
                    "none",
                    [],
                ):
                    continue
                offered = (
                    set(step._functions) if isinstance(step._functions, list) else set()
                )
                for where, text, also in _step_texts(step, prompt, registered, offered):
                    for tool in sorted(named_tools(text, tools) - offered - also):
                        key = (context_name, step_name, where, tool)
                        if key in self._warned():
                            continue
                        self._warned().add(key)
                        _design_warning(
                            "tool_named_but_not_offered",
                            f"step {step_name!r} in context {context_name!r} "
                            f"names the tool {tool!r} in its {where}, but doesn't "
                            "offer it: the model reads the name and may call a "
                            "tool it doesn't have. Name only the step's own tools.",
                            context=context_name,
                            step=step_name,
                            where=where,
                            function=tool,
                        )

    def to_dict(self) -> dict[str, Any]:
        """Convert all contexts to a dictionary for SWML generation.

        Calls ``validate()`` first.

        Returns:
            A dict mapping each context name, in the order added, to its serialized
            dict, ready for inclusion in the SWML document.

        Raises:
            ValueError: If ``validate()`` fails, or a step has neither text nor POM
                sections.

        Example:
            ```python
            contexts = agent.define_contexts()
            contexts.add_context("default").add_step("greet").set_text("Hello!")
            data = contexts.to_dict()
            # {"default": {"steps": [{"name": "greet", "text": "Hello!"}]}}
            ```
        """
        self.validate()

        return {
            context_name: context.to_dict()
            for context_name in self._context_order
            for context_name, context in [(context_name, self._contexts[context_name])]
        }


def _design_warning(event: str, message: str, **fields: Any) -> None:
    """A design problem found when the SWML is rendered, reported twice: to
    the SDK's logger, for production logs, and as a Python warning, which a
    developer sees with no logging set up (printed once per message by
    default, and listed in pytest's summary). Silence the second with
    ``warnings.filterwarnings("ignore", message="SignalWire ")``."""
    _logger.warning(event, hint=message, **fields)
    warnings.warn(f"SignalWire {event}: {message}", UserWarning, stacklevel=2)


def named_tools(text: str | None, tools: Iterable[str]) -> set[str]:
    """
    The tool names ``text`` names.

    A name with an underscore, such as ``place_order``, counts as a whole
    word anywhere. A one-word name, such as ``help``, counts only in
    backticks or before "(", since it's also an ordinary word.

    Args:
        text: The text: a step's, a prompt's or a tool result's.
        tools: The tool names to look for.

    Returns:
        The names it finds.
    """
    if not text:
        return set()
    found: set[str] = set()
    for name in tools:
        escaped = re.escape(name)
        if "_" in name:
            pattern = rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])"
        else:
            pattern = rf"`{escaped}`|(?<![A-Za-z0-9_]){escaped}\("
        if re.search(pattern, text):
            found.add(name)
    return found


def _gate_texts(definition: Any) -> list[tuple[str, str]]:
    """Each gate's output text on a tool, as (gate id, text)."""
    if isinstance(definition, dict):
        gates = definition.get("gates") or []
    else:
        gates = (getattr(definition, "extra_swaig_fields", None) or {}).get(
            "gates"
        ) or []
    texts: list[tuple[str, str]] = []
    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            continue
        gate_id = str(gate.get("id", f"gate_{index + 1}"))
        for key in ("on_fail", "on_unclear"):
            output = gate.get(key)
            response = output.get("response") if isinstance(output, dict) else None
            if isinstance(response, dict):
                response = " ".join(
                    str(response.get(k, "")) for k in ("tool_result", "tool_prompt")
                )
            if isinstance(response, str) and response:
                texts.append((f"{gate_id} {key}", response))
    return texts


def _step_texts(
    step: "Step",
    context_prompt: str | None,
    registered: dict[str, Any],
    offered: set[str],
) -> list[tuple[str, str, set[str]]]:
    """What the model reads in a step, as (where, text, tools also offered
    there): its text, criteria and context prompt, its gather questions, and
    the gate outputs of the tools it offers."""
    try:
        text: str | None = step._render_text()
    except ValueError:
        text = None
    texts: list[tuple[str, str, set[str]]] = [
        ("text", text or "", set()),
        ("criteria", step._step_criteria or "", set()),
        ("context prompt", context_prompt or "", set()),
    ]
    gather = step._gather_info
    if gather is not None:
        texts.extend(
            (
                f"gather question {question.key}",
                f"{question.question} {question.prompt or ''}",
                set(question.functions or ()),
            )
            for question in gather._questions
        )
    for tool in sorted(offered):
        for gate, output in _gate_texts(registered.get(tool)):
            texts.append((f"{tool} gate {gate}", output, set()))
    return texts


def _step_offers(step: "Step", function: str) -> bool:
    """Whether a step's own function list, or one of its gather questions',
    names ``function``."""
    if isinstance(step._functions, list) and function in step._functions:
        return True
    gather = step._gather_info
    return gather is not None and any(
        q.functions and function in q.functions for q in gather._questions
    )


def create_simple_context(name: str = "default") -> Context:
    """Create a standalone Context without a ContextBuilder.

    Useful for quick prototyping, or when you need a single context outside the
    builder pattern. This is a module-level function, not a method of
    ``ContextBuilder``.

    Args:
        name: Context name. Defaults to ``"default"``, the required name for a
            single-context agent.

    Returns:
        A new Context, ready for adding steps.

    Example:
        ```python
        ctx = create_simple_context()
        ctx.add_step("greet").set_text("Welcome the caller.")
        ctx.add_step("farewell").set_text("Thank the caller and end the call.")
        ```
    """
    return Context(name)
