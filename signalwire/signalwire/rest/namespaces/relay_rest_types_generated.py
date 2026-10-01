# AUTO-GENERATED from porting-sdk/rest-apis/relay-rest/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from enum import Enum
from typing import Any, Literal, TypeAlias, TypedDict


class AddNumberGroupMembershipRequest(TypedDict, total=False):
    """Request body for adding a phone number to a number group.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    phone_number_id: uuid


class Address(TypedDict, total=False):
    """Address model representing a physical address for regulatory compliance.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    label: str
    country: str
    first_name: str
    last_name: str
    street_number: str
    street_name: str
    address_type: AddressType | None
    address_number: str | None
    city: str
    state: str
    postal_code: str
    zip_code: str
    emergency_enabled: bool
    validated: bool
    validated_at: str | None


AddressCountryCode: TypeAlias = "Literal['AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AW', 'AX', 'AZ', 'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ', 'BR', 'BS', 'BT', 'BV', 'BW', 'BY', 'BZ', 'CA', 'CC', 'CD', 'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 'CO', 'CR', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'EH', 'ER', 'ES', 'ET', 'FI', 'FJ', 'FK', 'FM', 'FO', 'FR', 'GA', 'GB', 'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 'GS', 'GT', 'GU', 'GW', 'GY', 'HK', 'HM', 'HN', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IM', 'IN', 'IO', 'IQ', 'IR', 'IS', 'IT', 'JE', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KP', 'KR', 'KW', 'KY', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MF', 'MG', 'MH', 'MK', 'ML', 'MM', 'MN', 'MO', 'MP', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 'NC', 'NE', 'NF', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG', 'PH', 'PK', 'PL', 'PM', 'PN', 'PR', 'PS', 'PT', 'PW', 'PY', 'QA', 'RE', 'RO', 'RS', 'RU', 'RW', 'SA', 'SB', 'SC', 'SD', 'SE', 'SG', 'SH', 'SI', 'SJ', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'SS', 'ST', 'SV', 'SX', 'SY', 'SZ', 'TC', 'TD', 'TF', 'TG', 'TH', 'TJ', 'TK', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'UM', 'US', 'UY', 'UZ', 'VA', 'VC', 'VE', 'VG', 'VI', 'VN', 'VU', 'WF', 'WS', 'YE', 'YT', 'ZA', 'ZM', 'ZW']"


class AddressListResponse(TypedDict, total=False):
    """Response containing a list of addresses.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[Address]


class AddressResponse(TypedDict, total=False):
    """Response containing a single address.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    label: str
    country: str
    first_name: str
    last_name: str
    street_number: str
    street_name: str
    address_type: AddressType | None
    address_number: str | None
    city: str
    state: str
    postal_code: str
    zip_code: str
    emergency_enabled: bool
    validated: bool
    validated_at: str | None


AddressType: TypeAlias = "Literal['Apartment', 'Basement', 'Building', 'Department', 'Floor', 'Office', 'Penthouse', 'Suite', 'Trailer', 'Unit']"


class AssignedNumber(TypedDict, total=False):
    """Assigned number model for campaign registration.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    state: str
    campaign_id: uuid
    phone_number: AssignedPhoneNumber
    status_callback_url: str | None
    created_at: str
    updated_at: str


class AssignedNumberListResponse(TypedDict, total=False):
    """Response containing a list of assigned numbers.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[AssignedNumber]


class AssignedPhoneNumber(TypedDict, total=False):
    """Phone number details in an assignment.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    name: str
    number: str


class AvailablePhoneNumber(TypedDict, total=False):
    """Available phone number for purchase.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    region: str
    rate_center: str
    capabilities: list[PhoneNumberCapability]
    e164: str
    national_number_formatted: str | None
    international_number_formatted: str | None
    country_code: str | None


class AvailablePhoneNumbersResponse(TypedDict, total=False):
    """Response containing available phone numbers for purchase.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: dict[str, Any]
    data: list[AvailablePhoneNumber]


class Brand(TypedDict, total=False):
    """Brand model for 10DLC registration.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    state: str
    name: str
    company_name: str | None
    contact_email: str | None
    contact_phone: str | None
    ein_issuing_country: str | None
    legal_entity_type: str | None
    ein: str | None
    company_address: str | None
    company_vertical: str | None
    csp_brand_reference: str | None
    csp_self_registered: bool
    status_callback_url: str | None
    created_at: str
    updated_at: str
    signalwire_contact_emails: list[str]
    large_message_limit: str | None
    number_pooling_for_company: str | None


class BrandListResponse(TypedDict, total=False):
    """Response containing a list of brands.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[Brand]


class BrandResponse(TypedDict, total=False):
    """Response containing a single brand.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    state: str
    name: str
    company_name: str | None
    contact_email: str | None
    contact_phone: str | None
    ein_issuing_country: str | None
    legal_entity_type: str | None
    ein: str | None
    company_address: str | None
    company_vertical: str | None
    csp_brand_reference: str | None
    csp_self_registered: bool
    status_callback_url: str | None
    created_at: str
    updated_at: str
    signalwire_contact_emails: list[str]
    large_message_limit: str | None
    number_pooling_for_company: str | None


CallReceiveMode: TypeAlias = "Literal['voice', 'fax', 'none']"


class Campaign(TypedDict, total=False):
    """Campaign model for 10DLC registration.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    name: str
    state: str
    sms_use_case: str | None
    sub_use_cases: list[str]
    campaign_verify_token: str | None
    description: str | None
    sample1: str | None
    sample2: str | None
    sample3: str | None
    sample4: str | None
    sample5: str | None
    message_flow: str | None
    opt_in_message: str | None
    opt_out_message: str | None
    help_message: str | None
    opt_in_keywords: str | None
    opt_out_keywords: str | None
    help_keywords: str | None
    number_pooling_per_campaign: str | None
    direct_lending: bool | None
    embedded_link: bool | None
    embedded_phone: bool | None
    age_gated_content: bool | None
    lead_generation: bool | None
    csp_campaign_reference: str | None
    status_callback_url: str | None
    created_at: str
    updated_at: str
    dynamic_messages: str | None
    requested_throughput: str | None
    daily_messages_per_number: str | None
    privacy_policy_link: str | None
    purchase_or_port_numbers: str | None
    signalwire_contact_emails: list[str]


class CampaignListResponse(TypedDict, total=False):
    """Response containing a list of campaigns.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[Campaign]


