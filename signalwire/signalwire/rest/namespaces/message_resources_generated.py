# AUTO-GENERATED from porting-sdk/rest-apis/message/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**_reserved_kw`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from collections.abc import Mapping

from .._base import BaseResource, CrudResource, ReadResource, _required_via_extras

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .message_types_generated import (
        CreateWhatsappTemplateRequest,
        LogListResponse,
        LogRetrieveResponse,
        UpdateWhatsappTemplateRequest,
        WhatsappBusinessListResponse,
        WhatsappNumber,
        WhatsappNumberListResponse,
        WhatsappTemplate,
        WhatsappTemplateCategory,
        WhatsappTemplateComponent,
        WhatsappTemplateListResponse,
        WhatsappTemplateParameterFormat,
        uuid,
    )


class MessageLogs(ReadResource["LogListResponse", "LogRetrieveResponse"]):
    """Typed resource for ``/logs`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/messaging/logs")


class WhatsappNumbers(ReadResource["WhatsappNumberListResponse", "WhatsappNumber"]):
    """Typed resource for ``/whatsapp/numbers`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/messaging/whatsapp/numbers")


class WhatsappBusinesses(BaseResource):
    """Typed resource for ``/whatsapp/businesses`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/messaging/whatsapp/businesses")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> WhatsappBusinessListResponse:
        return cast(
            "WhatsappBusinessListResponse",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )


class WhatsappTemplates(
    CrudResource[
        "WhatsappTemplateListResponse",
        "WhatsappTemplate",
        "CreateWhatsappTemplateRequest",
        "UpdateWhatsappTemplateRequest",
    ]
):
    """Typed resource for ``/whatsapp/templates`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/messaging/whatsapp/templates")

    @_required_via_extras(
        "whatsapp_business_id",
        "name",
        "language",
        "category",
        "parameter_format",
        "components",
    )
    def create(  # type: ignore[override]
        self,
        *,
        whatsapp_business_id: uuid,
        name: str,
        language: str,
        category: WhatsappTemplateCategory,
        parameter_format: WhatsappTemplateParameterFormat,
        components: list[WhatsappTemplateComponent],
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> WhatsappTemplate:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "whatsapp_business_id": whatsapp_business_id,
                "name": name,
                "language": language,
                "category": category,
                "parameter_format": parameter_format,
                "components": components,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "WhatsappTemplate",
            self._http.post(
                self._base_path, body=body, request_options=request_options
            ),
        )

    def update(
        self,
        id: str,
        /,
        *,
        category: WhatsappTemplateCategory | None = None,
        components: list[WhatsappTemplateComponent] | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> WhatsappTemplate:
        body: dict[str, Any] = {
            k: v
            for k, v in {"category": category, "components": components}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "WhatsappTemplate",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )
