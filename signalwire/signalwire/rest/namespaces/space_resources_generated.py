# AUTO-GENERATED from porting-sdk/rest-apis/space/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One typed CRUD subclass per full-CRUD resource: closed typed create/update params
# (explicit spec fields) + an ``extras`` escape hatch and a ``**_reserved_kw`` tail for
# unknown / reserved-word wire fields, bound to the resource's spec types.
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast
from collections.abc import Mapping

from .._base import BaseResource, CrudResource

if TYPE_CHECKING:
    from .._request_options import RequestOptions

    from .space_types_generated import (
        Balance,
        BalanceAdjustment,
        BillingProfile,
        BillingStatement,
        BillingStatementPeriodList,
        GeographicPermission,
        LowBalanceSetting,
        Member,
        MemberCreate,
        MemberList,
        MemberProject,
        MemberProjectList,
        MemberUpdate,
        PaymentHistoryList,
        PaymentMethod,
        Space,
        Usage,
    )


class SpaceSettings(BaseResource):
    """Typed resource for ``/space`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/space")

    def get(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> Space:
        return cast(
            "Space",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        *,
        name: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Space:
        body: dict[str, Any] = {
            k: v for k, v in {"name": name}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "Space",
            self._http.put(self._base_path, body=body, request_options=request_options),
        )


class SpaceGeographicPermissions(BaseResource):
    """Typed resource for ``/space/geographic_permissions`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/space/geographic_permissions")

    def get(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> GeographicPermission:
        return cast(
            "GeographicPermission",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        *,
        countries: list[str],
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> GeographicPermission:
        body: dict[str, Any] = {
            k: v for k, v in {"countries": countries}.items() if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "GeographicPermission",
            self._http.put(self._base_path, body=body, request_options=request_options),
        )


class SpaceBillingProfile(BaseResource):
    """Typed resource for ``/space/billing_profile`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/space/billing_profile")

    def get(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> BillingProfile:
        return cast(
            "BillingProfile",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        *,
        address_line1: str,
        address_city: str,
        address_state: str,
        address_zip: str,
        address_country: str,
        company_name: str,
        contact_name: str,
        contact_email: list[str],
        contact_phone: str,
        address_line2: str | None = None,
        tax_id_number: str | None = None,
        monthly_invoices: bool | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> BillingProfile:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "address_line1": address_line1,
                "address_line2": address_line2,
                "address_city": address_city,
                "address_state": address_state,
                "address_zip": address_zip,
                "address_country": address_country,
                "company_name": company_name,
                "contact_name": contact_name,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "tax_id_number": tax_id_number,
                "monthly_invoices": monthly_invoices,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "BillingProfile",
            self._http.put(self._base_path, body=body, request_options=request_options),
        )


class SpaceBillingStatements(BaseResource):
    """Typed resource for ``/space`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/space")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> BillingStatementPeriodList:
        return cast(
            "BillingStatementPeriodList",
            self._http.get(
                self._path("billing_statements"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def get(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> BillingStatement:
        return cast(
            "BillingStatement",
            self._http.get(
                self._path("billing_statement"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def get_csv(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> str:
        return self._http.get_text(
            self._path("billing_statement.csv"),
            params=params or None,
            request_options=request_options,
            headers={"Accept": "text/csv"},
        )

    def get_pdf(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> str:
        return self._http.get_redirect_location(
            self._path("billing_statement.pdf"),
            params=params or None,
            request_options=request_options,
        )


class SpaceUsage(BaseResource):
    """Typed resource for ``/space/usage`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/space/usage")

    def get(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> Usage:
        return cast(
            "Usage",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )


class SpacePaymentHistory(BaseResource):
    """Typed resource for ``/space/payment_history`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/space/payment_history")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> PaymentHistoryList:
        return cast(
            "PaymentHistoryList",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )


class SpaceMembers(
    CrudResource["MemberList", "Member", "MemberCreate", "MemberUpdate"]
):
    """Typed resource for ``/space/members`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/space/members")

    def create(  # type: ignore[override]
        self,
        *,
        email: str,
        role: Literal["admin", "employee"],
        name: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Member:
        body: dict[str, Any] = {
            k: v
            for k, v in {"email": email, "role": role, "name": name}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "Member",
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
        role: Literal["admin", "employee"] | None = None,
        job_title: Literal["entrepreneur", "product_manager", "developer", "other"]
        | None
        | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> Member:
        body: dict[str, Any] = {
            k: v
            for k, v in {"name": name, "role": role, "job_title": job_title}.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "Member",
            self._http.patch(
                self._path(id), body=body, request_options=request_options
            ),
        )

    def list_projects(
        self,
        member_id: str,
        *,
        request_options: RequestOptions | None = None,
        **params: Any,
    ) -> MemberProjectList:
        return cast(
            "MemberProjectList",
            self._http.get(
                self._path(member_id, "projects"),
                params=params or None,
                request_options=request_options,
            ),
        )

    def enable_project(
        self,
        member_id: str,
        project_id: str,
        *,
        request_options: RequestOptions | None = None,
    ) -> MemberProject:
        return cast(
            "MemberProject",
            self._http.put(
                self._path(member_id, "projects", project_id),
                request_options=request_options,
            ),
        )

    def disable_project(
        self,
        member_id: str,
        project_id: str,
        *,
        request_options: RequestOptions | None = None,
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(
                self._path(member_id, "projects", project_id),
                request_options=request_options,
            ),
        )


class SpaceBalance(BaseResource):
    """Typed resource for ``/space/balance`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/space/balance")

    def get(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> Balance:
        return cast(
            "Balance",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def create_top_up(
        self,
        *,
        idempotency_key: str,
        amount_in_microdollars: int,
        payment_method_id: str,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> BalanceAdjustment:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "amount_in_microdollars": amount_in_microdollars,
                "payment_method_id": payment_method_id,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "BalanceAdjustment",
            self._http.post(
                self._path("top_ups"),
                body=body,
                request_options=request_options,
                headers={"Idempotency-Key": idempotency_key},
            ),
        )


class SpaceLowBalanceSetting(BaseResource):
    """Typed resource for ``/space/low_balance_setting`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/space/low_balance_setting")

    def get(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> LowBalanceSetting:
        return cast(
            "LowBalanceSetting",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def update(
        self,
        *,
        threshold_in_microdollars: int | None = None,
        send_email: bool | None = None,
        send_webhook: bool | None = None,
        webhook_url: str | None = None,
        webhook_method: Literal["GET", "POST"] | None = None,
        send_topup: bool | None = None,
        topup_amount_in_microdollars: int | None = None,
        topup_payment_method_id: str | None = None,
        extras: Mapping[str, Any] | None = None,
        request_options: RequestOptions | None = None,
        **_reserved_kw: Any,
    ) -> LowBalanceSetting:
        body: dict[str, Any] = {
            k: v
            for k, v in {
                "threshold_in_microdollars": threshold_in_microdollars,
                "send_email": send_email,
                "send_webhook": send_webhook,
                "webhook_url": webhook_url,
                "webhook_method": webhook_method,
                "send_topup": send_topup,
                "topup_amount_in_microdollars": topup_amount_in_microdollars,
                "topup_payment_method_id": topup_payment_method_id,
            }.items()
            if v is not None
        }
        if extras:
            body.update(extras)
        body.update(_reserved_kw)
        return cast(
            "LowBalanceSetting",
            self._http.put(self._base_path, body=body, request_options=request_options),
        )


class SpacePaymentMethods(BaseResource):
    """Typed resource for ``/space/payment_methods`` (generated)."""

    def __init__(self, http: Any) -> None:
        super().__init__(http, "/api/space/payment_methods")

    def list(
        self, *, request_options: RequestOptions | None = None, **params: Any
    ) -> PaymentMethod:
        return cast(
            "PaymentMethod",
            self._http.get(
                self._base_path, params=params or None, request_options=request_options
            ),
        )

    def delete(
        self, id: str, *, request_options: RequestOptions | None = None
    ) -> dict[str, Any]:
        return cast(
            "dict[str, Any]",
            self._http.delete(self._path(id), request_options=request_options),
        )
