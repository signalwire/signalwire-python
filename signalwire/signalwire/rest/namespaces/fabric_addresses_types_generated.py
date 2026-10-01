# AUTO-GENERATED from porting-sdk/rest-apis/fabric-addresses/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict

Codec: TypeAlias = "Literal['OPUS', 'G722', 'PCMU', 'PCMA', 'G729', 'VP8', 'H264']"

SrtpCipher: TypeAlias = "Literal['AEAD_AES_256_GCM_8', 'AES_256_CM_HMAC_SHA1_80', 'AES_CM_128_HMAC_SHA1_80', 'AES_256_CM_HMAC_SHA1_32', 'AES_CM_128_HMAC_SHA1_32']"

SipEncryption: TypeAlias = "Literal['required', 'optional', 'forbidden']"

HandlerType: TypeAlias = "Literal['calling', 'messaging']"

Channel: TypeAlias = "Literal['audio', 'messaging', 'video']"

AddressContext: TypeAlias = "Literal['public', 'private']"

DisplayType: TypeAlias = "Literal['app', 'room', 'call', 'subscriber']"


class PaginationLinks(TypedDict, total=False):
    """Cursor-pagination links for a page of results.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    self: str
    first: str
    next: str
    prev: str


class SipAddress(TypedDict, total=False):
    """A Call Fabric SIP address and its SIP configuration.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    type: Literal["sip_address"]
    resource_id: str
    name: str
    display_name: str
    context: str
    uri: str
    user: str
    encryption: SipEncryption
    codecs: list[Codec]
    ciphers: list[SrtpCipher]
    ip_auth_enabled: bool
    ip_auth: list[str]
    calling_handler_resource_id: str
    created_at: str
    updated_at: str


class SipAddressCreate(TypedDict, total=False):
    """Request body for creating a SIP address.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    user: str
    context_id: str
    calling_handler_resource_id: str
    ip_auth_enabled: bool
    ip_auth: list[str]
    codecs: list[Codec]
    ciphers: list[SrtpCipher]
    encryption: SipEncryption
    password: str


class SipAddressUpdate(TypedDict, total=False):
    """Partial update; omitted fields keep their current value. `calling_handler_resource_id` is not editable.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    user: str
    context_id: str
    ip_auth_enabled: bool
    ip_auth: list[str]
    codecs: list[Codec]
    ciphers: list[SrtpCipher]
    encryption: SipEncryption
    password: str


class SipAddressList(TypedDict, total=False):
    """A page of SIP addresses.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    items_count: int
    data: list[SipAddress]


class SipAddressCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class SipAddressUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class PhoneNumberAddress(TypedDict, total=False):
    """A Call Fabric address backed by an owned phone number, representing one channel (calling or messaging) routing to a handler resource.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    type: Literal["phone_number_address"]
    handler_type: HandlerType
    resource_id: str | None
    name: str
    phone_number: str
    phone_number_id: str
    created_at: str
    updated_at: str


class PhoneNumberAddressCreate(TypedDict, total=False):
    """Reference the owned number by `phone_number_id` or `number` (at least one is required).

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    phone_number_id: str
    number: str
    resource_id: str
    handler_type: HandlerType


class PhoneNumberAddressUpdate(TypedDict, total=False):
    """Partial update; omitted fields keep their current value. `handler_type` is not editable. Provide `name` (rename) and/or `resource_id` (re-point).

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    resource_id: str


class PhoneNumberAddressList(TypedDict, total=False):
    """A page of phone number addresses.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    items_count: int
    data: list[PhoneNumberAddress]


class PhoneNumberAddressCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class PhoneNumberAddressUpdateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class AliasAddress(TypedDict, total=False):
    """A named, context-scoped alias route that forwards to a handler resource.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    type: Literal["alias_address"]
    resource_id: str
    name: str
    display_name: str
    display_type: DisplayType
    channels: list[Channel]
    codecs: list[Codec]
    context: AddressContext
    uri: str
    created_at: str
    updated_at: str


class AliasAddressCreate(TypedDict, total=False):
    """Request body for creating an alias address.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    resource_id: str
    display_name: str
    channels: list[Channel]
    codecs: list[Codec]
    context: AddressContext


class AliasAddressUpdate(TypedDict, total=False):
    """Partial update; omitted fields keep their current value. `resource_id` is not accepted (the handler is create-only).

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    display_name: str
    channels: list[Channel]
    codecs: list[Codec]
    context: AddressContext


class AliasAddressList(TypedDict, total=False):
    """A page of alias addresses.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: PaginationLinks
    items_count: int
    data: list[AliasAddress]


class AliasAddressCreateStatusCode422(TypedDict, total=False):
    """The request contains invalid parameters. See errors for details.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    errors: list[Types_StatusCodes_RestApiErrorItem]


class AliasAddressUpdateStatusCode422(TypedDict, total=False):
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


class Types_StatusCodes_StatusCode401(TypedDict, total=False):
    """Access is unauthorized (missing/invalid credentials, a token without a Call Fabric scope, or a subdomain that does not match the token's project).

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


ListSipAddressesResponse: TypeAlias = "SipAddressList"
CreateSipAddressRequest: TypeAlias = "SipAddressCreate"
CreateSipAddressResponse: TypeAlias = "SipAddress"
GetSipAddressResponse: TypeAlias = "SipAddress"
UpdateSipAddressRequest: TypeAlias = "SipAddressUpdate"
UpdateSipAddressResponse: TypeAlias = "SipAddress"
ListPhoneNumberAddressesResponse: TypeAlias = "PhoneNumberAddressList"
CreatePhoneNumberAddressRequest: TypeAlias = "PhoneNumberAddressCreate"
CreatePhoneNumberAddressResponse: TypeAlias = "PhoneNumberAddress"
GetPhoneNumberAddressResponse: TypeAlias = "PhoneNumberAddress"
UpdatePhoneNumberAddressRequest: TypeAlias = "PhoneNumberAddressUpdate"
UpdatePhoneNumberAddressResponse: TypeAlias = "PhoneNumberAddress"
ListAliasAddressesResponse: TypeAlias = "AliasAddressList"
CreateAliasAddressRequest: TypeAlias = "AliasAddressCreate"
CreateAliasAddressResponse: TypeAlias = "AliasAddress"
GetAliasAddressResponse: TypeAlias = "AliasAddress"
UpdateAliasAddressRequest: TypeAlias = "AliasAddressUpdate"
UpdateAliasAddressResponse: TypeAlias = "AliasAddress"
