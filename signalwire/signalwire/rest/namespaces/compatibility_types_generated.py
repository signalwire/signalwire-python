# AUTO-GENERATED from porting-sdk/rest-apis/compatibility/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict


class Account(TypedDict, total=False):
    """Account/Project model representing a SignalWire project.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    friendly_name: str
    status: AccountStatus
    auth_token: str
    date_created: str
    date_updated: str
    type: AccountType
    owner_account_sid: str
    region_preference: str
    uri: str
    subproject: bool
    signing_key: str | None
    subresource_uris: SubresourceUris


class AccountListResponse(TypedDict, total=False):
    """Response containing a list of accounts.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    accounts: list[Account]


class AccountResponse(TypedDict, total=False):
    """Response containing a single account.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    friendly_name: str
    status: AccountStatus
    auth_token: str
    date_created: str
    date_updated: str
    type: AccountType
    owner_account_sid: str
    region_preference: str
    uri: str
    subproject: bool
    signing_key: str | None
    subresource_uris: SubresourceUris


AccountStatus: TypeAlias = "Literal['active']"

AccountType: TypeAlias = "Literal['Full']"

AddressRequirements: TypeAlias = "Literal['none', 'any', 'local', 'foreign']"

AnsweredBy: TypeAlias = "Literal['human', 'machine']"


class Application(TypedDict, total=False):
    """Application model representing a cXML application.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    api_version: str
    date_created: str
    date_updated: str
    friendly_name: str
    uri: str
    voice_url: str | None
    voice_method: str | None
    voice_fallback_url: str | None
    voice_fallback_method: str | None
    status_callback: str | None
    status_callback_method: str | None
    voice_caller_id_lookup: bool | None
    sms_url: str | None
    sms_method: str | None
    sms_fallback_url: str | None
    sms_fallback_method: str | None
    sms_status_callback: str | None
    sms_status_callback_method: str | None
    message_status_callback: str | None


class ApplicationListResponse(TypedDict, total=False):
    """Response containing a list of applications.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    applications: list[Application]


class ApplicationResponse(TypedDict, total=False):
    """Response containing a single application.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    api_version: str
    date_created: str
    date_updated: str
    friendly_name: str
    uri: str
    voice_url: str | None
    voice_method: str | None
    voice_fallback_url: str | None
    voice_fallback_method: str | None
    status_callback: str | None
    status_callback_method: str | None
    voice_caller_id_lookup: bool | None
    sms_url: str | None
    sms_method: str | None
    sms_fallback_url: str | None
    sms_fallback_method: str | None
    sms_status_callback: str | None
    sms_status_callback_method: str | None
    message_status_callback: str | None


class AvailablePhoneNumber(TypedDict, total=False):
    """Available phone number model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    friendly_name: str
    phone_number: str
    lata: str | None
    locality: str | None
    rate_center: str | None
    latitude: str | None
    longitude: str | None
    region: str | None
    postal_code: str | None
    iso_country: str
    capabilities: PhoneNumberCapabilities
    beta: bool


class AvailablePhoneNumberByCountryResponse(TypedDict, total=False):
    """Response containing available phone number resources for a specific country.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    country_code: str
    country: str
    uri: str
    beta: bool
    subresource_uris: CountrySubresourceUris


class AvailablePhoneNumberListResponse(TypedDict, total=False):
    """Response containing a list of available phone numbers.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    available_phone_numbers: list[AvailablePhoneNumber]


class AvailablePhoneNumberResourcesResponse(TypedDict, total=False):
    """Response containing a list of available phone number resources (countries).

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    countries: list[CountryResource]


class Call(TypedDict, total=False):
    """Call model representing a voice call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    date_created: str
    date_updated: str
    parent_call_sid: str | None
    to: str
    formatted_to: str
    to_formatted: str
    # non-identifier field 'from': str
    formatted_from: str
    from_formatted: str
    phone_number_sid: str | None
    status: CallStatus
    start_time: str | None
    end_time: str | None
    duration: int
    price: float | None
    price_unit: str
    direction: CallDirection
    answered_by: AnsweredBy | None
    api_version: str
    forwarded_from: str | None
    caller_name: str | None
    uri: str
    subresource_uris: CallSubresourceUris
    annotation: str | None
    group_sid: str | None
    audio_in_mos: float | None
    sip_result_code: str | None
    audio_rtt_avg: int | None
    audio_rtt_min: int | None
    audio_rtt_max: int | None
    audio_out_jitter_min: int | None
    audio_out_jitter_max: int | None
    audio_out_jitter_avg: int | None
    audio_out_lost: int | None


CallDirection: TypeAlias = "Literal['inbound', 'outbound']"


class CallListResponse(TypedDict, total=False):
    """Response containing a list of calls.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    calls: list[Call]