class CampaignResponse(TypedDict, total=False):
    """Response containing a single campaign.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    name: str
    state: str
    sms_use_case: str | None
    sub_use_cases: list[str]
    campaign_verify_token: str | None
    description: str | None
    sample1: str | None
    sample2: str | None
    sample3: str | None
    sample4: str | None
    sample5: str | None
    message_flow: str | None
    opt_in_message: str | None
    opt_out_message: str | None
    help_message: str | None
    opt_in_keywords: str | None
    opt_out_keywords: str | None
    help_keywords: str | None
    number_pooling_per_campaign: str | None
    direct_lending: bool | None
    embedded_link: bool | None
    embedded_phone: bool | None
    age_gated_content: bool | None
    lead_generation: bool | None
    csp_campaign_reference: str | None
    status_callback_url: str | None
    created_at: str
    updated_at: str
    dynamic_messages: str | None
    requested_throughput: str | None
    daily_messages_per_number: str | None
    privacy_policy_link: str | None
    purchase_or_port_numbers: str | None
    signalwire_contact_emails: list[str]


class CarrierLookupInfo(TypedDict, total=False):
    """Carrier lookup information.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    lrn: str
    spid: str
    ocn: str
    lata: str
    city: str
    state: str
    jurisdiction: str
    lec: str
    linetype: str
    dnc: str | None


class CnamInfo(TypedDict, total=False):
    """Caller ID (CNAM) information.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    caller_id: str


CompanyVertical: TypeAlias = "Literal['AGRICULTURE', 'COMMUNICATION', 'CONSTRUCTION', 'EDUCATION', 'ENERGY', 'ENTERTAINMENT', 'FINANCIAL', 'GAMBLING', 'GOVERNMENT', 'HEALTHCARE', 'HOSPITALITY', 'HUMAN_RESOURCES', 'INSURANCE', 'LEGAL', 'MANUFACTURING', 'NGO', 'POLITICAL', 'POSTAL', 'PROFESSIONAL', 'REAL_ESTATE', 'RETAIL', 'TECHNOLOGY', 'TRANSPORTATION']"


class CreateAddressRequest(TypedDict, total=False):
    """Request body for creating an address.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    label: str
    country: AddressCountryCode
    first_name: str
    last_name: str
    street_number: str
    street_name: str
    address_type: AddressType
    address_number: str
    city: str
    state: str
    postal_code: str
    emergency_enabled: bool
    auto_correct_address: bool


class CreateCspBrandRequest(TypedDict, total=False):
    """Request body for importing a self-registered CSP brand. Use this when you have already registered your brand directly with TCR.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    csp_self_registered: Literal[True]
    name: str
    csp_brand_reference: str
    status_callback_url: str
    signalwire_contact_emails: list[str] | str


class CreateDomainApplicationRequest(TypedDict, total=False):
    """Request body for creating a domain application.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    identifier: str
    user: str
    ip_auth_enabled: bool
    ip_auth: list[str]
    encryption: Literal["optional", "required", "forbidden"]
    codecs: list[str]
    ciphers: list[str]
    call_handler: DomainAppCallHandlerRequest
    call_relay_topic: str
    call_relay_topic_status_callback_url: str
    call_relay_application: str
    call_request_url: str
    call_request_method: Literal["GET", "POST"]
    call_fallback_url: str
    call_fallback_method: Literal["GET", "POST"]
    call_status_callback_url: str
    call_status_callback_method: Literal["GET", "POST"]
    call_laml_application_id: str
    call_video_room_id: uuid
    call_relay_script_url: str
    call_relay_script_url_method: str
    call_dialogflow_agent_id: uuid
    call_ai_agent_id: uuid
    call_flow_id: uuid
    call_flow_version: Literal["working_copy"]
    call_relay_context: str
    call_relay_context_status_callback_url: str


class CreateManagedBrandRequest(TypedDict, total=False):
    """Request body for registering a new managed brand for 10DLC registration.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    company_name: str
    contact_email: str
    contact_phone: str
    ein_issuing_country: str
    legal_entity_type: LegalEntityType
    ein: str
    company_address: str
    company_vertical: CompanyVertical
    company_website: str
    status_callback_url: str
    csp_brand_reference: str
    signalwire_contact_emails: list[str] | str


class CreateManagedCampaignRequest(TypedDict, total=False):
    """Request body for creating a managed campaign. Used when the brand is a managed (non-CSP) brand.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    sms_use_case: Literal[
        "2FA",
        "ACCOUNT_NOTIFICATION",
        "AGENTS_FRANCHISES",
        "CARRIER_EXEMPT",
        "CHARITY",
        "CUSTOMER_CARE",
        "DELIVERY_NOTIFICATION",
        "EMERGENCY",
        "FRAUD_ALERT",
        "HIGHER_EDUCATION",
        "K12_EDUCATION",
        "LOW_VOLUME_MIXED",
        "MARKETING",
        "MIXED",
        "POLITICAL",
        "POLITICAL_SECTION_527",
        "POLLING_VOTING",
        "PROXY",
        "PUBLIC_SERVICE_ANNOUNCEMENT",
        "SECURITY_ALERT",
        "SOCIAL",
        "SWEEPSTAKE",
        "TRIAL",
        "UCAAS_HIGH",
        "UCAAS_LOW",
    ]
    sub_use_cases: list[str]
    campaign_verify_token: str
    description: str
    sample1: str
    sample2: str
    sample3: str
    sample4: str
    sample5: str
    dynamic_messages: str
    message_flow: str
    opt_in_message: str
    opt_out_message: str
    help_message: str
    opt_in_keywords: str
    opt_out_keywords: str
    help_keywords: str
    number_pooling_required: bool
    number_pooling_per_campaign: str
    direct_lending: bool
    embedded_link: bool
    embedded_phone: bool
    age_gated_content: bool
    lead_generation: bool
    terms_and_conditions: bool
    status_callback_url: str
    csp_campaign_reference: str
    signalwire_contact_emails: list[str] | str


