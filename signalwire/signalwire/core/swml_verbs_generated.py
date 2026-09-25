# AUTO-GENERATED from porting-sdk/schema.json — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# Typed SWML verb surface: one <Verb>Config TypedDict per verb + a _SwmlVerbs
# Protocol declaring each verb method (config -> Self). SwmlBuilder installs these
# verbs dynamically from schema.json at runtime; this static surface lets the type
# checker SEE them (mirrors the TS SwmlVerbMethods.generated.ts augmentation).
# STATIC-ONLY: configs are plain dicts at runtime, never validated.
from __future__ import annotations
from collections.abc import Mapping
from typing import Any, Literal, TypeAlias, TypedDict
from typing import TypeVar

_Self = TypeVar("_Self", bound="_SwmlVerbs")


class AI(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ai: dict[str, Any] | list[Any]


class AiSidecar(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ai_sidecar: dict[str, Any]


class AmazonBedrock(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    amazon_bedrock: dict[str, Any]


class Answer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    answer: dict[str, Any] | list[Any]


class CallDeviceStream(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    authorization_bearer_token: str
    codec: str
    custom_parameters: Any
    name: str
    realtime: bool
    status_url: str
    status_url_method: Literal["GET", "POST"]
    url: str


class CallPayParameters(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    value: str


class CallPayPrompts(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    actions: list[CallPayPromptsActions]
    attempt: str
    card_type: str
    error_type: str
    # non-identifier field 'for': Literal['payment-card-number', 'expiration-date', 'security-code', 'postal-code', 'bank-routing-number', 'bank-account-number', 'payment-processing', 'payment-completed', 'payment-failed', 'payment-canceled']
    play: list[RingbackConfig]
    require_matching_inputs: str


class CallPayPromptsActions(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    type: Literal["Say", "Play"]
    phrase: str


class Cond(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    cond: list[dict[str, Any]]


class Connect(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    connect: dict[str, Any]


class ConnectDevice(TypedDict, total=False):
    """Body shape enforced by CHECK_swml_connect_device, swml_schema.c.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    authorization_bearer_token: str | SWMLVar
    call_state_events: list[str] | SWMLVar
    call_state_url: str | SWMLVar
    codec: str | SWMLVar
    codecs: str | list[Any]
    confirm: str | list[SWMLMethod] | dict[str, Any] | SWMLVar
    confirm_timeout: int | SWMLVar
    custom_parameters: dict[str, str] | SWMLVar
    encryption: Literal["mandatory", "optional", "forbidden"] | SWMLVar
    # non-identifier field 'from': str | SWMLVar
    from_name: str | SWMLVar
    fsvars: dict[str, str] | SWMLVar
    headers: list[ConnectSipHeader]
    name: str | SWMLVar
    password: str | SWMLVar
    realtime: bool | SWMLVar
    session_timeout: int | SWMLVar
    status_url: str | SWMLVar
    status_url_method: Literal["GET", "POST"] | SWMLVar
    timeout: int | SWMLVar
    to: str | SWMLVar
    username: str | SWMLVar
    webrtc_media: bool | SWMLVar


ConnectSerialParallel: TypeAlias = "list[ConnectDevice]"


class ConnectSipHeader(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    name: str
    value: str | SWMLVar


class Denoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    denoise: dict[str, Any]


class DetectMachine(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    detect_machine: dict[str, Any]


class Dial(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    dial: dict[str, Any]


class Echo(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    echo: dict[str, Any] | list[Any]


class EnterQueue(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    enter_queue: dict[str, Any]


class Eval(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    eval: dict[str, Any]


class Execute(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    execute: dict[str, Any] | list[Any]


class ExecuteRpc(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    execute_rpc: dict[str, Any]


class Goto(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    goto: dict[str, Any] | list[Any]


class Hangup(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    hangup: dict[str, Any] | list[Any]


class If(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'if': dict[str, Any]


class JoinConference(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    join_conference: dict[str, Any] | list[Any]


class JoinRoom(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    join_room: dict[str, Any] | list[Any]


class Label(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    label: dict[str, Any] | list[Any]


class LiveTranscribe(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_transcribe: dict[str, Any]


class LiveTranslate(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    live_translate: dict[str, Any]


class Pay(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    pay: dict[str, Any] | list[Any]


class Play(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    play: dict[str, Any] | list[Any]


class Prompt(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    prompt: dict[str, Any] | list[Any]


class ReceiveFax(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    receive_fax: dict[str, Any] | list[Any]


class Record(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    record: dict[str, Any]


class RecordCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    record_call: dict[str, Any]


class Request(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    request: dict[str, Any]


class Return(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    # non-identifier field 'return': dict[str, Any]


class Ring(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    ring: dict[str, Any]


class RingbackConfig(TypedDict, total=False):
    """Declared as a named $defs entry so every generator emits a TYPED shape via $ref rather than collapsing an inline object to an untyped map.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    url: str
    urls: list[str]
    volume: float | SWMLVar


class SIPRefer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sip_refer: dict[str, Any] | list[Any]


SWMLMethod: TypeAlias = "AI | AiSidecar | AmazonBedrock | Answer | Cond | Connect | Denoise | DetectMachine | Dial | Echo | EnterQueue | Eval | Execute | ExecuteRpc | Goto | Hangup | If | JoinConference | JoinRoom | Label | LiveTranscribe | LiveTranslate | Pay | Play | Prompt | ReceiveFax | Record | RecordCall | Request | Return | Ring | SIPRefer | SendDigits | SendFax | SendSMS | Set | SetMeta | Sleep | StopDenoise | StopRecordCall | StopStream | StopTap | Stream | Switch | Tap | Transcribe | TranscribeStop | Transfer | Unset | UserEvent"


SWMLVar: TypeAlias = "str"


class Section(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    main: list[SWMLMethod]


class SendDigits(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    send_digits: dict[str, Any] | list[Any]


class SendFax(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    send_fax: dict[str, Any] | list[Any]


class SendSMS(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    send_sms: dict[str, Any]


class Set(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set: dict[str, Any]


class SetMeta(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    set_meta: dict[str, Any]


class Sleep(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    sleep: dict[str, Any] | list[Any]


class StopDenoise(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_denoise: dict[str, Any]


class StopRecordCall(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_record_call: dict[str, Any] | list[Any]


class StopStream(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_stream: dict[str, Any] | list[Any]


class StopTap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stop_tap: dict[str, Any] | list[Any]


class Stream(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    stream: dict[str, Any] | list[Any]


class Switch(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    switch: dict[str, Any]


class Tap(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    tap: dict[str, Any] | list[Any]


class Transcribe(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    transcribe: dict[str, Any]


class TranscribeStop(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    transcribe_stop: dict[str, Any]


class Transfer(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    transfer: dict[str, Any] | list[Any]


class Unset(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    unset: list[str] | str


class UserEvent(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    user_event: dict[str, Any]


class AiSidecarConfig(TypedDict, total=False):
    """Start ai_sidecar mode — live_transcribe with an LLM/SWAIG/MCP loop on top.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    SWAIG: dict[str, Any] | SWMLVar
    action: dict[str, Any] | SWMLVar
    customer_role: Literal["remote-caller", "local-caller"] | SWMLVar
    direction: list[Literal["remote-caller", "local-caller"]] | SWMLVar
    global_data: dict[str, Any] | SWMLVar
    hints: list[str] | SWMLVar
    lang: str | SWMLVar
    model: str | SWMLVar
    params: dict[str, Any] | SWMLVar
    permissions: dict[str, Any] | SWMLVar
    prompt: dict[str, Any] | str | SWMLVar
    url: str | SWMLVar


class AmazonBedrockConfig(TypedDict, total=False):
    """Creates a new Bedrock AI Agent

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    SWAIG: dict[str, Any]
    app_name: str
    assistant_name: str
    assistant_prompt: str
    conversation_id: str
    global_data: dict[str, Any]
    greeting_prompt: dict[str, Any]
    params: dict[str, Any]
    post_prompt: dict[str, Any]
    post_prompt_url: str
    prompt: dict[str, Any]
    transcript_webhook_url: str


class ConnectConfig(TypedDict, total=False):
    """Dial a SIP URI or phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    answer_on_bridge: bool | str | SWMLVar
    authorization_bearer_token: str | SWMLVar
    call_state_events: list[str] | SWMLVar
    call_state_url: str | SWMLVar
    codec: str | SWMLVar
    codecs: str | list[Any] | SWMLVar
    confirm: str | list[SWMLMethod] | dict[str, Any] | SWMLVar
    confirm_timeout: int | SWMLVar
    custom_parameters: dict[str, str] | SWMLVar
    encryption: Literal["mandatory", "optional", "forbidden"] | SWMLVar
    execute_after_queue: str | SWMLVar
    # non-identifier field 'from': str | SWMLVar
    from_name: str | SWMLVar
    fsvars: dict[str, str] | SWMLVar
    headers: list[ConnectSipHeader]
    max_duration: float | SWMLVar
    name: str | SWMLVar
    parallel: list[ConnectDevice]
    password: str | SWMLVar
    realtime: bool | SWMLVar
    result: list[Any] | dict[str, Any]
    ringback: bool | str | list[RingbackConfig] | Play
    serial: list[ConnectDevice]
    serial_parallel: list[ConnectSerialParallel]
    session_timeout: int | SWMLVar
    status_url: str | SWMLVar
    status_url_method: Literal["GET", "POST"] | SWMLVar
    stop_all_on_reject: list[Any] | bool | str | SWMLVar
    timeout: int | SWMLVar
    to: str | SWMLVar
    username: str | SWMLVar
    webrtc_media: bool | SWMLVar


class DetectMachineConfig(TypedDict, total=False):
    """A detection method that combines AMD (Answering Machine Detection) and fax detection.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    detect_interruptions: bool | SWMLVar
    detect_message_end: bool | SWMLVar
    detectors: str | SWMLVar
    end_silence_timeout: float | SWMLVar
    initial_timeout: float | SWMLVar
    machine_ready_timeout: float | SWMLVar
    machine_voice_threshold: float | SWMLVar
    machine_words_threshold: int | SWMLVar
    status_url: str | SWMLVar
    timeout: float | SWMLVar
    tone: Literal["CNG", "CED", "cng", "ced"] | SWMLVar
    wait: bool | SWMLVar


class DialConfig(TypedDict, total=False):
    """Dial out to one or more endpoints (deprecated).

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    answer_on_bridge: bool | str
    call_state_events: list[str] | SWMLVar
    call_state_url: str | SWMLVar
    codecs: str | list[Any] | SWMLVar
    confirm: str | list[SWMLMethod] | dict[str, Any] | SWMLVar
    confirm_timeout: int | SWMLVar
    dest_swml: str | dict[str, Any] | list[Any]
    encryption: Literal["mandatory", "optional", "forbidden"] | SWMLVar
    execute_after_queue: str | SWMLVar
    # non-identifier field 'from': str | SWMLVar
    from_name: str | SWMLVar
    fsvars: dict[str, str] | SWMLVar
    headers: list[ConnectSipHeader]
    max_duration: float | SWMLVar
    parallel: list[ConnectDevice]
    password: str | SWMLVar
    result: Any
    ringback: Play | list[Any] | str
    serial: list[ConnectDevice]
    serial_parallel: list[ConnectSerialParallel]
    session_timeout: int | SWMLVar
    status_url: str | SWMLVar
    stop_all_on_reject: list[Any] | bool | str | SWMLVar
    timeout: int | SWMLVar
    to: str | SWMLVar
    username: str | SWMLVar
    webrtc_media: bool | SWMLVar


class EnterQueueConfig(TypedDict, total=False):
    """Place the current call in a named queue where it will wait to be connected to an available agent or resource.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    execute_after_queue: str | SWMLVar
    queue_name: str | SWMLVar
    status_url: str | SWMLVar
    wait_time: int | SWMLVar
    wait_url: str | SWMLVar
    whisper_url: str | SWMLVar


class ExecuteRpcConfig(TypedDict, total=False):
    """Execute a remote procedure call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: str | SWMLVar
    method: str | SWMLVar
    node_id: str | SWMLVar
    params: dict[str, Any] | SWMLVar


class IfConfig(TypedDict, total=False):
    """Conditional branching (deprecated).

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    condition: str | SWMLVar
    # non-identifier field 'else': list[SWMLMethod] | dict[str, Any]
    then: list[SWMLMethod] | dict[str, Any]


class LiveTranscribeConfig(TypedDict, total=False):
    """Start live transcription of the call. The transcription will be sent to the specified webhook URL.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    action: Literal["start", "stop", "summarize"] | dict[str, Any] | SWMLVar
    hints: list[dict[str, Any] | str] | SWMLVar


class LiveTranslateConfig(TypedDict, total=False):
    """Start live translation of the call. The translation will be sent to the specified webhook URL.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    action: Literal["inject", "start", "stop", "summarize"] | dict[str, Any] | SWMLVar


class RecordConfig(TypedDict, total=False):
    """Record the call audio in the foreground, pausing further SWML execution until recording ends.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    format: Literal["wav", "mp3", "mp4"] | SWMLVar
    beep: bool | SWMLVar
    direction: Literal["listen", "speak", "both"] | SWMLVar
    end_silence_timeout: float | SWMLVar
    initial_timeout: float | SWMLVar
    input_sensitivity: float | SWMLVar
    max_length: int | SWMLVar
    status_url: str | SWMLVar
    stereo: bool | SWMLVar
    terminators: str | SWMLVar


class RecordCallConfig(TypedDict, total=False):
    """Record call in the background.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    format: Literal["wav", "mp3", "mp4"] | SWMLVar
    beep: bool | SWMLVar
    control_id: str | SWMLVar
    direction: Literal["listen", "speak", "both"] | SWMLVar
    end_silence_timeout: float | SWMLVar
    initial_timeout: float | SWMLVar
    input_sensitivity: float | SWMLVar
    max_length: int | SWMLVar
    status_url: str | SWMLVar
    stereo: bool | SWMLVar
    terminators: str | SWMLVar


class RequestConfig(TypedDict, total=False):
    """Send a GET, POST, PUT, or DELETE request to a remote URL.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    body: dict[str, Any] | list[Any] | str | float | bool
    connect_timeout: int | SWMLVar
    headers: dict[str, Any]
    method: (
        Literal["get", "GET", "put", "PUT", "POST", "post", "DELETE", "delete"]
        | SWMLVar
    )
    save_variables: bool | SWMLVar
    timeout: int | SWMLVar
    url: str | SWMLVar


class SendSmsConfig(TypedDict, total=False):
    """Send an outbound SMS or MMS message to a PSTN phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    body: str | SWMLVar
    from_number: str | SWMLVar
    media: list[str]
    region: str | SWMLVar
    status_callback: str | SWMLVar
    tags: list[str]
    to_number: str | SWMLVar


class SetMetaConfig(TypedDict, total=False):
    """Add customer metadata to call and conference events

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    private: dict[str, Any]
    public: dict[str, Any]


class SwitchConfig(TypedDict, total=False):
    """Execute different instructions based on a variable's value.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    default: list[SWMLMethod] | dict[str, Any]
    case: dict[str, Any]
    variable: str | SWMLVar


class TranscribeConfig(TypedDict, total=False):
    """Start transcription on the call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    status_url: str | SWMLVar


class UserEventConfig(TypedDict, total=False):
    """Allows the user to set and send events to the connected client on the call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    event: dict[str, Any] | SWMLVar


class _SwmlVerbs:
    """The SWML verb methods SwmlBuilder installs at runtime (static view)."""

    def ai_sidecar(self: _Self, config: AiSidecarConfig | None = None) -> _Self:
        """Start ai_sidecar mode — live_transcribe with an LLM/SWAIG/MCP loop on top."""
        raise NotImplementedError  # installed dynamically at runtime

    def amazon_bedrock(self: _Self, config: AmazonBedrockConfig | None = None) -> _Self:
        """Creates a new Bedrock AI Agent"""
        raise NotImplementedError  # installed dynamically at runtime

    def cond(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by is_valid_cond_method, swml_schema.c:1249."""
        raise NotImplementedError  # installed dynamically at runtime

    def connect(self: _Self, config: ConnectConfig | None = None) -> _Self:
        """Dial a SIP URI or phone number."""
        raise NotImplementedError  # installed dynamically at runtime

    def denoise(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Start noise reduction. You can stop it at any time using `stop_denoise`."""
        raise NotImplementedError  # installed dynamically at runtime

    def detect_machine(self: _Self, config: DetectMachineConfig | None = None) -> _Self:
        """A detection method that combines AMD (Answering Machine Detection) and fax detection."""
        raise NotImplementedError  # installed dynamically at runtime

    def dial(self: _Self, config: DialConfig | None = None) -> _Self:
        """Dial out to one or more endpoints (deprecated)."""
        raise NotImplementedError  # installed dynamically at runtime

    def echo(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the echo verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def enter_queue(self: _Self, config: EnterQueueConfig | None = None) -> _Self:
        """Place the current call in a named queue where it will wait to be connected to an available agent or resource."""
        raise NotImplementedError  # installed dynamically at runtime

    def eval(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Evaluate expressions and assign to variables (deprecated)."""
        raise NotImplementedError  # installed dynamically at runtime

    def execute(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the execute verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def execute_rpc(self: _Self, config: ExecuteRpcConfig | None = None) -> _Self:
        """Execute a remote procedure call."""
        raise NotImplementedError  # installed dynamically at runtime

    def goto(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the goto verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def if_(self: _Self, config: IfConfig | None = None) -> _Self:
        """Conditional branching (deprecated)."""
        raise NotImplementedError  # installed dynamically at runtime

    def join_conference(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the join_conference verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def join_room(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the join_room verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def label(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the label verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def live_transcribe(
        self: _Self, config: LiveTranscribeConfig | None = None
    ) -> _Self:
        """Start live transcription of the call. The transcription will be sent to the specified webhook URL."""
        raise NotImplementedError  # installed dynamically at runtime

    def live_translate(self: _Self, config: LiveTranslateConfig | None = None) -> _Self:
        """Start live translation of the call. The translation will be sent to the specified webhook URL."""
        raise NotImplementedError  # installed dynamically at runtime

    def pay(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the pay verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def prompt(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the prompt verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def receive_fax(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the receive_fax verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def record(self: _Self, config: RecordConfig | None = None) -> _Self:
        """Record the call audio in the foreground, pausing further SWML execution until recording ends."""
        raise NotImplementedError  # installed dynamically at runtime

    def record_call(self: _Self, config: RecordCallConfig | None = None) -> _Self:
        """Record call in the background."""
        raise NotImplementedError  # installed dynamically at runtime

    def request(self: _Self, config: RequestConfig | None = None) -> _Self:
        """Send a GET, POST, PUT, or DELETE request to a remote URL."""
        raise NotImplementedError  # installed dynamically at runtime

    def return_(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Return a value from an execute call or exit the script. The value can be any type."""
        raise NotImplementedError  # installed dynamically at runtime

    def ring(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Send 180 Ringing on an inbound call without answering."""
        raise NotImplementedError  # installed dynamically at runtime

    def sip_refer(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the sip_refer verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def send_digits(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the send_digits verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def send_fax(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the send_fax verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def send_sms(self: _Self, config: SendSmsConfig | None = None) -> _Self:
        """Send an outbound SMS or MMS message to a PSTN phone number."""
        raise NotImplementedError  # installed dynamically at runtime

    def set(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Set script variables to the specified values."""
        raise NotImplementedError  # installed dynamically at runtime

    def set_meta(self: _Self, config: SetMetaConfig | None = None) -> _Self:
        """Add customer metadata to call and conference events"""
        raise NotImplementedError  # installed dynamically at runtime

    def sleep(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the sleep verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def stop_denoise(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Stop noise reduction that was started with denoise."""
        raise NotImplementedError  # installed dynamically at runtime

    def stop_record_call(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the stop_record_call verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def stop_stream(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the stop_stream verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def stop_tap(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the stop_tap verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def stream(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the stream verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def switch(self: _Self, config: SwitchConfig | None = None) -> _Self:
        """Execute different instructions based on a variable's value."""
        raise NotImplementedError  # installed dynamically at runtime

    def tap(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the tap verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def transcribe(self: _Self, config: TranscribeConfig | None = None) -> _Self:
        """Start transcription on the call."""
        raise NotImplementedError  # installed dynamically at runtime

    def transcribe_stop(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Stop transcription on the call."""
        raise NotImplementedError  # installed dynamically at runtime

    def transfer(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Add the transfer verb."""
        raise NotImplementedError  # installed dynamically at runtime

    def unset(self: _Self, config: Mapping[str, Any] | None = None) -> _Self:
        """Body shape enforced by CHECK_swml_method_unset, swml_schema.c."""
        raise NotImplementedError  # installed dynamically at runtime

    def user_event(self: _Self, config: UserEventConfig | None = None) -> _Self:
        """Allows the user to set and send events to the connected client on the call."""
        raise NotImplementedError  # installed dynamically at runtime