class CallRecordingResponse(TypedDict, total=False):
    """Response containing a single call recording.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    api_version: str
    call_sid: str | None
    conference_sid: str | None
    channel: Literal["1", "2"]
    channels: Literal["1", "2"]
    date_created: str
    date_updated: str
    start_time: str | None
    end_time: str | None
    duration: int
    price: str | None
    price_unit: str
    source: RecordingSource
    status: RecordingStatus
    error_code: str | None
    uri: str
    subresource_uris: RecordingSubresourceUris
    encryption_details: str | None
    trim: str


class CallResponse(TypedDict, total=False):
    """Response containing a single call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    date_created: str
    date_updated: str
    parent_call_sid: str | None
    to: str
    formatted_to: str
    to_formatted: str
    # non-identifier field 'from': str
    formatted_from: str
    from_formatted: str
    phone_number_sid: str | None
    status: CallStatus
    start_time: str | None
    end_time: str | None
    duration: int
    price: float | None
    price_unit: str
    direction: CallDirection
    answered_by: AnsweredBy | None
    api_version: str
    forwarded_from: str | None
    caller_name: str | None
    uri: str
    subresource_uris: CallSubresourceUris
    annotation: str | None
    group_sid: str | None
    audio_in_mos: float | None
    sip_result_code: str | None
    audio_rtt_avg: int | None
    audio_rtt_min: int | None
    audio_rtt_max: int | None
    audio_out_jitter_min: int | None
    audio_out_jitter_max: int | None
    audio_out_jitter_avg: int | None
    audio_out_lost: int | None


CallStatus: TypeAlias = "Literal['queued', 'ringing', 'in-progress', 'canceled', 'completed', 'busy', 'failed', 'no-answer']"


class CallStreamResponse(TypedDict, total=False):
    """Response containing a single call stream.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    call_sid: str
    name: str
    status: StreamStatus
    date_updated: str
    uri: str


class CallSubresourceUris(TypedDict, total=False):
    """Call subresource URIs.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    notifications: str | None
    recordings: str


class CompatibilityErrorArrayItem(TypedDict, total=False):
    """Error item in the errors array format.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    message: str
    more_info: str


class CompatibilityErrorArrayResponse(TypedDict, total=False):
    """Error response with errors array format.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[CompatibilityErrorArrayItem]


class CompatibilityErrorResponse(TypedDict, total=False):
    """Error response model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: int
    message: str
    more_info: str
    status: int


class CompatibilityErrorStringArrayResponse(TypedDict, total=False):
    """Error response with errors array of strings format.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[str]


class CompatibilityImportedPhoneNumberError(TypedDict, total=False):
    """Error response model with string code for ImportedPhoneNumbers.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    code: str
    message: str
    more_info: str
    status: int


class CompatibilityTokenValidationError(TypedDict, total=False):
    """Token validation error response model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: str
    code: str
    message: str
    attribute: str
    url: str


class Conference(TypedDict, total=False):
    """Conference model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    date_created: str
    date_updated: str
    friendly_name: str
    status: ConferenceStatus
    api_version: str
    region: str
    uri: str
    subresource_uris: ConferenceSubresourceUris


class ConferenceListResponse(TypedDict, total=False):
    """Response containing a list of conferences.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    conferences: list[Conference]


class ConferenceParticipant(TypedDict, total=False):
    """Conference participant model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_sid: str
    call_sid: str
    call_sid_to_coach: str | None
    coaching: bool
    conference_sid: str
    date_created: str
    status: ParticipantStatus
    date_updated: str
    end_conference_on_exit: bool
    muted: bool
    hold: bool
    start_conference_on_enter: bool
    uri: str


class ConferenceParticipantListResponse(TypedDict, total=False):
    """Response containing a list of conference participants.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    participants: list[ConferenceParticipant]


class ConferenceParticipantResponse(TypedDict, total=False):
    """Response containing a single conference participant.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_sid: str
    call_sid: str
    call_sid_to_coach: str | None
    coaching: bool
    conference_sid: str
    date_created: str
    status: ParticipantStatus
    date_updated: str
    end_conference_on_exit: bool
    muted: bool
    hold: bool
    start_conference_on_enter: bool
    uri: str


class ConferenceRecording(TypedDict, total=False):
    """Conference recording model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    api_version: str
    call_sid: str | None
    conference_sid: str | None
    channel: Literal["1", "2"]
    channels: Literal["1", "2"]
    date_created: str
    date_updated: str
    start_time: str | None
    end_time: str | None
    duration: int
    price: str | None
    price_unit: str
    source: ConferenceRecordingSource
    status: ConferenceRecordingStatus
    error_code: str | None
    uri: str
    subresource_uris: ConferenceRecordingSubresourceUris
    encryption_details: str | None
    trim: str


class ConferenceRecordingListResponse(TypedDict, total=False):
    """Response containing a list of conference recordings.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    recordings: list[ConferenceRecording]


class ConferenceRecordingResponse(TypedDict, total=False):
    """Response containing a single conference recording.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    api_version: str
    call_sid: str | None
    conference_sid: str | None
    channel: Literal["1", "2"]
    channels: Literal["1", "2"]
    date_created: str
    date_updated: str
    start_time: str | None
    end_time: str | None
    duration: int
    price: str | None
    price_unit: str
    source: ConferenceRecordingSource
    status: ConferenceRecordingStatus
    error_code: str | None
    uri: str
    subresource_uris: ConferenceRecordingSubresourceUris
    encryption_details: str | None
    trim: str