class CreateNumberGroupRequest(TypedDict, total=False):
    """Request body for creating a number group.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    sticky_sender: bool


class CreateOrderRequest(TypedDict, total=False):
    """Request body for creating an order.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    phone_numbers: list[str]
    status_callback_url: str


class CreatePartnerCampaignRequest(TypedDict, total=False):
    """Request body for creating a partner/CSP campaign. Used when the brand is a CSP (self-registered) brand.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    csp_campaign_reference: str
    status_callback_url: str
    signalwire_contact_emails: list[str] | str


class CreateQueueRequest(TypedDict, total=False):
    """Request body for creating a queue.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    max_size: int


class CreateSipEndpointRequest(TypedDict, total=False):
    """Request body for creating a SIP endpoint.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    username: str
    password: str
    caller_id: str
    send_as: str
    ciphers: list[str]
    codecs: list[str]
    encryption: Literal["default", "required", "optional"]
    call_handler: Literal[
        "default",
        "passthrough",
        "block-pstn",
        "relay_context",
        "relay_topic",
        "relay_application",
        "relay_connector",
        "relay_script",
        "laml_webhooks",
        "laml_webhook",
        "laml_application",
        "dialogflow",
        "video_room",
        "call_flow",
        "ai_agent",
    ]
    call_request_url: str
    call_request_method: Literal["GET", "POST"]
    call_fallback_url: str
    call_fallback_method: Literal["GET", "POST"]
    call_status_callback_url: str
    call_status_callback_method: Literal["GET", "POST"]
    call_laml_application_id: str
    call_dialogflow_agent_id: str
    call_relay_topic: str
    call_relay_topic_status_callback_url: str
    call_relay_context: str
    call_relay_context_status_callback_url: str
    call_relay_application: str
    call_video_room_id: str
    call_flow_id: str
    call_flow_version: str
    call_ai_agent_id: str
    call_relay_script_url: str
    call_relay_script_url_method: str


class CreateVerifiedCallerIDRequest(TypedDict, total=False):
    """Request body for creating a verified caller ID.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    number: str
    name: str
    extension: str


DomainAppCallHandler: TypeAlias = "Literal['relay_topic', 'relay_application', 'laml_webhooks', 'laml_application', 'video_room', 'relay_script', 'dialogflow', 'ai_agent', 'call_flow', 'relay_context', 'relay_connector', 'fabric_subscriber', 'sip_gateway', 'call_queue']"

DomainAppCallHandlerRequest: TypeAlias = "Literal['relay_topic', 'relay_application', 'laml_webhooks', 'laml_application', 'video_room', 'relay_script', 'dialogflow', 'ai_agent', 'call_flow', 'relay_context']"


class DomainApplication(TypedDict, total=False):
    """Domain application model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    type: str
    domain: str
    name: str | None
    identifier: str
    user: str
    ip_auth_enabled: bool
    ip_auth: list[str]
    call_handler: DomainAppCallHandler | None
    calling_handler_resource_id: uuid | None
    call_relay_topic: str | None
    call_relay_topic_status_callback_url: str | None
    call_relay_context: str | None
    call_relay_context_status_callback_url: str | None
    call_request_url: str | None
    call_request_method: str | None
    call_fallback_url: str | None
    call_fallback_method: str | None
    call_status_callback_url: str | None
    call_status_callback_method: str | None
    call_laml_application_id: str | None
    call_video_room_id: uuid | None
    call_relay_script_url: str | None
    encryption: Literal["optional", "required", "forbidden"]
    codecs: list[str]
    ciphers: list[str]


class DomainApplicationListResponse(TypedDict, total=False):
    """Response containing a list of domain applications.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[DomainApplication]


class DomainApplicationResponse(TypedDict, total=False):
    """Response containing a single domain application.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    type: str
    domain: str
    name: str | None
    identifier: str
    user: str
    ip_auth_enabled: bool
    ip_auth: list[str]
    call_handler: DomainAppCallHandler | None
    calling_handler_resource_id: uuid | None
    call_relay_topic: str | None
    call_relay_topic_status_callback_url: str | None
    call_relay_context: str | None
    call_relay_context_status_callback_url: str | None
    call_request_url: str | None
    call_request_method: str | None
    call_fallback_url: str | None
    call_fallback_method: str | None
    call_status_callback_url: str | None
    call_status_callback_method: str | None
    call_laml_application_id: str | None
    call_video_room_id: uuid | None
    call_relay_script_url: str | None
    encryption: Literal["optional", "required", "forbidden"]
    codecs: list[str]
    ciphers: list[str]


HttpMethod: TypeAlias = "Literal['GET', 'POST']"


class ImportPhoneNumberRequest(TypedDict, total=False):
    """Request body for importing a phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    number: str
    number_type: Literal["longcode", "tollfree"]
    capabilities: list[Literal["sms", "voice", "fax", "mms"]]


LegalEntityType: TypeAlias = (
    "Literal['PRIVATE_PROFIT', 'PUBLIC_PROFIT', 'NON_PROFIT', 'GOVERNMENT']"
)


class MembershipPhoneNumber(TypedDict, total=False):
    """Phone number representation within a membership.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    name: str
    number: str
    capabilities: list[str]


MfaRequest = TypedDict(
    "MfaRequest",
    {
        "to": "str",
        "from": "str",
        "message": "str",
        "token_length": "int",
        "valid_for": "int",
        "max_attempts": "int",
        "allow_alphas": "bool",
    },
    total=False,
)
MfaRequest.__doc__ = """MFA request model.

