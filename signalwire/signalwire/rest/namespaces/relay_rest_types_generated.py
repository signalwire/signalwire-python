# AUTO-GENERATED from porting-sdk/rest-apis/relay-rest/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``relay-rest`` REST API shapes, generated from the OpenAPI spec.

One ``TypedDict`` per spec schema plus per-operation ``*Request`` / ``*Response``
aliases. Every shape is static-only: at runtime each is a plain ``dict``, so a
differently-shaped server response is returned unchanged and never raises.
"""

from __future__ import annotations
from enum import Enum
from typing import Literal, TypeAlias, TypedDict


class AddNumberGroupMembershipRequest(TypedDict, total=False):
    """Request body for adding a phone number to a number group.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        phone_number_id: The phone number ID to add to the group.
    """

    phone_number_id: uuid


class Address(TypedDict, total=False):
    """Address model representing a physical address for regulatory compliance.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the Address on SignalWire.
        label: A friendly name given to the address to help distinguish and search for
            different addresses within your project.
        country: The ISO 3166 Alpha 2 country code.
        first_name: First name of the occupant associated with this address.
        last_name: Last name of the occupant associated with this address.
        street_number: The number portion of the street address.
        street_name: The name portion of the street address.
        address_type: If the address is divided into multiple sub-addresses, this
            identifies how the address is divided.
        address_number: If the address is divided into multiple sub-addresses, this
            identifies the particular sub-address.
        city: The city portion of the street address.
        state: The state/province/region of the street address. In the USA and Canada,
            use the two-letter abbreviated form.
        postal_code: The postal code of the street address.
        zip_code: The postal code of the street address. Alias for postal_code for
            backwards compatibility.
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


class AddressListResponse(TypedDict, total=False):
    """Response containing a list of addresses.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of addresses.
    """

    links: PaginationLinks
    data: list[Address]