ConferenceRecordingSource: TypeAlias = (
    "Literal['Conference', 'StartConferenceRecording']"
)

ConferenceRecordingStatus: TypeAlias = "Literal['queued', 'in-progress', 'paused', 'resumed', 'completed', 'absent', 'stopped']"


class ConferenceRecordingSubresourceUris(TypedDict, total=False):
    """Recording subresource URIs.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    transcriptions: str


class ConferenceResponse(TypedDict, total=False):
    """Response containing a single conference.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    date_created: str
    date_updated: str
    friendly_name: str
    status: ConferenceStatus
    api_version: str
    region: str
    uri: str
    subresource_uris: ConferenceSubresourceUris


ConferenceStatus: TypeAlias = "Literal['init', 'in-progress', 'completed']"


class ConferenceStreamResponse(TypedDict, total=False):
    """Response containing a single conference stream.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_sid: str
    conference_sid: str
    date_updated: str
    name: str | None
    sid: str
    status: ConferenceStreamStatus
    uri: str


ConferenceStreamStatus: TypeAlias = "Literal['queued', 'in-progress', 'stopped']"


class ConferenceSubresourceUris(TypedDict, total=False):
    """Conference subresource URIs.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    participants: str
    recordings: str


class CountryResource(TypedDict, total=False):
    """Country resource for available phone numbers.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    country_code: str
    country: str
    uri: str
    beta: bool
    subresource_uris: CountrySubresourceUris


class CountrySubresourceUris(TypedDict, total=False):
    """Country subresource URIs.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    local: str
    toll_free: str


class CreateApplicationRequest(TypedDict, total=False):
    """Request body for creating an application.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    FriendlyName: str
    VoiceUrl: str
    VoiceMethod: Literal["GET", "POST"]
    VoiceFallbackUrl: str
    VoiceFallbackMethod: Literal["GET", "POST"]
    StatusCallback: str
    StatusCallbackMethod: Literal["GET", "POST"]
    SmsUrl: str
    SmsMethod: Literal["GET", "POST"]
    SmsFallbackUrl: str
    SmsFallbackMethod: Literal["GET", "POST"]
    SmsStatusCallback: str
    SmsStatusCallbackMethod: Literal["GET", "POST"]


class CreateCallRecordingRequest(TypedDict, total=False):
    """Request body for creating a call recording.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    RecordingChannels: Literal["mono", "dual"]
    RecordingStatusCallback: str
    RecordingStatusCallbackEvent: str
    RecordingStatusCallbackMethod: Literal["GET", "POST"]
    RecordingTrack: Literal["inbound", "outbound", "both"]
    Trim: Literal["trim-silence", "do-not-trim"]


class CreateCallRequest(TypedDict, total=False):
    """Request body for creating a call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    To: str
    From: str
    Url: str
    ApplicationSid: str
    Method: Literal["GET", "POST"]
    FallbackUrl: str
    FallbackMethod: Literal["GET", "POST"]
    StatusCallback: str
    StatusCallbackMethod: Literal["GET", "POST"]
    StatusCallbackEvent: list[str]
    CallerId: str
    SendDigits: str
    Timeout: int
    MachineDetection: Literal["Enable", "DetectMessageEnd", "none"]
    MachineDetectionTimeout: int
    MachineDetectionSpeechThreshold: int
    MachineDetectionSpeechEndThreshold: int
    MachineDetectionSilenceTimeout: int
    MachineWordsThreshold: int
    AsyncAmd: bool
    AsyncAmdStatusCallbackMethod: Literal["GET", "POST"]
    AsyncAmdStatusCallback: str
    AsyncAmdPartialResults: bool
    Record: bool
    RecordingChannels: Literal["mono", "dual"]
    RecordingTrack: Literal["inbound", "outbound", "both"]
    RecordingStatusCallback: str
    RecordingStatusCallbackMethod: Literal["GET", "POST"]
    RecordingStatusCallbackEvent: str
    Trim: Literal["trim-silence", "do-not-trim"]
    SipAuthUsername: str
    SipAuthPassword: str
    MaxPricePerMinute: str


class CreateCallStreamRequest(TypedDict, total=False):
    """Request body for creating a call stream.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Name: str
    Track: Literal["inbound_track", "outbound_track", "both_tracks"]
    StatusCallbackMethod: Literal["GET", "POST"]
    StatusCallback: str
    Url: str
    # non-identifier field 'Parameter1.Name': str
    # non-identifier field 'Parameter1.Value': str
    # non-identifier field 'Parameter2.Name': str
    # non-identifier field 'Parameter2.Value': str
    AuthorizationBearerToken: str