Open shape: extra server keys are permitted and partial payloads are valid;
not validated at runtime (a TypedDict is a plain ``dict``).
"""


class MfaResponse(TypedDict, total=False):
    """MFA response model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    success: bool
    to: str
    channel: str


class MfaVerifyRequest(TypedDict, total=False):
    """MFA verification request model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    token: str


class MfaVerifyResponse(TypedDict, total=False):
    """MFA verification response model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    success: bool


class NumberGroup(TypedDict, total=False):
    """Number group model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    name: str
    sticky_sender: bool
    phone_number_count: int


class NumberGroupListResponse(TypedDict, total=False):
    """Response containing a list of number groups.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[NumberGroup]


class NumberGroupMembership(TypedDict, total=False):
    """Number group membership model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    number_group_id: uuid
    phone_number: MembershipPhoneNumber
    created_at: str
    updated_at: str


class NumberGroupMembershipListResponse(TypedDict, total=False):
    """Response containing a list of number group memberships.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[NumberGroupMembership]


class NumberGroupMembershipResponse(TypedDict, total=False):
    """Response containing a single number group membership.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    number_group_id: uuid
    phone_number: MembershipPhoneNumber
    created_at: str
    updated_at: str


class NumberGroupResponse(TypedDict, total=False):
    """Response containing a single number group.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    name: str
    sticky_sender: bool
    phone_number_count: int


class Order(TypedDict, total=False):
    """Order model for campaign registry operations.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    state: str
    processed_at: str
    created_at: str
    updated_at: str
    status_callback_url: str | None
    campaign_id: str
    brand_id: str
    phone_numbers: list[dict[str, Any]]


class OrderListResponse(TypedDict, total=False):
    """Response containing a list of orders.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[Order]


class OrderResponse(TypedDict, total=False):
    """Response containing a single order.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    state: str
    processed_at: str
    created_at: str
    updated_at: str
    status_callback_url: str | None
    campaign_id: str
    brand_id: str
    phone_numbers: list[dict[str, Any]]


class PaginationLinks(TypedDict, total=False):
    """Pagination links for list responses.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    self: str
    first: str
    next: str
    prev: str


class PhoneNumber(TypedDict, total=False):
    """Phone number model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    number: str
    name: str | None
    capabilities: list[PhoneNumberCapability]
    number_type: PhoneNumberType
    e911_address_id: uuid | None
    e911_status: PhoneNumberE911Status | None
    cnam: str | None
    created_at: str
    updated_at: str
    next_billed_at: str | None
    call_handler: PhoneNumberCallHandler
    calling_handler_resource_id: uuid | None
    call_receive_mode: CallReceiveMode
    call_request_url: str | None
    call_request_method: str | None
    call_fallback_url: str | None
    call_fallback_method: str | None
    call_status_callback_url: str | None
    call_status_callback_method: str | None
    call_laml_application_id: str | None
    call_dialogflow_agent_id: str | None
    call_relay_topic: str | None
    call_relay_topic_status_callback_url: str | None
    call_relay_script_url: str | None
    call_relay_context: str | None
    call_relay_context_status_callback_url: str | None
    call_relay_application: str | None
    call_relay_connector_id: str | None
    call_sip_endpoint_id: uuid | None
    call_verto_resource: str | None
    call_video_room_id: uuid | None
    message_handler: PhoneNumberMessageHandler
    messaging_handler_resource_id: uuid | None
    message_request_url: str | None
    message_request_method: str | None
    message_fallback_url: str | None
    message_fallback_method: str | None
    message_laml_application_id: str | None
    message_relay_topic: str | None
    message_relay_context: str | None
    country_code: str | None


PhoneNumberCallHandler: TypeAlias = "Literal['relay_context', 'relay_topic', 'relay_script', 'relay_application', 'relay_connector', 'relay_sip_endpoint', 'relay_verto_endpoint', 'laml_webhooks', 'laml_application', 'dialogflow', 'video_room', 'call_flow', 'ai_agent', 'fabric_subscriber', 'sip_gateway', 'call_queue']"

PhoneNumberCallHandlerRequest: TypeAlias = "Literal['relay_context', 'relay_topic', 'relay_script', 'relay_application', 'relay_connector', 'relay_sip_endpoint', 'relay_verto_endpoint', 'laml_webhooks', 'laml_application', 'dialogflow', 'video_room', 'ai_agent', 'call_flow']"


class PhoneNumberCapabilities(TypedDict, total=False):
    """Phone number capabilities.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    voice: bool
    sms: bool
    mms: bool
    fax: bool


PhoneNumberCapability: TypeAlias = "Literal['voice', 'sms', 'mms', 'fax']"


class PhoneNumberListResponse(TypedDict, total=False):
    """Response containing a list of phone numbers.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[PhoneNumber]


class PhoneNumberLookupResponse(TypedDict, total=False):
    """Response containing phone number lookup result.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    country_code_number: int
    national_number: str
    possible_number: bool
    valid_number: bool
    national_number_formatted: str
    international_number_formatted: str
    e164: str
    location: str
    country_code: str
    timezones: list[str]
    number_type: str
    carrier: CarrierLookupInfo
    cnam: CnamInfo


PhoneNumberMessageHandler: TypeAlias = "Literal['relay_context', 'relay_topic', 'relay_application', 'laml_webhooks', 'laml_application']"


