# AUTO-GENERATED from porting-sdk/rest-apis/fabric-addresses/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**_reserved_kw`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import CrudResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .fabric_addresses_types_generated import (
        AddressContext,
        AliasAddress,
        AliasAddressCreate,
        AliasAddressList,
        AliasAddressUpdate,
        Channel,
        Codec,
        HandlerType,
        PhoneNumberAddress,
        PhoneNumberAddressCreate,
        PhoneNumberAddressList,
        PhoneNumberAddressUpdate,
        SipAddress,
        SipAddressCreate,
        SipAddressList,
        SipAddressUpdate,
        SipEncryption,
        SrtpCipher,
    )


class SipAddresses(
    CrudResource["SipAddressList", "SipAddress", "SipAddressCreate", "SipAddressUpdate"]
):
    """Typed resource for ``/sip_addresses`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/sip_addresses")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        calling_handler_resource_id: str,
        user: str | None = None,
        context_id: str | None = None,
        ip_auth_enabled: bool | None = None,
        ip_auth: list[str] | None = None,
        codecs: list[Codec] | None = None,
        ciphers: list[SrtpCipher] | None = None,
        encryption: SipEncryption | None = None,
        password: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipAddress:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "user": user,
                "context_id": context_id,
                "calling_handler_resource_id": calling_handler_resource_id,
                "ip_auth_enabled": ip_auth_enabled,
                "ip_auth": ip_auth,
                "codecs": codecs,
                "ciphers": ciphers,
                "encryption": encryption,
                "password": password,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipAddress",
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
        user: str | None = None,
        context_id: str | None = None,
        ip_auth_enabled: bool | None = None,
        ip_auth: list[str] | None = None,
        codecs: list[Codec] | None = None,
        ciphers: list[SrtpCipher] | None = None,
        encryption: SipEncryption | None = None,
        password: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> SipAddress:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "user": user,
                "context_id": context_id,
                "ip_auth_enabled": ip_auth_enabled,
                "ip_auth": ip_auth,
                "codecs": codecs,
                "ciphers": ciphers,
                "encryption": encryption,
                "password": password,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "SipAddress",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class PhoneNumberAddresses(
    CrudResource[
        "PhoneNumberAddressList",
        "PhoneNumberAddress",
        "PhoneNumberAddressCreate",
        "PhoneNumberAddressUpdate",
    ]
):
    """Typed resource for ``/phone_number_addresses`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/phone_number_addresses")

    def create(  # type: ignore[override]
        self,
        *,
        resource_id: str,
        handler_type: HandlerType,
        phone_number_id: str | None = None,
        number: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> PhoneNumberAddress:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "phone_number_id": phone_number_id,
                "number": number,
                "resource_id": resource_id,
                "handler_type": handler_type,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "PhoneNumberAddress",
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
        resource_id: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> PhoneNumberAddress:
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "resource_id": resource_id}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "PhoneNumberAddress",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )


class AliasAddresses(
    CrudResource[
        "AliasAddressList", "AliasAddress", "AliasAddressCreate", "AliasAddressUpdate"
    ]
):
    """Typed resource for ``/alias_addresses`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/fabric/alias_addresses")

    def create(  # type: ignore[override]
        self,
        *,
        name: str,
        resource_id: str,
        display_name: str | None = None,
        channels: list[Channel] | None = None,
        codecs: list[Codec] | None = None,
        context: AddressContext | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> AliasAddress:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "resource_id": resource_id,
                "display_name": display_name,
                "channels": channels,
                "codecs": codecs,
                "context": context,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "AliasAddress",
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
        display_name: str | None = None,
        channels: list[Channel] | None = None,
        codecs: list[Codec] | None = None,
        context: AddressContext | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> AliasAddress:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "name": name,
                "display_name": display_name,
                "channels": channels,
                "codecs": codecs,
                "context": context,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "AliasAddress",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )
