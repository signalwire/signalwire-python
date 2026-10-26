# AUTO-GENERATED from porting-sdk/rest-apis/relay-rest/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
"""Typed ``relay-rest`` REST resources, generated from the OpenAPI spec.

One resource class per spec collection: closed, typed ``create`` / ``update``
parameters (the explicit spec fields) and typed sub-operation methods, plus an
``extras`` escape hatch and a ``**_reserved_kw`` tail for unknown or reserved-word
wire fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast
from collections.abc import Mapping

from .._base import BaseResource, CrudResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .relay_rest_types_generated import (
        AddressListResponse,
        AddressResponse,
        AddressType,
        AssignedNumberListResponse,
        AvailablePhoneNumbersResponse,
        BrandListResponse,
        BrandResponse,
        CampaignListResponse,
        CampaignResponse,
        CreateCspBrandRequest,
        CreateManagedBrandRequest,
        CreateManagedCampaignRequest,
        CreateNumberGroupRequest,
        CreatePartnerCampaignRequest,
        CreateQueueRequest,
        CreateVerifiedCallerIDRequest,
        HttpMethod,
        MfaResponse,
        MfaVerifyResponse,
        NumberGroupListResponse,
        NumberGroupMembershipListResponse,
        NumberGroupMembershipResponse,
        NumberGroupResponse,
        OrderListResponse,
        OrderResponse,
        PhoneNumberCallHandlerRequest,
        PhoneNumberListResponse,
        PhoneNumberLookupResponse,
        PhoneNumberMessageHandler,
        PhoneNumberResponse,
        PurchasePhoneNumberRequest,
        QueueListResponse,
        QueueMemberListResponse,
        QueueMemberResponse,
        QueueResponse,
        RecordingListResponse,
        ShortCodeListResponse,
        ShortCodeMessageHandler,
        ShortCodeResponse,
        SipProfileResponse,
        UpdateNumberGroupRequest,
        UpdatePhoneNumberRequest,
        UpdateQueueRequest,
        UpdateVerifiedCallerIDRequest,
        VerifiedCallerIDListResponse,
        VerifiedCallerIDResponse,
        uuid,
    )


class Addresses(BaseResource):
    """Typed resource for ``/addresses`` (generated).

    Bound to ``/api/relay/rest/addresses``; construct it as ``Addresses(http)`` with the
    client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/addresses")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> AddressListResponse:
        """Returns a list of your Addresses.

        The addresses are returned sorted by creation date, with the most recent
        appearing first.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``filter_label``: Filter addresses by label (partial match).
                - ``page_number``: The page number to retrieve (0-indexed).
                - ``page_size``: The number of items per page (1-1000).
                - ``page_token``: Token for cursor-based pagination. Required when
                  page_number > 0.

        Returns:
            Response containing a list of addresses.
        """
        return cast(
            "AddressListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def create(
        self,
        *,
        label: str,
        country: str,
        first_name: str,
        last_name: str,
        street_number: str,
        street_name: str,
        city: str,
        state: str,
        postal_code: str,
        address_type: AddressType | None = None,
        address_number: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> AddressResponse:
        """To create a new Address, make a POST request to the Address resource.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            label: A friendly name given to the address to help distinguish and search
                for different addresses within your project.
            country: The ISO 3166 Alpha 2 country code.
            first_name: First name of the occupant associated with this address.
            last_name: Last name of the occupant associated with this address.
            street_number: The number portion of the street address.
            street_name: The name portion of the street address.
            city: The city portion of the street address.
            state: The state/province/region of the street address. In the USA and
                Canada, use the two-letter abbreviated form.
            postal_code: The postal code of the street address.
            address_type: If the address is divided into multiple sub-addresses, this
                identifies how the address is divided. Possible values are: Apartment,
                Basement, Building, Department, Floor, Office, Penthouse, Suite,
                Trailer, Unit.
            address_number: If the address is divided into multiple sub-addresses, this
                identifies the particular sub-address.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single address.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "label": label,
                "country": country,
                "first_name": first_name,
                "last_name": last_name,
                "street_number": street_number,
                "street_name": street_name,
                "address_type": address_type,
                "address_number": address_number,
                "city": city,
                "state": state,
                "postal_code": postal_code,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "AddressResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> AddressResponse:
        """Retrieves the details of an Address that has been previously created.

        Use the unique ID that was returned from your previous request to identify the
        specific instance.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the address.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            Response containing a single address.
        """
        return cast(
            "AddressResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        """Permanently deletes an Address.

        It cannot be undone.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the address.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The decoded JSON response (an empty dict when the server sends no body).
        """
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )


class ImportedNumbers(BaseResource):
    """Typed resource for ``/imported_phone_numbers`` (generated).

    Bound to ``/api/relay/rest/imported_phone_numbers``; construct it as
    ``ImportedNumbers(http)`` with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/imported_phone_numbers")

    def create(
        self,
        *,
        number: str,
        number_type: Literal["longcode", "tollfree"],
        capabilities: list[Literal["sms", "voice", "fax", "mms"]] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> PhoneNumberResponse:
        """Import a phone number hosted elsewhere into your SignalWire Space.

        **Note:** This is a **Partner API**. To enable it on your SignalWire Space,
        contact [Sales](https://signalwire.com/company/contact).

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            number: The phone number to import in E.164 format. Number must be between 5
                and 30 characters with no special characters besides a leading +.
            number_type: The type of phone number being imported.
            capabilities: The capabilities to enable for this phone number. Can include
                any combination of SMS, Voice, Fax, and MMS. If not provided, defaults
                to all capabilities.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single phone number.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "number": number,
                "number_type": number_type,
                "capabilities": capabilities,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "PhoneNumberResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )


class Lookup(BaseResource):
    """Typed resource for ``/lookup`` (generated).

    Bound to ``/api/relay/rest/lookup``; construct it as ``Lookup(http)`` with the
    client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/lookup")

    def phone_number(
        self,
        e164_number: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> PhoneNumberLookupResponse:
        """This endpoint allows you to look up validity and formatting information about a number.

        You can optionally lookup additional information about the number such as
        carrier and caller ID data.

        **Permissions**

        No API token scope is required to make a successful request to this endpoint.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            e164_number: The phone number in E.164 format.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``include``: Further number information to include in the response,
                  some of which are billable. You can specify: carrier (Lookup full
                  carrier information for the number), cnam (Lookup Caller ID
                  information for the number). Separate multiple values with a comma:
                  include=carrier,cnam.

        Returns:
            Response containing phone number lookup result.
        """
        return cast(
            "PhoneNumberLookupResponse",
            self._http.get(
                self._path("phone_number", e164_number),
                params=params or None,
                request_options=request_options,
            ),
        )


class Mfa(BaseResource):
    """Typed resource for ``/mfa`` (generated).

    Bound to ``/api/relay/rest/mfa``; construct it as ``Mfa(http)`` with the client's
    HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/mfa")

    def sms(
        self,
        *,
        to: str,
        from_: str | None = None,
        message: str | None = None,
        token_length: int | None = None,
        valid_for: int | None = None,
        max_attempts: int | None = None,
        allow_alphas: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> MfaResponse:
        """Sends a multi-factor authentication code via SMS.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Management_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            to: The E164 number to use as the destination.
            from_: The E164 number from your account to use as the origin of the
                message. SignalWire will use a special verified number if not specified.
                Sent as the wire key ``from``.
            message: Specify a custom message to send before the token. The message must
                fit within one segment; either 160 characters or 70 characters when
                using non-GSM symbols.
            token_length: The number of characters in the token, from 4 to 20. Defaults
                to 6.
            valid_for: The number of seconds the token is considered valid for. Defaults
                to 3600, with a maximum of 604800.
            max_attempts: The number of allowed verification attempts, including the
                first one, from 1 to 20. Defaults to 3.
            allow_alphas: Set to true or false, whether to include letters or just
                numbers in the token. Defaults to false (numbers only).
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            MFA response model.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "to": to,
                "from": from_,
                "message": message,
                "token_length": token_length,
                "valid_for": valid_for,
                "max_attempts": max_attempts,
                "allow_alphas": allow_alphas,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "MfaResponse",
            self._http.post(
                self._path("sms"), body=body, request_options=request_options
            ),
        )

    def call(
        self,
        *,
        to: str,
        from_: str | None = None,
        message: str | None = None,
        token_length: int | None = None,
        valid_for: int | None = None,
        max_attempts: int | None = None,
        allow_alphas: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> MfaResponse:
        """Sends a multi-factor authentication code via voice call.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Management_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            to: The E164 number to use as the destination.
            from_: The E164 number from your account to use as the origin of the
                message. SignalWire will use a special verified number if not specified.
                Sent as the wire key ``from``.
            message: Specify a custom message to send before the token. The message must
                fit within one segment; either 160 characters or 70 characters when
                using non-GSM symbols.
            token_length: The number of characters in the token, from 4 to 20. Defaults
                to 6.
            valid_for: The number of seconds the token is considered valid for. Defaults
                to 3600, with a maximum of 604800.
            max_attempts: The number of allowed verification attempts, including the
                first one, from 1 to 20. Defaults to 3.
            allow_alphas: Set to true or false, whether to include letters or just
                numbers in the token. Defaults to false (numbers only).
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            MFA response model.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "to": to,
                "from": from_,
                "message": message,
                "token_length": token_length,
                "valid_for": valid_for,
                "max_attempts": max_attempts,
                "allow_alphas": allow_alphas,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "MfaResponse",
            self._http.post(
                self._path("call"), body=body, request_options=request_options
            ),
        )

    def verify(
        self,
        mfa_request_id: str,
        *,
        token: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> MfaVerifyResponse:
        """Verifies a multi-factor authentication code.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Management_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            mfa_request_id: The MFA request ID.
            token: The token to verify.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            MFA verification response model.
        """
        body: dict[str, Any] = {
            k: v for k, v in {"token": token}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "MfaVerifyResponse",
            self._http.post(
                self._path(mfa_request_id, "verify"),
                body=body,
                request_options=request_options,
            ),
        )


class NumberGroups(
    CrudResource[
        "NumberGroupListResponse",
        "NumberGroupResponse",
        "CreateNumberGroupRequest",
        "UpdateNumberGroupRequest",
    ]
):
    """Typed resource for ``/number_groups`` (generated).

    Bound to ``/api/relay/rest/number_groups``; construct it as ``NumberGroups(http)``
    with the client's HTTP transport.
    """

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/number_groups")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        sticky_sender: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> NumberGroupResponse:
        """Creates a new number group.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            name: The name given to the number group. Helps to distinguish different
                groups within your project.
            sticky_sender: Whether the number group uses the same 'From' number for
                outbound requests to a number, or chooses a random one.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single number group.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "sticky_sender": sticky_sender}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "NumberGroupResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        sticky_sender: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> NumberGroupResponse:
        """Updates a number group.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the number group.
            name: The name given to the number group. Helps to distinguish different
                groups within your project.
            sticky_sender: Whether the number group uses the same 'From' number for
                outbound requests to a number, or chooses a random one.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single number group.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "sticky_sender": sticky_sender}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "NumberGroupResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_memberships(
        self,
        number_group_id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> NumberGroupMembershipListResponse:
        """Returns a list of phone numbers in a number group.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            number_group_id: Unique ID of the number group.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: The page number to retrieve.
                - ``page_size``: The number of results per page.
                - ``page_token``: Token for cursor-based pagination.

        Returns:
            Response containing a list of number group memberships.
        """
        return cast(
            "NumberGroupMembershipListResponse",
            self._http.get(
                self._path(number_group_id, "number_group_memberships"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def add_membership(
        self,
        number_group_id: str,
        *,
        phone_number_id: uuid,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> NumberGroupMembershipResponse:
        """Adds a phone number to a number group.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            number_group_id: Unique ID of the number group.
            phone_number_id: The phone number ID to add to the group.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single number group membership.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {"phone_number_id": phone_number_id}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "NumberGroupMembershipResponse",
            self._http.post(
                self._path(number_group_id, "number_group_memberships"),
                body=body,
                request_options=request_options,
            ),
        )

    def get_membership(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> NumberGroupMembershipResponse:
        """Retrieves the details of a number group membership.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the number group membership.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            Response containing a single number group membership.
        """
        return cast(
            "NumberGroupMembershipResponse",
            self._http.get(
                f"/api/relay/rest/number_group_memberships/{id}",
                params=params or None,
                request_options=request_options,
            ),
        )

    def delete_membership(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        """Removes a phone number from a number group.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the number group membership.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The decoded JSON response (an empty dict when the server sends no body).
        """
        return cast(
            "dict[str, Any]",
            self._http.delete(
                f"/api/relay/rest/number_group_memberships/{id}",
                request_options=request_options,
            ),
        )


class PhoneNumbers(
    CrudResource[
        "PhoneNumberListResponse",
        "PhoneNumberResponse",
        "PurchasePhoneNumberRequest",
        "UpdatePhoneNumberRequest",
    ]
):
    """Typed resource for ``/phone_numbers`` (generated).

    Bound to ``/api/relay/rest/phone_numbers``; construct it as ``PhoneNumbers(http)``
    with the client's HTTP transport.
    """

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/phone_numbers")

    def create(  # type: ignore[override]
        self,
        *,
        number: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> PhoneNumberResponse:
        """Purchases a phone number.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            number: The phone number in E164 format.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single phone number.
        """
        body: dict[str, Any] = {
            k: v for k, v in {"number": number}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "PhoneNumberResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        call_handler: PhoneNumberCallHandlerRequest | None = None,
        call_receive_mode: str | None = None,
        call_request_url: str | None = None,
        call_request_method: Literal["GET", "POST"] | None = None,
        call_fallback_url: str | None = None,
        call_fallback_method: Literal["GET", "POST"] | None = None,
        call_status_callback_url: str | None = None,
        call_status_callback_method: Literal["GET", "POST"] | None = None,
        call_laml_application_id: str | None = None,
        call_dialogflow_agent_id: str | None = None,
        call_relay_topic: str | None = None,
        call_relay_topic_status_callback_url: str | None = None,
        call_relay_script_url: str | None = None,
        call_relay_context: str | None = None,
        call_relay_context_status_callback_url: str | None = None,
        call_relay_application: str | None = None,
        call_relay_connector_id: str | None = None,
        call_sip_endpoint_id: str | None = None,
        call_verto_resource: str | None = None,
        call_video_room_id: uuid | None = None,
        call_ai_agent_id: uuid | None = None,
        call_flow_id: uuid | None = None,
        call_flow_version: Literal["working_copy", "current_deployed"] | None = None,
        message_handler: PhoneNumberMessageHandler | None = None,
        message_request_url: str | None = None,
        message_request_method: Literal["GET", "POST"] | None = None,
        message_fallback_url: str | None = None,
        message_fallback_method: Literal["GET", "POST"] | None = None,
        message_laml_application_id: str | None = None,
        message_relay_topic: str | None = None,
        message_relay_context: str | None = None,
        message_relay_application: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> PhoneNumberResponse:
        """Updates a phone number.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the phone number.
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
            call_laml_application_id: The ID of the LaML Application to use when using
                the laml_application call handler.
            call_dialogflow_agent_id: The ID of the Dialogflow Agent to start when using
                the dialogflow call handler.
            call_relay_topic: A string representing the Relay topic to forward incoming
                calls to.
            call_relay_topic_status_callback_url: A string representing a URL to send
                status change messages to when call_handler is set to relay_topic.
            call_relay_script_url: The URL to make a request to when using the
                relay_script call handler.
            call_relay_context: This handler type is deprecated. Please use
                call_relay_application or call_relay_topic instead. Deprecated.
            call_relay_context_status_callback_url: This property is deprecated. Please
                use call_relay_topic_status_callback_url instead. Deprecated.
            call_relay_application: A string representing the Relay Application to
                forward incoming calls to.
            call_relay_connector_id: The ID of the Relay Connector to use when using the
                relay_connector call handler.
            call_sip_endpoint_id: The ID of the SIP Endpoint to use when using the
                relay_sip_endpoint call handler.
            call_verto_resource: The Verto resource to use when using the
                relay_verto_endpoint call handler.
            call_video_room_id: The ID of the Video Room to forward incoming calls to
                when using the video_room call handler.
            call_ai_agent_id: The ID of the AI Agent to forward incoming calls to when
                using the ai_agent call handler.
            call_flow_id: The ID of the Call Flow to forward incoming calls to when
                using the call_flow call handler.
            call_flow_version: The Call Flow version to use when using the call_flow
                call handler.
            message_handler: The message handler for the phone number.
            message_request_url: The message request URL for the phone number.
            message_request_method: The message request method for the phone number.
            message_fallback_url: The message fallback URL for the phone number.
            message_fallback_method: The message fallback method for the phone number.
            message_laml_application_id: The ID of the LaML Application to use for
                messages.
            message_relay_topic: A string representing the Relay topic to forward
                incoming messages to.
            message_relay_context: This handler type is deprecated. Please use
                message_relay_application or message_relay_topic instead. Deprecated.
            message_relay_application: A string representing the Relay Application to
                forward incoming messages to.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single phone number.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "call_handler": call_handler,
                "call_receive_mode": call_receive_mode,
                "call_request_url": call_request_url,
                "call_request_method": call_request_method,
                "call_fallback_url": call_fallback_url,
                "call_fallback_method": call_fallback_method,
                "call_status_callback_url": call_status_callback_url,
                "call_status_callback_method": call_status_callback_method,
                "call_laml_application_id": call_laml_application_id,
                "call_dialogflow_agent_id": call_dialogflow_agent_id,
                "call_relay_topic": call_relay_topic,
                "call_relay_topic_status_callback_url": call_relay_topic_status_callback_url,
                "call_relay_script_url": call_relay_script_url,
                "call_relay_context": call_relay_context,
                "call_relay_context_status_callback_url": call_relay_context_status_callback_url,
                "call_relay_application": call_relay_application,
                "call_relay_connector_id": call_relay_connector_id,
                "call_sip_endpoint_id": call_sip_endpoint_id,
                "call_verto_resource": call_verto_resource,
                "call_video_room_id": call_video_room_id,
                "call_ai_agent_id": call_ai_agent_id,
                "call_flow_id": call_flow_id,
                "call_flow_version": call_flow_version,
                "message_handler": message_handler,
                "message_request_url": message_request_url,
                "message_request_method": message_request_method,
                "message_fallback_url": message_fallback_url,
                "message_fallback_method": message_fallback_method,
                "message_laml_application_id": message_laml_application_id,
                "message_relay_topic": message_relay_topic,
                "message_relay_context": message_relay_context,
                "message_relay_application": message_relay_application,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "PhoneNumberResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def search(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> AvailablePhoneNumbersResponse:
        """Searches for available phone numbers to purchase.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``areacode``: An areacode to search within.
                - ``number_type``: Search for either local or toll-free numbers.
                  Defaults to local.
                - ``starts_with``: A string of 3 to 7 digits that should be used as the
                  start of a number. Cannot be used in combination with contains or
                  ends_with.
                - ``contains``: A string of 3 to 7 digits that should appear somewhere
                  in the number. Cannot be used in combination with starts_with or
                  ends_with.
                - ``ends_with``: A string of 3 to 7 digits that should be used as the
                  end of a number. Cannot be used in combination with starts_with or
                  contains.
                - ``max_results``: The maximum number of matches to return. Upper limit
                  of 100. Defaults to 50.
                - ``region``: A region or state to search within. Must be an ISO 3166-2
                  alpha-2 code, i.e. TX for Texas. Cannot be used in combination with
                  areacode.
                - ``city``: A specific City to search within. Must be used in
                  combination with region. Cannot be used in combination with areacode,
                  starts_with, contains, or ends_with.

        Returns:
            Response containing available phone numbers for purchase.
        """
        return cast(
            "AvailablePhoneNumbersResponse",
            self._http.get(
                self._path("search"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def set_swml_webhook(
        self,
        resource_id: str,
        url: str,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        """Route calls on this resource to the ``relay_script`` handler.

        Convenience wrapper around ``update()``: sets ``call_handler`` to
        ``relay_script`` and maps the arguments below onto the matching request fields.

        Args:
            resource_id: The ID of the resource to update.
            url: The URL to make a request to when using the relay_script call handler.
                Sets ``call_relay_script_url``.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **extra: Further fields forwarded to ``update()`` alongside the handler
                settings.

        Returns:
            Response containing a single phone number.
        """
        body: dict[str, Any] = {"call_handler": "relay_script"}
        body["call_relay_script_url"] = url
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)

    def set_cxml_webhook(
        self,
        resource_id: str,
        url: str,
        fallback_url: str | None = None,
        status_callback_url: str | None = None,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        """Route calls on this resource to the ``laml_webhooks`` handler.

        Convenience wrapper around ``update()``: sets ``call_handler`` to
        ``laml_webhooks`` and maps the arguments below onto the matching request fields.

        Args:
            resource_id: The ID of the resource to update.
            url: The call request URL for the phone number. Sets ``call_request_url``.
            fallback_url: The call fallback URL for the phone number. Sets
                ``call_fallback_url``.
            status_callback_url: The call status callback URL for the phone number. Sets
                ``call_status_callback_url``.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **extra: Further fields forwarded to ``update()`` alongside the handler
                settings.

        Returns:
            Response containing a single phone number.
        """
        body: dict[str, Any] = {"call_handler": "laml_webhooks"}
        body["call_request_url"] = url
        if fallback_url is not None:
            body["call_fallback_url"] = fallback_url
        if status_callback_url is not None:
            body["call_status_callback_url"] = status_callback_url
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)

    def set_cxml_application(
        self,
        resource_id: str,
        application_id: str,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        """Route calls on this resource to the ``laml_application`` handler.

        Convenience wrapper around ``update()``: sets ``call_handler`` to
        ``laml_application`` and maps the arguments below onto the matching request
        fields.

        Args:
            resource_id: The ID of the resource to update.
            application_id: The ID of the LaML Application to use when using the
                laml_application call handler. Sets ``call_laml_application_id``.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **extra: Further fields forwarded to ``update()`` alongside the handler
                settings.

        Returns:
            Response containing a single phone number.
        """
        body: dict[str, Any] = {"call_handler": "laml_application"}
        body["call_laml_application_id"] = application_id
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)

    def set_ai_agent(
        self,
        resource_id: str,
        agent_id: uuid,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        """Route calls on this resource to the ``ai_agent`` handler.

        Convenience wrapper around ``update()``: sets ``call_handler`` to ``ai_agent``
        and maps the arguments below onto the matching request fields.

        Args:
            resource_id: The ID of the resource to update.
            agent_id: The ID of the AI Agent to forward incoming calls to when using the
                ai_agent call handler. Sets ``call_ai_agent_id``.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **extra: Further fields forwarded to ``update()`` alongside the handler
                settings.

        Returns:
            Response containing a single phone number.
        """
        body: dict[str, Any] = {"call_handler": "ai_agent"}
        body["call_ai_agent_id"] = agent_id
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)

    def set_call_flow(
        self,
        resource_id: str,
        flow_id: uuid,
        version: Literal["working_copy", "current_deployed"] | None = None,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        """Route calls on this resource to the ``call_flow`` handler.

        Convenience wrapper around ``update()``: sets ``call_handler`` to ``call_flow``
        and maps the arguments below onto the matching request fields.

        Args:
            resource_id: The ID of the resource to update.
            flow_id: The ID of the Call Flow to forward incoming calls to when using the
                call_flow call handler. Sets ``call_flow_id``.
            version: The Call Flow version to use when using the call_flow call handler.
                Sets ``call_flow_version``.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **extra: Further fields forwarded to ``update()`` alongside the handler
                settings.

        Returns:
            Response containing a single phone number.
        """
        body: dict[str, Any] = {"call_handler": "call_flow"}
        body["call_flow_id"] = flow_id
        if version is not None:
            body["call_flow_version"] = version
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)

    def set_relay_application(
        self,
        resource_id: str,
        name: str,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        """Route calls on this resource to the ``relay_application`` handler.

        Convenience wrapper around ``update()``: sets ``call_handler`` to
        ``relay_application`` and maps the arguments below onto the matching request
        fields.

        Args:
            resource_id: The ID of the resource to update.
            name: A string representing the Relay Application to forward incoming calls
                to. Sets ``call_relay_application``.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **extra: Further fields forwarded to ``update()`` alongside the handler
                settings.

        Returns:
            Response containing a single phone number.
        """
        body: dict[str, Any] = {"call_handler": "relay_application"}
        body["call_relay_application"] = name
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)

    def set_relay_topic(
        self,
        resource_id: str,
        topic: str,
        status_callback_url: str | None = None,
        *,
        request_options: RequestOptions | None = None,
        **extra: Any,
    ) -> PhoneNumberResponse:
        """Route calls on this resource to the ``relay_topic`` handler.

        Convenience wrapper around ``update()``: sets ``call_handler`` to
        ``relay_topic`` and maps the arguments below onto the matching request fields.

        Args:
            resource_id: The ID of the resource to update.
            topic: A string representing the Relay topic to forward incoming calls to.
                Sets ``call_relay_topic``.
            status_callback_url: A string representing a URL to send status change
                messages to when call_handler is set to relay_topic. Sets
                ``call_relay_topic_status_callback_url``.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **extra: Further fields forwarded to ``update()`` alongside the handler
                settings.

        Returns:
            Response containing a single phone number.
        """
        body: dict[str, Any] = {"call_handler": "relay_topic"}
        body["call_relay_topic"] = topic
        if status_callback_url is not None:
            body["call_relay_topic_status_callback_url"] = status_callback_url
        body.update(extra)
        return self.update(resource_id, request_options=request_options, **body)


class Queues(
    CrudResource[
        "QueueListResponse", "QueueResponse", "CreateQueueRequest", "UpdateQueueRequest"
    ]
):
    """Typed resource for ``/queues`` (generated).

    Bound to ``/api/relay/rest/queues``; construct it as ``Queues(http)`` with the
    client's HTTP transport.
    """

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/queues")

    def create(
        self,
        *,
        name: str | None = None,
        max_size: int | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> QueueResponse:
        """Creates a new queue.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            name: The name of the queue.
            max_size: The maximum number of callers allowed in the queue.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single queue.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "max_size": max_size}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "QueueResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        max_size: int | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> QueueResponse:
        """Updates a queue.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the queue.
            name: The name of the queue.
            max_size: The maximum number of callers allowed in the queue.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single queue.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "max_size": max_size}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "QueueResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_members(
        self,
        queue_id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> QueueMemberListResponse:
        """Returns a list of members in a queue.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            queue_id: Unique ID of the queue.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            Response containing a list of queue members.
        """
        return cast(
            "QueueMemberListResponse",
            self._http.get(
                self._path(queue_id, "members"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def get_next_member(
        self,
        queue_id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> QueueMemberResponse:
        """Retrieves the next member in the queue without dequeuing.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            queue_id: Unique ID of the queue.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            Response containing a single queue member.
        """
        return cast(
            "QueueMemberResponse",
            self._http.get(
                self._path(queue_id, "members", "next"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def get_member(
        self,
        queue_id: str,
        id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> QueueMemberResponse:
        """Retrieves the details of a queue member.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            queue_id: Unique ID of the queue.
            id: The unique identifier (ID) of the queue member.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            Response containing a single queue member.
        """
        return cast(
            "QueueMemberResponse",
            self._http.get(
                self._path(queue_id, "members", id),
                params=params or None,
                request_options=request_options,
            ),
        )


class Recordings(BaseResource):
    """Typed resource for ``/recordings`` (generated).

    Bound to ``/api/relay/rest/recordings``; construct it as ``Recordings(http)`` with
    the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/recordings")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> RecordingListResponse:
        """Returns a list of your recordings.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``page_number``: The page number to retrieve (0-indexed).
                - ``page_size``: The number of items per page (1-1000).
                - ``page_token``: Token for cursor-based pagination. Required when
                  page_number > 0.

        Returns:
            Response containing a list of recordings.
        """
        return cast(
            "RecordingListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> dict[str, Any]:
        """Retrieves the details of a recording.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the recording.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            Recording model.
        """
        return cast(
            "dict[str, Any]",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        """Deletes a recording.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the recording.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The decoded JSON response (an empty dict when the server sends no body).
        """
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )


class RegistryBrands(BaseResource):
    """Typed resource for ``/registry/beta/brands`` (generated).

    Bound to ``/api/relay/rest/registry/beta/brands``; construct it as
    ``RegistryBrands(http)`` with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/registry/beta/brands")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> BrandListResponse:
        """Returns a list of your registered brands for 10DLC.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``filter_name``: The name given to the brand. Will return all Brands
                  containing this value as a substring.
                - ``filter_state``: The state of the brand in the registration process,
                  such as pending or complete. Will return all Brands with this value.

        Returns:
            Response containing a list of brands.
        """
        return cast(
            "BrandListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def create(
        self,
        body: CreateManagedBrandRequest | CreateCspBrandRequest,
        *,
        request_options: RequestOptions | None = None,
    ) -> BrandResponse:
        """Creates a new brand for 10DLC registration.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            body: The request body, one of: ``CreateManagedBrandRequest``,
                ``CreateCspBrandRequest``.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            Response containing a single brand.
        """
        return cast(
            "BrandResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> BrandResponse:
        """Retrieves the details of a brand.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the brand.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            Response containing a single brand.
        """
        return cast(
            "BrandResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def list_campaigns(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CampaignListResponse:
        """Returns a list of campaigns for a brand.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the brand.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``filter_name``: The name given to the campaign. Will return all
                  Campaigns containing this value as a substring.
                - ``filter_state``: The state of the campaign in the registration
                  process, such as pending or complete. Will return all campaigns with
                  this value.

        Returns:
            Response containing a list of campaigns.
        """
        return cast(
            "CampaignListResponse",
            self._http.get(
                self._path(id, "campaigns"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def create_campaign(
        self,
        id: str,
        body: CreateManagedCampaignRequest | CreatePartnerCampaignRequest,
        *,
        request_options: RequestOptions | None = None,
    ) -> CampaignResponse:
        """Creates a new campaign for 10DLC registration.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the brand.
            body: The request body, one of: ``CreateManagedCampaignRequest``,
                ``CreatePartnerCampaignRequest``.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            Response containing a single campaign.
        """
        return cast(
            "CampaignResponse",
            self._http.post(
                self._path(id, "campaigns"), body=body, request_options=request_options
            ),
        )


class RegistryCampaigns(BaseResource):
    """Typed resource for ``/registry/beta/campaigns`` (generated).

    Bound to ``/api/relay/rest/registry/beta/campaigns``; construct it as
    ``RegistryCampaigns(http)`` with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/registry/beta/campaigns")

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> CampaignResponse:
        """Retrieves the details of a campaign.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the campaign.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            Response containing a single campaign.
        """
        return cast(
            "CampaignResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        *,
        name: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> CampaignResponse:
        """Updates a campaign.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the campaign.
            name: A name for the campaign.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single campaign.
        """
        body: dict[str, Any] = {
            k: v for k, v in {"name": name}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "CampaignResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def list_numbers(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> AssignedNumberListResponse:
        """Returns a list of phone numbers assigned to a campaign.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the campaign.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``filter_state``: The state of the assignments in the registration
                  process, such as pending or complete. Will return all assignments with
                  this value.

        Returns:
            Response containing a list of assigned numbers.
        """
        return cast(
            "AssignedNumberListResponse",
            self._http.get(
                self._path(id, "numbers"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def list_orders(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> OrderListResponse:
        """Returns a list of orders for a campaign.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the campaign.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``filter_state``: The state of the orders in the registration process,
                  such as pending or processed. Will return all orders with this value.

        Returns:
            Response containing a list of orders.
        """
        return cast(
            "OrderListResponse",
            self._http.get(
                self._path(id, "orders"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def create_order(
        self,
        id: str,
        *,
        phone_numbers: list[str] | None = None,
        status_callback_url: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> OrderResponse:
        """Creates a new order for a campaign.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the campaign.
            phone_numbers: A list of phone numbers in E164 format.
            status_callback_url: Optional: Specify a URL to receive webhook
                notifications when your number assignment order and the number
                assignments that belong to it change state. See the [10DLC status
                callback](https://signalwire.com/docs/apis/relay-rest/campaign-registry/webhooks/ten-dlc-status-callback)
                docs for the webhook payload.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single order.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "phone_numbers": phone_numbers,
                "status_callback_url": status_callback_url,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "OrderResponse",
            self._http.post(
                self._path(id, "orders"), body=body, request_options=request_options
            ),
        )


class RegistryNumbers(BaseResource):
    """Typed resource for ``/registry/beta/numbers`` (generated).

    Bound to ``/api/relay/rest/registry/beta/numbers``; construct it as
    ``RegistryNumbers(http)`` with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/registry/beta/numbers")

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        """Removes a phone number from a campaign.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the assigned number.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            The decoded JSON response (an empty dict when the server sends no body).
        """
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )


class RegistryOrders(BaseResource):
    """Typed resource for ``/registry/beta/orders`` (generated).

    Bound to ``/api/relay/rest/registry/beta/orders``; construct it as
    ``RegistryOrders(http)`` with the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/registry/beta/orders")

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> OrderResponse:
        """Retrieves the details of an order.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the order.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            Response containing a single order.
        """
        return cast(
            "OrderResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )


class ShortCodes(BaseResource):
    """Typed resource for ``/short_codes`` (generated).

    Bound to ``/api/relay/rest/short_codes``; construct it as ``ShortCodes(http)`` with
    the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/short_codes")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ShortCodeListResponse:
        """Returns a list of your short codes.

        The short codes are returned sorted by creation date, with the most recent
        appearing first.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string. Recognized by
                this operation:
                - ``filter_name``: Filter by name. Returns all short codes containing
                  this value as a substring.
                - ``filter_number``: Filter by number. Returns all short codes
                  containing this value as a substring.
                - ``page_number``: The page number to retrieve.
                - ``page_size``: The number of results per page.
                - ``page_token``: Token for cursor-based pagination.

        Returns:
            Response containing a list of short codes.
        """
        return cast(
            "ShortCodeListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def get(
        self, id: str, *, request_options: RequestOptions | None = None, **params: Any
    ) -> ShortCodeResponse:
        """Retrieves the details of a short code.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the short code.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            Response containing a single short code.
        """
        return cast(
            "ShortCodeResponse",
            self._http.get(
                self._path(id), params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        *,
        name: str,
        message_handler: ShortCodeMessageHandler,
        message_request_url: str | None = None,
        message_request_method: HttpMethod | None = None,
        message_fallback_url: str | None = None,
        message_fallback_method: HttpMethod | None = None,
        message_laml_application_id: uuid | None = None,
        message_relay_context: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> ShortCodeResponse:
        """Updates a short code's configuration.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Numbers_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the short code.
            name: The name given to the short code.
            message_handler: The message handler type for incoming messages.
            message_request_url: The URL to send message requests to when using
                laml_webhooks handler.
            message_request_method: The HTTP method to use for message requests.
                Defaults to POST.
            message_fallback_url: The fallback URL for message requests.
            message_fallback_method: The HTTP method to use for fallback requests.
                Defaults to POST.
            message_laml_application_id: The ID of the LāML application to handle
                messages when using laml_application handler.
            message_relay_context: The Relay context to use when using relay_context
                handler.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single short code.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "message_handler": message_handler,
                "message_request_url": message_request_url,
                "message_request_method": message_request_method,
                "message_fallback_url": message_fallback_url,
                "message_fallback_method": message_fallback_method,
                "message_laml_application_id": message_laml_application_id,
                "message_relay_context": message_relay_context,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "ShortCodeResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )


class SipProfile(BaseResource):
    """Typed resource for ``/sip_profile`` (generated).

    Bound to ``/api/relay/rest/sip_profile``; construct it as ``SipProfile(http)`` with
    the client's HTTP transport.
    """

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/sip_profile")

    def get(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> SipProfileResponse:
        """Retrieves the SIP profile settings for your project.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **params: Optional query parameters, sent as the query string.

        Returns:
            Response containing the SIP profile.
        """
        return cast(
            "SipProfileResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        *,
        domain_identifier: str | None = None,
        default_codecs: list[str] | None = None,
        default_ciphers: list[str] | None = None,
        default_encryption: Literal["required", "optional"] | None = None,
        default_send_as: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipProfileResponse:
        """Updates the SIP profile settings for your project.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            domain_identifier: String representing the domain_identifier portion of the
                profile. Must be unique across your project.
            default_codecs: A list of codecs this profile will support. Currently
                supported values are: OPUS, G722, PCMU, PCMA, VP8, H264.
            default_ciphers: A list of encryption ciphers this profile will support.
                Currently supported values are: AEAD_AES_256_GCM_8,
                AES_256_CM_HMAC_SHA1_80, AES_CM_128_HMAC_SHA1_80,
                AES_256_CM_HMAC_SHA1_32, AES_CM_128_HMAC_SHA1_32.
            default_encryption: A string representing whether connections to an endpoint
                that uses this profile require encryption or if encryption is optional.
                Encryption will always be used if possible. Possible values are required
                or optional.
            default_send_as: The e164 formatted number you wish to set as the
                originating number when dialing PSTN phone numbers from a SIP Endpoint
                that uses this profile. Specify null or an empty string to randomly
                choose a purchased or verified number from within the project.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing the SIP profile.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "domain_identifier": domain_identifier,
                "default_codecs": default_codecs,
                "default_ciphers": default_ciphers,
                "default_encryption": default_encryption,
                "default_send_as": default_send_as,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipProfileResponse",
            self._http.put(self._base_path, body=body, request_options=request_options),
        )


class VerifiedCallers(
    CrudResource[
        "VerifiedCallerIDListResponse",
        "VerifiedCallerIDResponse",
        "CreateVerifiedCallerIDRequest",
        "UpdateVerifiedCallerIDRequest",
    ]
):
    """Typed resource for ``/verified_caller_ids`` (generated).

    Bound to ``/api/relay/rest/verified_caller_ids``; construct it as
    ``VerifiedCallers(http)`` with the client's HTTP transport.
    """

    _update_method = "PUT"

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/relay/rest/verified_caller_ids")

    def create(  # type: ignore[override]
        self,
        *,
        number: str,
        name: str | None = None,
        extension: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> VerifiedCallerIDResponse:
        """Creates a new verified caller ID.

        A verification code will be sent to the phone number.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            number: String representing the phone number for the caller ID. This must be
                a valid, routeable phone number in [E.164
                format](https://en.wikipedia.org/wiki/E.164) that is able to receive a
                voice phone call for verification.
            name: The name portion of the caller ID. If not provided, the default will
                be the formatted number.
            extension: The extension of the phone number for the caller ID. This is only
                used when placing the verification call.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single verified caller ID.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {"number": number, "name": name, "extension": extension}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "VerifiedCallerIDResponse",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        name: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> VerifiedCallerIDResponse:
        """Updates a verified caller ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the verified caller ID.
            name: The name portion of the caller ID.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single verified caller ID.
        """
        body: dict[str, Any] = {
            k: v for k, v in {"name": name}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "VerifiedCallerIDResponse",
            self._http.put(self._path(id), body=body, request_options=request_options),
        )

    def redial_verification(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> VerifiedCallerIDResponse:
        """Redials the verification call for a verified caller ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the verified caller ID.
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.

        Returns:
            Response containing a single verified caller ID.
        """
        return cast(
            "VerifiedCallerIDResponse",
            self._http.post(
                self._path(id, "verification"), request_options=request_options
            ),
        )

    def submit_verification(
        self,
        id: str,
        *,
        verification_code: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> VerifiedCallerIDResponse:
        """Validates the verification code for a verified caller ID.

        **Permissions**

        The API token used to authenticate must have the following scope(s) enabled to
        make a successful request: _Voice_.

        [Learn more about API
        scopes](https://signalwire.com/docs/platform/your-signalwire-api-space).

        Args:
            id: Unique ID of the verified caller ID.
            verification_code: The verification code received via call or SMS.
            extras: Additional wire fields to merge into the request body (fields the
                spec does not enumerate).
            request_options: Per-call HTTP options (timeout, retries, headers); never
                sent on the wire.
            **_reserved_kw: Further wire fields passed as bare keywords, including
                reserved-word keys such as ``from`` (``**{'from': ...}``).

        Returns:
            Response containing a single verified caller ID.
        """
        body: dict[str, Any] = {
            k: v
            for k, v in {"verification_code": verification_code}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "VerifiedCallerIDResponse",
            self._http.put(
                self._path(id, "verification"),
                body=body,
                request_options=request_options,
            ),
        )