class PhoneNumberResponse(TypedDict, total=False):
    """Response containing a single phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    number: str
    name: str | None
    capabilities: list[PhoneNumberCapability]
    number_type: PhoneNumberType
    e911_address_id: uuid | None
    e911_status: PhoneNumberE911Status | None
    cnam: str | None
    created_at: str
    updated_at: str
    next_billed_at: str | None
    call_handler: PhoneNumberCallHandler
    calling_handler_resource_id: uuid | None
    call_receive_mode: CallReceiveMode
    call_request_url: str | None
    call_request_method: str | None
    call_fallback_url: str | None
    call_fallback_method: str | None
    call_status_callback_url: str | None
    call_status_callback_method: str | None
    call_laml_application_id: str | None
    call_dialogflow_agent_id: str | None
    call_relay_topic: str | None
    call_relay_topic_status_callback_url: str | None
    call_relay_script_url: str | None
    call_relay_context: str | None
    call_relay_context_status_callback_url: str | None
    call_relay_application: str | None
    call_relay_connector_id: str | None
    call_sip_endpoint_id: uuid | None
    call_verto_resource: str | None
    call_video_room_id: uuid | None
    message_handler: PhoneNumberMessageHandler
    messaging_handler_resource_id: uuid | None
    message_request_url: str | None
    message_request_method: str | None
    message_fallback_url: str | None
    message_fallback_method: str | None
    message_laml_application_id: str | None
    message_relay_topic: str | None
    message_relay_context: str | None
    country_code: str | None


PhoneNumberType: TypeAlias = "Literal['tollfree', 'longcode']"


class PstnRecording(TypedDict, total=False):
    """Recording from a PSTN call leg.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    project_id: uuid
    created_at: str
    updated_at: str
    duration_in_seconds: int
    error_code: str | None
    price: float
    price_unit: str
    status: Literal["recording", "paused", "finished", "no_input"]
    url: str
    stereo: bool
    byte_size: int | None
    track: str
    relay_pstn_leg_id: uuid


class PurchasePhoneNumberRequest(TypedDict, total=False):
    """Request body for purchasing a phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    number: str
    number_type: Literal["local", "tollfree"]


class Queue(TypedDict, total=False):
    """Queue model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    project_id: uuid
    friendly_name: str
    max_size: int
    current_size: int
    average_wait_time: int
    uri: str
    date_created: str
    date_updated: str


class QueueListResponse(TypedDict, total=False):
    """Response containing a list of queues.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[Queue]


class QueueMember(TypedDict, total=False):
    """Queue member model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: uuid
    project_id: str
    queue_id: str
    position: int
    uri: str
    wait_time: int
    date_enqueued: str


class QueueMemberListResponse(TypedDict, total=False):
    """Response containing a list of queue members.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[QueueMember]


class QueueMemberResponse(TypedDict, total=False):
    """Response containing a single queue member.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    call_id: uuid
    project_id: str
    queue_id: str
    position: int
    uri: str
    wait_time: int
    date_enqueued: str


class QueueResponse(TypedDict, total=False):
    """Response containing a single queue.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    project_id: uuid
    friendly_name: str
    max_size: int
    current_size: int
    average_wait_time: int
    uri: str
    date_created: str
    date_updated: str


Recording: TypeAlias = (
    "PstnRecording | SipRecording | WebRtcRecording | RelayConferenceRecording"
)


class RelayConferenceRecording(TypedDict, total=False):
    """Recording from a RELAY conference.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    project_id: uuid
    created_at: str
    updated_at: str
    duration_in_seconds: int
    error_code: str
    price: float
    price_unit: str
    status: Literal["recording", "paused", "finished", "no_input"]
    url: str
    stereo: bool
    byte_size: int
    track: str
    relay_conference_id: uuid


class RecordingListResponse(TypedDict, total=False):
    """Response containing a list of recordings.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[Recording]


class ShortCode(TypedDict, total=False):
    """Short code model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    name: str | None
    number: str
    capabilities: list[ShortCodeCapability]
    number_type: Literal["shortcode"]
    code_type: ShortCodeType
    country_code: str
    created_at: str
    updated_at: str
    next_billed_at: str | None
    lease_duration: str | None
    message_handler: ShortCodeMessageHandler | None
    message_request_url: str | None
    message_request_method: str | None
    message_fallback_url: str | None
    message_fallback_method: str | None
    message_laml_application_id: uuid | None
    message_relay_context: str | None


ShortCodeCapability: TypeAlias = "Literal['sms', 'mms']"


class ShortCodeListResponse(TypedDict, total=False):
    """Response containing a list of short codes.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[ShortCode]


ShortCodeMessageHandler: TypeAlias = (
    "Literal['relay_context', 'laml_webhooks', 'laml_application']"
)


class ShortCodeResponse(TypedDict, total=False):
    """Response containing a single short code.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    name: str | None
    number: str
    capabilities: list[ShortCodeCapability]
    number_type: Literal["shortcode"]
    code_type: ShortCodeType
    country_code: str
    created_at: str
    updated_at: str
    next_billed_at: str | None
    lease_duration: str | None
    message_handler: ShortCodeMessageHandler | None
    message_request_url: str | None
    message_request_method: str | None
    message_fallback_url: str | None
    message_fallback_method: str | None
    message_laml_application_id: uuid | None
    message_relay_context: str | None


ShortCodeType: TypeAlias = "Literal['vanity', 'random']"


class SipEndpoint(TypedDict, total=False):
    """SIP endpoint model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: str
    id: uuid
    username: str
    caller_id: str | None
    send_as: str
    ciphers: list[str]
    codecs: list[str]
    encryption: Literal["required", "optional"]
    call_handler: SipEndpointCallHandler | None
    calling_handler_resource_id: uuid | None
    call_request_url: str | None
    call_request_method: str | None
    call_fallback_url: str | None
    call_fallback_method: str | None
    call_status_callback_url: str | None
    call_status_callback_method: str | None
    call_laml_application_id: str | None
    call_dialogflow_agent_id: str | None
    call_relay_topic: str | None
    call_relay_topic_status_callback_url: str | None
    call_relay_context: str | None
    call_relay_context_status_callback_url: str | None
    call_relay_application: str | None
    call_video_room_id: uuid | None
    call_relay_script_url: str | None


SipEndpointCallHandler: TypeAlias = "Literal['default', 'passthrough', 'block-pstn', 'laml_webhook', 'laml_application', 'dialogflow', 'relay_context', 'relay_application', 'relay_connector', 'video_room', 'ai_agent', 'relay_script', 'call_flow']"


class SipEndpointListResponse(TypedDict, total=False):
    """Response containing a list of SIP endpoints.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[SipEndpoint]