class AddressResponse(TypedDict, total=False):
    """Response containing a single address.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the Address on SignalWire.
        label: A friendly name given to the address to help distinguish and search for
            different addresses within your project.
        country: The ISO 3166 Alpha 2 country code.
        first_name: First name of the occupant associated with this address.
        last_name: Last name of the occupant associated with this address.
        street_number: The number portion of the street address.
        street_name: The name portion of the street address.
        address_type: If the address is divided into multiple sub-addresses, this
            identifies how the address is divided.
        address_number: If the address is divided into multiple sub-addresses, this
            identifies the particular sub-address.
        city: The city portion of the street address.
        state: The state/province/region of the street address. In the USA and Canada,
            use the two-letter abbreviated form.
        postal_code: The postal code of the street address.
        zip_code: The postal code of the street address. Alias for postal_code for
            backwards compatibility.
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


AddressType: TypeAlias = "Literal['Apartment', 'Basement', 'Building', 'Department', 'Floor', 'Office', 'Penthouse', 'Suite', 'Trailer', 'Unit']"


class AssignedNumber(TypedDict, total=False):
    """Assigned number model for campaign registration.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the assignment.
        state: The current state of the assignment.
        campaign_id: The campaign ID associated with the number.
        phone_number: The phone number details.
        created_at: Timestamp when the assignment was created.
        updated_at: Timestamp when the assignment was last updated.
    """

    id: uuid
    state: str
    campaign_id: uuid
    phone_number: AssignedPhoneNumber
    created_at: str
    updated_at: str


class AssignedNumberListResponse(TypedDict, total=False):
    """Response containing a list of assigned numbers.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of assigned numbers.
    """

    links: PaginationLinks
    data: list[AssignedNumber]


class AssignedPhoneNumber(TypedDict, total=False):
    """Phone number details in an assignment.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the phone number.
        name: The name of the phone number.
        number: The phone number in E.164 format.
        status_callback_url: Optional: Specify a URL to receive webhook notifications.
            See the [10DLC status
            callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
            docs for the webhook payload.
    """

    id: uuid
    name: str
    number: str
    status_callback_url: str


class AvailablePhoneNumber(TypedDict, total=False):
    """Available phone number for purchase.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        number: The phone number in E.164 format.
        region: The region of the phone number.
        city: The city of the phone number.
        rate_center: The rate center of the phone number.
        lata: The LATA of the phone number.
        capabilities: The capabilities of the phone number.
    """

    number: str
    region: str
    city: str
    rate_center: str
    lata: str
    capabilities: PhoneNumberCapabilities


class AvailablePhoneNumbersResponse(TypedDict, total=False):
    """Response containing available phone numbers for purchase.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of available phone numbers.
    """

    links: PaginationLinks
    data: list[AvailablePhoneNumber]


class Brand(TypedDict, total=False):
    """Brand model for 10DLC registration.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the brand.
        state: The current state of the brand.
        name: Brand/Marketing/DBA name of the business if applicable.
        company_name: The legal name of the business.
        contact_email: A company contact email for this brand.
        contact_phone: A contact phone number for this brand.
        ein_issuing_country: Country of registration.
        legal_entity_type: What type of legal entity is the organization?
            (PRIVATE_PROFIT, PUBLIC_PROFIT, NON_PROFIT)
        ein: Company EIN Number/Tax ID.
        company_address: Full company address.
        company_vertical: An optional Vertical for the brand (REAL_ESTATE, HEALTHCARE,
            ENERGY, ENTERTAINMENT, RETAIL, AGRICULTURE, INSURANCE, EDUCATION,
            HOSPITALITY, FINANCIAL, GAMBLING, CONSTRUCTION, NGO, MANUFACTURING,
            GOVERNMENT, TECHNOLOGY, COMMUNICATION).
        company_website: Link to the company website.
        csp_brand_reference: If you are your own Campaign Service Provider, this is the
            approved Brand ID (Mandatory for CSPs, otherwise please omit).
        csp_self_registered: This value must be true for all self-registered brands.
        status_callback_url: Optional: Specify a URL to receive webhook notifications
            when your brand's state changes. See the [10DLC status
            callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
            docs for the webhook payload.
        created_at: Timestamp when the brand was created.
        updated_at: Timestamp when the brand was last updated.
    """

    id: uuid
    state: str
    name: str
    company_name: str
    contact_email: str
    contact_phone: str
    ein_issuing_country: str
    legal_entity_type: str
    ein: str
    company_address: str
    company_vertical: str
    company_website: str
    csp_brand_reference: str
    csp_self_registered: bool
    status_callback_url: str
    created_at: str
    updated_at: str


class BrandListResponse(TypedDict, total=False):
    """Response containing a list of brands.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of brands.
    """

    links: PaginationLinks
    data: list[Brand]


class BrandResponse(TypedDict, total=False):
    """Response containing a single brand.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the brand.
        state: The current state of the brand.
        name: Brand/Marketing/DBA name of the business if applicable.
        company_name: The legal name of the business.
        contact_email: A company contact email for this brand.
        contact_phone: A contact phone number for this brand.
        ein_issuing_country: Country of registration.
        legal_entity_type: What type of legal entity is the organization?
            (PRIVATE_PROFIT, PUBLIC_PROFIT, NON_PROFIT)
        ein: Company EIN Number/Tax ID.
        company_address: Full company address.
        company_vertical: An optional Vertical for the brand (REAL_ESTATE, HEALTHCARE,
            ENERGY, ENTERTAINMENT, RETAIL, AGRICULTURE, INSURANCE, EDUCATION,
            HOSPITALITY, FINANCIAL, GAMBLING, CONSTRUCTION, NGO, MANUFACTURING,
            GOVERNMENT, TECHNOLOGY, COMMUNICATION).
        company_website: Link to the company website.
        csp_brand_reference: If you are your own Campaign Service Provider, this is the
            approved Brand ID (Mandatory for CSPs, otherwise please omit).
        csp_self_registered: This value must be true for all self-registered brands.
        status_callback_url: Optional: Specify a URL to receive webhook notifications
            when your brand's state changes. See the [10DLC status
            callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
            docs for the webhook payload.
        created_at: Timestamp when the brand was created.
        updated_at: Timestamp when the brand was last updated.
    """

    id: uuid
    state: str
    name: str
    company_name: str
    contact_email: str
    contact_phone: str
    ein_issuing_country: str
    legal_entity_type: str
    ein: str
    company_address: str
    company_vertical: str
    company_website: str
    csp_brand_reference: str
    csp_self_registered: bool
    status_callback_url: str
    created_at: str
    updated_at: str


CallReceiveMode: TypeAlias = "Literal['voice', 'fax']"


class Campaign(TypedDict, total=False):
    """Campaign model for 10DLC registration.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the campaign.
        name: A name for the campaign.
        state: The current state of the campaign.
        sms_use_case: An SMS Use Case category for the campaign (2FA,
            ACCOUNT_NOTIFICATION, AGENTS_FRANCHISES, CARRIER_EXEMPT, CHARITY,
            CUSTOMER_CARE, DELIVERY_NOTIFICATION, EMERGENCY, FRAUD_ALERT,
            HIGHER_EDUCATION, K12_EDUCATION, LOW_VOLUME_MIXED, MARKETING, MIXED,
            POLITICAL, POLITICAL_SECTION_527, POLLING_VOTING, PROXY,
            PUBLIC_SERVICE_ANNOUNCEMENT, SECURITY_ALERT, SOCIAL, SWEEPSTAKE, TRIAL,
            UCAAS_HIGH_VOLUME, UCAAS_LOW_VOLUME).
        sub_use_cases: A sub use case category for MIXED or LOW_VOLUME_MIXED campaigns
            (CUSTOMER_CARE, HIGHER_EDUCATION, POLLING_VOTING,
            PUBLIC_SERVICE_ANNOUNCEMENT, MARKETING, SECURITY_ALERT, 2FA,
            ACCOUNT_NOTIFICATION, DELIVERY_NOTIFICATION, FRAUD_ALERT).
        campaign_verify_token: Campaign Verify token. Required if sms use case is
            POLITICAL_SECTION_527.
        description: A description for the campaign. Please use at least 40 characters.
        sample1: Sample message template/content. At least two samples are required and
            up to five can be provided. Please use at least 20 characters.
        sample2: Sample 2.
        sample3: Sample 3.
        sample4: Sample 4.
        sample5: Sample 5.
        dynamic_templates: If your messaging content will be modified in any way beyond
            what you shared in your templates, please describe the nature of how the
            content will change.
        message_flow: Please describe the call to action/message flow your intended
            recipients will experience.
        opt_in_message: Please share the message subscribers receive when they opt in.
        opt_out_message: Please share the message subscribers receive when they opt out.
        help_message: Please share the message subscribers receive when they request
            help.
        opt_in_keywords: Opt in keywords that subscribers can use.
        opt_out_keywords: Opt out keywords that subscribers can use.
        help_keywords: Help keywords that subscribers can use.
        number_pooling_required: Will 50 or more numbers be used with this single
            campaign? If so, please enter true.
        number_pooling_per_campaign: If you will be using number pooling, please provide
            an explanation as to why it is needed.
        direct_lending: Will this campaign include content related to direct lending or
            other loan agreements?
        embedded_link: Will you be using an embedded link of any kind? Note that public
            URL shorteners (bitly, tinyurl) will not be accepted.
        embedded_phone: Are you using an embedded phone number (except the required HELP
            information contact phone number)?
        age_gated_content: Will this campaign include any age gated content as defined
            by carrier and CTA guidelines?
        lead_generation: Is there any intent of this campaign to generate leads?
        csp_campaign_reference: If you are your own Campaign Service Provider, what is
            the approved Campaign ID? (Mandatory for CSPs, otherwise please omit)
        status_callback_url: Optional: Specify a URL to receive webhook notifications
            when your campaign's state changes. See the [10DLC status
            callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
            docs for the webhook payload.
        created_at: Timestamp when the campaign was created.
        updated_at: Timestamp when the campaign was last updated.
    """

    id: uuid
    name: str
    state: str
    sms_use_case: str
    sub_use_cases: list[str]
    campaign_verify_token: str
    description: str
    sample1: str
    sample2: str
    sample3: str
    sample4: str
    sample5: str
    dynamic_templates: str
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
    csp_campaign_reference: str
    status_callback_url: str
    created_at: str
    updated_at: str


class CampaignListResponse(TypedDict, total=False):
    """Response containing a list of campaigns.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of campaigns.
    """

    links: PaginationLinks
    data: list[Campaign]


class CampaignResponse(TypedDict, total=False):
    """Response containing a single campaign.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the campaign.
        name: A name for the campaign.
        state: The current state of the campaign.
        sms_use_case: An SMS Use Case category for the campaign (2FA,
            ACCOUNT_NOTIFICATION, AGENTS_FRANCHISES, CARRIER_EXEMPT, CHARITY,
            CUSTOMER_CARE, DELIVERY_NOTIFICATION, EMERGENCY, FRAUD_ALERT,
            HIGHER_EDUCATION, K12_EDUCATION, LOW_VOLUME_MIXED, MARKETING, MIXED,
            POLITICAL, POLITICAL_SECTION_527, POLLING_VOTING, PROXY,
            PUBLIC_SERVICE_ANNOUNCEMENT, SECURITY_ALERT, SOCIAL, SWEEPSTAKE, TRIAL,
            UCAAS_HIGH_VOLUME, UCAAS_LOW_VOLUME).
        sub_use_cases: A sub use case category for MIXED or LOW_VOLUME_MIXED campaigns
            (CUSTOMER_CARE, HIGHER_EDUCATION, POLLING_VOTING,
            PUBLIC_SERVICE_ANNOUNCEMENT, MARKETING, SECURITY_ALERT, 2FA,
            ACCOUNT_NOTIFICATION, DELIVERY_NOTIFICATION, FRAUD_ALERT).
        campaign_verify_token: Campaign Verify token. Required if sms use case is
            POLITICAL_SECTION_527.
        description: A description for the campaign. Please use at least 40 characters.
        sample1: Sample message template/content. At least two samples are required and
            up to five can be provided. Please use at least 20 characters.
        sample2: Sample 2.
        sample3: Sample 3.
        sample4: Sample 4.
        sample5: Sample 5.
        dynamic_templates: If your messaging content will be modified in any way beyond
            what you shared in your templates, please describe the nature of how the
            content will change.
        message_flow: Please describe the call to action/message flow your intended
            recipients will experience.
        opt_in_message: Please share the message subscribers receive when they opt in.
        opt_out_message: Please share the message subscribers receive when they opt out.
        help_message: Please share the message subscribers receive when they request
            help.
        opt_in_keywords: Opt in keywords that subscribers can use.
        opt_out_keywords: Opt out keywords that subscribers can use.
        help_keywords: Help keywords that subscribers can use.
        number_pooling_required: Will 50 or more numbers be used with this single
            campaign? If so, please enter true.
        number_pooling_per_campaign: If you will be using number pooling, please provide
            an explanation as to why it is needed.
        direct_lending: Will this campaign include content related to direct lending or
            other loan agreements?
        embedded_link: Will you be using an embedded link of any kind? Note that public
            URL shorteners (bitly, tinyurl) will not be accepted.
        embedded_phone: Are you using an embedded phone number (except the required HELP
            information contact phone number)?
        age_gated_content: Will this campaign include any age gated content as defined
            by carrier and CTA guidelines?
        lead_generation: Is there any intent of this campaign to generate leads?
        csp_campaign_reference: If you are your own Campaign Service Provider, what is
            the approved Campaign ID? (Mandatory for CSPs, otherwise please omit)
        status_callback_url: Optional: Specify a URL to receive webhook notifications
            when your campaign's state changes. See the [10DLC status
            callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
            docs for the webhook payload.
        created_at: Timestamp when the campaign was created.
        updated_at: Timestamp when the campaign was last updated.
    """

    id: uuid
    name: str
    state: str
    sms_use_case: str
    sub_use_cases: list[str]
    campaign_verify_token: str
    description: str
    sample1: str
    sample2: str
    sample3: str
    sample4: str
    sample5: str
    dynamic_templates: str
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
    csp_campaign_reference: str
    status_callback_url: str
    created_at: str
    updated_at: str


class CarrierLookupInfo(TypedDict, total=False):
    """Carrier lookup information.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        lrn: The LRN associated with the number.
        spid: The Service Profile Identifier associated with the number.
        ocn: The Operating Company Number associated with the number.
        lata: The Local Access and Transport Area number associated with the number.
        city: The City associated with the number.
        state: The State/Province/Region associated with the number.
        jurisdiction: The Jurisdiction associated with the number.
        lec: The LEC or Carrier of the number.
        linetype: The type of line the number is. Generally either wireless or landline.
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


class CnamInfo(TypedDict, total=False):
    """Caller ID (CNAM) information.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        caller_id: The caller ID associated with the number.
    """

    caller_id: str


CompanyVertical: TypeAlias = "Literal['AGRICULTURE', 'COMMUNICATION', 'CONSTRUCTION', 'EDUCATION', 'ENERGY', 'ENTERTAINMENT', 'FINANCIAL', 'GAMBLING', 'GOVERNMENT', 'HEALTHCARE', 'HOSPITALITY', 'HUMAN_RESOURCES', 'INSURANCE', 'LEGAL', 'MANUFACTURING', 'NGO', 'POLITICAL', 'POSTAL', 'PROFESSIONAL', 'REAL_ESTATE', 'RETAIL', 'TECHNOLOGY', 'TRANSPORTATION']"


class CreateAddressRequest(TypedDict, total=False):
    """Request body for creating an address.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        label: A friendly name given to the address to help distinguish and search for
            different addresses within your project.
        country: The ISO 3166 Alpha 2 country code.
        first_name: First name of the occupant associated with this address.
        last_name: Last name of the occupant associated with this address.
        street_number: The number portion of the street address.
        street_name: The name portion of the street address.
        address_type: If the address is divided into multiple sub-addresses, this
            identifies how the address is divided. Possible values are: Apartment,
            Basement, Building, Department, Floor, Office, Penthouse, Suite, Trailer,
            Unit.
        address_number: If the address is divided into multiple sub-addresses, this
            identifies the particular sub-address.
        city: The city portion of the street address.
        state: The state/province/region of the street address. In the USA and Canada,
            use the two-letter abbreviated form.
        postal_code: The postal code of the street address.
    """

    label: str
    country: str
    first_name: str
    last_name: str
    street_number: str
    street_name: str
    address_type: AddressType
    address_number: str
    city: str
    state: str
    postal_code: str


class CreateCspBrandRequest(TypedDict, total=False):
    """Request body for importing a self-registered CSP brand.

    Use this when you have already registered your brand directly with TCR.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        csp_self_registered: Set to true to indicate this is a self-registered CSP
            brand.
        name: Brand/Marketing/DBA name of the business.
        csp_brand_reference: The approved Brand ID from TCR. Required for
            CSP/self-registered brands.
        status_callback_url: Specify a URL to receive webhook notifications when your
            brand's state changes. See the [10DLC status
            callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
            docs for the webhook payload.
    """

    csp_self_registered: Literal[True]
    name: str
    csp_brand_reference: str
    status_callback_url: str


class CreateDomainApplicationRequest(TypedDict, total=False):
    """Request body for creating a domain application.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: A string representing the friendly name for this domain application.
        identifier: A string representing the identifier portion of the domain
            application.
        user: The user portion of the domain application.
        ip_auth_enabled: Whether the domain application will enforce IP authentication
            for incoming requests.
        ip_auth: A list containing whitelisted IP addresses and IP blocks used if
            ip_auth_enabled is true.
        encryption: Whether connections to this domain application require encryption or
            if encryption is optional.
        codecs: A list of codecs this domain application will support.
        ciphers: A list of encryption ciphers this domain application will support.
        call_handler: Specify how the domain application will handle calls.
        call_relay_topic: A string representing the Relay topic to forward incoming
            calls to. Required when call_handler is relay_topic.
        call_relay_topic_status_callback_url: A string representing a URL to send status
            change messages to.
        call_relay_application: A string representing the Relay Application to forward
            incoming calls to. Required when call_handler is relay_application.
        call_request_url: A string representing the LaML URL to access when a call is
            received. Required when call_handler is laml_webhooks.
        call_request_method: A string representing the HTTP method to use with
            call_request_url.
        call_fallback_url: A string representing the LaML URL to access when the call to
            call_request_url fails.
        call_fallback_method: A string representing the HTTP method to use with
            call_fallback_url.
        call_status_callback_url: A string representing a URL to send status change
            messages to.
        call_status_callback_method: A string representing the HTTP method to use with
            call_status_callback_url.
        call_laml_application_id: A string representing the ID of the LaML application
            to forward incoming calls to. Required when call_handler is
            laml_application.
        call_video_room_id: A string representing the ID of the Video Room to forward
            incoming calls to. Required when call_handler is video_room.
        call_relay_script_url: A string representing the URL of the Relay script to
            execute when a call is received. Required when call_handler is relay_script.
        call_dialogflow_agent_id: A string representing the ID of the Dialogflow Agent
            to forward incoming calls to. Required when call_handler is dialogflow.
        call_ai_agent_id: A string representing the ID of the AI Agent to forward
            incoming calls to. Required when call_handler is ai_agent.
        call_flow_id: A string representing the ID of the Call Flow to forward incoming
            calls to. Required when call_handler is call_flow.
        call_flow_version: A string representing the version of your Call Flow you'd
            like to use.
        call_relay_context: This handler type is deprecated. Please use
            call_relay_application or call_relay_topic instead. Deprecated.
        call_relay_context_status_callback_url: This property is deprecated. Please use
            call_relay_topic_status_callback_url instead. Deprecated.
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
    call_dialogflow_agent_id: uuid
    call_ai_agent_id: uuid
    call_flow_id: uuid
    call_flow_version: Literal["working_copy", "current_deployed"]
    call_relay_context: str
    call_relay_context_status_callback_url: str


class CreateManagedBrandRequest(TypedDict, total=False):
    """Request body for registering a new managed brand for 10DLC registration.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: Brand/Marketing/DBA name of the business.
        company_name: The legal name of the business.
        contact_email: A company contact email for this brand.
        contact_phone: A contact phone number for this brand.
        ein_issuing_country: Country of registration.
        legal_entity_type: What type of legal entity is the organization?
        ein: Company EIN Number/Tax ID.
        company_address: Full company address.
        company_vertical: An optional Vertical for the brand.
        company_website: Link to the company website.
        status_callback_url: Specify a URL to receive webhook notifications when your
            brand's state changes. See the [10DLC status
            callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
            docs for the webhook payload.
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


class CreateManagedCampaignRequest(TypedDict, total=False):
    """Request body for creating a managed campaign.

    Used when the brand is a managed (non-CSP) brand.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: A name for the campaign.
        brand_id: The ID of the brand to associate with this campaign.
        sms_use_case: An SMS Use Case category for the campaign.
        sub_use_cases: A sub use case category. Required for MIXED (2-5 sub use cases)
            or LOW_VOLUME_MIXED (1-5 sub use cases) campaigns. Must not be provided for
            other use cases.
        campaign_verify_token: Campaign Verify token. Required if sms_use_case is
            POLITICAL_SECTION_527.
        description: A description for the campaign.
        sample1: Sample message template/content.
        sample2: Second sample message template/content.
        sample3: Third sample message template/content.
        sample4: Fourth sample message template/content.
        sample5: Fifth sample message template/content.
        dynamic_messages: If your messaging content will be modified in any way beyond
            what you shared in your templates, please describe the nature of how the
            content will change.
        message_flow: Please describe the call to action/message flow your intended
            recipients will experience.
        opt_in_message: Please share the message subscribers receive when they opt in.
        opt_out_message: Please share the message subscribers receive when they opt out.
        help_message: Please share the message subscribers receive when they request
            help.
        opt_in_keywords: Opt in keywords that subscribers can use. Must be
            comma-separated values with no spaces between keywords.
        opt_out_keywords: Opt out keywords that subscribers can use. Must be
            comma-separated values with no spaces between keywords.
        help_keywords: Help keywords that subscribers can use. Must be comma-separated
            values with no spaces between keywords.
        number_pooling_required: Will 50 or more numbers be used with this single
            campaign?
        number_pooling_per_campaign: If you will be using number pooling, please provide
            an explanation as to why it is needed. Required if number_pooling_required
            is true.
        direct_lending: Will this campaign include content related to direct lending or
            other loan agreements?
        embedded_link: Will you be using an embedded link of any kind? Note that public
            URL shorteners (bitly, tinyurl) will not be accepted.
        embedded_phone: Are you using an embedded phone number (except the required HELP
            information contact phone number)?
        age_gated_content: Will this campaign include any age gated content as defined
            by carrier and CTA guidelines?
        lead_generation: Is there any intent of this campaign to generate leads?
        terms_and_conditions: I agree to the terms and conditions which do not allow me
            to use this campaign for affiliate marketing.
        status_callback_url: Specify a URL to receive webhook notifications when your
            campaign's state changes. See the [10DLC status
            callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
            docs for the webhook payload.
    """

    name: str
    brand_id: uuid
    sms_use_case: str
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


class CreateNumberGroupRequest(TypedDict, total=False):
    """Request body for creating a number group.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: The name given to the number group. Helps to distinguish different groups
            within your project.
        sticky_sender: Whether the number group uses the same 'From' number for outbound
            requests to a number, or chooses a random one.
    """

    name: str
    sticky_sender: bool


class CreateOrderRequest(TypedDict, total=False):
    """Request body for creating an order.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        phone_numbers: A list of phone numbers in E164 format.
        status_callback_url: Optional: Specify a URL to receive webhook notifications
            when your number assignment order and the number assignments that belong to
            it change state. See the [10DLC status
            callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
            docs for the webhook payload.
    """

    phone_numbers: list[str]
    status_callback_url: str


class CreatePartnerCampaignRequest(TypedDict, total=False):
    """Request body for creating a partner/CSP campaign.

    Used when the brand is a CSP (self-registered) brand.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: A name for the campaign.
        brand_id: The ID of the brand to associate with this campaign. Must be a
            CSP/partner brand.
        csp_campaign_reference: The approved Campaign ID from TCR. Required for
            CSP/self-registered campaigns.
        status_callback_url: Specify a URL to receive webhook notifications when your
            campaign's state changes. See the [10DLC status
            callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
            docs for the webhook payload.
    """

    name: str
    brand_id: uuid
    csp_campaign_reference: str
    status_callback_url: str


class CreateQueueRequest(TypedDict, total=False):
    """Request body for creating a queue.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: The name of the queue.
        max_size: The maximum number of callers allowed in the queue.
    """

    name: str
    max_size: int


class CreateSipEndpointRequest(TypedDict, total=False):
    """Request body for creating a SIP endpoint.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        username: String representing the username portion of the endpoint. Must be
            unique across your project and must not contain white space characters or @.
        password: A password to authenticate registrations to this endpoint.
        caller_id: Friendly Caller ID used as the CNAM when dialing a phone number or
            the From when dialing another SIP Endpoint.
        send_as: When dialing a PSTN phone number, you must send it From a number you
            have purchased or verified. send_as indicates which number this endpoint has
            set as its origination. random indicates it will randomly choose a purchased
            or verified number from within the project.
        ciphers: A list of encryption ciphers this endpoint will support.
        codecs: A list of codecs this endpoint will support.
        encryption: Specifies the encryption requirements for connections to this
            endpoint.
        call_handler: What type of handler you want to run on inbound calls.
        call_request_url: The LaML URL to access when a call is received. Required when
            call_handler is laml_webhooks.
        call_request_method: The HTTP method to use with call_request_url.
        call_fallback_url: The LaML URL to access when the call to call_request_url
            fails. Required when call_handler is laml_webhooks.
        call_fallback_method: The HTTP method to use with call_fallback_url.
        call_status_callback_url: A URL to send status change messages to. Required when
            call_handler is laml_webhooks.
        call_status_callback_method: The HTTP method to use with
            call_status_callback_url.
        call_laml_application_id: The ID of the LaML application to forward incoming
            calls to. Required when call_handler is laml_application.
        call_dialogflow_agent_id: The ID of the Dialogflow agent to forward incoming
            calls to. Required when call_handler is dialogflow.
        call_relay_topic: The Relay topic to forward incoming calls to. Required when
            call_handler is relay_topic.
        call_relay_topic_status_callback_url: A URL to send status change messages to.
            Required when call_handler is relay_topic.
        call_relay_context: The Relay context to forward incoming calls to. Required
            when call_handler is relay_context.
        call_relay_context_status_callback_url: A URL to send status change messages to.
            Required when call_handler is relay_context.
        call_relay_application: The Relay application to forward incoming calls to.
            Required when call_handler is relay_application.
        call_video_room_id: The ID of the Video Room to forward incoming calls to.
            Required when call_handler is video_room.
        call_flow_id: The ID of the Call Flow to forward incoming calls to. Required
            when call_handler is call_flow.
        call_flow_version: The version of the Call Flow to use. Valid values are
            'working_copy' or 'current_deployed'.
        call_ai_agent_id: The ID of the AI Agent to forward incoming calls to. Required
            when call_handler is ai_agent.
        call_relay_script_url: A URL of a SWML script to respond to incoming calls.
            Required when call_handler is relay_script.
    """

    username: str
    password: str
    caller_id: str
    send_as: str
    ciphers: list[str]
    codecs: list[str]
    encryption: Literal["default", "required", "optional"]
    call_handler: Literal[
        "relay_context",
        "relay_topic",
        "relay_application",
        "relay_connector",
        "relay_script",
        "laml_webhooks",
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


class CreateVerifiedCallerIDRequest(TypedDict, total=False):
    """Request body for creating a verified caller ID.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        number: String representing the phone number for the caller ID. This must be a
            valid, routeable phone number in [E.164
            format](https://en.wikipedia.org/wiki/E.164) that is able to receive a voice
            phone call for verification.
        name: The name portion of the caller ID. If not provided, the default will be
            the formatted number.
        extension: The extension of the phone number for the caller ID. This is only
            used when placing the verification call.
    """

    number: str
    name: str
    extension: str


DomainAppCallHandler: TypeAlias = "Literal['relay_topic', 'relay_application', 'laml_webhooks', 'laml_application', 'video_room', 'relay_script', 'dialogflow', 'ai_agent', 'call_flow', 'relay_context', 'relay_connector', 'fabric_subscriber', 'sip_gateway', 'call_queue']"

DomainAppCallHandlerRequest: TypeAlias = "Literal['relay_topic', 'relay_application', 'laml_webhooks', 'laml_application', 'video_room', 'relay_script', 'dialogflow', 'ai_agent', 'call_flow', 'relay_context']"


class DomainApplication(TypedDict, total=False):
    """Domain application model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the domain application on SignalWire.
        type: A string representation of the type of object this record is.
        domain: The unique domain for this application, combining your space subdomain
            and identifier.
        name: A string representing the friendly name for this domain application.
        identifier: A string representing the identifier portion of the domain
            application.
        user: A string representing the user portion of the domain application.
        ip_auth_enabled: Whether the domain application will enforce IP authentication
            for incoming requests.
        ip_auth: A list containing whitelisted IP addresses and IP blocks used if
            ip_auth_enabled is true.
        call_handler: Specify how the domain application will handle calls.
        calling_handler_resource_id: The unique identifier of the calling handler
            resource.
        call_relay_topic: A string representing the Relay topic to forward incoming
            calls to.
        call_relay_topic_status_callback_url: A string representing a URL to send status
            change messages to.
        call_relay_context: Deprecated. Use call_relay_application instead. Deprecated.
        call_relay_context_status_callback_url: Deprecated. Use
            call_relay_topic_status_callback_url instead. Deprecated.
        call_request_url: A string representing the LaML URL to access when a call is
            received.
        call_request_method: A string representing the HTTP method to use with
            call_request_url.
        call_fallback_url: A string representing the LaML URL to access when the call to
            call_request_url fails.
        call_fallback_method: A string representing the HTTP method to use with
            call_fallback_url.
        call_status_callback_url: A string representing a URL to send status change
            messages to.
        call_status_callback_method: A string representing the HTTP method to use with
            call_status_callback_url.
        call_laml_application_id: A string representing the ID of the LaML application
            to forward incoming calls to.
        call_video_room_id: A string representing the ID of the Video Room to forward
            incoming calls to.
        call_relay_script_url: A string representing the URL of the Relay script to
            execute when a call is received.
        encryption: A string representing whether connections to this domain application
            require encryption or if encryption is optional. Valid values are optional,
            required, and forbidden.
        codecs: A list of codecs this domain application will support. Currently
            supported values are: OPUS, G722, PCMU, PCMA, G729, VP8, and H264.
        ciphers: A list of encryption ciphers this domain application will support.
            Currently supported values are: AEAD_AES_256_GCM_8, AES_256_CM_HMAC_SHA1_80,
            AES_CM_128_HMAC_SHA1_80, AES_256_CM_HMAC_SHA1_32, and
            AES_CM_128_HMAC_SHA1_32.
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
    call_request_method: Literal["GET", "POST"] | None
    call_fallback_url: str | None
    call_fallback_method: Literal["GET", "POST"] | None
    call_status_callback_url: str | None
    call_status_callback_method: Literal["GET", "POST"] | None
    call_laml_application_id: str | None
    call_video_room_id: uuid | None
    call_relay_script_url: str | None
    encryption: Literal["optional", "required", "forbidden"]
    codecs: list[str]
    ciphers: list[str]


class DomainApplicationListResponse(TypedDict, total=False):
    """Response containing a list of domain applications.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of domain applications.
    """

    links: PaginationLinks
    data: list[DomainApplication]


class DomainApplicationResponse(TypedDict, total=False):
    """Response containing a single domain application.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the domain application on SignalWire.
        type: A string representation of the type of object this record is.
        domain: The unique domain for this application, combining your space subdomain
            and identifier.
        name: A string representing the friendly name for this domain application.
        identifier: A string representing the identifier portion of the domain
            application.
        user: A string representing the user portion of the domain application.
        ip_auth_enabled: Whether the domain application will enforce IP authentication
            for incoming requests.
        ip_auth: A list containing whitelisted IP addresses and IP blocks used if
            ip_auth_enabled is true.
        call_handler: Specify how the domain application will handle calls.
        calling_handler_resource_id: The unique identifier of the calling handler
            resource.
        call_relay_topic: A string representing the Relay topic to forward incoming
            calls to.
        call_relay_topic_status_callback_url: A string representing a URL to send status
            change messages to.
        call_relay_context: Deprecated. Use call_relay_application instead. Deprecated.
        call_relay_context_status_callback_url: Deprecated. Use
            call_relay_topic_status_callback_url instead. Deprecated.
        call_request_url: A string representing the LaML URL to access when a call is
            received.
        call_request_method: A string representing the HTTP method to use with
            call_request_url.
        call_fallback_url: A string representing the LaML URL to access when the call to
            call_request_url fails.
        call_fallback_method: A string representing the HTTP method to use with
            call_fallback_url.
        call_status_callback_url: A string representing a URL to send status change
            messages to.
        call_status_callback_method: A string representing the HTTP method to use with
            call_status_callback_url.
        call_laml_application_id: A string representing the ID of the LaML application
            to forward incoming calls to.
        call_video_room_id: A string representing the ID of the Video Room to forward
            incoming calls to.
        call_relay_script_url: A string representing the URL of the Relay script to
            execute when a call is received.
        encryption: A string representing whether connections to this domain application
            require encryption or if encryption is optional. Valid values are optional,
            required, and forbidden.
        codecs: A list of codecs this domain application will support. Currently
            supported values are: OPUS, G722, PCMU, PCMA, G729, VP8, and H264.
        ciphers: A list of encryption ciphers this domain application will support.
            Currently supported values are: AEAD_AES_256_GCM_8, AES_256_CM_HMAC_SHA1_80,
            AES_CM_128_HMAC_SHA1_80, AES_256_CM_HMAC_SHA1_32, and
            AES_CM_128_HMAC_SHA1_32.
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
    call_request_method: Literal["GET", "POST"] | None
    call_fallback_url: str | None
    call_fallback_method: Literal["GET", "POST"] | None
    call_status_callback_url: str | None
    call_status_callback_method: Literal["GET", "POST"] | None
    call_laml_application_id: str | None
    call_video_room_id: uuid | None
    call_relay_script_url: str | None
    encryption: Literal["optional", "required", "forbidden"]
    codecs: list[str]
    ciphers: list[str]


HttpMethod: TypeAlias = "Literal['GET', 'POST']"


class ImportPhoneNumberRequest(TypedDict, total=False):
    """Request body for importing a phone number.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        number: The phone number to import in E.164 format. Number must be between 5 and
            30 characters with no special characters besides a leading +.
        number_type: The type of phone number being imported.
        capabilities: The capabilities to enable for this phone number. Can include any
            combination of SMS, Voice, Fax, and MMS. If not provided, defaults to all
            capabilities.
    """

    number: str
    number_type: Literal["longcode", "tollfree"]
    capabilities: list[Literal["sms", "voice", "fax", "mms"]]


LegalEntityType: TypeAlias = (
    "Literal['PRIVATE_PROFIT', 'PUBLIC_PROFIT', 'NON_PROFIT', 'GOVERNMENT']"
)


class MembershipPhoneNumber(TypedDict, total=False):
    """Phone number representation within a membership.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the phone number.
        name: The name given to the phone number.
        number: The phone number in E.164 format.
        capabilities: The capabilities of the phone number.
    """

    id: uuid
    name: str
    number: str
    capabilities: list[str]


class MfaRequest(TypedDict, total=False):
    """MFA request model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Wire-only keys (not valid Python identifiers, so they are listed here rather than as
    attributes; read them with item access):
    - ``from`` (``str``): The E164 number from your account to use as the origin of the
      message. SignalWire will use a special verified number if not specified.

    Attributes:
        to: The E164 number to use as the destination.
        message: Specify a custom message to send before the token. The message must fit
            within one segment; either 160 characters or 70 characters when using
            non-GSM symbols.
        token_length: The number of characters in the token, from 4 to 20. Defaults to
            6.
        valid_for: The number of seconds the token is considered valid for. Defaults to
            3600, with a maximum of 604800.
        max_attempts: The number of allowed verification attempts, including the first
            one, from 1 to 20. Defaults to 3.
        allow_alphas: Set to true or false, whether to include letters or just numbers
            in the token. Defaults to false (numbers only).
    """

    to: str
    # non-identifier field 'from': str
    message: str
    token_length: int
    valid_for: int
    max_attempts: int
    allow_alphas: bool


class MfaResponse(TypedDict, total=False):
    """MFA response model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The MFA request ID. Save this for verification.
        success: Whether the request was successfully queued.
        to: The destination of the MFA request.
        channel: Can be sms for a text message or call for a phone call.
    """

    id: uuid
    success: bool
    to: str
    channel: str


class MfaVerifyRequest(TypedDict, total=False):
    """MFA verification request model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        token: The token to verify.
    """

    token: str


class MfaVerifyResponse(TypedDict, total=False):
    """MFA verification response model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        success: Whether the token was successfully verified by the API. When
            `max_attempts` are reached or the request is no longer valid, the endpoint
            will return a `404 Not Found`.
    """

    success: bool


class NumberGroup(TypedDict, total=False):
    """Number group model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the Number Group on SignalWire. This can be used to
            update or delete the group programmatically.
        name: The name given to the number group. Helps to distinguish different groups
            within your project.
        sticky_sender: Whether the number group uses the same 'From' number for outbound
            requests to a number, or chooses a random one.
        phone_number_count: The number of phone numbers within the group.
    """

    id: uuid
    name: str
    sticky_sender: bool
    phone_number_count: int


class NumberGroupListResponse(TypedDict, total=False):
    """Response containing a list of number groups.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of number groups.
    """

    links: PaginationLinks
    data: list[NumberGroup]


class NumberGroupMembership(TypedDict, total=False):
    """Number group membership model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the Number Group Membership on SignalWire. This can
            be used to delete the membership programmatically.
        number_group_id: The unique identifier of the Number Group this membership is
            associated with.
        phone_number: A representation of the phone number this membership is associated
            with.
        created_at: The date and time when the membership was created.
        updated_at: The date and time when the membership was last updated.
    """

    id: uuid
    number_group_id: uuid
    phone_number: MembershipPhoneNumber
    created_at: str
    updated_at: str


class NumberGroupMembershipListResponse(TypedDict, total=False):
    """Response containing a list of number group memberships.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of number group memberships.
    """

    links: PaginationLinks
    data: list[NumberGroupMembership]


class NumberGroupMembershipResponse(TypedDict, total=False):
    """Response containing a single number group membership.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the Number Group Membership on SignalWire. This can
            be used to delete the membership programmatically.
        number_group_id: The unique identifier of the Number Group this membership is
            associated with.
        phone_number: A representation of the phone number this membership is associated
            with.
        created_at: The date and time when the membership was created.
        updated_at: The date and time when the membership was last updated.
    """

    id: uuid
    number_group_id: uuid
    phone_number: MembershipPhoneNumber
    created_at: str
    updated_at: str


class NumberGroupResponse(TypedDict, total=False):
    """Response containing a single number group.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the Number Group on SignalWire. This can be used to
            update or delete the group programmatically.
        name: The name given to the number group. Helps to distinguish different groups
            within your project.
        sticky_sender: Whether the number group uses the same 'From' number for outbound
            requests to a number, or chooses a random one.
        phone_number_count: The number of phone numbers within the group.
    """

    id: uuid
    name: str
    sticky_sender: bool
    phone_number_count: int


class Order(TypedDict, total=False):
    """Order model for campaign registry operations.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the order.
        state: The current state of the order.
        processed_at: Timestamp when the order was processed.
        created_at: Timestamp when the order was created.
        updated_at: Timestamp when the order was last updated.
        status_callback_url: Optional: Specify a URL to receive webhook notifications
            when your number assignment order and the number assignments that belong to
            it change state. See the [10DLC status
            callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
            docs for the webhook payload.
    """

    id: uuid
    state: str
    processed_at: str
    created_at: str
    updated_at: str
    status_callback_url: str


class OrderListResponse(TypedDict, total=False):
    """Response containing a list of orders.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of orders.
    """

    links: PaginationLinks
    data: list[Order]


class OrderResponse(TypedDict, total=False):
    """Response containing a single order.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the order.
        state: The current state of the order.
        processed_at: Timestamp when the order was processed.
        created_at: Timestamp when the order was created.
        updated_at: Timestamp when the order was last updated.
        status_callback_url: Optional: Specify a URL to receive webhook notifications
            when your number assignment order and the number assignments that belong to
            it change state. See the [10DLC status
            callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
            docs for the webhook payload.
    """

    id: uuid
    state: str
    processed_at: str
    created_at: str
    updated_at: str
    status_callback_url: str


class PaginationLinks(TypedDict, total=False):
    """Pagination links for list responses.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        self: Link to the current page.
        first: Link to the first page.
        next: Link to the next page. Only present when there are more results.
        prev: Link to the previous page. Only present when not on the first page.
    """

    self: str
    first: str
    next: str
    prev: str


class PhoneNumber(TypedDict, total=False):
    """Phone number model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the phone number.
        number: The phone number in E.164 format.
        name: The name given to the phone number. Helps to distinguish different phone
            numbers within your project.
        capabilities: A list of communication methods this phone number supports.
        number_type: The type of number this is defined as.
        e911_address_id: The E911 address ID associated with this phone number.
        created_at: The date the number was added to your project.
        updated_at: The date the number was last updated.
        next_billed_at: The next date the number will be billed for.
        call_handler: What type of handler you want to run on inbound calls.
        calling_handler_resource_id: The unique identifier of the calling handler
            resource.
        call_receive_mode: How do you want to receive the incoming call.
        call_request_url: The URL to make a request to when using the laml_webhooks call
            handler.
        call_request_method: The HTTP method to use when making a request to the
            call_request_url.
        call_fallback_url: The fallback URL to make a request to when using the
            laml_webhooks call handler and the call_request_url fails.
        call_fallback_method: The HTTP method to use when making a request to the
            call_fallback_url.
        call_status_callback_url: The URL to make status callbacks to when using the
            laml_webhooks call handler.
        call_status_callback_method: The HTTP method to use when making a request to the
            call_status_callback_url.
        call_laml_application_id: The ID of the LaML Application to use when using the
            laml_application call handler.
        call_dialogflow_agent_id: The ID of the Dialogflow Agent to start when using the
            dialogflow call handler.
        call_relay_topic: A string representing the Relay topic to forward incoming
            calls to. This is only used (and required) when call_handler is set to
            relay_topic.
        call_relay_topic_status_callback_url: A string representing a URL to send status
            change messages to. This is only used (and required) when call_handler is
            set to relay_topic.
        call_relay_script_url: The URL to make a request to when using the relay_script
            call handler. The URL must respond with a valid SWML script.
        call_relay_context: The name of the Relay Context to send this call to when
            using the relay_context call handler.
        call_relay_context_status_callback_url: A string representing a URL to send
            status change messages to. This is only used (and required) when
            call_handler is set to relay_context.
        call_relay_application: The name of the Relay Application to send this call to
            when using the relay_application call handler.
        call_relay_connector_id: The ID of the Relay Connector to send this call to when
            using the relay_connector call handler.
        call_sip_endpoint_id: The ID of the Relay SIP Endpoint to send this call to when
            using the relay_sip_endpoint call handler.
        call_verto_resource: The name of the Verto Relay Endpoint to send this call to
            when using the relay_verto_endpoint call handler.
        call_video_room_id: The ID of the Video Room to send this call to when using the
            video_room call handler.
        message_handler: What type of handler you want to run on inbound messages.
        messaging_handler_resource_id: The unique identifier of the messaging handler
            resource.
        message_request_url: The URL to make a request to when using the laml_webhooks
            message handler.
        message_request_method: The HTTP method to use when making a request to the
            message_request_url.
        message_fallback_url: The fallback URL to make a request to when using the
            laml_webhooks message handler and the message_request_url fails.
        message_fallback_method: The HTTP method to use when making a request to the
            message_fallback_url.
        message_laml_application_id: The ID of the LaML Application to use when using
            the laml_application message handler.
        message_relay_topic: The name of the Relay Topic to send this message to when
            using the relay_topic message handler.
        message_relay_context: The name of the Relay Context to send this message to
            when using the relay_context message handler.
        country_code: The ISO 3166-1 alpha-2 country code of the phone number.
    """

    id: uuid
    number: str
    name: str | None
    capabilities: list[PhoneNumberCapability]
    number_type: PhoneNumberType
    e911_address_id: uuid | None
    created_at: str
    updated_at: str
    next_billed_at: str | None
    call_handler: PhoneNumberCallHandler | None
    calling_handler_resource_id: uuid | None
    call_receive_mode: CallReceiveMode
    call_request_url: str | None
    call_request_method: HttpMethod | None
    call_fallback_url: str | None
    call_fallback_method: HttpMethod | None
    call_status_callback_url: str | None
    call_status_callback_method: HttpMethod | None
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
    message_handler: PhoneNumberMessageHandler | None
    messaging_handler_resource_id: uuid | None
    message_request_url: str | None
    message_request_method: HttpMethod | None
    message_fallback_url: str | None
    message_fallback_method: HttpMethod | None
    message_laml_application_id: str | None
    message_relay_topic: str | None
    message_relay_context: str | None
    country_code: str | None


PhoneNumberCallHandler: TypeAlias = "Literal['relay_context', 'relay_topic', 'relay_script', 'relay_application', 'relay_connector', 'relay_sip_endpoint', 'relay_verto_endpoint', 'laml_webhooks', 'laml_application', 'dialogflow', 'video_room', 'call_flow', 'ai_agent', 'fabric_subscriber', 'sip_gateway', 'call_queue']"

PhoneNumberCallHandlerRequest: TypeAlias = "Literal['relay_context', 'relay_topic', 'relay_script', 'relay_application', 'relay_connector', 'relay_sip_endpoint', 'relay_verto_endpoint', 'laml_webhooks', 'laml_application', 'dialogflow', 'video_room', 'ai_agent', 'call_flow']"


class PhoneNumberCapabilities(TypedDict, total=False):
    """Phone number capabilities.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        voice: Whether the phone number can receive voice calls.
        sms: Whether the phone number can send/receive SMS.
        mms: Whether the phone number can send/receive MMS.
        fax: Whether the phone number can send/receive fax.
    """

    voice: bool
    sms: bool
    mms: bool
    fax: bool


PhoneNumberCapability: TypeAlias = "Literal['voice', 'sms', 'mms', 'fax']"


class PhoneNumberListResponse(TypedDict, total=False):
    """Response containing a list of phone numbers.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of phone numbers.
    """

    links: PaginationLinks
    data: list[PhoneNumber]


class PhoneNumberLookupResponse(TypedDict, total=False):
    """Response containing phone number lookup result.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        country_code_number: The Country code associated with the number.
        national_number: Number in the countries national format.
        possible_number: Whether the number supplied is a possible number.
        valid_number: Whether the number supplied is a valid number.
        national_number_formatted: The E164 number formatted in national format.
        international_number_formatted: The E164 number formatted in international
            format.
        e164: The number in E164 format.
        location: The location of the number based on its area code and NPA.
        country_code: The ISO3166 alpha 2 country code associated with the number.
        timezones: The time zones associated with the number.
        number_type: The type of number based on its area code and NPA.
        carrier: Carrier information. Adding include=carrier to your request will do a
            live lookup to determine the current carrier information about this number.
        cnam: Caller ID information. Adding include=cnam to your request will do a live
            lookup to determine the current caller ID information about this number.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the phone number.
        number: The phone number in E.164 format.
        name: The name given to the phone number. Helps to distinguish different phone
            numbers within your project.
        capabilities: A list of communication methods this phone number supports.
        number_type: The type of number this is defined as.
        e911_address_id: The E911 address ID associated with this phone number.
        created_at: The date the number was added to your project.
        updated_at: The date the number was last updated.
        next_billed_at: The next date the number will be billed for.
        call_handler: What type of handler you want to run on inbound calls.
        calling_handler_resource_id: The unique identifier of the calling handler
            resource.
        call_receive_mode: How do you want to receive the incoming call.
        call_request_url: The URL to make a request to when using the laml_webhooks call
            handler.
        call_request_method: The HTTP method to use when making a request to the
            call_request_url.
        call_fallback_url: The fallback URL to make a request to when using the
            laml_webhooks call handler and the call_request_url fails.
        call_fallback_method: The HTTP method to use when making a request to the
            call_fallback_url.
        call_status_callback_url: The URL to make status callbacks to when using the
            laml_webhooks call handler.
        call_status_callback_method: The HTTP method to use when making a request to the
            call_status_callback_url.
        call_laml_application_id: The ID of the LaML Application to use when using the
            laml_application call handler.
        call_dialogflow_agent_id: The ID of the Dialogflow Agent to start when using the
            dialogflow call handler.
        call_relay_topic: A string representing the Relay topic to forward incoming
            calls to. This is only used (and required) when call_handler is set to
            relay_topic.
        call_relay_topic_status_callback_url: A string representing a URL to send status
            change messages to. This is only used (and required) when call_handler is
            set to relay_topic.
        call_relay_script_url: The URL to make a request to when using the relay_script
            call handler. The URL must respond with a valid SWML script.
        call_relay_context: The name of the Relay Context to send this call to when
            using the relay_context call handler.
        call_relay_context_status_callback_url: A string representing a URL to send
            status change messages to. This is only used (and required) when
            call_handler is set to relay_context.
        call_relay_application: The name of the Relay Application to send this call to
            when using the relay_application call handler.
        call_relay_connector_id: The ID of the Relay Connector to send this call to when
            using the relay_connector call handler.
        call_sip_endpoint_id: The ID of the Relay SIP Endpoint to send this call to when
            using the relay_sip_endpoint call handler.
        call_verto_resource: The name of the Verto Relay Endpoint to send this call to
            when using the relay_verto_endpoint call handler.
        call_video_room_id: The ID of the Video Room to send this call to when using the
            video_room call handler.
        message_handler: What type of handler you want to run on inbound messages.
        messaging_handler_resource_id: The unique identifier of the messaging handler
            resource.
        message_request_url: The URL to make a request to when using the laml_webhooks
            message handler.
        message_request_method: The HTTP method to use when making a request to the
            message_request_url.
        message_fallback_url: The fallback URL to make a request to when using the
            laml_webhooks message handler and the message_request_url fails.
        message_fallback_method: The HTTP method to use when making a request to the
            message_fallback_url.
        message_laml_application_id: The ID of the LaML Application to use when using
            the laml_application message handler.
        message_relay_topic: The name of the Relay Topic to send this message to when
            using the relay_topic message handler.
        message_relay_context: The name of the Relay Context to send this message to
            when using the relay_context message handler.
        country_code: The ISO 3166-1 alpha-2 country code of the phone number.
    """

    id: uuid
    number: str
    name: str | None
    capabilities: list[PhoneNumberCapability]
    number_type: PhoneNumberType
    e911_address_id: uuid | None
    created_at: str
    updated_at: str
    next_billed_at: str | None
    call_handler: PhoneNumberCallHandler | None
    calling_handler_resource_id: uuid | None
    call_receive_mode: CallReceiveMode
    call_request_url: str | None
    call_request_method: HttpMethod | None
    call_fallback_url: str | None
    call_fallback_method: HttpMethod | None
    call_status_callback_url: str | None
    call_status_callback_method: HttpMethod | None
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
    message_handler: PhoneNumberMessageHandler | None
    messaging_handler_resource_id: uuid | None
    message_request_url: str | None
    message_request_method: HttpMethod | None
    message_fallback_url: str | None
    message_fallback_method: HttpMethod | None
    message_laml_application_id: str | None
    message_relay_topic: str | None
    message_relay_context: str | None
    country_code: str | None


PhoneNumberType: TypeAlias = "Literal['toll-free', 'longcode']"


class PstnRecording(TypedDict, total=False):
    """Recording from a PSTN call leg.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique ID of the recording.
        project_id: Unique ID of the project.
        created_at: Date and time when the recording was created.
        updated_at: Date and time when the recording was last updated.
        duration_in_seconds: Duration of the recording in seconds.
        error_code: Error code if the recording failed.
        price: Price of the recording.
        price_unit: Currency unit for the price.
        status: Status of the recording.
        url: URL of the recording file.
        stereo: Indicates whether the recording is stereo.
        byte_size: Size of the recording file in bytes.
        track: Audio track of the recording.
        relay_pstn_leg_id: ID of the PSTN leg associated with the recording.
    """

    id: uuid
    project_id: uuid
    created_at: str
    updated_at: str
    duration_in_seconds: int
    error_code: str
    price: float
    price_unit: str
    status: str
    url: str
    stereo: bool
    byte_size: int
    track: str
    relay_pstn_leg_id: uuid


class PurchasePhoneNumberRequest(TypedDict, total=False):
    """Request body for purchasing a phone number.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        number: The phone number in E164 format.
    """

    number: str


class Queue(TypedDict, total=False):
    """Queue model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the queue.
        project_id: The project ID associated with this queue.
        friendly_name: The friendly name of the queue.
        max_size: The maximum number of callers allowed in the queue.
        current_size: The current number of callers in the queue.
        average_wait_time: The average wait time in seconds.
        uri: The URL of this queue.
        date_created: Timestamp when the queue was created.
        date_updated: Timestamp when the queue was last updated.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of queues.
    """

    links: PaginationLinks
    data: list[Queue]


class QueueMember(TypedDict, total=False):
    """Queue member model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        call_id: The call ID of the queue member.
        project_id: The ID of the project associated with this queue member.
        queue_id: The ID of the queue associated with this queue member.
        position: Queue member position in the queue.
        uri: The URL of this queue member.
        wait_time: Wait time in seconds since the member was enqueued. If not yet
            enqueued, it will be null.
        date_enqueued: When the queue member was last enqueued.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of queue members.
    """

    links: PaginationLinks
    data: list[QueueMember]


class QueueMemberResponse(TypedDict, total=False):
    """Response containing a single queue member.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        call_id: The call ID of the queue member.
        project_id: The ID of the project associated with this queue member.
        queue_id: The ID of the queue associated with this queue member.
        position: Queue member position in the queue.
        uri: The URL of this queue member.
        wait_time: Wait time in seconds since the member was enqueued. If not yet
            enqueued, it will be null.
        date_enqueued: When the queue member was last enqueued.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the queue.
        project_id: The project ID associated with this queue.
        friendly_name: The friendly name of the queue.
        max_size: The maximum number of callers allowed in the queue.
        current_size: The current number of callers in the queue.
        average_wait_time: The average wait time in seconds.
        uri: The URL of this queue.
        date_created: Timestamp when the queue was created.
        date_updated: Timestamp when the queue was last updated.
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


Recording: TypeAlias = "PstnRecording | SipRecording | WebRtcRecording"


class RecordingListResponse(TypedDict, total=False):
    """Response containing a list of recordings.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of recordings.
    """

    links: PaginationLinks
    data: list[Recording]


class ShortCode(TypedDict, total=False):
    """Short code model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the short code.
        name: The name given to the short code.
        number: The short code number.
        capabilities: The messaging capabilities of the short code.
        number_type: The type of number (always 'shortcode').
        code_type: The type of short code.
        country_code: The ISO 3166-1 alpha-2 country code.
        created_at: The date and time when the short code was created.
        updated_at: The date and time when the short code was last updated.
        next_billed_at: The date and time when the short code will next be billed.
        lease_duration: The lease duration of the short code (e.g., '12 months').
        message_handler: The message handler type for incoming messages.
        message_request_url: The URL to send message requests to when using
            laml_webhooks handler.
        message_request_method: The HTTP method to use for message requests.
        message_fallback_url: The fallback URL for message requests.
        message_fallback_method: The HTTP method to use for fallback requests.
        message_laml_application_id: The ID of the LāML application to handle messages
            when using laml_application handler.
        message_relay_context: The Relay context to use when using relay_context
            handler.
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
    message_request_method: HttpMethod | None
    message_fallback_url: str | None
    message_fallback_method: HttpMethod | None
    message_laml_application_id: uuid | None
    message_relay_context: str | None


ShortCodeCapability: TypeAlias = "Literal['sms', 'mms']"


class ShortCodeListResponse(TypedDict, total=False):
    """Response containing a list of short codes.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of short codes.
    """

    links: PaginationLinks
    data: list[ShortCode]


ShortCodeMessageHandler: TypeAlias = (
    "Literal['relay_context', 'laml_webhooks', 'laml_application']"
)


class ShortCodeResponse(TypedDict, total=False):
    """Response containing a single short code.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: The unique identifier of the short code.
        name: The name given to the short code.
        number: The short code number.
        capabilities: The messaging capabilities of the short code.
        number_type: The type of number (always 'shortcode').
        code_type: The type of short code.
        country_code: The ISO 3166-1 alpha-2 country code.
        created_at: The date and time when the short code was created.
        updated_at: The date and time when the short code was last updated.
        next_billed_at: The date and time when the short code will next be billed.
        lease_duration: The lease duration of the short code (e.g., '12 months').
        message_handler: The message handler type for incoming messages.
        message_request_url: The URL to send message requests to when using
            laml_webhooks handler.
        message_request_method: The HTTP method to use for message requests.
        message_fallback_url: The fallback URL for message requests.
        message_fallback_method: The HTTP method to use for fallback requests.
        message_laml_application_id: The ID of the LāML application to handle messages
            when using laml_application handler.
        message_relay_context: The Relay context to use when using relay_context
            handler.
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
    message_request_method: HttpMethod | None
    message_fallback_url: str | None
    message_fallback_method: HttpMethod | None
    message_laml_application_id: uuid | None
    message_relay_context: str | None


ShortCodeType: TypeAlias = "Literal['vanity', 'random']"


class SipEndpoint(TypedDict, total=False):
    """SIP endpoint model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        type: A string representation of the type of object this record is.
        id: The unique identifier of the SIP endpoint.
        username: The username for the SIP endpoint.
        caller_id: Friendly Caller ID used as the CNAM when dialing a phone number or
            the From when dialing another SIP Endpoint.
        send_as: When dialing a PSTN phone number, you must send it From a number you
            have purchased or verified. send_as indicates which number this endpoint has
            set as its origination. random indicates it will randomly choose a purchased
            or verified number from within the project.
        ciphers: A list of encryption ciphers this endpoint will support.
        codecs: A list of codecs this endpoint will support.
        encryption: Whether connections to this endpoint require encryption or if
            encryption is optional.
        call_handler: What type of handler you want to run on inbound calls.
        calling_handler_resource_id: The unique identifier of the calling handler
            resource.
        call_request_url: A string representing the LaML URL to access when a call is
            received. This is only used (and required) when call_handler is set to
            laml_webhooks.
        call_request_method: A string representing the HTTP method to use with
            call_request_url. Valid values are GET and POST.
        call_fallback_url: A string representing the LaML URL to access when the call to
            call_request_url fails. This is only used (and required) when call_handler
            is set to laml_webhooks.
        call_fallback_method: A string representing the HTTP method to use with
            call_fallback_url. Valid values are GET and POST.
        call_status_callback_url: A string representing a URL to send status change
            messages to. This is only used (and required) when call_handler is set to
            laml_webhooks.
        call_status_callback_method: A string representing the HTTP method to use with
            call_status_callback_url. Valid values are GET and POST.
        call_laml_application_id: A string representing the ID of the LaML application
            to forward incoming calls to. This is only used (and required) when
            call_handler is set to laml_application.
        call_dialogflow_agent_id: A string representing the ID of the Dialogflow agent
            to forward incoming calls to. This is only used (and required) when
            call_handler is set to dialogflow.
        call_relay_topic: A string representing the Relay topic to forward incoming
            calls to. This is only used (and required) when call_handler is set to
            relay_topic.
        call_relay_topic_status_callback_url: A string representing a URL to send status
            change messages to. This is only used (and required) when call_handler is
            set to relay_topic.
        call_relay_context: A string representing the Relay context to forward incoming
            calls to. This is only used (and required) when call_handler is set to
            relay_context.
        call_relay_context_status_callback_url: A string representing a URL to send
            status change messages to. This is only used (and required) when
            call_handler is set to relay_context.
        call_relay_application: A string representing the Relay application to forward
            incoming calls to. This is only used (and required) when call_handler is set
            to relay_application.
        call_video_room_id: A string representing the ID of the Video Room to forward
            incoming calls to. This is only used (and required) when call_handler is set
            to video_room.
        call_relay_script_url: A string representing a URL of a SWML script to respond
            to incoming calls. This is only used (and required) when call_handler is set
            to relay_script.
    """

    type: str
    id: uuid
    username: str
    caller_id: str | None
    send_as: str
    ciphers: list[str]
    codecs: list[str]
    encryption: Literal["default", "required", "optional"]
    call_handler: SipEndpointCallHandler | None
    calling_handler_resource_id: uuid | None
    call_request_url: str | None
    call_request_method: Literal["GET", "POST"] | None
    call_fallback_url: str | None
    call_fallback_method: Literal["GET", "POST"] | None
    call_status_callback_url: str | None
    call_status_callback_method: Literal["GET", "POST"] | None
    call_laml_application_id: str | None
    call_dialogflow_agent_id: str | None
    call_relay_topic: str | None
    call_relay_topic_status_callback_url: str | None
    call_relay_context: str | None
    call_relay_context_status_callback_url: str | None
    call_relay_application: str | None
    call_video_room_id: uuid | None
    call_relay_script_url: str | None


SipEndpointCallHandler: TypeAlias = "Literal['relay_context', 'relay_topic', 'relay_application', 'relay_connector', 'relay_script', 'laml_webhooks', 'laml_application', 'dialogflow', 'video_room', 'call_flow', 'ai_agent']"


class SipEndpointListResponse(TypedDict, total=False):
    """Response containing a list of SIP endpoints.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of SIP endpoints.
    """

    links: PaginationLinks
    data: list[SipEndpoint]


class SipEndpointResponse(TypedDict, total=False):
    """Response containing a single SIP endpoint.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        type: A string representation of the type of object this record is.
        id: The unique identifier of the SIP endpoint.
        username: The username for the SIP endpoint.
        caller_id: Friendly Caller ID used as the CNAM when dialing a phone number or
            the From when dialing another SIP Endpoint.
        send_as: When dialing a PSTN phone number, you must send it From a number you
            have purchased or verified. send_as indicates which number this endpoint has
            set as its origination. random indicates it will randomly choose a purchased
            or verified number from within the project.
        ciphers: A list of encryption ciphers this endpoint will support.
        codecs: A list of codecs this endpoint will support.
        encryption: Whether connections to this endpoint require encryption or if
            encryption is optional.
        call_handler: What type of handler you want to run on inbound calls.
        calling_handler_resource_id: The unique identifier of the calling handler
            resource.
        call_request_url: A string representing the LaML URL to access when a call is
            received. This is only used (and required) when call_handler is set to
            laml_webhooks.
        call_request_method: A string representing the HTTP method to use with
            call_request_url. Valid values are GET and POST.
        call_fallback_url: A string representing the LaML URL to access when the call to
            call_request_url fails. This is only used (and required) when call_handler
            is set to laml_webhooks.
        call_fallback_method: A string representing the HTTP method to use with
            call_fallback_url. Valid values are GET and POST.
        call_status_callback_url: A string representing a URL to send status change
            messages to. This is only used (and required) when call_handler is set to
            laml_webhooks.
        call_status_callback_method: A string representing the HTTP method to use with
            call_status_callback_url. Valid values are GET and POST.
        call_laml_application_id: A string representing the ID of the LaML application
            to forward incoming calls to. This is only used (and required) when
            call_handler is set to laml_application.
        call_dialogflow_agent_id: A string representing the ID of the Dialogflow agent
            to forward incoming calls to. This is only used (and required) when
            call_handler is set to dialogflow.
        call_relay_topic: A string representing the Relay topic to forward incoming
            calls to. This is only used (and required) when call_handler is set to
            relay_topic.
        call_relay_topic_status_callback_url: A string representing a URL to send status
            change messages to. This is only used (and required) when call_handler is
            set to relay_topic.
        call_relay_context: A string representing the Relay context to forward incoming
            calls to. This is only used (and required) when call_handler is set to
            relay_context.
        call_relay_context_status_callback_url: A string representing a URL to send
            status change messages to. This is only used (and required) when
            call_handler is set to relay_context.
        call_relay_application: A string representing the Relay application to forward
            incoming calls to. This is only used (and required) when call_handler is set
            to relay_application.
        call_video_room_id: A string representing the ID of the Video Room to forward
            incoming calls to. This is only used (and required) when call_handler is set
            to video_room.
        call_relay_script_url: A string representing a URL of a SWML script to respond
            to incoming calls. This is only used (and required) when call_handler is set
            to relay_script.
    """

    type: str
    id: uuid
    username: str
    caller_id: str | None
    send_as: str
    ciphers: list[str]
    codecs: list[str]
    encryption: Literal["default", "required", "optional"]
    call_handler: SipEndpointCallHandler | None
    calling_handler_resource_id: uuid | None
    call_request_url: str | None
    call_request_method: Literal["GET", "POST"] | None
    call_fallback_url: str | None
    call_fallback_method: Literal["GET", "POST"] | None
    call_status_callback_url: str | None
    call_status_callback_method: Literal["GET", "POST"] | None
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        domain: A string representation of the fully qualified domain name for this
            profile.
        domain_identifier: String representing the domain_identifier portion of the
            profile. Must be unique across your project.
        default_codecs: A list of codecs this profile will support. Currently supported
            values are: OPUS, G722, PCMU, PCMA, VP8, H264.
        default_ciphers: A list of encryption ciphers this profile will support.
            Currently supported values are: AEAD_AES_256_GCM_8, AES_256_CM_HMAC_SHA1_80,
            AES_CM_128_HMAC_SHA1_80, AES_256_CM_HMAC_SHA1_32, AES_CM_128_HMAC_SHA1_32.
        default_encryption: A string representing whether connections to an endpoint
            that uses this profile require encryption or if encryption is optional.
            Encryption will always be used if possible. Possible values are required or
            optional.
        default_send_as: The e164 formatted number you wish to set as the originating
            number when dialing PSTN phone numbers from a SIP Endpoint that uses this
            profile. Specify null or an empty string to randomly choose a purchased or
            verified number from within the project.
    """

    domain: str
    domain_identifier: str
    default_codecs: list[str]
    default_ciphers: list[str]
    default_encryption: Literal["required", "optional"]
    default_send_as: str


class SipRecording(TypedDict, total=False):
    """Recording from a SIP call leg.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique ID of the recording.
        project_id: Unique ID of the project.
        created_at: Date and time when the recording was created.
        updated_at: Date and time when the recording was last updated.
        duration_in_seconds: Duration of the recording in seconds.
        error_code: Error code if the recording failed.
        price: Price of the recording.
        price_unit: Currency unit for the price.
        status: Status of the recording.
        url: URL of the recording file.
        stereo: Indicates whether the recording is stereo.
        byte_size: Size of the recording file in bytes.
        track: Audio track of the recording.
        relay_sip_leg_id: ID of the SIP leg associated with the recording.
    """

    id: uuid
    project_id: uuid
    created_at: str
    updated_at: str
    duration_in_seconds: int
    error_code: str
    price: float
    price_unit: str
    status: str
    url: str
    stereo: bool
    byte_size: int
    track: str
    relay_sip_leg_id: uuid


class Types_StatusCodes_SpaceApiErrorItem(TypedDict, total=False):
    """Details about a specific validation error.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        detail: A description of what caused the error.
        status: The HTTP status code.
        title: A short summary of the error type.
        code: The error code.
    """

    detail: str
    status: str
    title: str
    code: str


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


class Types_StatusCodes_ValidationError(TypedDict, total=False):
    """The request failed validation.

    See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        errors: List of validation errors.
    """

    errors: list[Types_StatusCodes_SpaceApiErrorItem]


class UpdateCampaignRequest(TypedDict, total=False):
    """Request body for updating a campaign.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: A name for the campaign.
    """

    name: str


class UpdateDomainApplicationRequest(TypedDict, total=False):
    """Request body for updating a domain application.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: A string representing the friendly name for this domain application.
        identifier: A string representing the identifier portion of the domain
            application.
        user: A string representing the user portion of the domain application.
        ip_auth_enabled: Whether the domain application will enforce IP authentication
            for incoming requests.
        ip_auth: A list containing whitelisted IP addresses and IP blocks used if
            ip_auth_enabled is true.
        encryption: Whether connections to this domain application require encryption or
            if encryption is optional.
        codecs: A list of codecs this domain application will support.
        ciphers: A list of encryption ciphers this domain application will support.
        call_handler: Specify how the domain application will handle calls.
        call_relay_topic: A string representing the Relay topic to forward incoming
            calls to.
        call_relay_topic_status_callback_url: A string representing a URL to send status
            change messages to.
        call_relay_application: A string representing the Relay Application to forward
            incoming calls to.
        call_request_url: A string representing the LaML URL to access when a call is
            received.
        call_request_method: A string representing the HTTP method to use with
            call_request_url.
        call_fallback_url: A string representing the LaML URL to access when the call to
            call_request_url fails.
        call_fallback_method: A string representing the HTTP method to use with
            call_fallback_url.
        call_status_callback_url: A string representing a URL to send status change
            messages to.
        call_status_callback_method: A string representing the HTTP method to use with
            call_status_callback_url.
        call_laml_application_id: A string representing the ID of the LaML application
            to forward incoming calls to.
        call_video_room_id: A string representing the ID of the Video Room to forward
            incoming calls to.
        call_relay_script_url: A string representing the URL of the Relay script to
            execute when a call is received.
        call_dialogflow_agent_id: A string representing the ID of the Dialogflow Agent
            to forward incoming calls to.
        call_ai_agent_id: A string representing the ID of the AI Agent to forward
            incoming calls to.
        call_flow_id: A string representing the ID of the Call Flow to forward incoming
            calls to.
        call_flow_version: A string representing the version of your Call Flow you'd
            like to use.
        call_relay_context: This handler type is deprecated. Please use
            call_relay_application or call_relay_topic instead. Deprecated.
        call_relay_context_status_callback_url: This property is deprecated. Please use
            call_relay_topic_status_callback_url instead. Deprecated.
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
    call_dialogflow_agent_id: uuid
    call_ai_agent_id: uuid
    call_flow_id: uuid
    call_flow_version: Literal["working_copy", "current_deployed"]
    call_relay_context: str
    call_relay_context_status_callback_url: str


class UpdateNumberGroupRequest(TypedDict, total=False):
    """Request body for updating a number group.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: The name given to the number group. Helps to distinguish different groups
            within your project.
        sticky_sender: Whether the number group uses the same 'From' number for outbound
            requests to a number, or chooses a random one.
    """

    name: str
    sticky_sender: bool


class UpdatePhoneNumberRequest(TypedDict, total=False):
    """Request body for updating a phone number.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: The friendly name for the phone number.
        call_handler: The call handler for the phone number.
        call_receive_mode: The call receive mode for the phone number.
        call_request_url: The call request URL for the phone number.
        call_request_method: The call request method for the phone number.
        call_fallback_url: The call fallback URL for the phone number.
        call_fallback_method: The call fallback method for the phone number.
        call_status_callback_url: The call status callback URL for the phone number.
        call_status_callback_method: The call status callback method for the phone
            number.
        call_laml_application_id: The ID of the LaML Application to use when using the
            laml_application call handler.
        call_dialogflow_agent_id: The ID of the Dialogflow Agent to start when using the
            dialogflow call handler.
        call_relay_topic: A string representing the Relay topic to forward incoming
            calls to.
        call_relay_topic_status_callback_url: A string representing a URL to send status
            change messages to when call_handler is set to relay_topic.
        call_relay_script_url: The URL to make a request to when using the relay_script
            call handler.
        call_relay_context: This handler type is deprecated. Please use
            call_relay_application or call_relay_topic instead. Deprecated.
        call_relay_context_status_callback_url: This property is deprecated. Please use
            call_relay_topic_status_callback_url instead. Deprecated.
        call_relay_application: A string representing the Relay Application to forward
            incoming calls to.
        call_relay_connector_id: The ID of the Relay Connector to use when using the
            relay_connector call handler.
        call_sip_endpoint_id: The ID of the SIP Endpoint to use when using the
            relay_sip_endpoint call handler.
        call_verto_resource: The Verto resource to use when using the
            relay_verto_endpoint call handler.
        call_video_room_id: The ID of the Video Room to forward incoming calls to when
            using the video_room call handler.
        call_ai_agent_id: The ID of the AI Agent to forward incoming calls to when using
            the ai_agent call handler.
        call_flow_id: The ID of the Call Flow to forward incoming calls to when using
            the call_flow call handler.
        call_flow_version: The Call Flow version to use when using the call_flow call
            handler.
        message_handler: The message handler for the phone number.
        message_request_url: The message request URL for the phone number.
        message_request_method: The message request method for the phone number.
        message_fallback_url: The message fallback URL for the phone number.
        message_fallback_method: The message fallback method for the phone number.
        message_laml_application_id: The ID of the LaML Application to use for messages.
        message_relay_topic: A string representing the Relay topic to forward incoming
            messages to.
        message_relay_context: This handler type is deprecated. Please use
            message_relay_application or message_relay_topic instead. Deprecated.
        message_relay_application: A string representing the Relay Application to
            forward incoming messages to.
    """

    name: str
    call_handler: PhoneNumberCallHandlerRequest
    call_receive_mode: str
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: The name of the queue.
        max_size: The maximum number of callers allowed in the queue.
    """

    name: str
    max_size: int


class UpdateShortCodeRequest(TypedDict, total=False):
    """Request body for updating a short code.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: The name given to the short code.
        message_handler: The message handler type for incoming messages.
        message_request_url: The URL to send message requests to when using
            laml_webhooks handler.
        message_request_method: The HTTP method to use for message requests. Defaults to
            POST.
        message_fallback_url: The fallback URL for message requests.
        message_fallback_method: The HTTP method to use for fallback requests. Defaults
            to POST.
        message_laml_application_id: The ID of the LāML application to handle messages
            when using laml_application handler.
        message_relay_context: The Relay context to use when using relay_context
            handler.
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

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        username: String representing the username portion of the endpoint. Must be
            unique across your project and must not contain white space characters or @.
        password: A password to authenticate registrations to this endpoint.
        caller_id: Friendly Caller ID used as the CNAM when dialing a phone number or
            the From when dialing another SIP Endpoint.
        send_as: When dialing a PSTN phone number, you must send it From a number you
            have purchased or verified. send_as indicates which number this endpoint has
            set as its origination. random indicates it will randomly choose a purchased
            or verified number from within the project.
        ciphers: A list of encryption ciphers this endpoint will support.
        codecs: A list of codecs this endpoint will support.
        encryption: Specifies the encryption requirements for connections to this
            endpoint.
        call_handler: What type of handler you want to run on inbound calls.
        call_request_url: The LaML URL to access when a call is received. Required when
            call_handler is laml_webhooks.
        call_request_method: The HTTP method to use with call_request_url.
        call_fallback_url: The LaML URL to access when the call to call_request_url
            fails. Required when call_handler is laml_webhooks.
        call_fallback_method: The HTTP method to use with call_fallback_url.
        call_status_callback_url: A URL to send status change messages to. Required when
            call_handler is laml_webhooks.
        call_status_callback_method: The HTTP method to use with
            call_status_callback_url.
        call_laml_application_id: The ID of the LaML application to forward incoming
            calls to. Required when call_handler is laml_application.
        call_dialogflow_agent_id: The ID of the Dialogflow agent to forward incoming
            calls to. Required when call_handler is dialogflow.
        call_relay_topic: The Relay topic to forward incoming calls to. Required when
            call_handler is relay_topic.
        call_relay_topic_status_callback_url: A URL to send status change messages to.
            Required when call_handler is relay_topic.
        call_relay_context: The Relay context to forward incoming calls to. Required
            when call_handler is relay_context.
        call_relay_context_status_callback_url: A URL to send status change messages to.
            Required when call_handler is relay_context.
        call_relay_application: The Relay application to forward incoming calls to.
            Required when call_handler is relay_application.
        call_video_room_id: The ID of the Video Room to forward incoming calls to.
            Required when call_handler is video_room.
        call_flow_id: The ID of the Call Flow to forward incoming calls to. Required
            when call_handler is call_flow.
        call_flow_version: The version of the Call Flow to use. Valid values are
            'working_copy' or 'current_deployed'.
        call_ai_agent_id: The ID of the AI Agent to forward incoming calls to. Required
            when call_handler is ai_agent.
        call_relay_script_url: A URL of a SWML script to respond to incoming calls.
            Required when call_handler is relay_script.
    """

    username: str
    password: str
    caller_id: str
    send_as: str
    ciphers: list[str]
    codecs: list[str]
    encryption: Literal["default", "required", "optional"]
    call_handler: Literal[
        "relay_context",
        "relay_topic",
        "relay_application",
        "relay_connector",
        "relay_script",
        "laml_webhooks",
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


class UpdateSipProfileRequest(TypedDict, total=False):
    """Request body for updating the SIP profile.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        domain_identifier: String representing the domain_identifier portion of the
            profile. Must be unique across your project.
        default_codecs: A list of codecs this profile will support. Currently supported
            values are: OPUS, G722, PCMU, PCMA, VP8, H264.
        default_ciphers: A list of encryption ciphers this profile will support.
            Currently supported values are: AEAD_AES_256_GCM_8, AES_256_CM_HMAC_SHA1_80,
            AES_CM_128_HMAC_SHA1_80, AES_256_CM_HMAC_SHA1_32, AES_CM_128_HMAC_SHA1_32.
        default_encryption: A string representing whether connections to an endpoint
            that uses this profile require encryption or if encryption is optional.
            Encryption will always be used if possible. Possible values are required or
            optional.
        default_send_as: The e164 formatted number you wish to set as the originating
            number when dialing PSTN phone numbers from a SIP Endpoint that uses this
            profile. Specify null or an empty string to randomly choose a purchased or
            verified number from within the project.
    """

    domain_identifier: str
    default_codecs: list[str]
    default_ciphers: list[str]
    default_encryption: Literal["required", "optional"]
    default_send_as: str


class UpdateVerifiedCallerIDRequest(TypedDict, total=False):
    """Request body for updating a verified caller ID.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        name: The name portion of the caller ID.
    """

    name: str


class VerifiedCallerID(TypedDict, total=False):
    """Verified caller ID model.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        type: The type of the returned object, this should be verified_caller_id.
        id: The unique identifier of the Verified Caller ID on SignalWire.
        number: String representing the phone number for the caller ID. This must be a
            valid, routeable phone number in E.164 format.
        name: String representing the name portion of the caller ID. If not provided,
            the default will be the formatted number that has been provided.
        extension: String representing the extension of the phone number for the caller
            ID. This is only used when placing the verification call.
        verified: A boolean representing whether the number has been verified or not.
        verified_at: Nullable DateTime field representing the date and time that the
            number was verified. If the number has not been verified, it will be null.
        status: The verification status for the caller ID.
    """

    type: str
    id: uuid
    number: str
    name: str
    extension: str
    verified: bool
    verified_at: str
    status: Literal["Verified", "Awaiting Verification"]


class VerifiedCallerIDListResponse(TypedDict, total=False):
    """Response containing a list of verified caller IDs.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        links: Pagination links.
        data: List of verified caller IDs.
    """

    links: PaginationLinks
    data: list[VerifiedCallerID]


class VerifiedCallerIDResponse(TypedDict, total=False):
    """Response containing a single verified caller ID.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        type: The type of the returned object, this should be verified_caller_id.
        id: The unique identifier of the Verified Caller ID on SignalWire.
        number: String representing the phone number for the caller ID. This must be a
            valid, routeable phone number in E.164 format.
        name: String representing the name portion of the caller ID. If not provided,
            the default will be the formatted number that has been provided.
        extension: String representing the extension of the phone number for the caller
            ID. This is only used when placing the verification call.
        verified: A boolean representing whether the number has been verified or not.
        verified_at: Nullable DateTime field representing the date and time that the
            number was verified. If the number has not been verified, it will be null.
        status: The verification status for the caller ID.
    """

    type: str
    id: uuid
    number: str
    name: str
    extension: str
    verified: bool
    verified_at: str
    status: Literal["Verified", "Awaiting Verification"]


class VerifyCallerIDRequest(TypedDict, total=False):
    """Request body for verifying a caller ID.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        verification_code: The verification code received via call or SMS.
    """

    verification_code: str


class WebRtcRecording(TypedDict, total=False):
    """Recording from a WebRTC call leg.

    Open shape: extra server keys are permitted and partial payloads are valid; not
    validated at runtime (a TypedDict is a plain ``dict``).

    Attributes:
        id: Unique ID of the recording.
        project_id: Unique ID of the project.
        created_at: Date and time when the recording was created.
        updated_at: Date and time when the recording was last updated.
        duration_in_seconds: Duration of the recording in seconds.
        error_code: Error code if the recording failed.
        price: Price of the recording.
        price_unit: Currency unit for the price.
        status: Status of the recording.
        url: URL of the recording file.
        stereo: Indicates whether the recording is stereo.
        byte_size: Size of the recording file in bytes.
        track: Audio track of the recording.
        relay_webrtc_leg_id: ID of the WebRTC leg associated with the recording.
    """

    id: uuid
    project_id: uuid
    created_at: str
    updated_at: str
    duration_in_seconds: int
    error_code: str
    price: float
    price_unit: str
    status: str
    url: str
    stereo: bool
    byte_size: int
    track: str
    relay_webrtc_leg_id: uuid


uuid: TypeAlias = "str"

ListAddressesResponse: TypeAlias = "AddressListResponse"
CreateAddressResponse: TypeAlias = "AddressResponse"
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
ListQueuesResponse: TypeAlias = "QueueListResponse"
CreateQueueResponse: TypeAlias = "QueueResponse"
GetQueueResponse: TypeAlias = "QueueResponse"
UpdateQueueResponse: TypeAlias = "QueueResponse"
ListQueueMembersResponse: TypeAlias = "QueueMemberListResponse"
RetrieveNextQueueMemberResponse: TypeAlias = "QueueMemberResponse"
RetrieveQueueMemberResponse: TypeAlias = "QueueMemberResponse"
ListRecordingsResponse: TypeAlias = "RecordingListResponse"
GetRecordingResponse: TypeAlias = "PstnRecording | SipRecording | WebRtcRecording"
ListBrandsResponse: TypeAlias = "BrandListResponse"
CreateBrandRequest: TypeAlias = "CreateManagedBrandRequest | CreateCspBrandRequest"
CreateBrandResponse: TypeAlias = "BrandResponse"
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
    """Call handler type for phone number update requests.

    Attributes:
        RELAY_CONTEXT: The wire value ``relay_context``.
        RELAY_TOPIC: The wire value ``relay_topic``.
        RELAY_SCRIPT: The wire value ``relay_script``.
        RELAY_APPLICATION: The wire value ``relay_application``.
        RELAY_CONNECTOR: The wire value ``relay_connector``.
        RELAY_SIP_ENDPOINT: The wire value ``relay_sip_endpoint``.
        RELAY_VERTO_ENDPOINT: The wire value ``relay_verto_endpoint``.
        LAML_WEBHOOKS: The wire value ``laml_webhooks``.
        LAML_APPLICATION: The wire value ``laml_application``.
        DIALOGFLOW: The wire value ``dialogflow``.
        VIDEO_ROOM: The wire value ``video_room``.
        AI_AGENT: The wire value ``ai_agent``.
        CALL_FLOW: The wire value ``call_flow``.
    """

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