class CreateConferenceStreamRequest(TypedDict, total=False):
    """Request body for creating a conference stream.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Name: str
    Track: Literal["inbound_track", "outbound_track", "both_tracks"]
    StatusCallbackMethod: Literal["GET", "POST"]
    StatusCallback: str
    Url: str
    StreamCodec: Literal["PCMU", "PCMA", "L16", "L16@16000h", "L16@24000h"]
    StreamRealTime: bool
    # non-identifier field 'Parameter1.Name': str
    # non-identifier field 'Parameter1.Value': str
    # non-identifier field 'Parameter2.Name': str
    # non-identifier field 'Parameter2.Value': str
    AuthorizationBearerToken: str


class CreateCxmlScriptRequest(TypedDict, total=False):
    """Request body for creating a cXML script.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Name: str
    Contents: str


class CreateIncomingPhoneNumberRequest(TypedDict, total=False):
    """Request body for creating an incoming phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    PhoneNumber: str
    FriendlyName: str
    SmsApplicationSid: str
    SmsFallbackMethod: Literal["GET", "POST"]
    SmsFallbackUrl: str
    SmsMethod: Literal["GET", "POST"]
    SmsUrl: str
    StatusCallback: str
    StatusCallbackMethod: Literal["GET", "POST"]
    VoiceApplicationSid: str
    VoiceFallbackMethod: Literal["GET", "POST"]
    VoiceFallbackUrl: str
    VoiceMethod: Literal["GET", "POST"]
    VoiceReceiveMode: Literal["voice", "fax"]
    VoiceUrl: str


class CreateMessageRequest(TypedDict, total=False):
    """Request body for creating a message.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    To: str
    From: str
    Body: str
    MediaUrl: str | list[str]
    SendAsMms: bool
    ApplicationSid: str
    MaxPrice: str
    StatusCallback: str
    ValidityPeriod: int
    MessagingServiceSid: str


class CreateQueueRequest(TypedDict, total=False):
    """Request body for creating a queue.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    FriendlyName: str
    MaxSize: int


class CreateSubprojectRequest(TypedDict, total=False):
    """Request body for creating a subproject.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    FriendlyName: str


class CreateTokenRequest(TypedDict, total=False):
    """Request body for creating an API token.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    permissions: list[str]
    subproject_id: str


class CxmlScript(TypedDict, total=False):
    """cXML Script model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    date_created: str
    date_updated: str
    date_last_accessed: str | None
    account_sid: str
    name: str
    contents: str
    request_url: str
    num_requests: int
    api_version: str
    uri: str


class CxmlScriptListResponse(TypedDict, total=False):
    """Response containing a list of cXML scripts.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    laml_bins: list[CxmlScript]


class CxmlScriptResponse(TypedDict, total=False):
    """Response containing a single cXML script.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    date_created: str
    date_updated: str
    date_last_accessed: str | None
    account_sid: str
    name: str
    contents: str
    request_url: str
    num_requests: int
    api_version: str
    uri: str


class Fax(TypedDict, total=False):
    """Fax model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_sid: str
    api_version: str
    date_created: str
    date_updated: str
    direction: FaxDirection
    # non-identifier field 'from': str
    media_url: str | None
    media_sid: str
    num_pages: str | None
    price: str | None
    price_unit: str
    quality: FaxQuality
    sid: str
    status: FaxStatus
    to: str
    duration: int
    links: FaxLinks
    url: str
    error_code: str | None
    error_message: str | None


FaxDirection: TypeAlias = "Literal['inbound', 'outbound']"


class FaxLinks(TypedDict, total=False):
    """Fax links.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    media: str


class FaxListResponse(TypedDict, total=False):
    """Response containing a list of faxes.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    faxes: list[Fax]


class FaxMedia(TypedDict, total=False):
    """Fax media model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_sid: str
    content_type: str
    date_created: str
    date_updated: str
    fax_sid: str
    sid: str
    uri: str
    url: str


class FaxMediaListResponse(TypedDict, total=False):
    """Response containing a list of fax media.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    media: list[FaxMedia]
    fax_media: list[FaxMedia]


class FaxMediaResponse(TypedDict, total=False):
    """Response containing a single fax media.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_sid: str
    content_type: str
    date_created: str
    date_updated: str
    fax_sid: str
    sid: str
    uri: str
    url: str


FaxQuality: TypeAlias = "Literal['standard', 'fine', 'superfine']"


class FaxResponse(TypedDict, total=False):
    """Response containing a single fax.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_sid: str
    api_version: str
    date_created: str
    date_updated: str
    direction: FaxDirection
    # non-identifier field 'from': str
    media_url: str | None
    media_sid: str
    num_pages: str | None
    price: str | None
    price_unit: str
    quality: FaxQuality
    sid: str
    status: FaxStatus
    to: str
    duration: int
    links: FaxLinks
    url: str
    error_code: str | None
    error_message: str | None


FaxStatus: TypeAlias = "Literal['queued', 'processing', 'sending', 'delivered', 'receiving', 'received', 'no-answer', 'busy', 'failed', 'canceled']"


class ImportPhoneNumberRequest(TypedDict, total=False):
    """Request body for importing a phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    number: str
    number_type: NumberType
    capabilities: list[PhoneNumberCapability]