class SipEndpointResponse(TypedDict, total=False):
    """Response containing a single SIP endpoint.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: str
    id: uuid
    username: str
    caller_id: str | None
    send_as: str
    ciphers: list[str]
    codecs: list[str]
    encryption: Literal["required", "optional"]
    call_handler: SipEndpointCallHandler | None
    calling_handler_resource_id: uuid | None
    call_request_url: str | None
    call_request_method: str | None
    call_fallback_url: str | None
    call_fallback_method: str | None
    call_status_callback_url: str | None
    call_status_callback_method: str | None
    call_laml_application_id: str | None
    call_dialogflow_agent_id: str | None
    call_relay_topic: str | None
    call_relay_topic_status_callback_url: str | None
    call_relay_context: str | None
    call_relay_context_status_callback_url: str | None
    call_relay_application: str | None
    call_video_room_id: uuid | None
    call_relay_script_url: str | None


class SipProfileResponse(TypedDict, total=False):
    """Response containing the SIP profile.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    domain: str
    domain_identifier: str
    default_codecs: list[str]
    default_ciphers: list[str]
    default_encryption: Literal["required", "optional"]
    default_send_as: str
    default_outbound_policy: Literal["passthrough", "block-pstn"]


class SipRecording(TypedDict, total=False):
    """Recording from a SIP call leg.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    project_id: uuid
    created_at: str
    updated_at: str
    duration_in_seconds: int
    error_code: str
    price: float
    price_unit: str
    status: Literal["recording", "paused", "finished", "no_input"]
    url: str
    stereo: bool
    byte_size: int
    track: str
    relay_sip_leg_id: uuid


class Types_StatusCodes_SpaceApiErrorItem(TypedDict, total=False):
    """Details about a specific validation error.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    detail: str
    status: str
    title: str
    code: str


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


class Types_StatusCodes_ValidationError(TypedDict, total=False):
    """The request failed validation. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_SpaceApiErrorItem]


class UpdateCampaignRequest(TypedDict, total=False):
    """Request body for updating a campaign. Every field is optional; a field you omit keeps its current value.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    status_callback_url: str
    signalwire_contact_emails: list[str] | str


class UpdateDomainApplicationRequest(TypedDict, total=False):
    """Request body for updating a domain application.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    identifier: str
    user: str
    ip_auth_enabled: bool
    ip_auth: list[str]
    encryption: Literal["optional", "required", "forbidden"]
    codecs: list[str]
    ciphers: list[str]
    call_handler: DomainAppCallHandlerRequest
    call_relay_topic: str
    call_relay_topic_status_callback_url: str
    call_relay_application: str
    call_request_url: str
    call_request_method: Literal["GET", "POST"]
    call_fallback_url: str
    call_fallback_method: Literal["GET", "POST"]
    call_status_callback_url: str
    call_status_callback_method: Literal["GET", "POST"]
    call_laml_application_id: str
    call_video_room_id: uuid
    call_relay_script_url: str
    call_relay_script_url_method: str
    call_dialogflow_agent_id: uuid
    call_ai_agent_id: uuid
    call_flow_id: uuid
    call_flow_version: Literal["working_copy"]
    call_relay_context: str
    call_relay_context_status_callback_url: str


class UpdateNumberGroupRequest(TypedDict, total=False):
    """Request body for updating a number group.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    sticky_sender: bool


class UpdatePhoneNumberRequest(TypedDict, total=False):
    """Request body for updating a phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    call_handler: PhoneNumberCallHandlerRequest
    call_receive_mode: Literal["voice", "fax"]
    call_request_url: str
    call_request_method: Literal["GET", "POST"]
    call_fallback_url: str
    call_fallback_method: Literal["GET", "POST"]
    call_status_callback_url: str
    call_status_callback_method: Literal["GET", "POST"]
    call_laml_application_id: str
    call_dialogflow_agent_id: str
    call_relay_topic: str
    call_relay_topic_status_callback_url: str
    call_relay_script_url: str
    call_relay_script_url_method: str
    call_relay_context: str
    call_relay_context_status_callback_url: str
    call_relay_application: str
    call_relay_connector_id: str
    call_sip_endpoint_id: str
    call_verto_resource: str
    call_video_room_id: uuid
    call_ai_agent_id: uuid
    call_flow_id: uuid
    call_flow_version: Literal["working_copy", "current_deployed"]
    message_handler: PhoneNumberMessageHandler
    message_request_url: str
    message_request_method: Literal["GET", "POST"]
    message_fallback_url: str
    message_fallback_method: Literal["GET", "POST"]
    message_laml_application_id: str
    message_relay_topic: str
    message_relay_context: str
    message_relay_application: str


class UpdateQueueRequest(TypedDict, total=False):
    """Request body for updating a queue.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    max_size: int


class UpdateShortCodeRequest(TypedDict, total=False):
    """Request body for updating a short code.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    message_handler: ShortCodeMessageHandler
    message_request_url: str
    message_request_method: HttpMethod
    message_fallback_url: str
    message_fallback_method: HttpMethod
    message_laml_application_id: uuid
    message_relay_context: str


class UpdateSipEndpointRequest(TypedDict, total=False):
    """Request body for updating a SIP endpoint.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    username: str
    password: str
    caller_id: str
    send_as: str
    ciphers: list[str]
    codecs: list[str]
    encryption: Literal["default", "required", "optional"]
    call_handler: Literal[
        "default",
        "passthrough",
        "block-pstn",
        "relay_context",
        "relay_topic",
        "relay_application",
        "relay_connector",
        "relay_script",
        "laml_webhooks",
        "laml_webhook",
        "laml_application",
        "dialogflow",
        "video_room",
        "call_flow",
        "ai_agent",
    ]
    call_request_url: str
    call_request_method: Literal["GET", "POST"]
    call_fallback_url: str
    call_fallback_method: Literal["GET", "POST"]
    call_status_callback_url: str
    call_status_callback_method: Literal["GET", "POST"]
    call_laml_application_id: str
    call_dialogflow_agent_id: str
    call_relay_topic: str
    call_relay_topic_status_callback_url: str
    call_relay_context: str
    call_relay_context_status_callback_url: str
    call_relay_application: str
    call_video_room_id: str
    call_flow_id: str
    call_flow_version: str
    call_ai_agent_id: str
    call_relay_script_url: str
    call_relay_script_url_method: str


