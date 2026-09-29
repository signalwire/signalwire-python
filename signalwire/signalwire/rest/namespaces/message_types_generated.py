# AUTO-GENERATED from porting-sdk/rest-apis/message/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Any, Literal, TypeAlias, TypedDict


class ChargeDetail(TypedDict, total=False):
    """Details on charges associated with this log.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    description: str
    charge: float


class LogListResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    links: LogPaginationResponse
    data: list[MessageLog]


class LogPaginationResponse(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    self: str
    first: str
    next: str
    prev: str


LogRetrieveResponse = TypedDict(
    "LogRetrieveResponse",
    {
        "id": "uuid",
        "from": "str",
        "to": "str",
        "status": "Literal['queued', 'initiated', 'delivered', 'sent', 'received', 'undelivered', 'failed']",
        "direction": "Literal['inbound', 'outbound', 'outbound-api', 'outbound-call', 'outbound-reply']",
        "kind": "Literal['sms', 'mms']",
        "source": "Literal['realtime_api', 'laml']",
        "type": "Literal['relay_message', 'laml_message']",
        "url": "str | None",
        "number_of_segments": "int",
        "charge": "float",
        "charge_details": "list[ChargeDetail]",
        "created_at": "str",
    },
    total=False,
)
LogRetrieveResponse.__doc__ = """Response model for message log retrieve endpoint

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""

MessageLog = TypedDict(
    "MessageLog",
    {
        "id": "uuid",
        "from": "str",
        "to": "str",
        "status": "Literal['queued', 'initiated', 'delivered', 'sent', 'received', 'undelivered', 'failed']",
        "direction": "Literal['inbound', 'outbound', 'outbound-api', 'outbound-call', 'outbound-reply']",
        "kind": "Literal['sms', 'mms']",
        "source": "Literal['realtime_api', 'laml']",
        "type": "Literal['relay_message', 'laml_message']",
        "url": "str | None",
        "number_of_segments": "int",
        "charge": "float",
        "charge_details": "list[ChargeDetail]",
        "created_at": "str",
    },
    total=False,
)
MessageLog.__doc__ = """Message log entry with all activity details

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""


class MessageLogShowStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class MessageLogsListStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class Types_StatusCodes_RestApiErrorItem(TypedDict, total=False):
    """Details about a specific error.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: str
    code: str
    message: str
    attribute: str | None
    url: str


class Types_StatusCodes_StatusCode400(TypedDict, total=False):
    """The request is invalid.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Bad Request"]


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Unauthorized"]


class Types_StatusCodes_StatusCode404(TypedDict, total=False):
    """The server cannot find the requested resource.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Not Found"]


class Types_StatusCodes_StatusCode500(TypedDict, total=False):
    """An internal server error occurred.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    error: Literal["Internal Server Error"]


class WhatsappBusiness(TypedDict, total=False):
    """A WhatsApp Business Account (WABA) connected to your SignalWire Space. Each business account can have its own set of phone numbers and message templates.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    whatsapp_business_id: uuid
    business_name: str | None
    business_portfolio_id: str | None
    waba_id: str
    created_at: str
    updated_at: str


class WhatsappBusinessListResponse(TypedDict, total=False):
    """Response containing a list of WhatsApp Business Accounts.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    data: list[WhatsappBusiness]


class WhatsappNumber(TypedDict, total=False):
    """A WhatsApp phone number connected to your Space. Numbers are linked during the Meta embedded signup flow and used as the `from` address when sending messages.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    business_phone_number_id: str | None
    phone_number: str | None
    calling_handler_resource_id: uuid | None
    messaging_handler_resource_id: uuid | None
    business_name: str | None
    waba_id: str
    whatsapp_business_id: uuid
    voice_enabled: bool
    voice_capable: bool
    created_at: str
    updated_at: str


class WhatsappNumberListResponse(TypedDict, total=False):
    """Response containing a list of WhatsApp numbers.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    data: list[WhatsappNumber]


WhatsappTemplateCategory: TypeAlias = (
    "Literal['utility', 'marketing', 'authentication']"
)

WhatsappTemplateParameterFormat: TypeAlias = "Literal['named', 'positional']"

WhatsappTemplateStatus: TypeAlias = "Literal['approved', 'archived', 'deleted', 'disabled', 'flagged', 'in_appeal', 'limit_exceeded', 'locked', 'paused', 'pending', 'reinstated', 'pending_deletion', 'rejected']"

WhatsappTemplateComponent: TypeAlias = "dict[str, Any]"


class WhatsappTemplate(TypedDict, total=False):
    """A WhatsApp message template.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    name: str
    category: WhatsappTemplateCategory
    components: list[WhatsappTemplateComponent]
    language: str
    parameter_format: WhatsappTemplateParameterFormat
    template_id: str | None
    template_status: WhatsappTemplateStatus | None
    whatsapp_business_id: uuid
    created_at: str
    updated_at: str
    discarded_at: str


class WhatsappTemplateListResponse(TypedDict, total=False):
    """Response containing a list of message templates.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    data: list[WhatsappTemplate]


class CreateWhatsappTemplateRequest(TypedDict, total=False):
    """Request body for creating a message template.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    whatsapp_business_id: uuid
    name: str
    language: str
    category: WhatsappTemplateCategory
    parameter_format: WhatsappTemplateParameterFormat
    components: list[WhatsappTemplateComponent]


class UpdateWhatsappTemplateRequest(TypedDict, total=False):
    """Request body for updating a template. Provide `category`, `components`, or both. A template can only be updated while it is not yet approved.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    category: WhatsappTemplateCategory
    components: list[WhatsappTemplateComponent]


class WhatsappTemplateDeleteResponse(TypedDict, total=False):
    """Response returned when a template has been deleted.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    success: bool
    errors: dict[str, Any]


class WhatsappStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class WhatsappTemplateErrorItem(TypedDict, total=False):
    """Details about a specific error.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    detail: str
    status: Literal["422"]
    title: str
    code: str
    subcode: str


class WhatsappTemplateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[WhatsappTemplateErrorItem]


uuid: TypeAlias = "str"

ListMessageLogsResponse: TypeAlias = "LogListResponse"
GetMessageLogResponse: TypeAlias = "LogRetrieveResponse"
ListWhatsappNumbersResponse: TypeAlias = "WhatsappNumberListResponse"
RetrieveWhatsappNumberResponse: TypeAlias = "WhatsappNumber"
ListWhatsappBusinessesResponse: TypeAlias = "WhatsappBusinessListResponse"
ListWhatsappTemplatesResponse: TypeAlias = "WhatsappTemplateListResponse"
CreateWhatsappTemplateResponse: TypeAlias = "WhatsappTemplate"
RetrieveWhatsappTemplateResponse: TypeAlias = "WhatsappTemplate"
UpdateWhatsappTemplateResponse: TypeAlias = "WhatsappTemplate"
DeleteWhatsappTemplateResponse: TypeAlias = "WhatsappTemplateDeleteResponse"