class IncomingPhoneNumber(TypedDict, total=False):
    """Incoming phone number model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_id: str
    account_sid: str
    address_requirements: AddressRequirements
    address_sid: str | None
    api_version: str
    beta: bool
    capabilities: IncomingPhoneNumberCapabilities
    country_code: str
    date_created: str
    date_updated: str
    emergency_address_sid: str | None
    emergency_status: str
    friendly_name: str
    identity_sid: str | None
    origin: PhoneNumberOrigin
    phone_number: str
    sid: str
    sms_application_sid: str | None
    sms_fallback_method: str
    sms_fallback_url: str | None
    sms_method: str
    sms_url: str | None
    status_callback: str | None
    status_callback_method: str
    trunk_sid: str | None
    uri: str
    verification_status: str
    voice_application_sid: str | None
    voice_caller_id_lookup: bool | None
    voice_fallback_method: str
    voice_fallback_url: str | None
    voice_method: str
    voice_url: str | None


class IncomingPhoneNumberCapabilities(TypedDict, total=False):
    """Phone number capabilities.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    voice: bool
    sms: bool
    mms: bool
    fax: bool


class IncomingPhoneNumberListResponse(TypedDict, total=False):
    """Response containing a list of incoming phone numbers.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    incoming_phone_numbers: list[IncomingPhoneNumber]


class IncomingPhoneNumberResponse(TypedDict, total=False):
    """Response containing a single incoming phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_id: str
    account_sid: str
    address_requirements: AddressRequirements
    address_sid: str | None
    api_version: str
    beta: bool
    capabilities: IncomingPhoneNumberCapabilities
    country_code: str
    date_created: str
    date_updated: str
    emergency_address_sid: str | None
    emergency_status: str
    friendly_name: str
    identity_sid: str | None
    origin: PhoneNumberOrigin
    phone_number: str
    sid: str
    sms_application_sid: str | None
    sms_fallback_method: str
    sms_fallback_url: str | None
    sms_method: str
    sms_url: str | None
    status_callback: str | None
    status_callback_method: str
    trunk_sid: str | None
    uri: str
    verification_status: str
    voice_application_sid: str | None
    voice_caller_id_lookup: bool | None
    voice_fallback_method: str
    voice_fallback_url: str | None
    voice_method: str
    voice_url: str | None


class Message(TypedDict, total=False):
    """Message model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_sid: str
    api_version: str
    body: str | None
    num_segments: int
    num_media: int
    date_created: str
    date_sent: str | None
    date_updated: str
    direction: MessageDirection
    error_code: str | None
    error_message: str | None
    # non-identifier field 'from': str
    price: float | None
    price_unit: str
    sid: str
    status: MessageStatus
    to: str
    messaging_service_sid: str | None
    uri: str
    subresource_uris: MessageSubresourceUris


MessageDirection: TypeAlias = (
    "Literal['inbound', 'outbound-api', 'outbound-call', 'outbound-reply']"
)


class MessageListResponse(TypedDict, total=False):
    """Response containing a list of messages.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    messages: list[Message]


class MessageMedia(TypedDict, total=False):
    """Message media model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_sid: str
    content_type: str
    date_created: str
    date_updated: str
    parent_sid: str
    sid: str
    uri: str


class MessageMediaListResponse(TypedDict, total=False):
    """Response containing a list of message media.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    media_list: list[MessageMedia]


class MessageMediaResponse(TypedDict, total=False):
    """Response containing a single message media.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_sid: str
    content_type: str
    date_created: str
    date_updated: str
    parent_sid: str
    sid: str
    uri: str


class MessageResponse(TypedDict, total=False):
    """Response containing a single message.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    account_sid: str
    api_version: str
    body: str | None
    num_segments: int
    num_media: int
    date_created: str
    date_sent: str | None
    date_updated: str
    direction: MessageDirection
    error_code: str | None
    error_message: str | None
    # non-identifier field 'from': str
    price: float | None
    price_unit: str
    sid: str
    status: MessageStatus
    to: str
    messaging_service_sid: str | None
    uri: str
    subresource_uris: MessageSubresourceUris


MessageStatus: TypeAlias = "Literal['queued', 'initiated', 'sent', 'failed', 'delivered', 'undelivered', 'received']"


class MessageSubresourceUris(TypedDict, total=False):
    """Message subresource URIs.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    media: str


NumberType: TypeAlias = "Literal['longcode', 'tollfree']"

ParticipantStatus: TypeAlias = "Literal['completed', 'in-progress']"


class PhoneNumberCapabilities(TypedDict, total=False):
    """Phone number capabilities.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    voice: bool
    SMS: bool
    MMS: bool


PhoneNumberCapability: TypeAlias = "Literal['sms', 'voice', 'fax', 'mms']"

PhoneNumberOrigin: TypeAlias = "Literal['signalwire', 'hosted']"