class UpdateSipProfileRequest(TypedDict, total=False):
    """Request body for updating the SIP profile.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    domain_identifier: str
    default_codecs: list[str]
    default_ciphers: list[str]
    default_encryption: Literal["required", "optional"]
    default_send_as: str
    default_outbound_policy: Literal["passthrough", "block-pstn"]


class UpdateVerifiedCallerIDRequest(TypedDict, total=False):
    """Request body for updating a verified caller ID.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str


class VerifiedCallerID(TypedDict, total=False):
    """Verified caller ID model.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: str
    id: uuid
    number: str
    name: str | None
    extension: str | None
    verified: bool
    verified_at: str | None
    status: Literal["Verified", "Awaiting Verification"]


class VerifiedCallerIDListResponse(TypedDict, total=False):
    """Response containing a list of verified caller IDs.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    data: list[VerifiedCallerID]


class VerifiedCallerIDResponse(TypedDict, total=False):
    """Response containing a single verified caller ID.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: str
    id: uuid
    number: str
    name: str | None
    extension: str | None
    verified: bool
    verified_at: str | None
    status: Literal["Verified", "Awaiting Verification"]


class VerifyCallerIDRequest(TypedDict, total=False):
    """Request body for verifying a caller ID.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    verification_code: str


class WebRtcRecording(TypedDict, total=False):
    """Recording from a WebRTC call leg.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: uuid
    project_id: uuid
    created_at: str
    updated_at: str
    duration_in_seconds: int
    error_code: str
    price: float
    price_unit: str
    status: Literal["recording", "paused", "finished", "no_input"]
    url: str
    stereo: bool
    byte_size: int
    track: str
    relay_webrtc_leg_id: uuid


class UpdateAddressRequest(TypedDict, total=False):
    """Request body for updating an address.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    label: str
    country: AddressCountryCode
    first_name: str
    last_name: str
    street_number: str
    street_name: str
    address_type: AddressType
    address_number: str
    city: str
    state: str
    postal_code: str
    emergency_enabled: bool
    auto_correct_address: bool


class AddressCandidate(TypedDict, total=False):
    """A carrier-suggested alternative to the submitted address.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    street_number: str | None
    street_name: str | None
    city: str | None
    state: str | None
    postal_code: str | None


class AddressValidationError(TypedDict, total=False):
    """The request failed validation. See `errors` for details. When carrier validation rejected the address

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_SpaceApiErrorItem]
    candidates: list[AddressCandidate]


class UpdateBrandRequest(TypedDict, total=False):
    """Request body for updating a brand. Every field is optional; a field you omit keeps its current value. Only a brand in the `unverified` state accepts changes to fields other than `signalwire_contact_emails`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    company_name: str
    contact_email: str
    contact_phone: str
    ein_issuing_country: str
    legal_entity_type: LegalEntityType
    ein: str
    company_vertical: CompanyVertical
    company_website: str
    company_address: str
    csp_brand_reference: str
    status_callback_url: str
    signalwire_contact_emails: list[str] | str


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


class BrandUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class AssignE911AddressRequest(TypedDict, total=False):
    """Request body for assigning an E911 address to a phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    e911_address_id: uuid


PhoneNumberE911Status: TypeAlias = (
    "Literal['pending', 'active', 'failed', 'pending_removal', 'unregistered']"
)


class CreatePhoneNumberCnamRequest(TypedDict, total=False):
    """Request body for requesting a caller ID name for a phone number.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str


PhoneNumberCnamStatus: TypeAlias = (
    "Literal['pending', 'approved', 'in_review', 'rejected', 'failed', 'superseded']"
)

PhoneNumberCnamReason: TypeAlias = "Literal['offensive_language', 'impersonation', 'unverified_brand', 'implied_trusted_institution', 'scam_wording', 'deceptive', 'unsupported_personal_name', 'too_generic', 'invalid_format', 'unrelated_to_business', 'needs_documentation', 'other_compliance_concern', 'processing_failed', 'unsupported_provider']"


class PhoneNumberCnamResponse(TypedDict, total=False):
    """Details and review status returned for a caller ID name request.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["cnam"]
    id: uuid
    phone_number_id: uuid
    name: str
    status: PhoneNumberCnamStatus
    reason: PhoneNumberCnamReason | None
    required_action: str | None
    created_at: str
    updated_at: str


uuid: TypeAlias = "str"

