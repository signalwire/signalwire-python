"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Contexts and Steps System for SignalWire Agents

This module provides an alternative to traditional POM-based prompts by allowing
agents to be defined as structured contexts with sequential steps. Each step
contains its own prompt, completion criteria, and function restrictions.
"""

from typing import Optional, Any

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
HISTORY_MODES = ("keep", "default", "hide")


def _validate_history(mode: str) -> str:
    if mode not in HISTORY_MODES:
        raise ValueError(f"history must be one of {HISTORY_MODES}, got {mode!r}")
    return mode


class GatherQuestion:
    """Represents a single question in a gather_info configuration"""

    def __init__(
        self,
        key: str,
        question: str,
        type: str = "string",
        confirm: bool = False,
        prompt: str | None = None,
        functions: list[str] | None = None,
        isolated: bool | None = None,
    ):
        self.key = key
        self.question = question
        self.type = type
        self.confirm = confirm
        self.prompt = prompt
        self.functions = functions
        # Tri-state: None means "inherit the gather_info default"
        self.isolated = isolated

    def to_dict(self) -> dict[str, Any]:
        """Convert question to dictionary for SWML generation"""
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
        return d


class GatherInfo:
    """Configuration for gathering information in a step via the C-side gather_info system.

    This produces zero tool_call/tool_result entries in LLM-visible history,
    instead using dynamic step instruction re-injection to present one question
    at a time.
    """

    def __init__(
        self,
        output_key: str | None = None,
        completion_action: str | None = None,
        prompt: str | None = None,
        isolated: bool = False,
    ):
        self._questions: list[GatherQuestion] = []
        self._output_key = output_key
        self._completion_action = completion_action
        self._prompt = prompt
        self._isolated = isolated

    def add_question(self, key: str, question: str, **kwargs: Any) -> "GatherInfo":
        """
        Add a question to gather.

        Args:
            key: Key name for storing the answer in global_data
            question: The question text to ask
            **kwargs: Optional fields - type, confirm, prompt, functions, isolated

        Returns:
            Self for method chaining
        """
        q = GatherQuestion(
            key=key,
            question=question,
            type=kwargs.get("type", "string"),
            confirm=kwargs.get("confirm", False),
            prompt=kwargs.get("prompt"),
            functions=kwargs.get("functions"),
            isolated=kwargs.get("isolated"),
        )
        self._questions.append(q)
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for SWML generation"""
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
    """Represents a single step within a context"""

    def __init__(self, name: str):
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

        # Reset object for context switching from steps
        self._reset_system_prompt: str | None = None
        self._reset_user_prompt: str | None = None
        self._reset_consolidate: bool = False
        self._reset_full_reset: bool = False

    def set_text(self, text: str) -> "Step":
        """
        Set the step's prompt text directly

        Args:
            text: The prompt text for this step

        Returns:
            Self for method chaining
        """
        if self._sections:
            raise ValueError(
                "Cannot use set_text() when POM sections have been added. Use one approach or the other."
            )
        self._text = text
        return self

    def add_section(self, title: str, body: str) -> "Step":
        """
        Add a POM section to the step

        Args:
            title: Section title
            body: Section body text

        Returns:
            Self for method chaining
        """
        if self._text is not None:
            raise ValueError(
                "Cannot add POM sections when set_text() has been used. Use one approach or the other."
            )
        self._sections.append({"title": title, "body": body})
        return self

    def add_bullets(self, title: str, bullets: list[str]) -> "Step":
        """
        Add a POM section with bullet points

        Args:
            title: Section title
            bullets: List of bullet points

        Returns:
            Self for method chaining
        """
        if self._text is not None:
            raise ValueError(
                "Cannot add POM sections when set_text() has been used. Use one approach or the other."
            )
        self._sections.append({"title": title, "bullets": bullets})
        return self

    def set_step_criteria(self, criteria: str) -> "Step":
        """
        Set the criteria for determining when this step is complete

        Args:
            criteria: Description of step completion criteria

        Returns:
            Self for method chaining
        """
        self._step_criteria = criteria
        return self

    def set_functions(self, functions: str | list[str]) -> "Step":
        """
        Set which non-internal functions are callable while this step is active.

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
            Self for method chaining.

        Examples:
            step.set_functions(["lookup_account", "check_balance"])  # whitelist
            step.set_functions([])                                   # disable all
            step.set_functions("none")                               # disable all (alt)
        """
        self._functions = functions
        return self

    def set_valid_steps(self, steps: list[str]) -> "Step":
        """
        Set which steps can be navigated to from this step

        Args:
            steps: List of valid step names (include "next" for sequential flow)

        Returns:
            Self for method chaining
        """
        self._valid_steps = steps
        return self

    def set_valid_contexts(self, contexts: list[str]) -> "Step":
        """
        Set which contexts can be navigated to from this step

        Args:
            contexts: List of valid context names

        Returns:
            Self for method chaining
        """
        self._valid_contexts = contexts
        return self

    def set_end(self, end: bool) -> "Step":
        """
        Mark this step as terminal for the step flow.

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
            Self for method chaining.
        """
        self._end = end
        return self

    def set_skip_user_turn(self, skip: bool) -> "Step":
        """
        Set whether to skip waiting for user input after this step

        Args:
            skip: Whether to skip the user turn after this step

        Returns:
            Self for method chaining
        """
        self._skip_user_turn = skip
        return self

    def set_skip_to_next_step(self, skip: bool) -> "Step":
        """
        Set whether to automatically advance to the next step

        Args:
            skip: Whether to skip to the next step automatically

        Returns:
            Self for method chaining
        """
        self._skip_to_next_step = skip
        return self

    def set_history(self, history: str) -> "Step":
        """
        Control what the model still sees when this step is entered.

        The mode applies at the moment this step is entered and governs
        everything that came before it — including the turn that triggered the
        transition. It does not affect this step's own turns, which accumulate
        fresh. Nothing is deleted: the call log keeps every message.

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

        Raises:
            ValueError: if history is not one of the three modes.

        Returns:
            Self for method chaining

        Example:
            >>> step.set_history("hide").set_text(
            ...     "Previously: ${step_history.prev.summary}\\n\\nNow help them."
            ... )
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
        """
        Enable info gathering for this step. Questions are presented one at a time
        via dynamic step instruction re-injection, producing zero tool_call/tool_result
        entries in LLM-visible history.

        After calling this, use add_gather_question() to define questions.

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
            Self for method chaining
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
    ) -> "Step":
        """
        Add a question to this step's gather_info configuration.
        set_gather_info() must be called before this method.

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

        Returns:
            Self for method chaining.
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
        )
        return self

    def clear_sections(self) -> "Step":
        """
        Remove all POM sections and direct text from this step, allowing it
        to be repopulated with new content.

        Returns:
            Self for method chaining
        """
        self._sections = []
        self._text = None
        return self

    def set_reset_system_prompt(self, system_prompt: str) -> "Step":
        """
        Set system prompt for context switching when this step navigates to a context

        Args:
            system_prompt: New system prompt for context switching

        Returns:
            Self for method chaining
        """
        self._reset_system_prompt = system_prompt
        return self

    def set_reset_user_prompt(self, user_prompt: str) -> "Step":
        """
        Set user prompt for context switching when this step navigates to a context

        Args:
            user_prompt: User message to inject for context switching

        Returns:
            Self for method chaining
        """
        self._reset_user_prompt = user_prompt
        return self

    def set_reset_consolidate(self, consolidate: bool) -> "Step":
        """
        Set whether to consolidate conversation when this step switches contexts

        Args:
            consolidate: Whether to consolidate previous conversation

        Returns:
            Self for method chaining
        """
        self._reset_consolidate = consolidate
        return self

    def set_reset_full_reset(self, full_reset: bool) -> "Step":
        """
        Set whether to do full reset when this step switches contexts

        Args:
            full_reset: Whether to completely rewrite system prompt vs inject

        Returns:
            Self for method chaining
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
        """Convert step to dictionary for SWML generation"""
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
    """A single context containing an ordered list of steps.

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
    """

    def __init__(self, name: str):
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
        """
        Add a new step to this context.

        When called with only ``name`` the returned Step can be configured
        with the usual method-chaining API.  When the optional keyword
        arguments are supplied the step is fully configured in one call:

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
            The configured Step object for optional further chaining.
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
        """
        Get an existing step by name for inspection or modification.

        Args:
            name: Step name

        Returns:
            Step object if found, None otherwise
        """
        return self._steps.get(name)

    def remove_step(self, name: str) -> "Context":
        """
        Remove a step from this context entirely.

        Args:
            name: Step name to remove

        Returns:
            Self for method chaining
        """
        if name in self._steps:
            del self._steps[name]
            self._step_order = [s for s in self._step_order if s != name]
        return self

    def move_step(self, name: str, position: int) -> "Context":
        """
        Move an existing step to a specific position in the step order.

        Args:
            name: Step name to move
            position: Target index in the step order (0 = first)

        Returns:
            Self for method chaining
        """
        if name not in self._steps:
            raise ValueError(f"Step '{name}' not found in context '{self.name}'")
        self._step_order.remove(name)
        self._step_order.insert(position, name)
        return self

    def set_valid_contexts(self, contexts: list[str]) -> "Context":
        """
        Set which contexts can be navigated to from this context

        Args:
            contexts: List of valid context names

        Returns:
            Self for method chaining
        """
        self._valid_contexts = contexts
        return self

    def set_valid_steps(self, steps: list[str]) -> "Context":
        """
        Set which steps can be navigated to from any step in this context

        Args:
            steps: List of valid step names (include "next" for sequential flow)

        Returns:
            Self for method chaining
        """
        self._valid_steps = steps
        return self

    def set_initial_step(self, step_name: str) -> "Context":
        """
        Set which step the context starts on when entered.

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
            Self for method chaining.

        Example:
            ctx = contexts.add_context("support")
            ctx.add_step("greeting").set_text("Welcome!")
            ctx.add_step("triage").set_text("What do you need help with?")
            ctx.set_initial_step("triage")  # skip greeting on re-entry
        """
        self._initial_step = step_name
        return self

    def set_post_prompt(self, post_prompt: str) -> "Context":
        """
        Set post prompt override for this context

        Args:
            post_prompt: Post prompt text to use when this context is active

        Returns:
            Self for method chaining
        """
        self._post_prompt = post_prompt
        return self

    def set_system_prompt(self, system_prompt: str) -> "Context":
        """
        Set system prompt for context switching (triggers context reset)

        Args:
            system_prompt: New system prompt for when this context is entered

        Returns:
            Self for method chaining
        """
        if self._system_prompt_sections:
            raise ValueError(
                "Cannot use set_system_prompt() when POM sections have been added for system prompt. Use one approach or the other."
            )
        self._system_prompt = system_prompt
        return self

    def set_consolidate(self, consolidate: bool) -> "Context":
        """
        Set whether to consolidate conversation history when entering this context

        Args:
            consolidate: Whether to consolidate previous conversation

        Returns:
            Self for method chaining
        """
        self._consolidate = consolidate
        return self

    def set_full_reset(self, full_reset: bool) -> "Context":
        """
        Set whether to do full reset when entering this context

        Args:
            full_reset: Whether to completely rewrite system prompt vs inject

        Returns:
            Self for method chaining
        """
        self._full_reset = full_reset
        return self

    def set_user_prompt(self, user_prompt: str) -> "Context":
        """
        Set user prompt to inject when entering this context

        Args:
            user_prompt: User message to inject for context

        Returns:
            Self for method chaining
        """
        self._user_prompt = user_prompt
        return self

    def set_history(self, history: str) -> "Context":
        """
        Set the default visibility mode for every step in this context.

        A step's own ``set_history()`` overrides this. See ``Step.set_history``
        for what each mode does.

        Args:
            history: One of "keep", "default", or "hide".

        Raises:
            ValueError: if history is not one of the three modes.

        Returns:
            Self for method chaining
        """
        self._history = _validate_history(history)
        return self

    def set_isolated(self, isolated: bool) -> "Context":
        """
        Mark this context as isolated — entering it wipes conversation history.

        When `isolated=True` and the context is entered via change_context,
        the runtime calls ai_conversation_restart() and the entire conversation
        array is wiped. The model starts fresh with only the new context's
        system_prompt + step instructions, with no memory of prior turns.

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
            Self for method chaining.
        """
        self._isolated = isolated
        return self

    def add_system_section(self, title: str, body: str) -> "Context":
        """
        Add a POM section to the system prompt

        Args:
            title: Section title
            body: Section body text

        Returns:
            Self for method chaining
        """
        if self._system_prompt is not None:
            raise ValueError(
                "Cannot add POM sections for system prompt when set_system_prompt() has been used. Use one approach or the other."
            )
        self._system_prompt_sections.append({"title": title, "body": body})
        return self

    def add_system_bullets(self, title: str, bullets: list[str]) -> "Context":
        """
        Add a POM section with bullet points to the system prompt

        Args:
            title: Section title
            bullets: List of bullet points

        Returns:
            Self for method chaining
        """
        if self._system_prompt is not None:
            raise ValueError(
                "Cannot add POM sections for system prompt when set_system_prompt() has been used. Use one approach or the other."
            )
        self._system_prompt_sections.append({"title": title, "bullets": bullets})
        return self

    def set_prompt(self, prompt: str) -> "Context":
        """
        Set the context's prompt text directly

        Args:
            prompt: The prompt text for this context

        Returns:
            Self for method chaining
        """
        if self._prompt_sections:
            raise ValueError(
                "Cannot use set_prompt() when POM sections have been added. Use one approach or the other."
            )
        self._prompt_text = prompt
        return self

    def add_section(self, title: str, body: str) -> "Context":
        """
        Add a POM section to the context prompt

        Args:
            title: Section title
            body: Section body text

        Returns:
            Self for method chaining
        """
        if self._prompt_text is not None:
            raise ValueError(
                "Cannot add POM sections when set_prompt() has been used. Use one approach or the other."
            )
        self._prompt_sections.append({"title": title, "body": body})
        return self

    def add_bullets(self, title: str, bullets: list[str]) -> "Context":
        """
        Add a POM section with bullet points to the context prompt

        Args:
            title: Section title
            bullets: List of bullet points

        Returns:
            Self for method chaining
        """
        if self._prompt_text is not None:
            raise ValueError(
                "Cannot add POM sections when set_prompt() has been used. Use one approach or the other."
            )
        self._prompt_sections.append({"title": title, "bullets": bullets})
        return self

    def set_enter_fillers(self, enter_fillers: dict[str, list[str]]) -> "Context":
        """
        Set fillers that the AI says when entering this context

        Args:
            enter_fillers: Dictionary mapping language codes (or "default") to lists of filler phrases
                          Example: {"en-US": ["Welcome...", "Hello..."], "default": ["Entering..."]}

        Returns:
            Self for method chaining
        """
        if enter_fillers and isinstance(enter_fillers, dict):
            self._enter_fillers = enter_fillers
        return self

    def set_exit_fillers(self, exit_fillers: dict[str, list[str]]) -> "Context":
        """
        Set fillers that the AI says when exiting this context

        Args:
            exit_fillers: Dictionary mapping language codes (or "default") to lists of filler phrases
                         Example: {"en-US": ["Goodbye...", "Thank you..."], "default": ["Exiting..."]}

        Returns:
            Self for method chaining
        """
        if exit_fillers and isinstance(exit_fillers, dict):
            self._exit_fillers = exit_fillers
        return self

    def add_enter_filler(self, language_code: str, fillers: list[str]) -> "Context":
        """
        Add enter fillers for a specific language

        Args:
            language_code: Language code (e.g., "en-US", "es") or "default" for catch-all
            fillers: List of filler phrases for entering this context

        Returns:
            Self for method chaining
        """
        if language_code and fillers and isinstance(fillers, list):
            if self._enter_fillers is None:
                self._enter_fillers = {}
            self._enter_fillers[language_code] = fillers
        return self

    def add_exit_filler(self, language_code: str, fillers: list[str]) -> "Context":
        """
        Add exit fillers for a specific language

        Args:
            language_code: Language code (e.g., "en-US", "es") or "default" for catch-all
            fillers: List of filler phrases for exiting this context

        Returns:
            Self for method chaining
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
        """Convert context to dictionary for SWML generation"""
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
    """Builder for multi-step, multi-context AI agent workflows.

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

    Their `enum` schemas are rewritten on every turn to match whatever
    valid_steps / valid_contexts apply to the current step. You do NOT need
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
    """

    def __init__(self, agent: Any) -> None:
        self._agent = agent
        self._contexts: dict[str, Context] = {}
        self._context_order: list[str] = []

    def reset(self) -> "ContextBuilder":
        """
        Remove all contexts, returning the builder to its initial state.

        Use this in a dynamic config callback when you need to rebuild
        contexts from scratch for a specific request — e.g. skipping a
        greeting context on transfers.

        Returns:
            Self for method chaining.

        Example::

            def on_dynamic_config(query, body, headers, agent):
                if query.get("transfer"):
                    agent.define_contexts().reset()
                    ctx = agent.define_contexts().add_context("default")
                    ctx.add_step("route").set_text("Route the caller.")
        """
        self._contexts.clear()
        self._context_order.clear()
        return self

    def add_context(self, name: str) -> Context:
        """
        Add a new context

        Args:
            name: Context name

        Returns:
            Context object for method chaining
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
        """
        Get an existing context by name for inspection or modification.

        Args:
            name: Context name

        Returns:
            Context object if found, None otherwise
        """
        return self._contexts.get(name)

    def validate(self) -> None:
        """Validate the contexts configuration"""
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

    def to_dict(self) -> dict[str, Any]:
        """Convert all contexts to dictionary for SWML generation"""
        self.validate()

        return {
            context_name: context.to_dict()
            for context_name in self._context_order
            for context_name, context in [(context_name, self._contexts[context_name])]
        }


def create_simple_context(name: str = "default") -> Context:
    """
    Helper function to create a simple single context

    Args:
        name: Context name (defaults to "default")

    Returns:
        Context object for method chaining
    """
    return Context(name)