class Queue(TypedDict, total=False):
    """Queue model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    friendly_name: str
    max_size: int | None
    current_size: int
    average_wait_time: int
    date_created: str
    date_updated: str
    api_version: str
    uri: str


class QueueListResponse(TypedDict, total=False):
    """Response containing a list of queues.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    queues: list[Queue]


class QueueMember(TypedDict, total=False):
    """Queue member model representing a call waiting in a queue.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_sid: str
    account_sid: str
    queue_sid: str
    date_enqueued: str
    position: int
    wait_time: int
    member_type: str
    uri: str


class QueueMemberListResponse(TypedDict, total=False):
    """Response containing a list of queue members.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    queue_members: list[QueueMember]


class QueueMemberResponse(TypedDict, total=False):
    """Response containing a single queue member.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_sid: str
    account_sid: str
    queue_sid: str
    date_enqueued: str
    position: int
    wait_time: int
    member_type: str
    uri: str


class QueueResponse(TypedDict, total=False):
    """Response containing a single queue.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    friendly_name: str
    max_size: int | None
    current_size: int
    average_wait_time: int
    date_created: str
    date_updated: str
    api_version: str
    uri: str


class Recording(TypedDict, total=False):
    """Recording model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    api_version: str
    call_sid: str | None
    conference_sid: str | None
    channel: Literal["1", "2"]
    channels: Literal["1", "2"]
    date_created: str
    date_updated: str
    start_time: str | None
    end_time: str | None
    duration: int
    price: str | None
    price_unit: str
    source: RecordingSource
    status: RecordingStatus
    error_code: str | None
    uri: str
    subresource_uris: RecordingSubresourceUris
    encryption_details: str | None
    trim: str


class RecordingListResponse(TypedDict, total=False):
    """Response containing a list of recordings.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    recordings: list[Recording]


class RecordingResponse(TypedDict, total=False):
    """Response containing a single recording.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    api_version: str
    call_sid: str | None
    conference_sid: str | None
    channel: Literal["1", "2"]
    channels: Literal["1", "2"]
    date_created: str
    date_updated: str
    start_time: str | None
    end_time: str | None
    duration: int
    price: str | None
    price_unit: str
    source: RecordingSource
    status: RecordingStatus
    error_code: str | None
    uri: str
    subresource_uris: RecordingSubresourceUris
    encryption_details: str | None
    trim: str


RecordingSource: TypeAlias = "Literal['DialVerb', 'Conference', 'OutBoundApi', 'Trunking', 'RecordVerb', 'StartCallRecordingApi', 'StartConferenceRecording']"

RecordingStatus: TypeAlias = "Literal['queued', 'in-progress', 'paused', 'resumed', 'completed', 'absent', 'stopped']"


class RecordingSubresourceUris(TypedDict, total=False):
    """Recording subresource URIs.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    transcriptions: str


class SendFaxRequest(TypedDict, total=False):
    """Request body for sending a fax.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    MediaUrl: str
    To: str
    From: str
    Quality: Literal["standard", "fine", "superfine"]
    StatusCallback: str
    StatusCallbackMethod: Literal["GET", "POST"]
    StatusCallbackEvent: list[str]
    StoreMedia: Literal["true", "false"]
    Ttl: int
    SipAuthUsername: str
    SipAuthPassword: str


StreamStatus: TypeAlias = "Literal['queued', 'in-progress', 'stopped']"


class SubresourceUris(TypedDict, total=False):
    """A Map of sub-resources that are linked to the given Project.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    addresses: None
    available_phone_numbers: str
    applications: str
    authorized_connect_apps: None
    calls: str
    conferences: str
    connect_apps: None
    incoming_phone_numbers: str
    keys: None
    notifications: None
    outgoing_caller_ids: None
    queues: str
    recordings: str
    sandbox: None
    sip: None
    short_codes: None
    messages: str
    transcriptions: str
    usage: None


class TokenResponse(TypedDict, total=False):
    """Response containing a single token.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    name: str
    permissions: list[str]
    token: str


class Transcription(TypedDict, total=False):
    """Transcription model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    api_version: str
    recording_sid: str
    date_created: str
    date_updated: str
    duration: int
    price: str | None
    price_unit: str
    status: str
    transcription_text: str | None
    type: str
    uri: str


class TranscriptionListResponse(TypedDict, total=False):
    """Response containing a list of transcriptions.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    uri: str
    first_page_uri: str
    next_page_uri: str | None
    previous_page_uri: str | None
    page: int
    page_size: int
    transcriptions: list[Transcription]


class TranscriptionResponse(TypedDict, total=False):
    """Response containing a single transcription.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    sid: str
    account_sid: str
    api_version: str
    recording_sid: str
    date_created: str
    date_updated: str
    duration: int
    price: str | None
    price_unit: str
    status: str
    transcription_text: str | None
    type: str
    uri: str