ListAddressesResponse: TypeAlias = "AddressListResponse"
CreateAddressResponse: TypeAlias = "AddressResponse"
UpdateAddressResponse: TypeAlias = "AddressResponse"
GetAddressResponse: TypeAlias = "AddressResponse"
ListDomainApplicationsResponse: TypeAlias = "DomainApplicationListResponse"
CreateDomainApplicationResponse: TypeAlias = "DomainApplicationResponse"
RetrieveDomainApplicationResponse: TypeAlias = "DomainApplicationResponse"
UpdateDomainApplicationResponse: TypeAlias = "DomainApplicationResponse"
ListSipEndpointsResponse: TypeAlias = "SipEndpointListResponse"
CreateSipEndpointResponse: TypeAlias = "SipEndpointResponse"
RetrieveSipEndpointResponse: TypeAlias = "SipEndpointResponse"
UpdateSipEndpointResponse: TypeAlias = "SipEndpointResponse"
CreateImportedPhoneNumberRequest: TypeAlias = "ImportPhoneNumberRequest"
CreateImportedPhoneNumberResponse: TypeAlias = "PhoneNumberResponse"
LookupPhoneNumberResponse: TypeAlias = "PhoneNumberLookupResponse"
RequestMfaCallRequest: TypeAlias = "MfaRequest"
RequestMfaCallResponse: TypeAlias = "MfaResponse"
RequestMfaSmsRequest: TypeAlias = "MfaRequest"
RequestMfaSmsResponse: TypeAlias = "MfaResponse"
VerifyMfaTokenRequest: TypeAlias = "MfaVerifyRequest"
VerifyMfaTokenResponse: TypeAlias = "MfaVerifyResponse"
RetrieveNumberGroupMembershipResponse: TypeAlias = "NumberGroupMembershipResponse"
ListNumberGroupsResponse: TypeAlias = "NumberGroupListResponse"
CreateNumberGroupResponse: TypeAlias = "NumberGroupResponse"
ListNumberGroupMembershipsResponse: TypeAlias = "NumberGroupMembershipListResponse"
CreateNumberGroupMembershipRequest: TypeAlias = "AddNumberGroupMembershipRequest"
CreateNumberGroupMembershipResponse: TypeAlias = "NumberGroupMembershipResponse"
RetrieveNumberGroupResponse: TypeAlias = "NumberGroupResponse"
UpdateNumberGroupResponse: TypeAlias = "NumberGroupResponse"
ListPhoneNumbersResponse: TypeAlias = "PhoneNumberListResponse"
PurchasePhoneNumberResponse: TypeAlias = "PhoneNumberResponse"
SearchAvailablePhoneNumbersResponse: TypeAlias = "AvailablePhoneNumbersResponse"
RetrievePhoneNumberResponse: TypeAlias = "PhoneNumberResponse"
UpdatePhoneNumberResponse: TypeAlias = "PhoneNumberResponse"
AssignE911AddressResponse: TypeAlias = "PhoneNumberResponse"
RemoveE911AddressResponse: TypeAlias = "PhoneNumberResponse"
RetrieveCallerIdNameResponse: TypeAlias = "PhoneNumberCnamResponse"
RequestCallerIdNameRequest: TypeAlias = "CreatePhoneNumberCnamRequest"
RequestCallerIdNameResponse: TypeAlias = "PhoneNumberCnamResponse"
ListQueuesResponse: TypeAlias = "QueueListResponse"
CreateQueueResponse: TypeAlias = "QueueResponse"
GetQueueResponse: TypeAlias = "QueueResponse"
UpdateQueueResponse: TypeAlias = "QueueResponse"
ListQueueMembersResponse: TypeAlias = "QueueMemberListResponse"
RetrieveNextQueueMemberResponse: TypeAlias = "QueueMemberResponse"
RetrieveQueueMemberResponse: TypeAlias = "QueueMemberResponse"
ListRecordingsResponse: TypeAlias = "RecordingListResponse"
GetRecordingResponse: TypeAlias = "Recording"
ListBrandsResponse: TypeAlias = "BrandListResponse"
CreateBrandRequest: TypeAlias = "CreateManagedBrandRequest | CreateCspBrandRequest"
CreateBrandResponse: TypeAlias = "BrandResponse"
UpdateBrandResponse: TypeAlias = "BrandResponse"
RetrieveBrandResponse: TypeAlias = "BrandResponse"
ListCampaignsResponse: TypeAlias = "CampaignListResponse"
CreateCampaignRequest: TypeAlias = (
    "CreateManagedCampaignRequest | CreatePartnerCampaignRequest"
)
CreateCampaignResponse: TypeAlias = "CampaignResponse"
RetrieveCampaignResponse: TypeAlias = "CampaignResponse"
UpdateCampaignResponse: TypeAlias = "CampaignResponse"
ListNumberAssignmentsResponse: TypeAlias = "AssignedNumberListResponse"
ListOrdersResponse: TypeAlias = "OrderListResponse"
CreateOrderResponse: TypeAlias = "OrderResponse"
RetrieveOrderResponse: TypeAlias = "OrderResponse"
ListShortCodesResponse: TypeAlias = "ShortCodeListResponse"
RetrieveShortCodeResponse: TypeAlias = "ShortCodeResponse"
UpdateShortCodeResponse: TypeAlias = "ShortCodeResponse"
RetrieveSipProfileResponse: TypeAlias = "SipProfileResponse"
UpdateSipProfileResponse: TypeAlias = "SipProfileResponse"
ListVerifiedCallerIdsResponse: TypeAlias = "VerifiedCallerIDListResponse"
CreateVerifiedCallerIdRequest: TypeAlias = "CreateVerifiedCallerIDRequest"
CreateVerifiedCallerIdResponse: TypeAlias = "VerifiedCallerIDResponse"
RetrieveVerifiedCallerIdResponse: TypeAlias = "VerifiedCallerIDResponse"
UpdateVerifiedCallerIdRequest: TypeAlias = "UpdateVerifiedCallerIDRequest"
UpdateVerifiedCallerIdResponse: TypeAlias = "VerifiedCallerIDResponse"
RedialVerificationCallResponse: TypeAlias = "VerifiedCallerIDResponse"
ValidateVerificationCodeRequest: TypeAlias = "VerifyCallerIDRequest"
ValidateVerificationCodeResponse: TypeAlias = "VerifiedCallerIDResponse"


class PhoneCallHandler(str, Enum):
    RELAY_CONTEXT = "relay_context"
    RELAY_TOPIC = "relay_topic"
    RELAY_SCRIPT = "relay_script"
    RELAY_APPLICATION = "relay_application"
    RELAY_CONNECTOR = "relay_connector"
    RELAY_SIP_ENDPOINT = "relay_sip_endpoint"
    RELAY_VERTO_ENDPOINT = "relay_verto_endpoint"
    LAML_WEBHOOKS = "laml_webhooks"
    LAML_APPLICATION = "laml_application"
    DIALOGFLOW = "dialogflow"
    VIDEO_ROOM = "video_room"
    AI_AGENT = "ai_agent"
    CALL_FLOW = "call_flow"
