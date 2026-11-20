"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

import threading
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from signalwire.core.agent_base import AgentBase  # type: ignore[attr-defined]  # cycle: agent_base imports the mixins; the name resolves at type-check time but mypy flags the back-reference


from signalwire.core.mixins._mixin_host import _HostTyped


class AIConfigMixin(_HostTyped):  # type: ignore[misc]  # _HostTyped is object at runtime; AgentBase under TYPE_CHECKING — intentional split
    """
    Mixin class containing all AI configuration methods for AgentBase
    """

    # Optional ASR-driven multilingual config (Mode B). AgentBase.__init__ sets it
    # to None; set_multilingual() assigns the dict. Declared explicitly so the base
    # type is dict|None (mypy would otherwise infer a non-optional dict from the
    # setter and reject AgentBase's None initializer).
    _multilingual: dict[str, Any] | None = None

    def add_hint(self, hint: str) -> "AgentBase":
        """
        Add a single speech recognition hint.

        Hints boost the speech recognition (ASR) engine's accuracy for specific words
        or phrases that it may otherwise misrecognize, such as product names,
        technical jargon, or uncommon proper nouns. Empty or non-string values are
        ignored.

        Args:
            hint: A word or phrase to boost recognition accuracy for.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.add_hint("SignalWire")
            ```
        """
        if isinstance(hint, str) and hint:
            self._hints.append(hint)
        return self

    def add_hints(self, hints: list[str]) -> "AgentBase":
        """
        Add multiple speech recognition hints at once.

        Empty or non-string entries in the list are skipped.

        Args:
            hints: A list of words or phrases to boost recognition accuracy for.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.add_hints(["SWML", "SWAIG", "FreeSWITCH"])
            ```
        """
        if hints and isinstance(hints, list):
            for hint in hints:
                if isinstance(hint, str) and hint:
                    self._hints.append(hint)
        return self

    def add_pattern_hint(
        self, hint: str, pattern: str, replace: str, ignore_case: bool = False
    ) -> "AgentBase":
        """
        Add a hint with pattern matching and replacement.

        This lets you intercept specific speech recognition output and rewrite it
        before it reaches the AI. It is useful for correcting consistent
        misrecognitions or normalizing variations. The hint is ignored unless
        `hint`, `pattern` and `replace` are all non-empty.

        Args:
            hint: The hint string to match against recognition output.
            pattern: Regular expression pattern to match.
            replace: Replacement text to substitute when the pattern matches.
            ignore_case: Whether to ignore case when matching the pattern. Default
                False.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            # Correct a common misrecognition
            agent.add_pattern_hint(
                hint="SignalWire",
                pattern=r"signal\\s*wire|signal\\s*wired",
                replace="SignalWire",
                ignore_case=True,
            )
            ```
        """
        if hint and pattern and replace:
            self._hints.append(
                {
                    "hint": hint,
                    "pattern": pattern,
                    "replace": replace,
                    "ignore_case": ignore_case,
                }
            )
        return self

    def add_language(
        self,
        name: str,
        code: str,
        voice: str,
        speech_fillers: list[str] | None = None,
        function_fillers: list[str] | None = None,
        engine: str | None = None,
        model: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> "AgentBase":
        """
        Add a language configuration with voice settings.

        The agent uses these configurations to support multilingual conversations
        with the matching text-to-speech voices. Each call appends one entry to the
        `languages` array of the AI verb in the SWML document.

        Name the engine, either in the `voice` string or through `engine`. A bare
        voice name such as `"en-US-Neural2-F"` is resolved against a default
        engine, and that default can change.

        Voice formats:

        - `engine.voice:model`, for example `"elevenlabs.josh:eleven_turbo_v2_5"`.
          The SDK splits a string that contains both `.` and `:` into the engine,
          voice and model fields.
        - `engine.voice`, for example `"rime.spore"`. The string is passed through
          as it is.
        - A bare voice name such as `"josh"`, together with the `engine` or `model`
          argument. When either is given, `voice` is used as it is.

        Args:
            name: Human-readable language name (e.g., "English", "French").
            code: Language code (e.g., "en-US", "fr-FR", "es-MX").
            voice: TTS voice identifier, in one of the formats above.
            speech_fillers: Filler phrases used during natural speech pauses
                (e.g., ["Um...", "Let me see..."]).
            function_fillers: Filler phrases spoken while SWAIG functions run
                (e.g., ["One moment please...", "Looking that up..."]). When only
                one of the two filler lists is given, it is emitted under the
                deprecated `fillers` key instead.
            engine: Explicit TTS engine name (e.g., "elevenlabs", "rime"). When
                given, the combined voice string is not parsed.
            model: Explicit TTS model name (e.g., "eleven_turbo_v2_5"). When
                given, the combined voice string is not parsed.
            params: Per-language params for engine-specific tuning and voice
                settings. Emitted as the language object's `params` key in SWML,
                and only when non-empty.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            # Engine and voice
            agent.add_language("English", "en-US", "rime.spore")

            # Combined engine, voice and model
            agent.add_language(
                "English", "en-US", "elevenlabs.josh:eleven_turbo_v2_5"
            )

            # Explicit engine and model
            agent.add_language(
                "English", "en-US", "josh",
                engine="elevenlabs",
                model="eleven_turbo_v2_5",
            )

            # With fillers
            agent.add_language(
                "English", "en-US", "rime.spore",
                speech_fillers=["Um...", "Let me think..."],
                function_fillers=["One moment please...", "Looking that up..."],
            )

            # With per-language params
            agent.add_language(
                "English", "en-US", "josh",
                engine="elevenlabs",
                params={"stability": 0.5, "similarity_boost": 0.75},
            )
            ```
        """
        language: dict[str, Any] = {"name": name, "code": code}

        # Handle voice formatting (either explicit params or combined string)
        if engine or model:
            # Use explicit parameters if provided
            language["voice"] = voice
            if engine:
                language["engine"] = engine
            if model:
                language["model"] = model
        elif "." in voice and ":" in voice:
            # Parse combined string format: "engine.voice:model"
            try:
                engine_voice, model_part = voice.split(":", 1)
                engine_part, voice_part = engine_voice.split(".", 1)

                language["voice"] = voice_part
                language["engine"] = engine_part
                language["model"] = model_part
            except ValueError:
                # If parsing fails, use the voice string as-is
                language["voice"] = voice
        else:
            # Simple voice string
            language["voice"] = voice

        # Add fillers if provided
        if speech_fillers and function_fillers:
            language["speech_fillers"] = speech_fillers
            language["function_fillers"] = function_fillers
        elif speech_fillers or function_fillers:
            # If only one type of fillers is provided, use the deprecated "fillers" field
            fillers = speech_fillers or function_fillers
            language["fillers"] = fillers

        # Per-language params (engine-specific tuning, voice settings, etc.).
        # Only emit the key when non-empty so we don't pollute SWML with
        # empty objects.
        if params:
            language["params"] = params

        self._languages.append(language)
        return self

    def set_language_params(self, code: str, params: dict[str, Any]) -> "AgentBase":
        """
        Set or replace the engine-specific `params` on an added language.

        Useful when language entries are built with `add_language()` first and
        engine-specific tuning is added later, for example from a config loader.
        The params are emitted as the language object's `params` key in SWML.
        Read them back with `get_language_params()`.

        Args:
            code: Language code as previously passed to `add_language()` (e.g.,
                "en-US").
            params: Engine-specific params to attach. An empty dict removes the
                `params` key.

        Returns:
            This agent, for chaining. Nothing changes if the code isn't found.

        Example:
            ```python
            agent.add_language("English", "en-US", "josh", engine="elevenlabs")
            agent.set_language_params(
                "en-US", {"stability": 0.5, "similarity_boost": 0.75}
            )
            ```
        """
        for language in self._languages:
            if language.get("code") == code:
                if params:
                    language["params"] = params
                else:
                    language.pop("params", None)
                break
        return self

    def get_language_params(self, code: str) -> dict[str, Any] | None:
        """
        Read the engine-specific `params` of a language that was already added.

        Set or replace the params with `set_language_params()`. The params map to
        the `params` key of the matching entry in the `languages` array of the SWML
        AI verb.

        Args:
            code: Language code as previously passed to `add_language()` (e.g.,
                "en-US").

        Returns:
            The params dict if set, `None` otherwise, including when the code is
            unknown.

        Example:
            ```python
            agent.add_language("English", "en-US", "josh", engine="elevenlabs")
            agent.set_language_params("en-US", {"stability": 0.5})
            params = agent.get_language_params("en-US")  # {"stability": 0.5}
            ```
        """
        for language in self._languages:
            if language.get("code") == code:
                return language.get("params")
        return None

    def set_languages(self, languages: list[dict[str, Any]]) -> "AgentBase":
        """
        Replace all language configurations at once with raw dictionaries.

        To let the caller switch languages mid-call instead, use
        `set_multilingual()`; the two are mutually exclusive. An empty list is
        ignored and leaves the current languages in place.

        Args:
            languages: List of language configuration dictionaries. Each should
                include `name`, `code` and `voice` keys, and optionally `engine`,
                `model`, `speech_fillers` and `function_fillers`.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_languages([
                {"name": "English", "code": "en-US", "voice": "rime.spore"},
                {"name": "Spanish", "code": "es-MX", "voice": "rime.luna"},
                {"name": "French", "code": "fr-FR", "voice": "rime.soleil"},
            ])
            ```
        """
        if languages and isinstance(languages, list):
            self._languages = languages
        return self

    def set_multilingual(self, config: dict[str, Any]) -> "AgentBase":
        """
        Configure recognizer-driven multilingual mode.

        The speech recognizer runs in code-switching mode and the agent answers in
        whichever language the caller actually spoke; the model doesn't pick the
        language. The SDK emits the object as the top-level `multilingual` key of
        the AI verb.

        This is mutually exclusive with `set_languages()` and `add_language()`. If
        both are set, the platform uses `multilingual` and ignores `languages`.

        In multilingual mode, speech recognition hints added with `add_hints()` or
        `add_dynamic_hints()` are not used, and no error is returned. Pattern hints
        from `add_pattern_hint()` still rewrite what the agent hears.

        Args:
            config: The multilingual configuration object, passed through
                unchanged. Its keys include the language list (`languages`), the
                languages the caller may switch to (`allowed`), the starting
                language (`start_language`), switching thresholds such as
                `min_switch_words`, and `fillers`. An empty or non-dict value is
                ignored.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_multilingual({
                "start_language": "en",
                "allowed": ["en", "es", "fr"],
                "languages": [
                    {"language": "default", "voice": "elevenlabs.rachel"},
                    {"language": "es", "voice": "elevenlabs.maria"},
                    {"language": "fr", "voice": "gcloud.fr-FR-Neural2-B"},
                ],
            })
            ```
        """
        if config and isinstance(config, dict):
            self._multilingual = config
        return self

    def add_pronunciation(
        self, replace: str, with_text: str, ignore_case: bool = False
    ) -> "AgentBase":
        """
        Add a pronunciation rule that tells the TTS engine how to say a word.

        Useful for brand names, acronyms, and technical terms that text-to-speech
        engines commonly mispronounce. The rule is ignored unless both `replace`
        and `with_text` are non-empty.

        Args:
            replace: The expression to match in the AI's output text.
            with_text: The phonetic spelling or alternative text the TTS engine
                should speak instead. Emitted as the rule's `with` key.
            ignore_case: Whether to ignore case when matching `replace`. Default
                False; the `ignore_case` key is only emitted when True.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.add_pronunciation("SQL", "sequel")
            agent.add_pronunciation("SWAIG", "swig", ignore_case=True)
            ```
        """
        if replace and with_text:
            rule: dict[str, Any] = {"replace": replace, "with": with_text}
            if ignore_case:
                rule["ignore_case"] = True

            self._pronounce.append(rule)
        return self

    def set_pronunciations(self, pronunciations: list[dict[str, Any]]) -> "AgentBase":
        """
        Replace all pronunciation rules at once with raw rule dictionaries.

        An empty list is ignored and leaves the current rules in place.

        Args:
            pronunciations: List of pronunciation rule dictionaries. Each must
                contain `replace` and `with` keys, and optionally `ignore_case`.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_pronunciations([
                {"replace": "SQL", "with": "sequel"},
                {"replace": "SWML", "with": "swimmel", "ignore_case": True},
                {"replace": "IEEE", "with": "I triple E"},
            ])
            ```
        """
        if pronunciations and isinstance(pronunciations, list):
            self._pronounce = pronunciations
        return self

    def set_param(self, key: str, value: Any) -> "AgentBase":
        """
        Set a single AI parameter by key.

        AI parameters map to the `params` object of the SWML AI verb and control
        speech recognition, timing, barge-in and other agent behavior. They are not
        LLM sampling settings; set those with `set_prompt_llm_params()`. The SDK
        sends only the parameters you set. See `set_params()` for the common ones.

        Args:
            key: Parameter name (e.g., "end_of_speech_timeout", "barge_min_words").
                An empty key is ignored.
            value: Parameter value. The type depends on the parameter being set.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_param("end_of_speech_timeout", 700)
            agent.set_param("barge_min_words", 2)
            ```
        """
        if key:
            self._params[key] = value
        return self

    def set_params(self, params: dict[str, Any]) -> "AgentBase":
        """
        Set multiple AI parameters at once, merging into any already set.

        These parameters map to the `params` object of the SWML AI verb. They
        control speech recognition, timing, audio and agent behavior. LLM sampling
        settings such as `temperature` and `top_p` are not AI parameters; set them
        with `set_prompt_llm_params()`. The SDK sends no defaults: only parameters
        you set are included in the SWML document. The defaults noted below are
        applied by the platform when a parameter is omitted.

        Timing parameters:

        - `end_of_speech_timeout`: silence in milliseconds that marks the end of
          speech. Default 700, range 0 to 10000.
        - `attention_timeout`: silence in milliseconds before the AI re-engages
          the caller. Default 5000; 0 turns it off, otherwise 1000 to 600000.
        - `inactivity_timeout`: inactivity delay in milliseconds before the call is
          disconnected. Default 600000; 0 turns it off, otherwise 10000 to
          3600000.
        - `speech_timeout`: maximum length in milliseconds of a single recognized
          utterance. Default 60000.

        Behavior parameters:

        - `wait_for_user`: wait for the caller to speak before the AI begins
          talking. Default False.
        - `transparent_barge`: fold the caller's interrupting speech into the
          conversation. Default True.
        - `barge_min_words`: how many words the caller must speak to interrupt the
          AI. See also `enable_barge`.
        - `save_conversation`: persist the conversation summary after the call
          ends. Ignored unless `conversation_id` is also set. Default False.

        Audio parameters:

        - `ai_volume`: AI voice volume adjustment, -50 to 50. Default 0.
        - `background_file`: URL of an audio file to play in the background during
          the conversation.
        - `hold_music`: URL of hold music, or a tone string such as "tone:440".

        Args:
            params: Dictionary of parameter name/value pairs. An empty or non-dict
                value is ignored.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_params({
                "end_of_speech_timeout": 1000,
                "attention_timeout": 10000,
                "wait_for_user": True,
            })
            ```
        """
        if params and isinstance(params, dict):
            self._params.update(params)
        return self

    def set_semantic_gates(
        self,
        enabled: bool | None = None,
        timeout_ms: int | None = None,
        history: int | None = None,
        dialogue: str | None = None,
    ) -> "AgentBase":
        """
        Set how the call checks its functions' semantic gates.

        Each argument sets one AI parameter. Each argument left as None keeps
        the platform's default.

        Args:
            enabled: False dispatches gated functions without checking their
                gates. Sets `semantic_gates_enabled`. Default True.
            timeout_ms: The time one check may take, 500 to 10000
                milliseconds, preparing the request and any retry included.
                A check that runs out blocks the call. Sets
                `semantic_gate_timeout_ms`. Default 2500.
            history: How many recent dialogue entries the decision model
                sees, 0 to 100. Sets `semantic_gate_history`. Default 20.
            dialogue: Which dialogue the decision model judges: "window",
                the newest ``history`` entries, or "proposal", those since
                ``global_data.semantic_state`` last changed (see
                ``FunctionResult.set_semantic_state``), from the agent's
                first turn after it: the read-back and the caller's reply.
                With no ``semantic_state`` set, the window. A gate's own
                ``dialogue`` and ``history`` take the place of these for its
                function. Sets `semantic_gate_dialogue`. Default "window".

        Returns:
            This agent, for chaining.

        Raises:
            ValueError: If a value has the wrong type or is out of range. Values
                checked before the one that raised stay set.

        Example:
            ```python
            agent.set_semantic_gates(timeout_ms=4000, history=40)
            ```
        """
        if enabled is not None:
            if not isinstance(enabled, bool):
                raise ValueError(f"enabled must be a boolean, got {enabled!r}")
            self._params["semantic_gates_enabled"] = enabled
        if dialogue is not None:
            from signalwire.core.semantic_gate import GATE_DIALOGUES

            if not isinstance(dialogue, str) or dialogue not in GATE_DIALOGUES:
                raise ValueError(
                    f"dialogue must be one of {GATE_DIALOGUES}, got {dialogue!r}"
                )
            self._params["semantic_gate_dialogue"] = dialogue
        for param, value, low, high in (
            ("semantic_gate_timeout_ms", timeout_ms, 500, 10000),
            ("semantic_gate_history", history, 0, 100),
        ):
            if value is None:
                continue
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or not low <= value <= high
            ):
                name = "timeout_ms" if param.endswith("timeout_ms") else "history"
                raise ValueError(
                    f"{name} must be an integer from {low} to {high}, got {value!r}"
                )
            self._params[param] = value
        return self

    def set_unavailable_function_response(self, text: str) -> "AgentBase":
        """
        Set what the model is told when it calls a tool it can't use now.

        Without it, the platform says nothing ran, which steps offer the
        tool, and which tools are available now. ``text`` takes its place,
        with ``${function}`` for the tool's name, ``${tools}`` for the tools
        the request offered, comma-separated, and ``${steps}`` for the
        current context's steps whose functions include it (empty for a name
        the agent doesn't have).

        Args:
            text: The text, as the ``unavailable_function_response`` param.

        Returns:
            This agent, for chaining.

        Raises:
            ValueError: If `text` is not a non-empty string.
        """
        if not isinstance(text, str) or not text:
            raise ValueError("text must be a non-empty string")
        self._params["unavailable_function_response"] = text
        return self

    def set_global_data(self, data: dict[str, Any]) -> "AgentBase":
        """
        Merge data into the global data available to the AI during the conversation.

        This merges rather than replaces, so skills, dynamic config callbacks and
        other callers can each contribute keys without clobbering each other. The
        method is thread-safe: concurrent calls are serialized by an internal lock.

        Args:
            data: Dictionary of key/value pairs to merge into global data. Values
                can be any JSON-serializable type. An empty or non-dict value is
                ignored.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_global_data({
                "company_name": "Acme Corp",
                "support_hours": "9am-5pm EST",
                "user_tier": "standard",
            })
            ```
        """
        if data and isinstance(data, dict):
            if not hasattr(self, "_global_data_lock"):
                self._global_data_lock = threading.Lock()
            with self._global_data_lock:
                self._global_data.update(data)
        return self

    def update_global_data(self, data: dict[str, Any]) -> "AgentBase":
        """
        Update the global data with new values.

        Functionally identical to `set_global_data()`: both merge the dictionary
        into the existing global data. The method is thread-safe.

        Args:
            data: Dictionary of key/value pairs to merge into global data. An empty
                or non-dict value is ignored.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.update_global_data({
                "authenticated": True,
                "user_name": "Alice",
                "user_tier": "gold",
            })
            ```
        """
        if data and isinstance(data, dict):
            if not hasattr(self, "_global_data_lock"):
                self._global_data_lock = threading.Lock()
            with self._global_data_lock:
                self._global_data.update(data)
        return self

    def set_native_functions(self, function_names: list[str]) -> "AgentBase":
        """
        Set the list of native SWAIG functions to enable.

        Native functions are built into the SignalWire platform and run
        server-side without a webhook. They provide common utility operations the
        AI can invoke during a conversation. They can also be passed at
        construction time through the `native_functions` constructor parameter.

        Args:
            function_names: Native function names to enable: "check_time" (the
                current time, optionally in a timezone), "wait_for_user" (wait
                until the caller speaks again, for when they ask the agent to
                hold on), "wait_seconds" (pause for a number of seconds) and
                "adjust_response_latency" (make the agent respond slower or
                faster). Non-string entries are dropped; an empty list is
                ignored.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_native_functions(["check_time", "wait_for_user"])
            ```
        """
        if function_names and isinstance(function_names, list):
            self.native_functions = [
                name for name in function_names if isinstance(name, str)
            ]
        return self

    #: The complete set of internal SWAIG function names that accept fillers,
    #: matching the SWAIGInternalFiller schema definition. Any name outside
    #: this set is rejected by the runtime — set_internal_fillers /
    #: add_internal_filler will warn if you pass an unknown name.
    SUPPORTED_INTERNAL_FILLER_NAMES = frozenset(
        {
            "hangup",  # AI is hanging up the call
            "check_time",  # AI is checking the time
            "wait_for_user",  # AI is waiting for user input
            "wait_seconds",  # deliberate pause / wait period
            "adjust_response_latency",  # AI is adjusting response timing
            "next_step",  # transitioning between steps in prompt.contexts
            "change_context",  # switching between contexts in prompt.contexts
            "get_visual_input",  # processing visual input (enable_vision)
            "get_ideal_strategy",  # thinking (enable_thinking)
        }
    )

    def set_internal_fillers(
        self, internal_fillers: dict[str, dict[str, list[str]]]
    ) -> "AgentBase":
        """
        Set internal fillers for native SWAIG functions.

        Internal fillers are short phrases the AI agent speaks (via TTS) while
        an internal/native function is running, so the caller doesn't hear
        dead air during transitions or background work.

        Supported function names (matches the SWAIGInternalFiller schema):

        - `hangup`: when the agent is hanging up
        - `check_time`: when checking the time
        - `wait_for_user`: when waiting for user input
        - `wait_seconds`: during deliberate pauses
        - `adjust_response_latency`: when adjusting response timing
        - `next_step`: transitioning between steps in prompt.contexts
        - `change_context`: switching between contexts in prompt.contexts
        - `get_visual_input`: processing visual input (enable_vision=True)
        - `get_ideal_strategy`: thinking (enable_thinking=True)

        Notably NOT supported: change_step, gather_submit, or arbitrary
        user-defined SWAIG function names. The runtime only honors fillers
        for the names listed above; everything else is silently ignored at
        the SWML level. This method warns at registration time if you pass
        an unknown name so you catch the typo early.

        Without internal fillers, callers hear dead air during context
        switches and other internal transitions. Set this on every agent
        that uses contexts/steps with audio.

        Args:
            internal_fillers: Dictionary mapping function names to
                language-specific filler phrases.
                Format: {"function_name": {"language_code": ["phrase1", "phrase2"]}}

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_internal_fillers({
                "next_step": {
                    "en-US": ["Moving on...", "Great, let's continue..."],
                    "es": ["Pasando al siguiente paso...", "Continuemos..."],
                },
                "change_context": {
                    "en-US": ["Let me switch modes...", "One moment..."],
                },
                "check_time": {
                    "en-US": ["Let me check the time...", "One moment..."],
                },
            })
            ```
        """
        if internal_fillers and isinstance(internal_fillers, dict):
            unknown = sorted(
                set(internal_fillers.keys()) - self.SUPPORTED_INTERNAL_FILLER_NAMES
            )
            if unknown:
                from signalwire.core.logging_config import get_logger

                get_logger("ai_config_mixin").warning(
                    "unknown_internal_filler_names",
                    unknown=unknown,
                    supported=sorted(self.SUPPORTED_INTERNAL_FILLER_NAMES),
                    hint=(
                        "set_internal_fillers received names that the SWML "
                        "schema does not recognize. Those entries will be "
                        "ignored by the runtime. Use one of the supported "
                        "names listed in 'supported'."
                    ),
                )
            if not hasattr(self, "_internal_fillers"):
                self._internal_fillers = {}
            self._internal_fillers.update(internal_fillers)
        return self

    def add_internal_filler(
        self, function_name: str, language_code: str, fillers: list[str]
    ) -> "AgentBase":
        """
        Add internal fillers for a single internal function and language.

        See `set_internal_fillers()` for the complete list of supported function
        names and an explanation of what fillers do.

        Args:
            function_name: One of the supported internal function names (see
                `SUPPORTED_INTERNAL_FILLER_NAMES`). Common values are "next_step",
                "change_context", "check_time", "wait_for_user" and "hangup". A
                name outside the supported set logs a warning and is ignored by
                the runtime.
            language_code: Language code (e.g., "en-US", "es", "fr").
            fillers: Filler phrases for this function and language. The AI
                randomly selects one each time the function runs.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.add_internal_filler(
                "next_step", "en-US",
                ["Moving to the next step...", "Great, let's continue..."],
            )
            agent.add_internal_filler(
                "next_step", "es",
                ["Pasando al siguiente paso...", "Continuemos..."],
            )
            ```
        """
        if function_name and language_code and fillers and isinstance(fillers, list):
            if function_name not in self.SUPPORTED_INTERNAL_FILLER_NAMES:
                from signalwire.core.logging_config import get_logger

                get_logger("ai_config_mixin").warning(
                    "unknown_internal_filler_name",
                    function_name=function_name,
                    supported=sorted(self.SUPPORTED_INTERNAL_FILLER_NAMES),
                    hint=(
                        "add_internal_filler received a function name the "
                        "SWML schema does not recognize. The entry will be "
                        "stored but the runtime will not play these fillers."
                    ),
                )
            if not hasattr(self, "_internal_fillers"):
                self._internal_fillers = {}

            if function_name not in self._internal_fillers:
                self._internal_fillers[function_name] = {}

            self._internal_fillers[function_name][language_code] = fillers
        return self

    def enable_debug_events(self, level: int = 1) -> "AgentBase":
        """
        Enable the debug event webhook for this agent.

        When enabled, the SDK wires a `debug_webhook_url` into the AI parameters and
        registers a `/debug_events` endpoint. The AI module then POSTs real-time
        debug events to that endpoint during calls. Events are logged through the
        agent's structured logger, and can optionally be handled with a custom
        callback registered through `on_debug_event()`.

        Args:
            level: Debug event verbosity level.
                1 = high-level events (barge, errors, session start/end, step
                changes).
                2 and above add high-volume events (every LLM request/response,
                conversation_add).

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.enable_debug_events(level=1)

            @agent.on_debug_event
            def handle_debug(event_type, data):
                if event_type == "llm_error":
                    alert_ops_team(data)
            ```
        """
        self._debug_events_enabled = True
        self._debug_events_level = level
        return self

    def add_function_include(
        self, url: str, functions: list[str], meta_data: dict[str, Any] | None = None
    ) -> "AgentBase":
        """
        Add a remote SWAIG function include to the SWAIG configuration.

        The agent can then call tools hosted on an external server. The remote
        endpoint is contacted at session start and the listed functions become
        available to the AI like locally defined tools. Each include is added to the
        `includes` array of the `SWAIG` object in the SWML document.

        Args:
            url: URL of the remote SWAIG server that hosts the functions.
            functions: Names of the functions to include from the remote server.
            meta_data: Metadata passed along with the include, for example to
                provide authentication tokens or context to the remote server.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.add_function_include(
                url="https://tools.example.com/swaig",
                functions=["lookup_order", "cancel_order"],
                meta_data={"auth_token": "secret-token"},
            )
            ```
        """
        if url and functions and isinstance(functions, list):
            include: dict[str, Any] = {"url": url, "functions": functions}
            if meta_data and isinstance(meta_data, dict):
                include["meta_data"] = meta_data

            self._function_includes.append(include)
        return self

    def set_function_includes(self, includes: list[dict[str, Any]]) -> "AgentBase":
        """
        Replace the entire list of remote SWAIG function includes at once.

        Each entry must contain a `url` and a `functions` list. Invalid entries,
        with a missing key or a `functions` value that is not a list, are silently
        dropped. Use `add_function_include()` to append a single include without
        replacing the existing ones.

        Args:
            includes: List of include objects. Each has `url` (the remote SWAIG
                server URL) and `functions` (the function names to include).
                Optional keys such as `meta_data` are passed through unchanged.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_function_includes([
                {
                    "url": "https://tools.example.com/swaig",
                    "functions": ["lookup_order"],
                },
                {
                    "url": "https://billing.example.com/swaig",
                    "functions": ["get_invoice", "process_refund"],
                },
            ])
            ```
        """
        if includes and isinstance(includes, list):
            # Validate each include has required properties
            valid_includes = [
                include
                for include in includes
                if (
                    isinstance(include, dict)
                    and "url" in include
                    and "functions" in include
                )
                and isinstance(include["functions"], list)
            ]

            self._function_includes = valid_includes
        return self

    def add_mcp_server(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        resources: bool = False,
        resource_vars: dict[str, str] | None = None,
    ) -> "AgentBase":
        """
        Add an external MCP server for tool discovery and invocation.

        This connects your agent to an MCP (Model Context Protocol) server as a
        client. Tools are discovered via the MCP protocol at session start and
        registered as SWAIG functions. Resources are optionally fetched into
        `global_data`. Each server added appears in the `mcp_servers` field of the
        `SWAIG` object in the SWML document.

        To expose the agent's own tools as an MCP server instead, use
        `enable_mcp_server()`.

        Args:
            url: MCP server HTTP endpoint URL.
            headers: HTTP headers sent with every request to the MCP server (e.g.,
                {"Authorization": "Bearer sk-xxx"}).
            resources: Whether to fetch the server's resources into `global_data`.
                Default False.
            resource_vars: Variables for URI template substitution when fetching
                resources. Supports SignalWire call variables such as
                "${caller_id_number}".

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.add_mcp_server(
                url="https://mcp.example.com/sse",
                headers={"Authorization": "Bearer sk-xxx"},
                resources=True,
                resource_vars={"caller_id": "${caller_id_number}"},
            )
            ```
        """
        server: dict[str, Any] = {"url": url}
        if headers:
            server["headers"] = headers
        if resources:
            server["resources"] = True
        if resource_vars:
            server["resource_vars"] = resource_vars
        self._mcp_servers.append(server)
        return self

    def enable_mcp_server(self) -> "AgentBase":
        """
        Expose this agent's `@tool` functions as an MCP server endpoint.

        Adds a `/mcp` route that speaks JSON-RPC 2.0 (the MCP protocol), so
        external MCP clients such as Claude Desktop or other agents can discover
        and invoke the same tools.

        Note:
            This method only registers the `/mcp` HTTP route. To include the
            endpoint in the SWML document for native tool discovery, also call
            `add_mcp_server()` with the agent's own `/mcp` URL. To connect your
            agent to an external MCP server as a client, use `add_mcp_server()`.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            @agent.tool(name="get_weather", description="Get weather for a city")
            def get_weather(args, raw_data):
                return FunctionResult(f"It is sunny in {args.get('city')}.")

            agent.enable_mcp_server()
            ```
        """
        self._mcp_server_enabled = True
        return self

    def set_prompt_llm_params(self, **params: Any) -> "AgentBase":
        """
        Set LLM parameters for the main prompt.

        Accepts any keyword arguments and passes them through to the SignalWire
        server, which validates them against the target model's capabilities. The
        SDK sends only the parameters you set and injects no defaults. Parameters
        that don't apply to the selected model are handled or ignored by the
        server.

        LLM parameters tune the language model's output. Interruption (barge-in) is
        not one of them: tune it with AI parameters through `set_param()` or
        `set_params()` (for example `barge_min_words`), or with `enable_barge`.

        The common parameters are listed below.

        - `model`: the AI model to use (gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano,
          nova-micro, nova-lite, qwen3-235b-A22b-instruct).
        - `temperature`: randomness. Lower values make output more deterministic.
        - `top_p`: alternative to temperature; controls nucleus sampling.
        - `presence_penalty`: topic diversity. Positive values encourage new topics.
        - `frequency_penalty`: repetition control. Positive values reduce
          repetition.
        - `max_tokens`: the maximum number of tokens in a response.

        Args:
            **params: LLM parameter names and values, such as `model`,
                `temperature`, `top_p`, `presence_penalty`, `frequency_penalty` or
                `max_tokens`. Calls merge into any parameters already set.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_prompt_llm_params(
                model="nova-micro",
                temperature=0.7,
                top_p=0.9,
            )
            ```
        """
        # Accept any parameters without validation
        if params:
            self._prompt_llm_params.update(params)

        return self

    def set_post_prompt_llm_params(self, **params: Any) -> "AgentBase":
        """
        Set LLM parameters for the post-prompt.

        Accepts the same keyword arguments as `set_prompt_llm_params()` and passes
        them through to the SignalWire server, which validates them against the
        target model's capabilities. The SDK sends only the parameters you set and
        injects no defaults. Use it to give the post-prompt summary different
        settings from the main prompt, such as a lower temperature.

        The common parameters are listed below.

        - `model`: the AI model to use (gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano,
          nova-micro, nova-lite, qwen3-235b-A22b-instruct).
        - `temperature`: randomness. Lower values make output more deterministic.
        - `top_p`: alternative to temperature; controls nucleus sampling.
        - `presence_penalty`: topic diversity. Positive values encourage new topics.
        - `frequency_penalty`: repetition control. Positive values reduce
          repetition.
        - `max_tokens`: the maximum number of tokens in a response.

        Args:
            **params: LLM parameter names and values, as for
                `set_prompt_llm_params()`. Calls merge into any parameters already
                set.

        Returns:
            This agent, for chaining.

        Example:
            ```python
            agent.set_post_prompt("Summarize this call as JSON.")
            agent.set_post_prompt_llm_params(
                model="gpt-4o-mini",
                temperature=0.3,
            )
            ```
        """
        # Accept any parameters without validation
        if params:
            self._post_prompt_llm_params.update(params)

        return self