class UpdateAccountRequest(TypedDict, total=False):
    """Request body for updating an account.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    FriendlyName: str


class UpdateApplicationRequest(TypedDict, total=False):
    """Request body for updating an application.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    FriendlyName: str
    VoiceUrl: str
    VoiceMethod: Literal["GET", "POST"]
    VoiceFallbackUrl: str
    VoiceFallbackMethod: Literal["GET", "POST"]
    StatusCallback: str
    StatusCallbackMethod: Literal["GET", "POST"]
    SmsUrl: str
    SmsMethod: Literal["GET", "POST"]
    SmsFallbackUrl: str
    SmsFallbackMethod: Literal["GET", "POST"]
    SmsStatusCallback: str
    SmsStatusCallbackMethod: Literal["GET", "POST"]


class UpdateCallRecordingRequest(TypedDict, total=False):
    """Request body for updating a call recording.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Status: Literal["paused", "in-progress", "stopped"]
    PauseBehavior: Literal["skip", "silence"]


class UpdateCallRequest(TypedDict, total=False):
    """Request body for updating a call.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Url: str
    Method: Literal["GET", "POST"]
    Status: Literal["canceled", "completed"]
    FallbackUrl: str
    FallbackMethod: Literal["GET", "POST"]
    StatusCallback: str
    StatusCallbackMethod: Literal["GET", "POST"]


class UpdateCallStreamRequest(TypedDict, total=False):
    """Request body for updating a call stream.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Status: Literal["stopped"]


class UpdateConferenceParticipantRequest(TypedDict, total=False):
    """Request body for updating a conference participant.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    AnnounceUrl: str
    AnnounceMethod: Literal["GET", "POST"]
    Coaching: bool
    CallSidToCoach: str
    Hold: bool
    HoldMethod: Literal["GET", "POST"]
    HoldUrl: str
    Muted: bool
    WaitUrl: str
    WaitMethod: Literal["GET", "POST"]


class UpdateConferenceRecordingRequest(TypedDict, total=False):
    """Request body for updating a conference recording.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Status: Literal["paused", "in-progress", "stopped"]
    PauseBehavior: Literal["skip", "silence"]


class UpdateConferenceRequest(TypedDict, total=False):
    """Request body for updating a conference.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Status: Literal["completed"]
    AnnounceUrl: str
    AnnounceMethod: Literal["GET", "POST"]


class UpdateConferenceStreamRequest(TypedDict, total=False):
    """Request body for updating a conference stream.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Status: Literal["stopped"]


class UpdateCxmlScriptRequest(TypedDict, total=False):
    """Request body for updating a cXML script.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Name: str
    Contents: str


class UpdateFaxRequest(TypedDict, total=False):
    """Request body for updating (canceling) a fax.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Status: Literal["canceled"]


class UpdateIncomingPhoneNumberRequest(TypedDict, total=False):
    """Request body for updating an incoming phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    AccountSid: str
    EmergencyAddressSid: str
    FriendlyName: str
    SmsApplicationSid: str
    SmsFallbackMethod: Literal["GET", "POST"]
    SmsFallbackUrl: str
    SmsMethod: Literal["GET", "POST"]
    SmsUrl: str
    StatusCallback: str
    StatusCallbackMethod: Literal["GET", "POST"]
    VoiceApplicationSid: str
    VoiceFallbackMethod: Literal["GET", "POST"]
    VoiceFallbackUrl: str
    VoiceMethod: Literal["GET", "POST"]
    VoiceReceiveMode: Literal["voice", "fax"]
    VoiceUrl: str


class UpdateMessageRequest(TypedDict, total=False):
    """Request body for updating (redacting) a message.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Body: str


class UpdateQueueMemberRequest(TypedDict, total=False):
    """Request body for dequeuing a queue member.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    Url: str
    Method: Literal["GET", "POST"]


class UpdateQueueRequest(TypedDict, total=False):
    """Request body for updating a queue.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    FriendlyName: str
    MaxSize: int


class UpdateTokenRequest(TypedDict, total=False):
    """Request body for updating an API token.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    permissions: list[str]


