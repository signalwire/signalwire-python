# AUTO-GENERATED from porting-sdk/swaig-specs/post-prompt.yaml — DO NOT EDIT.
# (vendored from mod_openai; regenerate via
#  python3 porting-sdk/scripts/generate_python_rest_types.py)
#
# The post-prompt callback payload — the call summary + enriched call log the agent's
# post-prompt handler RECEIVES. STATIC-ONLY: a plain dict at runtime; conditional fields
# are optional, extra keys tolerated.
from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict
from typing import TYPE_CHECKING

# SwaigRequest is generated in swaig_request_generated; aliased here for the
# swaig_log entry's post_data field.
if TYPE_CHECKING:
    from signalwire.core.swaig_request_generated import SwaigRequest as SwaigRequest


class PostPrompt(TypedDict, total=False):
    """Built by ais_get_post_data (ai_utils.c) + openai_post_process (post_process.c). No `version` field. Open shape: conditional fields appear only when their precondition holds.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    content_type: Literal["text/json"]
    content_disposition: Literal["agent.summary"]
    conversation_type: Literal["voice"]
    action: Literal["post_conversation"]
    project_id: str
    space_id: str
    call_id: str
    app_name: str
    ai_session_id: str
    ai_id_tag: str
    conversation_id: str
    call_ended_by: str
    caller_id_name: str
    caller_id_number: str
    conversation_summary: str
    hard_timeout: bool
    call_start_date: int
    call_answer_date: int
    call_end_date: int
    ai_start_date: int
    ai_end_date: int
    post_prompt_data: PostPromptData
    global_data: dict[str, Any]
    SWMLVars: dict[str, Any]
    SWMLCall: dict[str, Any]
    call_log: list[PostPromptCallLogEntry]
    raw_call_log: list[PostPromptCallLogEntry]
    call_timeline: list[dict[str, Any]]
    previous_contexts: list[list[dict[str, Any]]]
    times: list[PostPromptTimesEntry]
    swaig_log: list[PostPromptSwaigLogEntry]
    total_minutes: float
    total_input_tokens: float
    total_output_tokens: float
    total_wire_input_tokens: float
    total_wire_input_tokens_per_minute: float
    total_wire_output_tokens: float
    total_wire_output_tokens_per_minute: float
    total_tts_chars: float
    total_tts_chars_per_min: float
    total_asr_minutes: float
    total_asr_cost_factor: float


class PostPromptData(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    parsed: list[dict[str, Any]]
    raw: str
    substituted: str


PostPromptCallLogEntry: TypeAlias = "PostPromptUserEntry | PostPromptAssistantEntry | PostPromptThinkingEntry | PostPromptToolEntry | PostPromptSystemLogEntry | PostPromptSystemEntry"


class PostPromptUserEntry(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    role: str
    content: str
    timestamp: int
    confidence: float
    content_type: str
    speaker: str
    start_timestamp: int
    end_timestamp: int
    speaking_to_final_event: float
    speaking_to_turn_detection: float
    turn_detection_to_final_event: float
    barge_count: int
    merged: bool
    merge_count: int
    entity: PostPromptEntity
    eot: PostPromptEot
    timing: PostPromptTiming


class PostPromptAssistantEntry(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    role: str
    content: str
    timestamp: int
    tool_calls: list[dict[str, Any]]
    latency: float
    utterance_latency: float
    audio_latency: float
    acoustic_latency: float | None
    eos_to_push_latency: float | None
    dg_decision_latency: float | None
    poll: float | None
    speech_start_wall_us: int
    last_word_end_wall_us: int
    turn_decided_wall_us: int
    status_pushed_wall_us: int
    stamps_us: PostPromptStampsUs
    barged: bool
    barge_elapsed_ms: float
    text_heard_approx: str
    text_spoken_total: str


class PostPromptThinkingEntry(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    role: str
    content: str
    timestamp: int
    lang: str
    tokens: int


class PostPromptToolEntry(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    role: str
    tool_call_id: str
    content: str
    timestamp: int
    function_name: str
    latency: float
    utterance_latency: float
    function_latency: float
    audio_latency: float
    execution_latency: float
    deprecation_warning: str
    start_timestamp: int
    end_timestamp: int
    distilled: bool
    original_result: str


class PostPromptSystemLogEntry(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    role: str
    content: str
    timestamp: int
    action: str
    lang: str
    tokens: int
    content_type: str
    metadata: dict[str, Any]
    context: str
    step: str
    step_index: int


class PostPromptSystemEntry(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    role: str
    content: str
    timestamp: int


class PostPromptSwaigLogEntry(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    command_name: str
    command_arg: str
    epoch_time: int
    native: bool
    active_count: int | Literal["endless"]
    url: str
    post_data: SwaigRequest
    post_response: dict[str, Any]
    delayed_post_response: dict[str, Any]
    mcp_url: str
    mcp_tool: str
    mcp_response: dict[str, Any]
    mcp_error: str


class PostPromptTimesEntry(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    response: str
    response_word_count: int
    answer_time: float
    token_time: float
    tokens: int
    avg_tps: float
    tps: float


class PostPromptEntity(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal[
        "phone",
        "email",
        "ssn",
        "card",
        "uuid",
        "url",
        "money",
        "time",
        "date",
        "ordinal",
    ]
    value: str
    valid: bool


class PostPromptEot(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    basis: Literal["entity_snap", "growth_stop", "ceiling", "natural"]
    confidence: float


class PostPromptTiming(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hold_ms: float
    commit_latency_ms: float
    segments: int
    walkbacks: int


class PostPromptStampsUs(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    speech_start: int
    last_word_end: int
    suspected_end: int
    turn_decided: int
    status_pushed: int
    request_detect: int
    first_token: int
    first_utterance: int
    first_audio: int
