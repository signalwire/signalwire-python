# AUTO-GENERATED from porting-sdk/rest-apis/calling/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``calling`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict


class AI(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        ai: Creates an AI agent that conducts voice conversations using automatic speech
            recognition (ASR), large language models (LLMs), and text-to-speech (TTS)
            synthesis. The agent processes caller speech in real-time, generates
            contextually appropriate responses, and can execute custom functions to
            interact with external systems through SignalWire AI Gateway (SWAIG).
    """

    ai: AIObject


class AIObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        global_data: A key-value object for storing data that persists throughout the AI
            session. Can be set initially in the SWML script or modified during the
            conversation using the set_global_data action. The global_data object is
            accessible everywhere in the AI session: prompts, AI parameters, and SWML
            returned from SWAIG functions. Access properties using template strings
            (e.g. ${global_data.property_name}).
        hints: Hints help the AI agent understand certain words or phrases better. Words
            that can commonly be misinterpreted can be added to the hints to help the AI
            speak more accurately.
        languages: An array of JSON objects defining supported languages in the
            conversation.
        params: A JSON object containing parameters as key-value pairs.
        post_prompt: The final set of instructions and configuration settings to send to
            the agent.
        post_prompt_url: The URL to which to send status callbacks and reports.
            Authentication can also be set in the url in the format of
            `username:password@url`.
        pronounce: An array of JSON objects to clarify the AI's pronunciation of words
            or expressions.
        prompt: Defines the AI agent's personality, goals, behaviors, and instructions
            for handling conversations. The prompt establishes how the agent should
            interact with callers, what information it should gather, and how it should
            respond to various scenarios. It is recommended to write prompts using
            markdown formatting.
        SWAIG: An array of JSON objects to create user-defined functions/endpoints that
            can be executed during the dialogue.
    """

    global_data: dict[str, Any]
    hints: list[str | Hint]
    languages: list[Languages]
    params: AIParams
    post_prompt: AIPostPrompt
    post_prompt_url: str
    pronounce: list[Pronounce]
    prompt: AIPrompt
    SWAIG: SWAIG


class AIParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        acknowledge_interruptions: Instructs the agent to acknowledge crosstalk and
            confirm user input when the user speaks over the agent.
        ai_model: The model to use for the AI. Allowed values are `gpt-4o-mini`,
            `gpt-4.1-mini`, and `gpt-4.1-nano`.
        ai_name: Sets the name the AI agent responds to for wake/activation purposes.
            When using `enable_pause`, `start_paused`, or `speak_when_spoken_to`, the
            user must say this name to get the agent's attention. The name matching is
            case-insensitive.
        ai_volume: Adjust the volume of the AI. Allowed values from `-50` - `50`.
            **Default:** `0`.
        app_name: A custom identifier for the AI application instance. This name is
            included in webhook payloads, allowing backend systems to identify which AI
            configuration made the request.
        asr_smart_format: If true, enables smart formatting in ASR (Automatic Speech
            Recognition). This improves the formatting of numbers, dates, times, and
            other entities in the transcript. **Default:** `false`
        attention_timeout: Amount of time, in ms, to wait before prompting the user to
            respond. Allowed values from `10,000` - `600,000`. Set to `0` to disable.
            **Default:** `5000` ms (note: user-configurable values must be `0` or within
            the `10,000` - `600,000` range).
        attention_timeout_prompt: A custom prompt that is fed into the AI when the
            attention_timeout is reached.
        asr_diarize: If true, enables speaker diarization in ASR (Automatic Speech
            Recognition). This will break up the transcript into chunks, with each chunk
            containing a unique identity (e.g speaker1, speaker2, etc.) and the text
            they spoke. **Default:** `false`
        asr_speaker_affinity: If true, will force the AI Agent to only respond to the
            speaker who reesponds to the AI Agent first. Any other speaker will be
            ignored. **Default:** `false`
        background_file: URL of audio file to play in the background while AI plays in
            foreground.
        background_file_loops: Maximum number of times to loop playing the background
            file. `undefined` means loop indefinitely.
        background_file_volume: Defines background_file volume within a range of `-50`
            to `50`. **Default:** `0`.
        enable_barge: Controls the barge behavior. Allowed values are `"complete"`,
            `"partial"`, `"all"`, or boolean. **Default:** `"complete,partial"`
        enable_inner_dialog: Enables the inner dialog feature, which runs a separate AI
            process in the background that analyzes the conversation and provides
            real-time insights to the main AI agent. This gives the agent a form of
            "internal thought process" that can help it make better decisions.
        enable_pause: Enables the pause/resume functionality for the AI agent. When
            enabled, a `pause_conversation` function is automatically added that the AI
            can call when the user says things like "hold on", "wait", or "pause". While
            paused, the agent stops responding until the user speaks the agent's name
            (set via `ai_name`) to resume. Cannot be used together with
            `speak_when_spoken_to`.
        enable_turn_detection: Enables intelligent turn detection that monitors partial
            speech transcripts for sentence-ending punctuation. When detected, the
            system can proactively finalize the speech recognition, reducing latency
            before the AI responds. Works with `turn_detection_timeout`.
        barge_match_string: Takes a string, including a regular expression, defining
            barge behavior. For example, this param can direct the AI to stop when the
            word 'hippopotomus' is input.
        barge_min_words: Defines the number of words that must be input before
            triggering barge behavior, in a range of `1-99`.
        barge_functions: If `true`, allows functions to be executed while the AI is
            being interrupted. **Default:** `true`.
        conscience: Sets the prompt which binds the agent to its purpose.
        convo: Injects pre-existing conversation history into the AI session at startup.
            This allows you to seed the AI agent with context from a previous
            conversation or provide example interactions.
        conversation_id: Used by `check_for_input` and `save_conversation` to identify
            an individual conversation.
        conversation_sliding_window: Sets the size of the sliding window for
            conversation history. This limits how much conversation history is sent to
            the AI model.
        debug_webhook_level: Enables debugging to the set URL. Allowed values from `0` -
            `2`. Default is `1` if url is set.
        debug_webhook_url: Each interaction between the AI and end user is posted in
            real time to the established URL.
        debug: Enables debug mode for the AI session. When enabled, additional
            diagnostic information is logged including turn detection events, speech
            processing details, and internal state changes.
        direction: Forces the direction of the call to the assistant. Valid values are
            `inbound` and `outbound`.
        digit_terminators: DTMF digit, as a string, to signal the end of input (ex: '#')
        digit_timeout: Time, in ms, at the end of digit input to detect end of input.
            Allowed values from `0` - `30,000`. **Default:** `3000` ms.
        end_of_speech_timeout: Amount of silence, in ms, at the end of an utterance to
            detect end of speech. Allowed values from `250` - `10,000`. **Default:**
            `700` ms.
        enable_thinking: Enables thinking output for the AI Agent. When set to `true`,
            the AI Agent will be able to utilize thinking capabilities. **Important**:
            This may introduce a little bit of latency as the AI will use an additional
            turn in the conversation to think about the query.
        enable_vision: Enables visual input processing for the AI Agent. When set to
            `true`, the AI Agent will be able to utilize visual processing capabilities,
            while leveraging the `get_visual_input` function.
        energy_level: Amount of energy necessary for bot to hear you (in dB). Allowed
            values from `0.0` - `100.0`. **Default:** `52.0` dB.
        first_word_timeout: Amount of time, in ms, to wait for the first word after
            speech is detected. Allowed values from `0` - `10,000`. **Default:** `1000`
            ms.
        function_wait_for_talking: If `true`, the AI will wait for any `filler` to
            finish playing before executing a function. If `false`, the AI will execute
            a function asynchronously as the `filler` plays. **Default:** `false`.
        functions_on_no_response: If `true`, functions can be executed when there is no
            user response after a timeout. **Default:** `false`.
        hard_stop_prompt: A final prompt that is fed into the AI when the
            `hard_stop_time` is reached.
        hard_stop_time: Specifies the maximum duration fopr the AI Agent to remain
            active before it exists the session. After the timeout, the AI will stop
            responding, and will proceed with the next SWML instruction.

            **Time Format:**
              - Seconds Format: `30s`
              - Minutes Format: `2m`
              - Hours Format: `1h`
              - Combined Format: `1h45m30s`
        hold_music: A URL for the hold music to play, accepting WAV, mp3, and FreeSWITCH
            tone_stream.
        hold_on_process: Enables hold music during SWAIG processing.
        inactivity_timeout: Amount of time, in ms, to wait before exiting the app due to
            inactivity. Allowed values from `10,000` - `3,600,000`. **Default:**
            `600000` ms (10 minutes).
        inner_dialog_model: Specifies the AI model to use for the inner dialog feature.
            Can be set to a different (often smaller/faster) model than the main
            conversation model. Only used when `enable_inner_dialog` is `true`.
        inner_dialog_prompt: The system prompt that guides the inner dialog AI's
            behavior. This prompt shapes how the background AI analyzes the conversation
            and what kind of insights it provides to the main agent. Only used when
            `enable_inner_dialog` is `true`.
        inner_dialog_synced: When enabled, synchronizes the inner dialog with the main
            conversation flow. This ensures the inner dialog AI waits for the main
            conversation turn to complete before providing its analysis, rather than
            running fully asynchronously. Only used when `enable_inner_dialog` is
            `true`.
        initial_sleep_ms: Amount of time, in ms, to wait before starting the
            conversation. Allowed values from `0` - `300,000`.
        input_poll_freq: Check for input function with check_for_input. Example use
            case: Feeding an inbound SMS to AI on a voice call, eg., for collecting an
            email address or other complex information. Allowed values from `1000` to
            `10000` ms. **Default:** `2000` ms.
        interrupt_on_noise: When enabled, barges agent upon any sound interruption
            longer than 1 second.
        interrupt_prompt: Provide a prompt for the agent to handle crosstalk.
        languages_enabled: Allows multilingualism when `true`. Deprecated.
        local_tz: The local timezone setting for the AI. Value should use `IANA TZ ID`
        llm_diarize_aware: If true, the AI Agent will be involved with the diarization
            process. Users can state who they are at the start of the conversation and
            the AI Agent will be able to correctly identify them when they are speaking
            later in the conversation. **Default:** `false`
        max_emotion: Sets the maximum emotion intensity for the AI voice. Allowed values
            from `1` - `30`. **Default:** `30`.
        max_response_tokens: Sets the maximum number of tokens the AI model can generate
            in a single response. Lower values produce shorter responses and reduce
            latency.
        openai_asr_engine: The ASR (Automatic Speech Recognition) engine to use. Common
            values include `nova-2` and `nova-3`.
        outbound_attention_timeout: Sets a time duration for the outbound call recipient
            to respond to the AI agent before timeout, in a range from `10000` to
            `600000`. **Default:** `120000` ms (2 minutes).
        persist_global_data: When enabled, the `global_data` object is automatically
            saved to a channel variable and restored when a new AI session starts on the
            same call. This allows data to persist across multiple AI agent invocations
            within the same call.
        pom_format: Specifies the output format for structured prompts when using the
            `pom` array in prompt definitions. Valid values are `markdown` or `xml`.
        save_conversation: Send a summary of the conversation after the call ends. This
            requires a `post_url` to be set in the ai parameters and the
            `conversation_id` defined below. This eliminates the need for a
            `post_prompt` in the ai parameters.
        speech_event_timeout: Amount of time, in ms, to wait for a speech event. Allowed
            values from `0` - `10,000`. **Default:** `1400` ms.
        speech_gen_quick_stops: Number of quick stops to generate for speech. Allowed
            values from `0` - `10`. **Default:** `3`.
        speech_timeout: Overall speech timeout, in ms. Allowed values from `0` -
            `600,000`. **Default:** `60000` ms.
        speak_when_spoken_to: When enabled, the AI agent remains silent until directly
            addressed by name (using `ai_name`). This creates a "push-to-talk" style
            interaction where the agent only responds when explicitly called upon,
            useful for scenarios where the agent should listen but not interrupt. Cannot
            be used together with `enable_pause`.
        start_paused: When enabled, the AI agent starts in a paused state and will not
            respond until the user speaks the agent's name (set via `ai_name`).
            Automatically enables `enable_pause`. This is useful for scenarios where you
            want the agent to wait for explicit activation.
        static_greeting: The static greeting to play when the call is answered. This
            will always play at the beginning of the call.
        static_greeting_no_barge: If `true`, the static greeting will not be interrupted
            by the user if they speak over the greeting. If `false`, the static greeting
            can be interrupted by the user if they speak over the greeting.
        summary_mode: Defines the mode for summary generation. Allowed values are
            `"string"` and `"original"`.
        swaig_allow_settings: Allows tweaking any of the indicated settings, such as
            `barge_match_string`, using the returned SWML from the SWAIG function.
            **Default:** `true`.
        swaig_allow_swml: Allows your SWAIG to return SWML to be executed. **Default:**
            `true`.
        swaig_post_conversation: Post entire conversation to any SWAIG call.
        swaig_set_global_data: Allows SWAIG to set global data that persists across
            calls. **Default:** `true`.
        swaig_post_swml_vars: Controls whether SWML variables are included in SWAIG
            function webhook payloads. When set to `true`, all SWML variables are
            posted. When set to an array of strings, only the specified variable names
            are included.
        thinking_model: The model to use for the AI's thinking capabilities. Allowed
            values are `gpt-4o-mini`, `gpt-4.1-mini`, and `gpt-4.1-nano`.
        transparent_barge: When enabled, the AI will not respond to the user's input
            when the user is speaking over the agent. The agent will wait for the user
            to finish speaking before responding. Additionally, any attempt the LLM
            makes to barge will be ignored and scraped from the conversation logs.
            **Default:** `true`.
        transparent_barge_max_time: Maximum time, in ms, for transparent barge mode.
            Allowed values from `0` - `60,000`. **Default:** `3000` ms.
        transfer_summary: Pass a summary of a conversation from one AI agent to another.
            For example, transfer a call summary between support agents in two
            departments.
        turn_detection_timeout: Time in milliseconds to wait after detecting a potential
            end-of-turn before finalizing speech recognition. A shorter timeout results
            in faster response times but may cut off the user if they pause
            mid-sentence. Set to `0` to finalize immediately. Only used when
            `enable_turn_detection` is `true`.
        tts_number_format: The format for the AI agent to reference phone numbers.
            Allowed values are `international` and `national`. **Default:**
            `international`.

            **Example:**
            - `international`: `+12345678901`
            - `national`: `(234) 567-8901`
        video_listening_file: URL of a video file to play when AI is listening to the
            user speak. Only works for calls that support video.
        video_idle_file: URL of a video file to play when AI is idle. Only works for
            calls that support video.
        video_talking_file: URL of a video file to play when AI is talking. Only works
            for calls that support video.
        vision_model: The model to use for the AI's vision capabilities. Allowed values
            are `gpt-4o-mini`, `gpt-4.1-mini`, and `gpt-4.1-nano`.
        vad_config: Configures Silero Voice Activity Detection (VAD) settings. Format:
            `"threshold"` or `"threshold:frame_ms"`. The threshold (0-100) sets
            sensitivity for detecting voice activity. The optional frame_ms (16-40) sets
            frame duration in milliseconds.
        wait_for_user: When false, AI agent will initialize dialogue after call is
            setup. When true, agent will wait for the user to speak first.
        wake_prefix: Specifies an additional prefix that must be spoken along with the
            agent's name (`ai_name`) to wake the agent from a paused state. For example,
            if `ai_name` is "computer" and `wake_prefix` is "hey", the user would need
            to say "hey computer" to activate the agent.
        eleven_labs_stability: The stability slider determines how stable the voice is
            and the randomness between each generation. Lowering this slider introduces
            a broader emotional range for the voice. Deprecated.
        eleven_labs_similarity: The similarity slider dictates how closely the AI should
            adhere to the original voice when attempting to replicate it. The higher the
            similarity, the closer the AI will sound to the original voice. Deprecated.
    """

    acknowledge_interruptions: bool | SWMLVar
    ai_model: Literal["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano"] | str
    ai_name: str
    ai_volume: int | SWMLVar
    app_name: str
    asr_smart_format: bool | SWMLVar
    attention_timeout: AttentionTimeout | Literal[0] | SWMLVar
    attention_timeout_prompt: str
    asr_diarize: bool | SWMLVar
    asr_speaker_affinity: bool | SWMLVar
    background_file: str
    background_file_loops: int | None | SWMLVar
    background_file_volume: int | SWMLVar
    enable_barge: str | bool | SWMLVar
    enable_inner_dialog: bool | SWMLVar
    enable_pause: bool | SWMLVar
    enable_turn_detection: bool | SWMLVar
    barge_match_string: str
    barge_min_words: int | SWMLVar
    barge_functions: bool | SWMLVar
    conscience: str
    convo: list[ConversationMessage]
    conversation_id: str
    conversation_sliding_window: int | SWMLVar
    debug_webhook_level: int | SWMLVar
    debug_webhook_url: str
    debug: bool | int | SWMLVar
    direction: Direction | SWMLVar
    digit_terminators: str
    digit_timeout: int | SWMLVar
    end_of_speech_timeout: int | SWMLVar
    enable_thinking: bool | SWMLVar
    enable_vision: bool | SWMLVar
    energy_level: float | SWMLVar
    first_word_timeout: int | SWMLVar
    function_wait_for_talking: bool | SWMLVar
    functions_on_no_response: bool | SWMLVar
    hard_stop_prompt: str
    hard_stop_time: str | SWMLVar
    hold_music: str
    hold_on_process: bool | SWMLVar
    inactivity_timeout: int | SWMLVar
    inner_dialog_model: Literal["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano"] | str
    inner_dialog_prompt: str
    inner_dialog_synced: bool | SWMLVar
    initial_sleep_ms: int | SWMLVar
    input_poll_freq: int | SWMLVar
    interrupt_on_noise: bool | SWMLVar
    interrupt_prompt: str
    # deprecated: languages_enabled
    languages_enabled: bool | SWMLVar
    local_tz: str
    llm_diarize_aware: bool | SWMLVar
    max_emotion: int | SWMLVar
    max_response_tokens: int | SWMLVar
    openai_asr_engine: str
    outbound_attention_timeout: int | SWMLVar
    persist_global_data: bool | SWMLVar
    pom_format: Literal["markdown", "xml"]
    save_conversation: bool | SWMLVar
    speech_event_timeout: int | SWMLVar
    speech_gen_quick_stops: int | SWMLVar
    speech_timeout: int | SWMLVar
    speak_when_spoken_to: bool | SWMLVar
    start_paused: bool | SWMLVar
    static_greeting: str
    static_greeting_no_barge: bool | SWMLVar
    summary_mode: Literal["string", "original"] | SWMLVar
    swaig_allow_settings: bool | SWMLVar
    swaig_allow_swml: bool | SWMLVar
    swaig_post_conversation: bool | SWMLVar
    swaig_set_global_data: bool | SWMLVar
    swaig_post_swml_vars: bool | list[str] | SWMLVar
    thinking_model: Literal["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano"] | str
    transparent_barge: bool | SWMLVar
    transparent_barge_max_time: int | SWMLVar
    transfer_summary: bool | SWMLVar
    turn_detection_timeout: int | SWMLVar
    tts_number_format: Literal["international", "national"]
    video_listening_file: str
    video_idle_file: str
    video_talking_file: str
    vision_model: Literal["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano"] | str
    vad_config: str
    wait_for_user: bool | SWMLVar
    wake_prefix: str
    eleven_labs_stability: float | SWMLVar
    eleven_labs_similarity: float | SWMLVar


AIPostPrompt: TypeAlias = "AIPostPromptText | AIPostPromptPom"


class AIPostPromptPom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        max_tokens: Limits the amount of tokens that the AI agent may generate when
            creating its response
        temperature: Randomness setting. Float value between 0.0 and 1.5. Closer to 0
            will make the output less random. **Default:** `1.0`.
        top_p: Randomness setting. Alternative to `temperature`. Float value between 0.0
            and 1.0. Closer to 0 will make the output less random. **Default:** `1.0`.
        confidence: Threshold to fire a speech-detect event at the end of the utterance.
            Float value between 0.0 and 1.0. Decreasing this value will reduce the pause
            after the user speaks, but may introduce false positives. **Default:**
            `0.6`.
        presence_penalty: Aversion to staying on topic. Float value between -2.0 and
            2.0. Positive values increase the model's likelihood to talk about new
            topics. **Default:** `0`.
        frequency_penalty: Aversion to repeating lines. Float value between -2.0 and
            2.0. Positive values decrease the model's likelihood to repeat the same line
            verbatim. **Default:** `0`.
        pom: The instructions to send to the agent.
    """

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    pom: list[POM]


class AIPostPromptText(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        max_tokens: Limits the amount of tokens that the AI agent may generate when
            creating its response
        temperature: Randomness setting. Float value between 0.0 and 1.5. Closer to 0
            will make the output less random. **Default:** `1.0`.
        top_p: Randomness setting. Alternative to `temperature`. Float value between 0.0
            and 1.0. Closer to 0 will make the output less random. **Default:** `1.0`.
        confidence: Threshold to fire a speech-detect event at the end of the utterance.
            Float value between 0.0 and 1.0. Decreasing this value will reduce the pause
            after the user speaks, but may introduce false positives. **Default:**
            `0.6`.
        presence_penalty: Aversion to staying on topic. Float value between -2.0 and
            2.0. Positive values increase the model's likelihood to talk about new
            topics. **Default:** `0`.
        frequency_penalty: Aversion to repeating lines. Float value between -2.0 and
            2.0. Positive values decrease the model's likelihood to repeat the same line
            verbatim. **Default:** `0`.
        text: The instructions to send to the agent.
    """

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    text: str


AIPrompt: TypeAlias = "AIPromptText | AIPromptPom"


class AIPromptPom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        max_tokens: Limits the amount of tokens that the AI agent may generate when
            creating its response
        temperature: Randomness setting. Float value between 0.0 and 1.5. Closer to 0
            will make the output less random. **Default:** `1.0`.
        top_p: Randomness setting. Alternative to `temperature`. Float value between 0.0
            and 1.0. Closer to 0 will make the output less random. **Default:** `1.0`.
        confidence: Threshold to fire a speech-detect event at the end of the utterance.
            Float value between 0.0 and 1.0. Decreasing this value will reduce the pause
            after the user speaks, but may introduce false positives. **Default:**
            `0.6`.
        presence_penalty: Aversion to staying on topic. Float value between -2.0 and
            2.0. Positive values increase the model's likelihood to talk about new
            topics. **Default:** `0`.
        frequency_penalty: Aversion to repeating lines. Float value between -2.0 and
            2.0. Positive values decrease the model's likelihood to repeat the same line
            verbatim. **Default:** `0`.
        pom: Prompt Object Model (POM) is a structured data format for composing,
            organizing, and rendering prompt instructions for AI agents. POM ensures
            that the prompt is structured in a way that is best for the AI agent to
            understand and execute. The first item in the array MUST be FirstPOMSection
            (with optional title). All subsequent items MUST be PomSection (with
            required title and body).
        contexts: An object that defines the context steps for the AI. The context steps
            are used to define the flow of the conversation. Every context object
            requires a `default` key, which is the default context to use at the
            beginning of the conversation. Additionally, more context steps can be
            defined as any other key in the object.
    """

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    pom: list[POM]
    contexts: Contexts


class AIPromptText(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        max_tokens: Limits the amount of tokens that the AI agent may generate when
            creating its response
        temperature: Randomness setting. Float value between 0.0 and 1.5. Closer to 0
            will make the output less random. **Default:** `1.0`.
        top_p: Randomness setting. Alternative to `temperature`. Float value between 0.0
            and 1.0. Closer to 0 will make the output less random. **Default:** `1.0`.
        confidence: Threshold to fire a speech-detect event at the end of the utterance.
            Float value between 0.0 and 1.0. Decreasing this value will reduce the pause
            after the user speaks, but may introduce false positives. **Default:**
            `0.6`.
        presence_penalty: Aversion to staying on topic. Float value between -2.0 and
            2.0. Positive values increase the model's likelihood to talk about new
            topics. **Default:** `0`.
        frequency_penalty: Aversion to repeating lines. Float value between -2.0 and
            2.0. Positive values decrease the model's likelihood to repeat the same line
            verbatim. **Default:** `0`.
        text: The instructions to send to the agent.
        contexts: An object that defines the context steps for the AI. The context steps
            are used to define the flow of the conversation. Every context object
            requires a `default` key, which is the default context to use at the
            beginning of the conversation. Additionally, more context steps can be
            defined as any other key in the object.
    """

    max_tokens: int
    temperature: float | SWMLVar
    top_p: float | SWMLVar
    confidence: float | SWMLVar
    presence_penalty: float | SWMLVar
    frequency_penalty: float | SWMLVar
    text: str
    contexts: Contexts


Action: TypeAlias = "SWMLAction | ChangeContextAction | ChangeStepAction | ContextSwitchAction | HangupAction | HoldAction | PlaybackBGAction | SayAction | SetGlobalDataAction | SetMetaDataAction | StopAction | StopPlaybackBGAction | ToggleFunctionsAction | UnsetGlobalDataAction | UnsetMetaDataAction | UserInputAction"


class AllOfProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        allOf: An array of schemas where all of the schemas must be valid.
    """

    allOf: list[SchemaType]


class AmazonBedrock(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        amazon_bedrock: Creates a new Bedrock AI Agent
    """

    amazon_bedrock: AmazonBedrockObject


class AmazonBedrockObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        global_data: A powerful and flexible environmental variable which can accept
            arbitrary data that is set initially in the SWML script or from the SWML
            `set_global_data` action. This data can be referenced `globally`. All
            contained information can be accessed and expanded within the prompt - for
            example, by using a template string.
        params: A JSON object containing parameters as key-value pairs.
        post_prompt: The final set of instructions and configuration settings to send to
            the agent.
        post_prompt_url: The URL to which to send status callbacks and reports.
            Authentication can also be set in the url in the format of
            `username:password@url`.
        prompt: Establishes the initial set of instructions and settings to configure
            the agent.
        SWAIG: An array of JSON objects to create user-defined functions/endpoints that
            can be executed during the dialogue.
    """

    global_data: dict[str, Any]
    params: BedrockParams
    post_prompt: BedrockPostPrompt
    post_prompt_url: str
    prompt: BedrockPrompt
    SWAIG: BedrockSWAIG


class Answer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        answer: Answer incoming call and set an optional maximum duration.
    """

    answer: dict[str, Any]


class AnyOfProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        anyOf: An array of schemas where at least one of the schemas must be valid.
    """

    anyOf: list[SchemaType]


class ArrayProperty(TypedDict, total=False):
    """Base interface for all property types.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        description: A description of the property.
        nullable: Whether the property can be null.
        type: The type of parameter(s) the AI is passing to the function.
        default: The default array value
        items: Schema for array items
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["array"]
    default: list[Any]
    items: SchemaType


AttentionTimeout: TypeAlias = "int"


class BedrockParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        attention_timeout: Amount of time, in ms, to wait before prompting the user to
            respond. Allowed values from `10,000` - `600,000`. Set to `0` to disable.
            **Default:** `5000` ms (note: user-configurable values must be `0` or within
            the `10,000` - `600,000` range).
        hard_stop_time: Specifies the maximum duration fopr the AI Agent to remain
            active before it exists the session. After the timeout, the AI will stop
            responding, and will proceed with the next SWML instruction.

            **Time Format:**
              - Seconds Format: `30s`
              - Minutes Format: `2m`
              - Hours Format: `1h`
              - Combined Format: `1h45m30s`
        inactivity_timeout: Amount of time, in ms, to wait before exiting the app due to
            inactivity. Allowed values from `10,000` - `3,600,000`. **Default:**
            `600000` ms (10 minutes).
        video_listening_file: URL of a video file to play when AI is listening to the
            user speak. Only works for calls that support video.
        video_idle_file: URL of a video file to play when AI is idle. Only works for
            calls that support video.
        video_talking_file: URL of a video file to play when AI is talking. Only works
            for calls that support video.
        hard_stop_prompt: A final prompt that is fed into the AI when the
            `hard_stop_time` is reached.
    """

    attention_timeout: AttentionTimeout | Literal[0] | SWMLVar
    hard_stop_time: str | SWMLVar
    inactivity_timeout: int | SWMLVar
    video_listening_file: str
    video_idle_file: str
    video_talking_file: str
    hard_stop_prompt: str


BedrockPostPrompt: TypeAlias = "dict[str, Any]"

BedrockPrompt: TypeAlias = "dict[str, Any]"


class BedrockSWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        functions: An array of JSON objects to define functions that can be executed
            during the interaction with the Bedrock AI. Default is not set. The fields
            of this object are the six following.
        defaults: Default settings for all SWAIG functions. If `defaults` is not set,
            settings may be set in each function object. Default is not set.
        native_functions: Prebuilt functions the AI agent is able to call from this list
            of available native functions
        includes: An array of objects to include remote function signatures. This allows
            you to include functions that are defined in a remote location. The object
            fields are `url` to specify where the remote functions are defined and
            `functions` which is an array of the function names as strings.
    """

    functions: list[BedrockSWAIGFunction]
    defaults: SWAIGDefaults
    native_functions: list[SWAIGNativeFunction]
    includes: list[SWAIGIncludes]


BedrockSWAIGFunction: TypeAlias = "dict[str, Any]"


class BooleanProperty(TypedDict, total=False):
    """Base interface for all property types.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        description: A description of the property.
        nullable: Whether the property can be null.
        type: The type of parameter(s) the AI is passing to the function.
        default: The default boolean value
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["boolean"]
    default: bool | SWMLVar


class CallAIMessageRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of a existing call.
        command: The `calling.ai_message` command is used to inject a message into the
            AI conversation.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.ai_message"]
    params: dict[str, Any]


class CallAIMessageResetParams(TypedDict, total=False):
    """Parameters for resetting the AI conversation state.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        full_reset: Whether to perform a full reset of the AI conversation, clearing all
            history.
        user_prompt: A new user prompt to set after resetting the conversation.
        system_prompt: A new system prompt to set after resetting the conversation.
    """

    full_reset: bool
    user_prompt: str
    system_prompt: str


class CallCreate422Error(TypedDict, total=False):
    """The request contains invalid parameters.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class CallCreateParamsSWML(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The address that initiated the call. Can be either a E.164
      formatted number (`+xxxxxxxxxxx`), or a SIP endpoint (`sip:xxx@yyy.zzz`).

    Attributes:
        to: The address that received the call. Can be either a E.164 formatted number
            (`+xxxxxxxxxxx`), or a SIP endpoint (`sip:xxx@yyy.zzz`).
        caller_id: The number, in E.164 format, or identifier of the caller.
        fallback_url: The Fallback URL to handle the call. This parameter allows you to
            specify a backup webhook or different route in your code containing SWML
            instructions for handling the call.
        status_url: A URL that will recieve status updates of the current call. Any call
            events defined in `status_events` will be delivered to the defined URL.
        status_events: The call events that will be monitored and sent to the
            `status_url` when active.
        url_method: The HTTP method to use when requesting the URL.
        codecs: A list of codecs to use for the call. Can be an array of codec strings
            or a comma-separated string. Valid codecs are: `PCMU`, `PCMA`, `G722`,
            `G729`, `OPUS`, `VP8`, `H264`. For PSTN calls, `PCMA` and `PCMU` are
            recommended as many other codecs are not supported by PSTN gateways. If a
            SIP URI with included codecs is passed in the `to` field along with this
            parameter, the SIP URI codecs will be prioritized.
        swml: Inline SWML object containing SWML instructions for handling the call.
            Either `url` or `swml` must be included for a new call.
    """

    # non-identifier field 'from': str
    to: str
    caller_id: str
    fallback_url: str
    status_url: str
    status_events: list[
        Literal["answered", "queued", "initiated", "ringing", "ending", "ended"]
    ]
    url_method: str
    codecs: list[str] | str
    swml: SWMLObject


class CallCreateParamsURL(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The address that initiated the call. Can be either a E.164
      formatted number (`+xxxxxxxxxxx`), or a SIP endpoint (`sip:xxx@yyy.zzz`).

    Attributes:
        to: The address that received the call. Can be either a E.164 formatted number
            (`+xxxxxxxxxxx`), or a SIP endpoint (`sip:xxx@yyy.zzz`).
        caller_id: The number, in E.164 format, or identifier of the caller.
        fallback_url: The Fallback URL to handle the call. This parameter allows you to
            specify a backup webhook or different route in your code containing SWML
            instructions for handling the call.
        status_url: A URL that will recieve status updates of the current call. Any call
            events defined in `status_events` will be delivered to the defined URL.
        status_events: The call events that will be monitored and sent to the
            `status_url` when active.
        url_method: The HTTP method to use when requesting the URL.
        url: The URL to handle the call. This parameter allows you to specify a webhook
            or different route in your code containing SWML instructions for handling
            the call. Either `url` or `swml` must be included for a new call.
    """

    # non-identifier field 'from': str
    to: str
    caller_id: str
    fallback_url: str
    status_url: str
    status_events: list[
        Literal["answered", "queued", "initiated", "ringing", "ending", "ended"]
    ]
    url_method: str
    url: str


class CallCreateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        command: The `dial` command is used to create a new call.
        params: An object of parameters that will be utilized by the active command.
    """

    command: Literal["dial"]
    params: CallCreateParamsURL | CallCreateParamsSWML


CallDirection: TypeAlias = "Literal['inbound', 'outbound', 'outbound-api']"


class CallHangupRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of a existing call.
        command: The `calling.end` command is used to hang up a call.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.end"]
    params: dict[str, Any]


class CallHoldRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of a existing call.
        command: The `calling.ai_hold` command is used to hold a call.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.ai_hold"]
    params: dict[str, Any]


class CallLeg(TypedDict, total=False):
    """A Call leg (PSTN, SIP, or WebRTC).

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The origin number or address.

    Attributes:
        id: The unique identifier of the call on SignalWire. This can be used to update
            the call programmatically.
        to: The destination number or address.
        direction: The direction of the call.
        source: Source of this call.
        url: The URL associated with this call.
        charge: Total charge for this call.
        created_at: The date and time when the call was created.
        charge_details: Details on charges associated with this call.
        status: The status of the call.
        duration: The duration of the call in seconds.
        duration_ms: The duration of the call in milliseconds.
        billing_ms: The billable duration of the call in milliseconds.
        type: Type of this call.
        parent_id: The parent call ID if this is a child call.
    """

    id: uuid
    # non-identifier field 'from': str
    to: str
    direction: CallDirection
    source: Literal["realtime_api"]
    url: str | None
    charge: float
    created_at: str
    charge_details: list[ChargeDetails]
    status: CallResponseStatus | None
    duration: int | None
    duration_ms: int | None
    billing_ms: int | None
    type: (
        Literal["relay_pstn_call"]
        | Literal["relay_sip_call"]
        | Literal["relay_webrtc_call"]
    )
    parent_id: uuid | None


class CallLiveTranscribeRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of a existing call.
        command: The `calling.live_transcribe` command is used to control live
            transcription on an active call.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.live_transcribe"]
    params: dict[str, Any]


class CallLiveTranslateRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of a existing call.
        command: The `calling.live_translate` command is used to control live
            translation on an active call.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.live_translate"]
    params: dict[str, Any]


CallRequest: TypeAlias = "CallCreateRequest | CallUpdateCurrentCallRequest | CallHangupRequest | CallHoldRequest | CallUnholdRequest | CallAIMessageRequest | CallLiveTranscribeRequest | CallLiveTranslateRequest | CallTransferRequest | CallUserEventRequest | CallDisconnectRequest | CallPlayRequest | CallPlayPauseRequest | CallPlayResumeRequest | CallPlayStopRequest | CallPlayVolumeRequest | CallRecordRequest | CallRecordPauseRequest | CallRecordResumeRequest | CallRecordStopRequest | CallCollectRequest | CallCollectStopRequest | CallCollectStartInputTimersRequest | CallDetectRequest | CallDetectStopRequest | CallTapRequest | CallTapStopRequest | CallStreamRequest | CallStreamStopRequest | CallDenoiseRequest | CallDenoiseStopRequest | CallTranscribeRequest | CallTranscribeStopRequest | CallAIStopRequest | CallSendFaxStopRequest | CallReceiveFaxStopRequest | CallReferRequest"


class CallDisconnectRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.disconnect` command disconnects bridged calls without
            hanging up either leg.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.disconnect"]
    params: dict[str, Any]


class CallPlayRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.play` command plays audio, TTS, silence, or ringtone to a
            call.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.play"]
    params: dict[str, Any]


class CallPlayPauseRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.play.pause` command pauses an active play operation.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.play.pause"]
    params: dict[str, Any]


class CallPlayResumeRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.play.resume` command resumes a paused play operation.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.play.resume"]
    params: dict[str, Any]


class CallPlayStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.play.stop` command stops an active play operation.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.play.stop"]
    params: dict[str, Any]


class CallPlayVolumeRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.play.volume` command adjusts the volume of an active play
            operation.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.play.volume"]
    params: dict[str, Any]


class CallRecordRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.record` command starts recording a call. Supports parallel
            recordings via multiple control_ids.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.record"]
    params: dict[str, Any]


class CallRecordPauseRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.record.pause` command pauses an active recording.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.record.pause"]
    params: dict[str, Any]


class CallRecordResumeRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.record.resume` command resumes a paused recording.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.record.resume"]
    params: dict[str, Any]


class CallRecordStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.record.stop` command stops an active recording.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.record.stop"]
    params: dict[str, Any]


class CallCollectRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.collect` command collects DTMF or speech input from a
            call.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.collect"]
    params: dict[str, Any]


class CallCollectStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.collect.stop` command stops an active input collection.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.collect.stop"]
    params: dict[str, Any]


class CallCollectStartInputTimersRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.collect.start_input_timers` command starts input timers on
            an active collect operation.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.collect.start_input_timers"]
    params: dict[str, Any]


class CallDetectRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.detect` command starts a detector (answering machine, fax,
            or digit).
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.detect"]
    params: dict[str, Any]


class CallDetectStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.detect.stop` command stops an active detector.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.detect.stop"]
    params: dict[str, Any]


class CallTapRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.tap` command taps call audio to an RTP or WebSocket
            endpoint.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.tap"]
    params: dict[str, Any]


class CallTapStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.tap.stop` command stops an active tap.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.tap.stop"]
    params: dict[str, Any]


class CallStreamRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.stream` command streams call audio to a WebSocket
            endpoint.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.stream"]
    params: dict[str, Any]


class CallStreamStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.stream.stop` command stops an active audio stream.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.stream.stop"]
    params: dict[str, Any]


class CallDenoiseRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.denoise` command starts noise reduction on a call.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.denoise"]
    params: dict[str, Any]


class CallDenoiseStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.denoise.stop` command stops noise reduction on a call.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.denoise.stop"]
    params: dict[str, Any]


class CallTranscribeRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.transcribe` command starts call transcription. Only one
            active transcription per call.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.transcribe"]
    params: dict[str, Any]


class CallTranscribeStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.transcribe.stop` command stops active transcription.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.transcribe.stop"]
    params: dict[str, Any]


class CallAIStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.ai.stop` command stops an active AI session on a call.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.ai.stop"]
    params: dict[str, Any]


class CallSendFaxStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.send_fax.stop` command stops an active fax send operation.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.send_fax.stop"]
    params: dict[str, Any]


class CallReceiveFaxStopRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.receive_fax.stop` command stops an active fax receive
            operation.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.receive_fax.stop"]
    params: dict[str, Any]


class CallReferRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of an existing call.
        command: The `calling.refer` command transfers a SIP call via SIP REFER.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.refer"]
    params: dict[str, Any]


CallResponse: TypeAlias = "CallLeg | FabricDeviceLeg"

CallResponseStatus: TypeAlias = "Literal['queued', 'initiated', 'created', 'ringing', 'answered', 'ending', 'ended', 'failed', 'canceled', 'completed']"

CallStatus: TypeAlias = "Literal['created', 'ringing', 'answered', 'ended']"


class CallTransferRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of a existing call.
        command: The `calling.transfer` command is used to transfer an active call to a
            new destination.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.transfer"]
    params: dict[str, Any]


class CallUnholdRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of a existing call.
        command: The `calling.ai_unhold` command is used to unhold a call.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.ai_unhold"]
    params: dict[str, Any]


class CallUpdateCurrentCallRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        command: The `update` command is used to update a existing call with a new
            dialplan.
        params: An object of parameters that will be utilized by the active command.
    """

    command: Literal["update"]
    params: CallUpdateParamsURL | CallUpdateParamsSWML


class CallUpdateParamsSWML(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of a existing call.
        fallback_url: The Fallback URL to handle the call. This parameter allows you to
            specify a backup webhook or different route in your code containing SWML
            instructions for handling the call.
        status: Either `canceled` (to cancel a not yet connected call) or `completed`
            (to end a call that is in progress).
        status_url: A URL to receive call status update callbacks.
        swml: Inline SWML object containing SWML instructions for handling the call.
            Either `url` or `swml` must be included for a new call.
    """

    id: uuid
    fallback_url: str
    status: Literal["canceled", "completed"]
    status_url: str
    swml: SWMLObject


class CallUpdateParamsURL(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of a existing call.
        fallback_url: The Fallback URL to handle the call. This parameter allows you to
            specify a backup webhook or different route in your code containing SWML
            instructions for handling the call.
        status: Either `canceled` (to cancel a not yet connected call) or `completed`
            (to end a call that is in progress).
        status_url: A URL to receive call status update callbacks.
        url: The URL to handle the call. This parameter allows you to specify a webhook
            or different route in your code containing SWML instructions for handling
            the call. Either `url` or `swml` must be included for a new call.
    """

    id: uuid
    fallback_url: str
    status: Literal["canceled", "completed"]
    status_url: str
    url: str


class CallUserEventRequest(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        id: The unique identifying ID of a existing call.
        command: The `calling.user_event` command is used to fire a custom user event on
            the call.
        params: An object of parameters that will be utilized by the active command.
    """

    id: uuid
    command: Literal["calling.user_event"]
    params: dict[str, Any]


class ChangeContextAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        change_context: The name of the context to switch to. The context must be
            defined in the AI's prompt.contexts configuration.
    """

    change_context: str


class ChangeStepAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        change_step: The name of the step to switch to. The step must be defined in the
            current context's steps array.
    """

    change_step: str


class ChargeDetails(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        description: Description for this charge.
        charge: Charged amount.
    """

    description: str
    charge: float


class Cond(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        cond: Execute a sequence of instructions depending on the value of a JavaScript
            condition.
    """

    cond: list[CondParams]


class CondElse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``else`` (``list[SWMLMethod]``): Sequence of SWML methods to execute when none of
      the other conditions evaluate to true.
    """

    # non-identifier field 'else': list[SWMLMethod]


CondParams: TypeAlias = "CondReg | CondElse"


class CondReg(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``else`` (``list[SWMLMethod]``): Sequence of SWML methods to execute when none of
      the other conditions evaluate to true.

    Attributes:
        when: The JavaScript condition to act on.
        then: Sequence of SWML methods to execute when the condition evaluates to true.
    """

    when: str
    then: list[SWMLMethod]
    # non-identifier field 'else': list[SWMLMethod]


class Connect(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        connect: Connect to a phone number, SIP URI, Call Fabric resource, queue, or
            WebSocket stream.
    """

    connect: (
        ConnectDeviceSingle
        | ConnectDeviceSerial
        | ConnectDeviceParallel
        | ConnectDeviceSerialParallel
    )


class ConnectDeviceParallel(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The caller ID to use when dialing the number.

    Attributes:
        headers: Custom SIP headers to add to INVITE. It Has no effect on calls to phone
            numbers.
        codecs: Comma-separated string of codecs to offer. It has no effect on calls to
            phone numbers. Based on SignalWire settings.
        webrtc_media: If true, WebRTC media is offered to the SIP endpoint. It has no
            effect on calls to phone numbers. Default is `false`.
        session_timeout: Time, in seconds, to set the SIP `Session-Expires` header in
            INVITE. Must be a positive, non-zero number. It has no effect on calls to
            phone numbers. Based on SignalWire settings.
        ringback: Array of URIs to play as ringback tone. If not specified, plays audio
            from the provider.
        result: Action to take based on the result of the call. This will run once the
            peer leg of the call has ended. Will use the switch method when the
            return_value is an object, and will use the cond method when the
            return_value is an array.
        timeout: Time, in seconds, to wait for the call to be answered. Default is 60
            seconds.
        max_duration: Maximum duration, in seconds, allowed for the call. Default is
            `14400` seconds.
        answer_on_bridge: Delay answer until the B-leg answers. Default is `false`.
        confirm: Confirmation to execute when the call is connected. Can be either:
            - A URL (string) that returns a SWML document
            - An array of SWML methods to execute inline
        confirm_timeout: The amount of time, in seconds, to wait for the `confirm` URL
            to return a response
        username: SIP username to use for authentication when dialing a SIP URI. Has no
            effect on calls to phone numbers.
        password: SIP password to use for authentication when dialing a SIP URI. Has no
            effect on calls to phone numbers.
        encryption: Encryption setting to use. **Possible values:** `mandatory`,
            `optional`, `forbidden`
        call_state_url: Webhook URL to send call status change notifications to.
            Authentication can also be set in the URL in the format of
            `username:password@url`.
        transfer_after_bridge: SWML to execute after the bridge completes. This defines
            what should happen after the call is connected and the bridge ends. Can be
            either:
            - A URL (http or https) that returns a SWML document
            - An inline SWML document (as a JSON string)

            **Note:** This parameter is REQUIRED when connecting to a queue (when `to`
            starts with "queue:")
        call_state_events: An array of call state event names to be notified about.
            Allowed event names are:
            - `created`
            - `ringing`
            - `answered`
            - `ended`
        status_url: HTTP or HTTPS URL to deliver connect status events. These events
            report the overall status of the connect operation (connecting, connected,
            failed, disconnected) via a `calling.call.connect` event.
        parallel: Array of destinations to dial simultaneously.
    """

    # non-identifier field 'from': str
    headers: list[ConnectHeaders]
    codecs: str
    webrtc_media: bool | SWMLVar
    session_timeout: int | SWMLVar
    ringback: list[str]
    result: ConnectSwitch | list[CondParams]
    timeout: int | SWMLVar
    max_duration: int | SWMLVar
    answer_on_bridge: bool | SWMLVar
    confirm: str | list[ValidConfirmMethods]
    confirm_timeout: int | SWMLVar
    username: str
    password: str
    encryption: Literal["mandatory", "optional", "forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    status_url: str
    parallel: list[ConnectDeviceSingle]


class ConnectDeviceSerial(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The caller ID to use when dialing the number.

    Attributes:
        headers: Custom SIP headers to add to INVITE. It Has no effect on calls to phone
            numbers.
        codecs: Comma-separated string of codecs to offer. It has no effect on calls to
            phone numbers. Based on SignalWire settings.
        webrtc_media: If true, WebRTC media is offered to the SIP endpoint. It has no
            effect on calls to phone numbers. Default is `false`.
        session_timeout: Time, in seconds, to set the SIP `Session-Expires` header in
            INVITE. Must be a positive, non-zero number. It has no effect on calls to
            phone numbers. Based on SignalWire settings.
        ringback: Array of URIs to play as ringback tone. If not specified, plays audio
            from the provider.
        result: Action to take based on the result of the call. This will run once the
            peer leg of the call has ended. Will use the switch method when the
            return_value is an object, and will use the cond method when the
            return_value is an array.
        timeout: Time, in seconds, to wait for the call to be answered. Default is 60
            seconds.
        max_duration: Maximum duration, in seconds, allowed for the call. Default is
            `14400` seconds.
        answer_on_bridge: Delay answer until the B-leg answers. Default is `false`.
        confirm: Confirmation to execute when the call is connected. Can be either:
            - A URL (string) that returns a SWML document
            - An array of SWML methods to execute inline
        confirm_timeout: The amount of time, in seconds, to wait for the `confirm` URL
            to return a response
        username: SIP username to use for authentication when dialing a SIP URI. Has no
            effect on calls to phone numbers.
        password: SIP password to use for authentication when dialing a SIP URI. Has no
            effect on calls to phone numbers.
        encryption: Encryption setting to use. **Possible values:** `mandatory`,
            `optional`, `forbidden`
        call_state_url: Webhook URL to send call status change notifications to.
            Authentication can also be set in the URL in the format of
            `username:password@url`.
        transfer_after_bridge: SWML to execute after the bridge completes. This defines
            what should happen after the call is connected and the bridge ends. Can be
            either:
            - A URL (http or https) that returns a SWML document
            - An inline SWML document (as a JSON string)

            **Note:** This parameter is REQUIRED when connecting to a queue (when `to`
            starts with "queue:")
        call_state_events: An array of call state event names to be notified about.
            Allowed event names are:
            - `created`
            - `ringing`
            - `answered`
            - `ended`
        status_url: HTTP or HTTPS URL to deliver connect status events. These events
            report the overall status of the connect operation (connecting, connected,
            failed, disconnected) via a `calling.call.connect` event.
    """

    # non-identifier field 'from': str
    headers: list[ConnectHeaders]
    codecs: str
    webrtc_media: bool | SWMLVar
    session_timeout: int | SWMLVar
    ringback: list[str]
    result: ConnectSwitch | list[CondParams]
    timeout: int | SWMLVar
    max_duration: int | SWMLVar
    answer_on_bridge: bool | SWMLVar
    confirm: str | list[ValidConfirmMethods]
    confirm_timeout: int | SWMLVar
    username: str
    password: str
    encryption: Literal["mandatory", "optional", "forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    status_url: str
    serial: list[ConnectDeviceSingle]


class ConnectDeviceSerialParallel(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The caller ID to use when dialing the number.

    Attributes:
        headers: Custom SIP headers to add to INVITE. It Has no effect on calls to phone
            numbers.
        codecs: Comma-separated string of codecs to offer. It has no effect on calls to
            phone numbers. Based on SignalWire settings.
        webrtc_media: If true, WebRTC media is offered to the SIP endpoint. It has no
            effect on calls to phone numbers. Default is `false`.
        session_timeout: Time, in seconds, to set the SIP `Session-Expires` header in
            INVITE. Must be a positive, non-zero number. It has no effect on calls to
            phone numbers. Based on SignalWire settings.
        ringback: Array of URIs to play as ringback tone. If not specified, plays audio
            from the provider.
        result: Action to take based on the result of the call. This will run once the
            peer leg of the call has ended. Will use the switch method when the
            return_value is an object, and will use the cond method when the
            return_value is an array.
        timeout: Time, in seconds, to wait for the call to be answered. Default is 60
            seconds.
        max_duration: Maximum duration, in seconds, allowed for the call. Default is
            `14400` seconds.
        answer_on_bridge: Delay answer until the B-leg answers. Default is `false`.
        confirm: Confirmation to execute when the call is connected. Can be either:
            - A URL (string) that returns a SWML document
            - An array of SWML methods to execute inline
        confirm_timeout: The amount of time, in seconds, to wait for the `confirm` URL
            to return a response
        username: SIP username to use for authentication when dialing a SIP URI. Has no
            effect on calls to phone numbers.
        password: SIP password to use for authentication when dialing a SIP URI. Has no
            effect on calls to phone numbers.
        encryption: Encryption setting to use. **Possible values:** `mandatory`,
            `optional`, `forbidden`
        call_state_url: Webhook URL to send call status change notifications to.
            Authentication can also be set in the URL in the format of
            `username:password@url`.
        transfer_after_bridge: SWML to execute after the bridge completes. This defines
            what should happen after the call is connected and the bridge ends. Can be
            either:
            - A URL (http or https) that returns a SWML document
            - An inline SWML document (as a JSON string)

            **Note:** This parameter is REQUIRED when connecting to a queue (when `to`
            starts with "queue:")
        call_state_events: An array of call state event names to be notified about.
            Allowed event names are:
            - `created`
            - `ringing`
            - `answered`
            - `ended`
        status_url: HTTP or HTTPS URL to deliver connect status events. These events
            report the overall status of the connect operation (connecting, connected,
            failed, disconnected) via a `calling.call.connect` event.
        serial_parallel: Array of arrays. Inner arrays contain destinations to dial
            simultaneously. Outer array attempts each parallel group in order.
    """

    # non-identifier field 'from': str
    headers: list[ConnectHeaders]
    codecs: str
    webrtc_media: bool | SWMLVar
    session_timeout: int | SWMLVar
    ringback: list[str]
    result: ConnectSwitch | list[CondParams]
    timeout: int | SWMLVar
    max_duration: int | SWMLVar
    answer_on_bridge: bool | SWMLVar
    confirm: str | list[ValidConfirmMethods]
    confirm_timeout: int | SWMLVar
    username: str
    password: str
    encryption: Literal["mandatory", "optional", "forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    status_url: str
    serial_parallel: list[list[ConnectDeviceSingle]]


class ConnectDeviceSingle(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The caller ID to use when dialing the number.

    Attributes:
        headers: Custom SIP headers to add to INVITE. It Has no effect on calls to phone
            numbers.
        codecs: Comma-separated string of codecs to offer. It has no effect on calls to
            phone numbers. Based on SignalWire settings.
        webrtc_media: If true, WebRTC media is offered to the SIP endpoint. It has no
            effect on calls to phone numbers. Default is `false`.
        session_timeout: Time, in seconds, to set the SIP `Session-Expires` header in
            INVITE. Must be a positive, non-zero number. It has no effect on calls to
            phone numbers. Based on SignalWire settings.
        ringback: Array of URIs to play as ringback tone. If not specified, plays audio
            from the provider.
        result: Action to take based on the result of the call. This will run once the
            peer leg of the call has ended. Will use the switch method when the
            return_value is an object, and will use the cond method when the
            return_value is an array.
        timeout: Time, in seconds, to wait for the call to be answered. Default is 60
            seconds.
        max_duration: Maximum duration, in seconds, allowed for the call. Default is
            `14400` seconds.
        answer_on_bridge: Delay answer until the B-leg answers. Default is `false`.
        confirm: Confirmation to execute when the call is connected. Can be either:
            - A URL (string) that returns a SWML document
            - An array of SWML methods to execute inline
        confirm_timeout: The amount of time, in seconds, to wait for the `confirm` URL
            to return a response
        username: SIP username to use for authentication when dialing a SIP URI. Has no
            effect on calls to phone numbers.
        password: SIP password to use for authentication when dialing a SIP URI. Has no
            effect on calls to phone numbers.
        encryption: Encryption setting to use. **Possible values:** `mandatory`,
            `optional`, `forbidden`
        call_state_url: Webhook URL to send call status change notifications to.
            Authentication can also be set in the URL in the format of
            `username:password@url`.
        transfer_after_bridge: SWML to execute after the bridge completes. This defines
            what should happen after the call is connected and the bridge ends. Can be
            either:
            - A URL (http or https) that returns a SWML document
            - An inline SWML document (as a JSON string)

            **Note:** This parameter is REQUIRED when connecting to a queue (when `to`
            starts with "queue:")
        call_state_events: An array of call state event names to be notified about.
            Allowed event names are:
            - `created`
            - `ringing`
            - `answered`
            - `ended`
        status_url: HTTP or HTTPS URL to deliver connect status events. These events
            report the overall status of the connect operation (connecting, connected,
            failed, disconnected) via a `calling.call.connect` event.
        to: Destination to dial. Can be:
            - Phone number in E.164 format (e.g., "+15552345678")
            - SIP URI (e.g., "sip:alice@example.com")
            - Call Fabric Resource address (e.g., "/public/test_room")
            - Queue (e.g., "queue:support")
            - WebSocket stream (e.g., "stream:wss://example.com/audio")
        name: Stream name identifier. Only applies to stream destinations.
        codec: Audio codec for the stream. Supported values: `PCMU`, `PCMA`, `G722`,
            `L16`. Codec can include rate and ptime modifiers (e.g., `PCMU@40i`,
            `L16@24000h@40i`). Only applies to stream destinations.
        realtime: Enable realtime mode for bidirectional audio. Only applies to stream
            destinations.
        status_url_method: HTTP method for the stream status webhook. Only applies to
            stream destinations.
        authorization_bearer_token: Bearer token sent as an `Authorization` header
            during the WebSocket handshake. Only applies to stream destinations.
        custom_parameters: Custom key-value pairs sent in the WebSocket start message.
            Only applies to stream destinations.
    """

    # non-identifier field 'from': str
    headers: list[ConnectHeaders]
    codecs: str
    webrtc_media: bool | SWMLVar
    session_timeout: int | SWMLVar
    ringback: list[str]
    result: ConnectSwitch | list[CondParams]
    timeout: int | SWMLVar
    max_duration: int | SWMLVar
    answer_on_bridge: bool | SWMLVar
    confirm: str | list[ValidConfirmMethods]
    confirm_timeout: int | SWMLVar
    username: str
    password: str
    encryption: Literal["mandatory", "optional", "forbidden"]
    call_state_url: str
    transfer_after_bridge: str | SWMLVar
    call_state_events: list[CallStatus]
    status_url: str
    to: str
    name: str
    codec: str
    realtime: bool | SWMLVar
    status_url_method: Literal["GET", "POST"]
    authorization_bearer_token: str
    custom_parameters: dict[str, Any]


class ConnectHeaders(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        name: The name of the header.
        value: The value of the header.
    """

    name: str
    value: str


class ConnectSwitch(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        variable: Name of the variable whose value needs to be compared. If not
            provided, it will check the `connect_result` variable.
        case: Object of values mapped to array of instructions to execute
        default: Array of instructions to execute if no cases match
    """

    variable: str
    case: dict[str, Any]
    default: list[SWMLMethod]


class ConstProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        const: A constant value that can be passed to the function.
    """

    const: dict[str, Any]


class ContextPOMSteps(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        name: The name of the step. The name must be unique within the context. The name
            is used for referencing the step in the context.
        step_criteria: The criteria that must be met for the AI to proceed to the next
            step. The criteria is an instruction given to the AI. It's **highly**
            recommended you create a custom criteria for the step to get the intended
            behavior.
        functions: An array of strings, where each string is the name of a
            SWAIG.function that can be executed from this step.
        valid_contexts: An array of context names that the AI can transition to from
            this step. This must be a valid `contexts.name` that is present in your
            `contexts` object.
        skip_user_turn: A boolean value, if set to `true`, will skip the user's turn to
            respond in the conversation and proceed to the next step. **Default:**
            `false`.
        end: A boolean value that determines if the step is the last in the context. If
            `true`, the context ends after this step. Cannot be used along with the
            `valid_steps` parameter. **Default:** `false`.
        valid_steps: An array of valid steps that the conversation can proceed to from
            this step. If the array is empty, or the `valid_steps` key is not present,
            the conversation will proceed to the next step in the context.
        pom: An array of objects that define the POM for the step. POM is the
            Post-Prompt Object Model, which is used to define the flow of the
            conversation.
    """

    name: str
    step_criteria: str
    functions: list[str]
    valid_contexts: list[str]
    skip_user_turn: bool | SWMLVar
    end: bool
    valid_steps: list[str]
    pom: list[POM]


ContextSteps: TypeAlias = "ContextPOMSteps | ContextTextSteps"


class ContextSwitchAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        context_switch: A JSON object containing the context to switch to. Default is
            not set.
    """

    context_switch: dict[str, Any]


class ContextTextSteps(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        name: The name of the step. The name must be unique within the context. The name
            is used for referencing the step in the context.
        step_criteria: The criteria that must be met for the AI to proceed to the next
            step. The criteria is an instruction given to the AI. It's **highly**
            recommended you create a custom criteria for the step to get the intended
            behavior.
        functions: An array of strings, where each string is the name of a
            SWAIG.function that can be executed from this step.
        valid_contexts: An array of context names that the AI can transition to from
            this step. This must be a valid `contexts.name` that is present in your
            `contexts` object.
        skip_user_turn: A boolean value, if set to `true`, will skip the user's turn to
            respond in the conversation and proceed to the next step. **Default:**
            `false`.
        end: A boolean value that determines if the step is the last in the context. If
            `true`, the context ends after this step. Cannot be used along with the
            `valid_steps` parameter. **Default:** `false`.
        valid_steps: An array of valid steps that the conversation can proceed to from
            this step. If the array is empty, or the `valid_steps` key is not present,
            the conversation will proceed to the next step in the context.
        text: The prompt or instructions given to the AI at this step.
    """

    name: str
    step_criteria: str
    functions: list[str]
    valid_contexts: list[str]
    skip_user_turn: bool | SWMLVar
    end: bool
    valid_steps: list[str]
    text: str


class Contexts(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        default: The default context to use at the beginning of the conversation.
            Additional context steps can be defined as any other key in the object.
    """

    default: ContextsObject


ContextsObject: TypeAlias = "ContextsPOMObject | ContextsTextObject"


class ContextsPOMObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        steps: An array of step objects that define the conversation flow for this
            context. Steps execute sequentially unless otherwise specified.
        isolated: When `true`, resets conversation history to only the system prompt
            when entering this context. Useful for focused tasks that shouldn't be
            influenced by previous conversation. **Default:** `false`.
        enter_fillers: Language-specific filler phrases played when transitioning into
            this context. Helps provide smooth context switches.
        exit_fillers: Language-specific filler phrases played when leaving this context.
            Ensures natural transitions out of specialized modes.
        pom: An array of objects that define the POM for the context. POM is the
            Post-Prompt Object Model, which is used to define the flow of the
            conversation.
    """

    steps: list[ContextSteps]
    isolated: bool
    enter_fillers: list[FunctionFillers]
    exit_fillers: list[FunctionFillers]
    pom: list[POM]


class ContextsTextObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        steps: An array of step objects that define the conversation flow for this
            context. Steps execute sequentially unless otherwise specified.
        isolated: When `true`, resets conversation history to only the system prompt
            when entering this context. Useful for focused tasks that shouldn't be
            influenced by previous conversation. **Default:** `false`.
        enter_fillers: Language-specific filler phrases played when transitioning into
            this context. Helps provide smooth context switches.
        exit_fillers: Language-specific filler phrases played when leaving this context.
            Ensures natural transitions out of specialized modes.
        text: The text to send to the agent.
    """

    steps: list[ContextSteps]
    isolated: bool
    enter_fillers: list[FunctionFillers]
    exit_fillers: list[FunctionFillers]
    text: str


class ConversationMessage(TypedDict, total=False):
    """A message object representing a single turn in the conversation history.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        role: The role of the message sender.
        content: The text content of the message.
        lang: Optional language code for the message (e.g., 'en', 'es', 'fr').
    """

    role: ConversationRole
    content: str
    lang: str


ConversationRole: TypeAlias = "Literal['user', 'assistant', 'system']"

CustomTranslationFilter: TypeAlias = "str"


class DataMap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        output: An object that contains a response and a list of actions to be performed
            upon a SWAIG function call. This functions like a return statement in a
            function.
        expressions: An array of objects that have pattern matching logic to process the
            user's input data. A user can define multiple expressions to match against
            the user's input data.
        webhooks: An array of objects that define external API calls.
    """

    output: Output
    expressions: list[Expression]
    webhooks: list[Webhook]


class Denoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        denoise: Start noise reduction. You can stop it at any time using
            `stop_denoise`.
    """

    denoise: dict[str, Any]


class DetectMachine(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        detect_machine: A detection method that combines AMD (Answering Machine
            Detection) and fax detection. Detect whether the user on the other end of
            the call is a machine (fax, voicemail, etc.) or a human. The detection
            result(s) will be sent to the specified status_url as a POST request and
            will also be saved in the detect_result variable.
    """

    detect_machine: dict[str, Any]


Direction: TypeAlias = "Literal['inbound', 'outbound']"


class EnterQueue(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        enter_queue: Place the current call in a named queue where it will wait to be
            connected to an available agent or resource. While waiting, callers will
            hear music or custom audio. When an agent connects to the queue (using the
            connect method), the caller and agent are bridged together. After the bridge
            completes, execution continues with the SWML script specified in
            transfer_after_bridge.
    """

    enter_queue: EnterQueueObject


class EnterQueueObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        queue_name: Name of the queue to enter. If a queue with this name does not
            exist, it will be automatically created.
        transfer_after_bridge: SWML to execute after the bridge completes. This defines
            what should happen after the call is connected to an agent and the bridge
            ends. Can be either:
            - A URL (http or https) that returns a SWML document
            - An inline SWML document (as a JSON string)
        status_url: HTTP or HTTPS URL to deliver queue status events. Default not set
        wait_url: URL for media to play while waiting in the queue. Default hold music
            will be played if not set
        wait_time: Maximum time in seconds to wait in the queue before timeout. Default
            `3600`
    """

    queue_name: str
    transfer_after_bridge: str | SWMLVar
    status_url: str
    wait_url: str | SWMLVar
    wait_time: int | SWMLVar


class Execute(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        execute: Execute a specified section or URL as a subroutine, and upon
            completion, return to the current document. Use the return statement to pass
            any return values or objects back to the current document.
    """

    execute: dict[str, Any]


class ExecuteSwitch(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        variable: Name of the variable whose value needs to be compared. If not
            provided, it will check the `return_value` variable. Can be one of the
            listed set of variables, or a string to represent a custom variable.
        case: Object of values mapped to array of instructions to execute
        default: Array of instructions to execute if no cases match
    """

    variable: str
    case: dict[str, Any]
    default: list[SWMLMethod]


class Expression(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        string: The actual input or value from the user or system.
        pattern: A regular expression pattern to validate or match the string.
        output: An object that contains a response and a list of actions to be performed
            upon a expression match.
    """

    string: str
    pattern: str
    output: Output


class FabricDeviceLeg(TypedDict, total=False):
    """A Fabric subscriber device leg.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The origin number or address.

    Attributes:
        id: The unique identifier of the call on SignalWire. This can be used to update
            the call programmatically.
        to: The destination number or address.
        direction: The direction of the call.
        source: Source of this call.
        url: The URL associated with this call.
        charge: Total charge for this call.
        created_at: The date and time when the call was created.
        charge_details: Details on charges associated with this call.
        status: The status of the call. Always null for Fabric subscriber device legs.
        type: Type of this call.
    """

    id: uuid
    # non-identifier field 'from': str
    to: str
    direction: CallDirection
    source: Literal["realtime_api"]
    url: str | None
    charge: float
    created_at: str
    charge_details: list[ChargeDetails]
    status: None
    type: Literal["fabric_subscriber_device_leg"]


FunctionFillers: TypeAlias = "dict[str, Any]"


class FunctionParameters(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        type: The type of argument the AI is passing to the function. Possible values
            are 'string' and 'object'.
        properties: An object containing the property definitions that are passed to the
            function.

            A property definition is a valid JSON schema type with dynamic property
            names, where:
            - Keys: User-defined strings, that set the property names.
            - Values: A valid property type, which can be one of the following:
              `string`, `integer`, `number`, `boolean`, `array`, `object`, or `null`.
        required: An array of required property names from the `properties` object.
    """

    type: Literal["object"]
    properties: dict[str, Any]
    required: list[str]


class Goto(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        goto: Jump to a label within the current section, optionally based on a
            condition. The goto method will only navigate to a label within the same
            section.
    """

    goto: dict[str, Any]


class HangUpHookSWAIGFunction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        description: A description of the context and purpose of the function, to
            explain to the agent when to use it.
        purpose: The purpose field has been deprecated and is replaced by the
            `description` field. A description of the context and purpose of the
            function, to explain to the agent when to use it. Deprecated.
        parameters: A JSON object that defines the expected user input parameters and
            their validation rules for the function.
        fillers: A JSON object defining the fillers that should be played when calling a
            `swaig function`. This helps the AI break silence between responses. The
            filler is played asynchronously during the function call.
        argument: The argument field has been deprecated and is replaced by the
            `parameters` field. A JSON object defining the input that should be passed
            to the function. The fields of this object are the following two parameters.
            Deprecated.
        active: Whether the function is active. **Default:** `true`.
        meta_data: A powerful and flexible environmental variable which can accept
            arbitrary data that is set initially in the SWML script or from the SWML
            set_meta_data action. This data can be referenced locally to the function.
            All contained information can be accessed and expanded within the prompt -
            for example, by using a template string. Default is not set.
        meta_data_token: Scoping token for meta_data. If not supplied, metadata will be
            scoped to function's `web_hook_url`. Default is set by SignalWire.
        data_map: An object that processes function inputs and executes operations
            through expressions, webhooks, or direct output. Properties are evaluated in
            strict priority order:
            1. expressions
            2. webhooks
            3. output

            Evaluation stops at the first property that returns a valid output result,
            similar to a return statement in a function. Any subsequent properties are
            ignored when a valid output is returned. If a valid output is not returned
            from any of the properties, a generic error message is returned.
        skip_fillers: Skips the top-level fillers specified in `ai.languages` (which
            includes `speech_fillers` and `function_fillers`). When set to `true`, only
            function-specific fillers defined directly on `SWAIG.functions.fillers` will
            play. **Default:** `false`.
        web_hook_url: Function-specific URL to send status callbacks and reports to.
            Takes precedence over a default setting. Authentication can also be set in
            the url in the format of `username:password@url.`
        wait_file: A file to play while the function is running. `wait_file_loops` can
            specify the amount of times that files should continously play. Default is
            not set.
        wait_file_loops: The number of times to loop playing the file. Default is not
            set.
        wait_for_fillers: Whether to wait for fillers to finish playing before
            continuing with the function. **Default:** `false`.
        function: A unique name for the function. This can be any user-defined string or
            can reference a reserved function. Reserved functions are SignalWire
            functions that will be executed at certain points in the conversation. For
            the stop_hook function, the function name is 'stop_hook'.
    """

    description: str
    purpose: str
    parameters: FunctionParameters
    fillers: FunctionFillers
    argument: FunctionParameters
    active: bool | SWMLVar
    meta_data: dict[str, Any]
    meta_data_token: str
    data_map: DataMap
    skip_fillers: bool | SWMLVar
    web_hook_url: str
    wait_file: str
    wait_file_loops: int | str
    wait_for_fillers: bool | SWMLVar
    function: Literal["hangup_hook"]


class Hangup(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        hangup: End the call with an optional reason.
    """

    hangup: dict[str, Any]


class HangupAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        hangup: Whether to hang up the call. When set to `true`, the call will be
            terminated after the AI agent finishes speaking.
    """

    hangup: bool | SWMLVar


HangupReason: TypeAlias = (
    "Literal['hangup', 'cancel', 'busy', 'noAnswer', 'decline', 'error']"
)


class Hint(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        hint: The hint to match. This will match the string exactly as provided
        pattern: A regular expression to match the hint against. This will ensure that
            the hint has a valid matching pattern before being replaced.
        replace: The text to replace the hint with. This will replace the portion of the
            hint that matches the pattern.
        ignore_case: If true, the hint will be matched in a case-insensitive manner.
            **Default:** `false`.
    """

    hint: str
    pattern: str
    replace: str
    ignore_case: bool | SWMLVar


class HoldAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        hold: Places the caller on hold while playing hold music (configured via
            params.hold_music). During hold, speech detection is paused and the AI agent
            will not respond to the caller. The value specifies the hold timeout in
            seconds. Can be a number or an object with timeout property.
    """

    hold: int | SWMLVar | dict[str, Any]


class InjectAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        inject: Injects a message into the conversation to be translated and spoken to
            the specified party.
    """

    inject: dict[str, Any]


class IntegerProperty(TypedDict, total=False):
    """Base interface for all property types.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        description: A description of the property.
        nullable: Whether the property can be null.
        type: The type of parameter(s) the AI is passing to the function.
        enum: An array of integers that are the possible values
        default: The default integer value
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["integer"]
    enum: list[int]
    default: int | SWMLVar


class JoinConference(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        join_conference: Join an ad-hoc audio conference started on either the
            SignalWire or Compatibility API. This method allows you to connect the
            current call to a named conference where multiple participants can
            communicate simultaneously.
    """

    join_conference: JoinConferenceObject


class JoinConferenceObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        name: Name of conference
        muted: Whether to join the conference in a muted state. If set to `true`, the
            participant will be muted upon joining. Default `false`.
        beep: Sets the behavior of the beep sound when joining or leaving the
            conference. Default `"true"`.
        start_on_enter: Starts the conference when the main participant joins. This
            means the start action will not wait on more participants to join before
            starting. Default `true`.
        end_on_exit: Ends the conference when the main participant leaves. This means
            the end action will not wait on more participants to leave before ending.
            Default `false`.
        wait_url: A URL that will play media when the conference is put on hold. Default
            hold music will be played if not set
        max_participants: The maximum number of participants allowed in the conference.
            If the limit is reached, new participants will not be able to join. Default
            `100000`.
        record: Enables or disables recording of the conference. Default
            `"do-not-record"`.
        region: Specifies the geographical region where the conference will be hosted.
            Default not set
        trim: If set to `trim-silence`, it will remove silence from the start of the
            recording. If set to `do-not-trim`, it will keep the silence. Default
            `"trim-silence"`.
        coach: Coach accepts a call SID of a call that is currently connected to an
            in-progress conference. Specifying a call SID that does not exist or is no
            longer connected will result in a failure.
        status_callback_event: The events to listen for and send to the status callback
            URL. Default not set
        status_callback: The URL to which status events will be sent. This URL must be
            publicly accessible and able to handle HTTP requests. Default not set
        status_callback_method: The HTTP method to use when sending status events to the
            status callback URL. Default `"POST"`.
        recording_status_callback: The URL to which recording status events will be
            sent. This URL must be publicly accessible and able to handle HTTP requests.
            Default not set
        recording_status_callback_method: The HTTP method to use when sending recording
            status events to the recording status callback URL. Default `"POST"`.
        recording_status_callback_event: The events to listen for and send to the
            recording status callback URL. Default not set
        result: Allows the user to specify a custom action to be executed when the
            conference result is returned (typically when it has ended). The actions can
            a `switch` object or a `cond` array. The `switch` object allows for
            conditional execution based on the result of the conference, while the
            `cond` array allows for multiple conditions to be checked in sequence. If
            neither is provided, the default action will be to end the conference.
    """

    name: str
    muted: bool | SWMLVar
    beep: Literal["true", "false", "onEnter", "onExit"]
    start_on_enter: bool | SWMLVar
    end_on_exit: bool | SWMLVar
    wait_url: str | SWMLVar
    max_participants: int | SWMLVar
    record: Literal["do-not-record", "record-from-start"]
    region: str
    trim: Literal["trim-silence", "do-not-trim"]
    coach: str
    status_callback_event: Literal[
        "start",
        "end",
        "join",
        "leave",
        "mute",
        "hold",
        "modify",
        "speaker",
        "announcement",
    ]
    status_callback: str
    status_callback_method: Literal["GET", "POST"]
    recording_status_callback: str
    recording_status_callback_method: Literal["GET", "POST"]
    recording_status_callback_event: Literal["in-progress", "completed", "absent"]
    result: dict[str, Any] | list[CondParams]


class JoinRoom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        join_room: Join a RELAY room. If the room doesn't exist, it creates a new room.
    """

    join_room: dict[str, Any]


class Label(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        label: Mark any point of the SWML section with a label so that goto can jump to
            it.
    """

    label: str


class LanguageParams(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        stability: The stability slider determines how stable the voice is and the
            randomness between each generation. Lowering this slider introduces a
            broader emotional range for the voice. IMPORTANT: Only works with ElevenLabs
            TTS engine.
        similarity: The similarity slider dictates how closely the AI should adhere to
            the original voice when attempting to replicate it. The higher the
            similarity, the closer the AI will sound to the original voice. IMPORTANT:
            Only works with ElevenLabs TTS engine.
    """

    stability: float | SWMLVar
    similarity: float | SWMLVar


Languages: TypeAlias = "LanguagesWithSoloFillers | LanguagesWithFillers"


class LanguagesWithFillers(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        name: Name of the language (e.g., 'French', 'English'). This value is used in
            the system prompt to instruct the LLM what language is being spoken.
        code: The language code for ASR (Automatic Speech Recognition) purposes. By
            default, SignalWire uses Deepgram's Nova-3 STT engine, so this value should
            match a code from Deepgram's Nova-3 language codes. If a different STT model
            was selected using the `openai_asr_engine` parameter, you must select a code
            supported by that engine.
        voice: Voice to use for the language. String format: `<engine id>.<voice id>`.
            Select engine from `gcloud`, `polly`, `elevenlabs`, `cartesia`, or
            `deepgram`. For example, `gcloud.fr-FR-Neural2-B`.
        model: The model to use for the specified TTS engine. For example, 'arcana'.
        emotion: Enables emotion detection for the set TTS engine. This allows the AI to
            express emotions when speaking. A global emotion or specific emotions for
            certain topics can be set within the prompt of the AI. IMPORTANT: Only works
            with
            [`Cartesia`](https://signalwire.com/docs/voice/getting-started/voice-and-languages#cartesia)
            TTS engine.
        speed: The speed to use for the specified TTS engine. This allows the AI to
            speak at a different speed at different points in the conversation. The
            speed behavior can be defined in the prompt of the AI. IMPORTANT: Only works
            with
            [`Cartesia`](https://signalwire.com/docs/voice/getting-started/voice-and-languages#cartesia)
            TTS engine.
        engine: The engine to use for the language. For example, 'elevenlabs'.
            Deprecated.
        params: TTS engine-specific parameters for this language.
        function_fillers: An array of strings to be used as fillers in the conversation
            when calling a `swaig function`. This helps the AI break silence between
            responses. The filler is played asynchronously during the function call.
        speech_fillers: An array of strings to be used as fillers in the conversation.
            This helps the AI break silence between responses. Note: `speech_fillers`
            are used between every 'turn' taken by the LLM, including at the beginning
            of the call. For more targeted fillers, consider using `function_fillers`.
    """

    name: str
    code: str
    voice: str
    model: str
    emotion: Literal["auto"]
    speed: Literal["auto"]
    engine: str
    params: LanguageParams
    function_fillers: list[str]
    speech_fillers: list[str]


class LanguagesWithSoloFillers(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        name: Name of the language (e.g., 'French', 'English'). This value is used in
            the system prompt to instruct the LLM what language is being spoken.
        code: The language code for ASR (Automatic Speech Recognition) purposes. By
            default, SignalWire uses Deepgram's Nova-3 STT engine, so this value should
            match a code from Deepgram's Nova-3 language codes. If a different STT model
            was selected using the `openai_asr_engine` parameter, you must select a code
            supported by that engine.
        voice: Voice to use for the language. String format: `<engine id>.<voice id>`.
            Select engine from `gcloud`, `polly`, `elevenlabs`, `cartesia`, or
            `deepgram`. For example, `gcloud.fr-FR-Neural2-B`.
        model: The model to use for the specified TTS engine. For example, 'arcana'.
        emotion: Enables emotion detection for the set TTS engine. This allows the AI to
            express emotions when speaking. A global emotion or specific emotions for
            certain topics can be set within the prompt of the AI. IMPORTANT: Only works
            with
            [`Cartesia`](https://signalwire.com/docs/voice/getting-started/voice-and-languages#cartesia)
            TTS engine.
        speed: The speed to use for the specified TTS engine. This allows the AI to
            speak at a different speed at different points in the conversation. The
            speed behavior can be defined in the prompt of the AI. IMPORTANT: Only works
            with
            [`Cartesia`](https://signalwire.com/docs/voice/getting-started/voice-and-languages#cartesia)
            TTS engine.
        engine: The engine to use for the language. For example, 'elevenlabs'.
            Deprecated.
        params: TTS engine-specific parameters for this language.
        fillers: An array of strings to be used as fillers in the conversation. This
            will be used for both speech and function fillers if provided. Deprecated.
    """

    name: str
    code: str
    voice: str
    model: str
    emotion: Literal["auto"]
    speed: Literal["auto"]
    engine: str
    params: LanguageParams
    fillers: list[str]


class LiveTranscribe(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        live_transcribe: Start live transcription of the call. The transcription will be
            sent to the specified webhook URL.
    """

    live_transcribe: dict[str, Any]


class LiveTranscribeStartAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        start: Starts live transcription of the call.
    """

    start: dict[str, Any]


LiveTranscribeStopAction: TypeAlias = "Literal['stop']"


class LiveTranscribeSummarizeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        summarize: Request an on-demand AI summary of the conversation.
    """

    summarize: dict[str, Any]


class LiveTranslate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        live_translate: Start live translation of the call. The translation will be sent
            to the specified webhook URL.
    """

    live_translate: dict[str, Any]


class LiveTranslateInjectAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        inject: Inject a message into the conversation to be translated and spoken.
    """

    inject: dict[str, Any]


class LiveTranslateStartAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        start: Starts live translation of the call.
    """

    start: dict[str, Any]


LiveTranslateStopAction: TypeAlias = "Literal['stop']"


class LiveTranslateSummarizeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        summarize: Request an on-demand AI summary of the translated conversation.
    """

    summarize: dict[str, Any]


class NullProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        type: The type of parameter(s) the AI is passing to the function.
        description: A description of the property.
    """

    type: Literal["null"]
    description: str


class NumberProperty(TypedDict, total=False):
    """Base interface for all property types.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        description: A description of the property.
        nullable: Whether the property can be null.
        type: The type of parameter(s) the AI is passing to the function.
        enum: An array of integers that are the possible values
        default: The default integer value
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["number"]
    enum: list[int | float] | list[SWMLVar]
    default: int | float | SWMLVar


class ObjectProperty(TypedDict, total=False):
    """Base interface for all property types.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        description: A description of the property.
        nullable: Whether the property can be null.
        type: The type of parameter(s) the AI is passing to the function.
        default: The default object value
        properties: Nested properties
        required: Required property names
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["object"]
    default: dict[str, Any]
    properties: dict[str, Any]
    required: list[str]


class OneOfProperty(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        oneOf: An array of schemas where exactly one of the schemas must be valid.
    """

    oneOf: list[SchemaType]


class Output(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        response: A static response text or message returned to the AI agent's context.
        action: A list of actions to be performed upon matching.
    """

    response: str
    action: list[Action]


POM: TypeAlias = "PomSectionBodyContent | PomSectionBulletsContent"


class Pay(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        pay: Enables secure payment processing during voice calls. When implemented, it
            manages the entire payment flow including data collection, validation, and
            processing through your configured payment gateway.
    """

    pay: dict[str, Any]


class PayParameters(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        name: The identifier for your custom parameter. This will be the key in the
            parameters object.
        value: The value associated with the parameter. This will be the value in the
            parameters object.
    """

    name: str
    value: str


PayPromptAction: TypeAlias = "PayPromptSayAction | PayPromptPlayAction"


class PayPromptPlayAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        type: When the action `type` is `Say`, this value is the text to be spoken; when
            the type is `Play`, it should be a URL to the audio file.
        phrase: The URL of the audio file to play
    """

    type: Literal["Play"]
    phrase: str


class PayPromptSayAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        type: When the action `type` is `Say`, this value is the text to be spoken; when
            the type is `Play`, it should be a URL to the audio file.
        phrase: The phrase to speak
    """

    type: Literal["Say"]
    phrase: str


class PayPrompts(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``for`` (``str``): The payment step this prompt is for. See Payment Steps for a
      list of available steps.

    - `payment-card-number`: Collect the payment card number.
    - `expiration-date`: Collect the payment card expiration date.
    - `security-code`: Collect the payment card security code.
    - `postal-code`: Collect the payment card postal code.
    - `payment-processing`: The step used during the payment processing.
    - `payment-completed`: The step used when the payment is completed.
    - `payment-failed`: The step used when the payment fails.
    - `payment-cancelled`: The step used when the payment is cancelled.

    Attributes:
        actions: Array of action objects to execute for this prompt. These actions can
            either play an audio file or speak a phrase.
        attempts: Specifies which payment attempt(s) this prompt applies to. The value
            increments when a payment fails. Use a single number (e.g., "1") or
            space-separated numbers (e.g., "2 3") to target the specific attempts.
        card_type: Space-seperated list of card types that are allowed to be used for
            this prompt.

            Supported card types:
            - `visa`
            - `mastercard`
            - `amex`
            - `maestro`
            - `discover`
            - `optima`
            - `jcb`
            - `diners-club`
        error_type: Space-separated list of error types this prompt applies to.

            Available error types:
            - `timeout` - User input timeout
            - `invalid-card-number` - Failed card validation
            - `invalid-card-type` - Unsupported card type
            - `invalid-date` - Invalid expiration date
            - `invalid-security-code` - Invalid CVV format
            - `invalid-postal-code` - Invalid postal code format
            - `invalid-bank-routing-number` - Invalid bank routing number
            - `invalid-bank-account-number` - Invalid bank account number
            - `input-matching-failed` - Input matching failed
            - `session-in-progress` - Concurrent session attempt
            - `card-declined` - Payment declined
    """

    actions: list[PayPromptAction]
    # non-identifier field 'for': str
    attempts: str
    card_type: str
    error_type: str


class Play(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        play: Play file(s), ringtones, speech or silence.
    """

    play: PlayWithURL | PlayWithURLS


class PlayWithURL(TypedDict, total=False):
    """Play with a single URL.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        auto_answer: If `true`, the call will automatically answer as the sound is
            playing. If `false`, you will start playing the audio during early media.
            Default `true`.
        volume: Volume level for the audio file. Default is `0`. Valid range is -40 to
            40.
        say_voice: The voice to use for the text to speech.
        say_language: The language to use for the text to speech.
        say_gender: Gender to use for the text to speech.
        status_url: http or https URL to deliver play status events
        url: URL to play. Required if `urls` is not present. Allowed URLs are:
            - http:// or https:// - audio file to GET
            - ring:[duration:]`<country code>` - ring tone to play. For example: ring:us
              to play single ring or ring:20.0:us to play ring for 20 seconds.
            - say:`<text to speak>` - Sentence to say
            - silence: `<duration>` - seconds of silence to play
    """

    auto_answer: bool | SWMLVar
    volume: float | SWMLVar
    say_voice: str
    say_language: str
    say_gender: str
    status_url: str
    url: play_url | SWMLVar


class PlayWithURLS(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        auto_answer: If `true`, the call will automatically answer as the sound is
            playing. If `false`, you will start playing the audio during early media.
            Default `true`.
        volume: Volume level for the audio file. Default is `0`. Valid range is -40 to
            40.
        say_voice: The voice to use for the text to speech.
        say_language: The language to use for the text to speech.
        say_gender: Gender to use for the text to speech.
        status_url: http or https URL to deliver play status events
        urls: Array of URLs to play. Required if `url` is not present. Allowed URLs are:
            - http:// or https:// - audio file to GET
            - ring:[duration:]`<country code>` - ring tone to play. For example: ring:us
              to play single ring or ring:20.0:us to play ring for 20 seconds.
            - say:`<text to speak>` - Sentence to say
            - silence: `<duration>` - seconds of silence to play
    """

    auto_answer: bool | SWMLVar
    volume: float | SWMLVar
    say_voice: str
    say_language: str
    say_gender: str
    status_url: str
    urls: list[play_url] | list[SWMLVar]


class PlaybackBGAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        playback_bg: A JSON object containing the audio file to play.
    """

    playback_bg: dict[str, Any]


class PomSectionBodyContent(TypedDict, total=False):
    """Content model with body text and optional bullets.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        title: Title for the section
        subsections: Optional array of nested subsections
        numbered: Whether to number the section
        numberedBullets: Whether to number the bullets
        body: Body text for the section
        bullets: Optional array of bullet points
    """

    title: str
    subsections: list[POM]
    numbered: bool | SWMLVar
    numberedBullets: bool | SWMLVar
    body: str
    bullets: list[str]


class PomSectionBulletsContent(TypedDict, total=False):
    """Content model with bullets and optional body.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        title: Title for the section
        subsections: Optional array of nested subsections
        numbered: Whether to number the section
        numberedBullets: Whether to number the bullets
        body: Body text for the section (optional)
        bullets: Array of bullet points
    """

    title: str
    subsections: list[POM]
    numbered: bool | SWMLVar
    numberedBullets: bool | SWMLVar
    body: str
    bullets: list[str]


class Prompt(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        prompt: Play a prompt and wait for input. The input can be received either as
            digits from the keypad, or from speech, or both depending on what parameters
            are set. By default, only digit input is enabled. To enable speech input,
            set at least one speech parameter. To enable both digit and speech input,
            set at least one parameter for each.
    """

    prompt: dict[str, Any]


class Pronounce(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``with`` (``str``): The phonetic spelling of the expression.

    Attributes:
        replace: The expression to replace.
        ignore_case: Whether the pronunciation replacement should ignore case.
            **Default:** `true`.
    """

    replace: str
    # non-identifier field 'with': str
    ignore_case: bool | SWMLVar


class ReceiveFax(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        receive_fax: Receive a fax being delivered to this call.
    """

    receive_fax: dict[str, Any]


class Record(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        record: Record the call audio in the foreground, pausing further SWML execution
            until recording ends. Use this, for example, to record voicemails. To record
            calls in the background in a non-blocking fashion, use the record_call
            method.
    """

    record: dict[str, Any]


class RecordCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        record_call: Record call in the background. Unlike the record method, the
            record_call method will start the recording and continue executing the SWML
            script while allowing the recording to happen in the background. To stop
            call recordings started with record_call, use the stop_record_call method.
    """

    record_call: dict[str, Any]


class Request(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        request: Send a GET, POST, PUT, or DELETE request to a remote URL.
    """

    request: dict[str, Any]


class Return(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``return`` (``dict[str, Any]``): Return a value from an execute call or exit the
      script. The value can be any type.
    """

    # non-identifier field 'return': dict[str, Any]


class SIPRefer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        sip_refer: Send SIP REFER to a SIP call.
    """

    sip_refer: dict[str, Any]


class SMSWithBody(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        to_number: Phone number to send SMS message to in E.164 format.
        from_number: Phone number the SMS message will be sent from in E.164 format.
        region: Region of the world to originate the message from. Chosen based on
            account preferences or device location if not specified.
        tags: Array of tags to associate with the message to facilitate log searches.
        body: Required if `media` is not present. The body of the SMS message.
    """

    to_number: str
    from_number: str
    region: str
    tags: list[str]
    body: str


class SMSWithMedia(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        to_number: Phone number to send SMS message to in E.164 format.
        from_number: Phone number the SMS message will be sent from in E.164 format.
        region: Region of the world to originate the message from. Chosen based on
            account preferences or device location if not specified.
        tags: Array of tags to associate with the message to facilitate log searches.
        media: Required if `body` is not present. Array of media URLs to include in the
            message.
        body: Optional if `media` is present. The body of the SMS message.
    """

    to_number: str
    from_number: str
    region: str
    tags: list[str]
    media: list[str]
    body: str


class SWAIG(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        defaults: Default settings for all SWAIG functions. If `defaults` is not set,
            settings may be set in each function object. Default is not set.
        native_functions: Prebuilt functions the AI agent is able to call from this list
            of available native functions
        includes: An array of objects to include remote function signatures. This allows
            you to include functions that are defined in a remote location. The object
            fields are `url` to specify where the remote functions are defined and
            `functions` which is an array of the function names as strings.
        functions: An array of JSON objects to define functions that can be executed
            during the interaction with the AI. Default is not set.
        internal_fillers: An object containing filler phrases for internal SWAIG
            functions. These fillers are played while utilizing internal functions.
    """

    defaults: SWAIGDefaults
    native_functions: list[SWAIGNativeFunction]
    includes: list[SWAIGIncludes]
    functions: list[SWAIGFunction]
    internal_fillers: SWAIGInternalFiller


class SWAIGDefaults(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        web_hook_url: Default URL to send status callbacks and reports to.
            Authentication can also be set in the url in the format of
            `username:password@url.`
    """

    web_hook_url: str


SWAIGFunction: TypeAlias = "UserSWAIGFunction | StartUpHookSWAIGFunction | HangUpHookSWAIGFunction | SummarizeConversationSWAIGFunction"


class SWAIGIncludes(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        functions: Remote functions to fetch and include in your AI application.
        url: URL to fetch remote functions and include in your AI application.
            Authentication can also be set in the url in the format of
            `username:password@url`.
        meta_data: User-defined metadata to pass with the remote function request.
    """

    functions: list[str]
    url: str
    meta_data: dict[str, Any]


class SWAIGInternalFiller(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        hangup: Filler phrases played when the AI Agent is hanging up the call.
        check_time: Filler phrases played when the AI Agent is checking the time.
        wait_for_user: Filler phrases played when the AI Agent is waiting for user
            input.
        wait_seconds: Filler phrases played during deliberate pauses or wait periods.
        adjust_response_latency: Filler phrases played when the AI Agent is adjusting
            response timing.
        next_step: Filler phrases played when transitioning between conversation steps
            when utilizing `prompt.contexts`.
        change_context: Filler phrases played when switching between conversation
            contexts when utilizing `prompt.contexts`.
        get_visual_input: Filler phrases played when the AI Agent is processing visual
            input. This function is enabled when `enable_vision` is set to `true` in
            `ai.params`.
        get_ideal_strategy: Filler phrases played when the AI Agent is thinking or
            considering options. This is utilized when `enable_thinking` is set to
            `true` in `ai.params`.
    """

    hangup: FunctionFillers
    check_time: FunctionFillers
    wait_for_user: FunctionFillers
    wait_seconds: FunctionFillers
    adjust_response_latency: FunctionFillers
    next_step: FunctionFillers
    change_context: FunctionFillers
    get_visual_input: FunctionFillers
    get_ideal_strategy: FunctionFillers


SWAIGNativeFunction: TypeAlias = (
    "Literal['check_time', 'wait_seconds', 'wait_for_user', 'adjust_response_latency']"
)


class SWMLAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        SWML: A SWML object to be executed.
    """

    SWML: SWMLObject


SWMLMethod: TypeAlias = "Answer | AI | AmazonBedrock | Cond | Connect | Denoise | EnterQueue | Execute | Goto | Label | LiveTranscribe | LiveTranslate | Hangup | JoinRoom | JoinConference | Play | Prompt | ReceiveFax | Record | RecordCall | Request | Return | SendDigits | SendFax | SendSMS | Set | Sleep | SIPRefer | StopDenoise | StopRecordCall | StopTap | Switch | Tap | Transfer | Unset | Pay | DetectMachine | UserEvent"


class SWMLObject(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    version: Literal["1.0.0"]
    sections: Section


SWMLVar: TypeAlias = "str"


class SayAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        say: A message to be spoken by the AI agent.
    """

    say: str


SchemaType: TypeAlias = "StringProperty | IntegerProperty | NumberProperty | BooleanProperty | ArrayProperty | ObjectProperty | NullProperty | OneOfProperty | AllOfProperty | AnyOfProperty | ConstProperty"


class Section(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    main: list[SWMLMethod]


class SendDigits(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        send_digits: Send digit presses as DTMF tones.
    """

    send_digits: dict[str, Any]


class SendFax(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        send_fax: Send a fax.
    """

    send_fax: dict[str, Any]


class SendSMS(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        send_sms: Send an outbound SMS or MMS message to a PSTN phone number.
    """

    send_sms: SMSWithBody | SMSWithMedia


class Set(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        set: Set script variables to the specified values. Accepts an object mapping
            variable names to values. Variables set using set can be removed using
            unset.
    """

    set: dict[str, Any]


class SetGlobalDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        set_global_data: A JSON object containing any global data, as a key-value map.
            This action sets the data in the `global_data` to be globally referenced.
    """

    set_global_data: dict[str, Any]


class SetMetaDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        set_meta_data: A JSON object containing any metadata, as a key-value map. This
            action sets the data in the `meta_data` to be referenced locally in the
            function.
    """

    set_meta_data: dict[str, Any]


class Sleep(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        sleep: Pause execution for a specified duration.
    """

    sleep: dict[str, Any] | int | SWMLVar


SpeechEngine: TypeAlias = "Literal['deepgram', 'google']"


class StartAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        start: Starts live translation of the call. The translation will be sent to the
            specified URL.
    """

    start: dict[str, Any]


class StartUpHookSWAIGFunction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        description: A description of the context and purpose of the function, to
            explain to the agent when to use it.
        purpose: The purpose field has been deprecated and is replaced by the
            `description` field. A description of the context and purpose of the
            function, to explain to the agent when to use it. Deprecated.
        parameters: A JSON object that defines the expected user input parameters and
            their validation rules for the function.
        fillers: A JSON object defining the fillers that should be played when calling a
            `swaig function`. This helps the AI break silence between responses. The
            filler is played asynchronously during the function call.
        argument: The argument field has been deprecated and is replaced by the
            `parameters` field. A JSON object defining the input that should be passed
            to the function. The fields of this object are the following two parameters.
            Deprecated.
        active: Whether the function is active. **Default:** `true`.
        meta_data: A powerful and flexible environmental variable which can accept
            arbitrary data that is set initially in the SWML script or from the SWML
            set_meta_data action. This data can be referenced locally to the function.
            All contained information can be accessed and expanded within the prompt -
            for example, by using a template string. Default is not set.
        meta_data_token: Scoping token for meta_data. If not supplied, metadata will be
            scoped to function's `web_hook_url`. Default is set by SignalWire.
        data_map: An object that processes function inputs and executes operations
            through expressions, webhooks, or direct output. Properties are evaluated in
            strict priority order:
            1. expressions
            2. webhooks
            3. output

            Evaluation stops at the first property that returns a valid output result,
            similar to a return statement in a function. Any subsequent properties are
            ignored when a valid output is returned. If a valid output is not returned
            from any of the properties, a generic error message is returned.
        skip_fillers: Skips the top-level fillers specified in `ai.languages` (which
            includes `speech_fillers` and `function_fillers`). When set to `true`, only
            function-specific fillers defined directly on `SWAIG.functions.fillers` will
            play. **Default:** `false`.
        web_hook_url: Function-specific URL to send status callbacks and reports to.
            Takes precedence over a default setting. Authentication can also be set in
            the url in the format of `username:password@url.`
        wait_file: A file to play while the function is running. `wait_file_loops` can
            specify the amount of times that files should continously play. Default is
            not set.
        wait_file_loops: The number of times to loop playing the file. Default is not
            set.
        wait_for_fillers: Whether to wait for fillers to finish playing before
            continuing with the function. **Default:** `false`.
        function: A unique name for the function. This can be any user-defined string or
            can reference a reserved function. Reserved functions are SignalWire
            functions that will be executed at certain points in the conversation. For
            the start_hook function, the function name is 'start_hook'.
    """

    description: str
    purpose: str
    parameters: FunctionParameters
    fillers: FunctionFillers
    argument: FunctionParameters
    active: bool | SWMLVar
    meta_data: dict[str, Any]
    meta_data_token: str
    data_map: DataMap
    skip_fillers: bool | SWMLVar
    web_hook_url: str
    wait_file: str
    wait_file_loops: int | str
    wait_for_fillers: bool | SWMLVar
    function: Literal["startup_hook"]


class StopAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        stop: Whether to stop the conversation.
    """

    stop: bool | SWMLVar


class StopDenoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        stop_denoise: Stop noise reduction that was started with denoise.
    """

    stop_denoise: dict[str, Any]


class StopPlaybackBGAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        stop_playback_bg: Whether to stop the background audio file.
    """

    stop_playback_bg: bool | SWMLVar


class StopRecordCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        stop_record_call: Stop an active background recording.
    """

    stop_record_call: dict[str, Any]


class StopTap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        stop_tap: Stop an active tap stream.
    """

    stop_tap: dict[str, Any]


StringFormat: TypeAlias = "Literal['date_time', 'time', 'date', 'duration', 'email', 'hostname', 'ipv4', 'ipv6', 'uri', 'uuid']"


class StringProperty(TypedDict, total=False):
    """Base interface for all property types.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        description: A description of the property.
        nullable: Whether the property can be null.
        type: The type of parameter(s) the AI is passing to the function.
        enum: An array of strings that are the possible values
        default: The default string value
        pattern: Regular expression pattern
        format: String format (email, date-time, etc.)
    """

    description: str
    nullable: bool | SWMLVar
    type: Literal["string"]
    enum: list[str]
    default: str
    pattern: str
    format: StringFormat


class SummarizeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        summarize: Summarizes the conversation as an object, allowing you to specify the
            webhook url and prompt for the summary.
    """

    summarize: dict[str, Any]


SummarizeActionUnion: TypeAlias = "SummarizeAction | Literal['summarize']"


class SummarizeConversationSWAIGFunction(TypedDict, total=False):
    """An internal reserved function that generates a summary of the conversation and sends any specified properties to the configured webhook after the conversation has ended.

    This ensures that key parts of the conversation, as interpreted by the LLM, are
    reliably captured and delivered to the webhook.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        description: A description of the context and purpose of the function, to
            explain to the agent when to use it.
        purpose: The purpose field has been deprecated and is replaced by the
            `description` field. A description of the context and purpose of the
            function, to explain to the agent when to use it. Deprecated.
        parameters: A JSON object that defines the expected user input parameters and
            their validation rules for the function.
        fillers: A JSON object defining the fillers that should be played when calling a
            `swaig function`. This helps the AI break silence between responses. The
            filler is played asynchronously during the function call.
        argument: The argument field has been deprecated and is replaced by the
            `parameters` field. A JSON object defining the input that should be passed
            to the function. The fields of this object are the following two parameters.
            Deprecated.
        active: Whether the function is active. **Default:** `true`.
        meta_data: A powerful and flexible environmental variable which can accept
            arbitrary data that is set initially in the SWML script or from the SWML
            set_meta_data action. This data can be referenced locally to the function.
            All contained information can be accessed and expanded within the prompt -
            for example, by using a template string. Default is not set.
        meta_data_token: Scoping token for meta_data. If not supplied, metadata will be
            scoped to function's `web_hook_url`. Default is set by SignalWire.
        data_map: An object that processes function inputs and executes operations
            through expressions, webhooks, or direct output. Properties are evaluated in
            strict priority order:
            1. expressions
            2. webhooks
            3. output

            Evaluation stops at the first property that returns a valid output result,
            similar to a return statement in a function. Any subsequent properties are
            ignored when a valid output is returned. If a valid output is not returned
            from any of the properties, a generic error message is returned.
        skip_fillers: Skips the top-level fillers specified in `ai.languages` (which
            includes `speech_fillers` and `function_fillers`). When set to `true`, only
            function-specific fillers defined directly on `SWAIG.functions.fillers` will
            play. **Default:** `false`.
        web_hook_url: Function-specific URL to send status callbacks and reports to.
            Takes precedence over a default setting. Authentication can also be set in
            the url in the format of `username:password@url.`
        wait_file: A file to play while the function is running. `wait_file_loops` can
            specify the amount of times that files should continously play. Default is
            not set.
        wait_file_loops: The number of times to loop playing the file. Default is not
            set.
        wait_for_fillers: Whether to wait for fillers to finish playing before
            continuing with the function. **Default:** `false`.
        function: A unique name for the function. This can be any user-defined string or
            can reference a reserved function. Reserved functions are SignalWire
            functions that will be executed at certain points in the conversation.. For
            the summarize_conversation function, the function name is
            'summarize_conversation'.
    """

    description: str
    purpose: str
    parameters: FunctionParameters
    fillers: FunctionFillers
    argument: FunctionParameters
    active: bool | SWMLVar
    meta_data: dict[str, Any]
    meta_data_token: str
    data_map: DataMap
    skip_fillers: bool | SWMLVar
    web_hook_url: str
    wait_file: str
    wait_file_loops: int | str
    wait_for_fillers: bool | SWMLVar
    function: Literal["summarize_conversation"]


class Switch(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        switch: Execute different instructions based on a variable's value.
    """

    switch: dict[str, Any]


class Tap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        tap: Start background call tap. Media is streamed over Websocket or RTP to
            customer controlled URI.
    """

    tap: dict[str, Any]


class ToggleFunctionsAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        toggle_functions: Whether to toggle the functions on or off.
    """

    toggle_functions: list[dict[str, Any]]


TranscribeAction: TypeAlias = (
    "TranscribeStartAction | Literal['stop'] | TranscribeSummarizeActionUnion"
)

TranscribeDirection: TypeAlias = "Literal['remote-caller', 'local-caller']"


class TranscribeStartAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        start: Starts live transcription of the call. The transcription will be sent to
            the specified URL.
    """

    start: dict[str, Any]


class TranscribeSummarizeAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        summarize: Summarizes the conversation as an object, allowing you to specify the
            webhook url and prompt for the summary.
    """

    summarize: dict[str, Any]


TranscribeSummarizeActionUnion: TypeAlias = (
    "TranscribeSummarizeAction | Literal['summarize']"
)


class Transfer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        transfer: Transfer the execution of the script to a different SWML section, URL,
            or Relay application. Once the transfer is complete, the script will
            continue executing SWML from the new location.
    """

    transfer: dict[str, Any]


TranslateAction: TypeAlias = (
    "StartAction | Literal['stop'] | SummarizeActionUnion | InjectAction"
)

TranslateDirection: TypeAlias = "Literal['remote-caller', 'local-caller']"

TranslationFilterPreset: TypeAlias = (
    "Literal['polite', 'rude', 'professional', 'shakespeare', 'gen-z']"
)


class Types_StatusCodes_RestApiErrorItem(TypedDict, total=False):
    """Details about a specific error.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        type: The category of error.
        code: A specific error code.
        message: A description of what caused the error.
        attribute: The request parameter that caused the error, if applicable.
        url: A link to documentation about this error.
    """

    type: str
    code: str
    message: str
    attribute: str | None
    url: str


class Types_StatusCodes_StatusCode400(TypedDict, total=False):
    """The request is invalid.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Bad Request"]


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Unauthorized"]


class Types_StatusCodes_StatusCode404(TypedDict, total=False):
    """The server cannot find the requested resource.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Not Found"]


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


class Unset(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        unset: Unset specified variables. The variables may have been set using the set
            method or as a byproduct of other statements or methods. Accepts a single
            variable name as a string or an array of variable names.
    """

    unset: str | list[str]


class UnsetGlobalDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        unset_global_data: The key of the global data to unset from the `global_data`.
            You can also reset the `global_data` by passing in a new object.
    """

    unset_global_data: str | dict[str, Any]


class UnsetMetaDataAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        unset_meta_data: The key of the local data to unset from the `meta_data`. You
            can also reset the `meta_data` by passing in a new object.
    """

    unset_meta_data: str | dict[str, Any]


class UserEvent(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        user_event: Allows the user to set and send events to the connected client on
            the call. This is useful for triggering actions on the client side. Commonly
            used with the
            [browser-sdk](https://signalwire.com/docs/sdks/reference/browser-sdk/SignalWire%20Client/).
            The event object can be any valid JSON object. Any key-value pair in the
            object is sent to the client as an event type called `user_event`.
    """

    user_event: dict[str, Any]


class UserInputAction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        user_input: Used to inject text into the users queue as if they input the data
            themselves.
    """

    user_input: str


class UserSWAIGFunction(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        description: A description of the context and purpose of the function, to
            explain to the agent when to use it.
        purpose: The purpose field has been deprecated and is replaced by the
            `description` field. A description of the context and purpose of the
            function, to explain to the agent when to use it. Deprecated.
        parameters: A JSON object that defines the expected user input parameters and
            their validation rules for the function.
        fillers: A JSON object defining the fillers that should be played when calling a
            `swaig function`. This helps the AI break silence between responses. The
            filler is played asynchronously during the function call.
        argument: The argument field has been deprecated and is replaced by the
            `parameters` field. A JSON object defining the input that should be passed
            to the function. The fields of this object are the following two parameters.
            Deprecated.
        active: Whether the function is active. **Default:** `true`.
        meta_data: A powerful and flexible environmental variable which can accept
            arbitrary data that is set initially in the SWML script or from the SWML
            set_meta_data action. This data can be referenced locally to the function.
            All contained information can be accessed and expanded within the prompt -
            for example, by using a template string. Default is not set.
        meta_data_token: Scoping token for meta_data. If not supplied, metadata will be
            scoped to function's `web_hook_url`. Default is set by SignalWire.
        data_map: An object that processes function inputs and executes operations
            through expressions, webhooks, or direct output. Properties are evaluated in
            strict priority order:
            1. expressions
            2. webhooks
            3. output

            Evaluation stops at the first property that returns a valid output result,
            similar to a return statement in a function. Any subsequent properties are
            ignored when a valid output is returned. If a valid output is not returned
            from any of the properties, a generic error message is returned.
        skip_fillers: Skips the top-level fillers specified in `ai.languages` (which
            includes `speech_fillers` and `function_fillers`). When set to `true`, only
            function-specific fillers defined directly on `SWAIG.functions.fillers` will
            play. **Default:** `false`.
        web_hook_url: Function-specific URL to send status callbacks and reports to.
            Takes precedence over a default setting. Authentication can also be set in
            the url in the format of `username:password@url.`
        wait_file: A file to play while the function is running. `wait_file_loops` can
            specify the amount of times that files should continously play. Default is
            not set.
        wait_file_loops: The number of times to loop playing the file. Default is not
            set.
        wait_for_fillers: Whether to wait for fillers to finish playing before
            continuing with the function. **Default:** `false`.
        function: A unique name for the function. This can be any user-defined string or
            can reference a reserved function. Reserved functions are SignalWire
            functions that will be executed at certain points in the conversation.
    """

    description: str
    purpose: str
    parameters: FunctionParameters
    fillers: FunctionFillers
    argument: FunctionParameters
    active: bool | SWMLVar
    meta_data: dict[str, Any]
    meta_data_token: str
    data_map: DataMap
    skip_fillers: bool | SWMLVar
    web_hook_url: str
    wait_file: str
    wait_file_loops: int | str
    wait_for_fillers: bool | SWMLVar
    function: str


ValidConfirmMethods: TypeAlias = "Cond | Set | Unset | Hangup | Play | Prompt | Record | RecordCall | StopRecordCall | Tap | StopTap | SendDigits | SendSMS | Denoise | StopDenoise"


class Webhook(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime.

    Attributes:
        expressions: A list of expressions to be evaluated upon matching. If the
            following properties are set (foreach, expressions, output), they will be
            processed in the following order:
            1. foreach
            2. expressions
            3. output
        error_keys: A string or array of strings that represent the keys to be used for
            error handling. This will match the key(s) in the response from the API
            call.
        url: The endpoint for the external service or API.
        foreach: Iterates over an array of objects and processes a output based on each
            element in the array. Works similarly to JavaScript's forEach method. If the
            following properties are set (foreach, expressions, output), they will be
            processed in the following order:
            1. foreach
            2. expressions
            3. output
        headers: Any necessary headers for the API call.
        method: The HTTP method (GET, POST, etc.) for the API call.
        input_args_as_params: A boolean to determine if the input arguments should be
            passed as parameters.
        params: An object of any necessary parameters for the API call. The key is the
            parameter name and the value is the parameter value.
        require_args: A string or array of strings that represent the `arguments` that
            are required to make the webhook request.
        output: An object that contains a response and a list of actions to be performed
            upon completion of the webhook request. If the following properties are set
            (foreach, expressions, output), they will be processed in the following
            order:
            1. foreach
            2. expressions
            3. output
    """

    expressions: list[Expression]
    error_keys: str | list[str]
    url: str
    foreach: dict[str, Any]
    headers: dict[str, Any]
    method: Literal["GET", "POST", "PUT", "DELETE"]
    input_args_as_params: bool | SWMLVar
    params: dict[str, Any]
    require_args: str | list[str]
    output: Output


play_url: TypeAlias = "str"

uuid: TypeAlias = "str"

CallCommandsRequest: TypeAlias = "CallRequest"
CallCommandsResponse: TypeAlias = "CallResponse"