ListAccountsResponse: TypeAlias = "AccountListResponse"
CreateSubprojectsRequest: TypeAlias = "CreateSubprojectRequest"
CreateSubprojectsResponse: TypeAlias = "Account"
ListApplicationsResponse: TypeAlias = "ApplicationListResponse"
CreateApplicationResponse: TypeAlias = "Application"
GetApplicationResponse: TypeAlias = "ApplicationResponse"
UpdateApplicationResponse: TypeAlias = "ApplicationResponse"
ListAvailablePhoneNumberResourcesResponse: TypeAlias = (
    "AvailablePhoneNumberResourcesResponse"
)
ListAvailablePhoneNumberResourcesByCountryResponse: TypeAlias = (
    "AvailablePhoneNumberByCountryResponse"
)
SearchLocalAvailablePhoneNumbersResponse: TypeAlias = "AvailablePhoneNumberListResponse"
SearchTollFreeAvailablePhoneNumbersResponse: TypeAlias = (
    "AvailablePhoneNumberListResponse"
)
ListAllCallsResponse: TypeAlias = "CallListResponse"
CreateACallRequest: TypeAlias = "CreateCallRequest"
CreateACallResponse: TypeAlias = "CallResponse"
CreateRecordingRequest: TypeAlias = "CreateCallRecordingRequest"
CreateRecordingResponse: TypeAlias = "CallRecordingResponse"
UpdateRecordingRequest: TypeAlias = "UpdateCallRecordingRequest"
UpdateRecordingResponse: TypeAlias = "CallRecordingResponse"
CreateStreamRequest: TypeAlias = "CreateCallStreamRequest"
CreateStreamResponse: TypeAlias = "CallStreamResponse"
UpdateStreamRequest: TypeAlias = "UpdateCallStreamRequest"
UpdateStreamResponse: TypeAlias = "CallStreamResponse"
RetrieveACallResponse: TypeAlias = "CallResponse"
UpdateACallRequest: TypeAlias = "UpdateCallRequest"
UpdateACallResponse: TypeAlias = "CallResponse"
ListAllConferencesResponse: TypeAlias = "ConferenceListResponse"
ListAllParticipantsResponse: TypeAlias = "ConferenceParticipantListResponse"
RetrieveParticipantResponse: TypeAlias = "ConferenceParticipantResponse"
UpdateParticipantRequest: TypeAlias = "UpdateConferenceParticipantRequest"
UpdateParticipantResponse: TypeAlias = "ConferenceParticipantResponse"
ListConferenceRecordingsResponse: TypeAlias = "ConferenceRecordingListResponse"
GetConferenceRecordingResponse: TypeAlias = "ConferenceRecordingResponse"
UpdateConferenceRecordingResponse: TypeAlias = "ConferenceRecordingResponse"
CreateConferenceStreamResponse: TypeAlias = "ConferenceStreamResponse"
UpdateConferenceStreamResponse: TypeAlias = "ConferenceStreamResponse"
RetrieveConferenceResponse: TypeAlias = "ConferenceResponse"
UpdateConferenceResponse: TypeAlias = "ConferenceResponse"
ListAllFaxesResponse: TypeAlias = "FaxListResponse"
SendFaxResponse: TypeAlias = "FaxResponse"
ListAllFaxMediaResponse: TypeAlias = "FaxMediaListResponse"
RetrieveMediasResponse: TypeAlias = "FaxMediaResponse"
RetrieveFaxResponse: TypeAlias = "FaxResponse"
UpdateFaxResponse: TypeAlias = "FaxResponse"
CreateImportedPhoneNumberRequest: TypeAlias = "ImportPhoneNumberRequest"
CreateImportedPhoneNumberResponse: TypeAlias = "IncomingPhoneNumber"
ListIncomingPhoneNumbersResponse: TypeAlias = "IncomingPhoneNumberListResponse"
CreateIncomingPhoneNumberResponse: TypeAlias = "IncomingPhoneNumber"
RetrieveIncomingPhoneNumberResponse: TypeAlias = "IncomingPhoneNumberResponse"
UpdateIncomingPhoneNumberResponse: TypeAlias = "IncomingPhoneNumberResponse"
ListCxmlScriptsResponse: TypeAlias = "CxmlScriptListResponse"
CreateCxmlScriptResponse: TypeAlias = "CxmlScript"
RetrieveCxmlScriptResponse: TypeAlias = "CxmlScriptResponse"
UpdateCxmlScriptResponse: TypeAlias = "CxmlScriptResponse"
ListMessagesResponse: TypeAlias = "MessageListResponse"
CreateMessageResponse: TypeAlias = "Message"
ListMediaResponse: TypeAlias = "MessageMediaListResponse"
RetrieveMediaResponse: TypeAlias = "MessageMediaResponse"
RetrieveMessageResponse: TypeAlias = "MessageResponse"
UpdateMessageResponse: TypeAlias = "MessageResponse"
ListQueuesResponse: TypeAlias = "QueueListResponse"
CreateQueueResponse: TypeAlias = "Queue"
ListAllQueueMembersResponse: TypeAlias = "QueueMemberListResponse"
RetrieveQueueMemberResponse: TypeAlias = "QueueMemberResponse"
UpdateQueueMemberResponse: TypeAlias = "QueueMemberResponse"
RetrieveQueueResponse: TypeAlias = "QueueResponse"
UpdateQueueResponse: TypeAlias = "QueueResponse"
ListRecordingsResponse: TypeAlias = "RecordingListResponse"
RetrieveRecordingResponse: TypeAlias = "RecordingResponse"
ListTranscriptionsResponse: TypeAlias = "TranscriptionListResponse"
RetrieveTranscriptionResponse: TypeAlias = "TranscriptionResponse"
CreateTokenResponse: TypeAlias = "TokenResponse"
UpdateTokenResponse: TypeAlias = "TokenResponse"
GetAccountResponse: TypeAlias = "AccountResponse"
UpdateAccountResponse: TypeAlias = "AccountResponse"
