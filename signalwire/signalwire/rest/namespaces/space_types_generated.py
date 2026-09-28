# AUTO-GENERATED from porting-sdk/rest-apis/space/openapi.yaml — DO NOT EDIT.
# Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py
#
# One TypedDict per components/schemas entry + per-operation Request/Response
# aliases. TypedDicts are STATIC-ONLY: at runtime each is a plain dict, so a
# differently-shaped server response is returned unchanged and never raises.
from __future__ import annotations
from typing import Literal, TypeAlias, TypedDict


class Space(TypedDict, total=False):
    """The space named by the request subdomain.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["space"]
    id: str
    name: str
    subdomain: str
    verified: bool
    trial: bool
    created_at: str
    updated_at: str


class SpaceUpdate(TypedDict, total=False):
    """Request body for renaming the space.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str


class GeographicPermission(TypedDict, total=False):
    """The countries the space has selected for international traffic, and the countries it may select.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["geographic_permission"]
    countries: list[str]
    supported_countries: list[str]


class GeographicPermissionUpdate(TypedDict, total=False):
    """Request body for replacing the selected countries.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    countries: list[str]


class BillingProfile(TypedDict, total=False):
    """The billing address and contacts for the space. A profile that has never been configured is returned with `null` fields rather than a `404`.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["billing_profile"]
    address_line1: str | None
    address_line2: str | None
    address_city: str | None
    address_state: str | None
    address_zip: str | None
    address_country: str | None
    company_name: str | None
    contact_name: str | None
    contact_email: list[str] | None
    contact_phone: str | None
    tax_id_number: str | None
    monthly_invoices: bool
    tax_id_number_required: bool
    monthly_invoices_locked: bool


class BillingProfileUpdate(TypedDict, total=False):
    """Request body for updating the billing profile. The update writes the whole profile, so send every field you want to keep.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    address_line1: str
    address_line2: str
    address_city: str
    address_state: str
    address_zip: str
    address_country: str
    company_name: str
    contact_name: str
    contact_email: list[str]
    contact_phone: str
    tax_id_number: str
    monthly_invoices: bool


class BillingStatementPeriod(TypedDict, total=False):
    """A month a statement is available for.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["billing_statement_period"]
    month: str
    uri: str
    formats: list[Literal["json", "csv", "pdf"]]


class BillingStatementPeriodList(TypedDict, total=False):
    """The months a statement is available for, newest first. This list is not paged.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    data: list[BillingStatementPeriod]


class BillingStatement(TypedDict, total=False):
    """One month's statement: the totals, company-wide usage by kind, and usage per project. Statements are computed on request from the usage reporting pipeline.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["billing_statement"]
    month: str
    summary: BillingStatementSummary
    usage_by_kind: list[AmountByKind]
    projects: list[ProjectUsage]


class BillingStatementSummary(TypedDict, total=False):
    """The totals for the month.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    usage_in_microdollars: int
    usage_in_dollars: float
    carrier_fees_in_microdollars: int
    carrier_fees_in_dollars: float
    taxes_in_microdollars: int
    taxes_in_dollars: float
    adjustments: list[AmountByKind]


class AmountByKind(TypedDict, total=False):
    """An amount for one kind of usage or adjustment, in microdollars (millionths of a US dollar) and again in dollars.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    kind: str
    description: str
    amount_in_microdollars: int
    amount_in_dollars: float


class ProjectUsage(TypedDict, total=False):
    """Usage attributed to one project, with its own breakdown by kind.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    id: str
    name: str | None
    amount_in_microdollars: int
    amount_in_dollars: float
    usage_by_kind: list[AmountByKind]


class Usage(TypedDict, total=False):
    """Company-wide usage for a month, in total, by kind, and per project. Usage is computed on request from the usage reporting pipeline.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["usage"]
    month: str
    total_in_microdollars: int
    total_in_dollars: float
    usage_by_kind: list[AmountByKind]
    projects: list[ProjectUsage]


class BalanceAdjustment(TypedDict, total=False):
    """A change to the space balance: a top-up, an auto top-up, or a credit or debit applied by SignalWire.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["balance_adjustment"]
    id: str
    kind: str
    amount_in_microdollars: int
    amount: float
    created_at: str
    payment_method_last4: str | None


class PaymentHistoryList(TypedDict, total=False):
    """A page of balance adjustments.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: SpacePaginationLinks
    data: list[BalanceAdjustment]


class Member(TypedDict, total=False):
    """A membership in the space.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["member"]
    id: str
    email: str
    name: str
    role: Literal["owner", "admin", "employee", "guest"]
    job_title: Literal["entrepreneur", "product_manager", "developer", "other"] | None
    activated: bool
    last_logged_in: str | None
    created_at: str
    updated_at: str


class MemberList(TypedDict, total=False):
    """A page of members.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: SpacePaginationLinks
    data: list[Member]


class MemberCreate(TypedDict, total=False):
    """Request body for inviting a member.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    email: str
    role: Literal["admin", "employee"]
    name: str


class MemberUpdate(TypedDict, total=False):
    """Request body for updating a member.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    name: str
    role: Literal["admin", "employee"]
    job_title: Literal["entrepreneur", "product_manager", "developer", "other"] | None


class SpaceProject(TypedDict, total=False):
    """A project as the space sees it. The full project object, including its settings, is returned by the [Projects API](/docs/apis/rest/projects/get-project).

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["project"]
    id: str
    name: str
    created_at: str
    updated_at: str


class MemberProject(TypedDict, total=False):
    """A root project a member is enabled for, with the subprojects reached through that enablement.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["project"]
    id: str
    name: str
    created_at: str
    updated_at: str
    subprojects: list[SpaceProject]


class MemberProjectList(TypedDict, total=False):
    """A page of the root projects a member is enabled for.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    links: SpacePaginationLinks
    data: list[MemberProject]


class Balance(TypedDict, total=False):
    """The current balance of the space and its auto top-up state. Amounts are given in microdollars (millionths of a US dollar) and again in dollars.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["balance"]
    balance_in_microdollars: int
    current_balance: float
    low_balance_threshold_in_microdollars: int
    low_balance_threshold: float
    auto_topup_enabled: bool


class TopUpCreate(TypedDict, total=False):
    """Request body for charging a payment method and depositing the amount to the balance.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    amount_in_microdollars: int
    payment_method_id: str


class LowBalanceSetting(TypedDict, total=False):
    """How the space is notified when its balance falls below the threshold, and whether it tops itself up automatically.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["low_balance_setting"]
    threshold_in_microdollars: int
    threshold: float
    send_email: bool
    send_webhook: bool
    webhook_url: str | None
    webhook_method: str | None
    send_topup: bool
    topup_amount_in_microdollars: int | None
    topup_amount: float | None
    topup_payment_method_id: str | None


class LowBalanceSettingUpdate(TypedDict, total=False):
    """Request body for updating low balance notifications and auto top-up. The update writes the whole setting, so omitted fields take their defaults.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    threshold_in_microdollars: int
    send_email: bool
    send_webhook: bool
    webhook_url: str
    webhook_method: Literal["GET", "POST"]
    send_topup: bool
    topup_amount_in_microdollars: int
    topup_payment_method_id: str


class PaymentMethod(TypedDict, total=False):
    """A card on file for the space. Cards are added in the Dashboard; the API lists and deletes them.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    type: Literal["payment_method"]
    id: str
    brand: str | None
    last4: str | None
    expires_month: int | None
    expires_year: int | None
    country: str | None
    auto_topup_source: bool


class SpacePaginationLinks(TypedDict, total=False):
    """Cursor pagination links. Filters given on the request are preserved in every link.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    self: str
    first: str
    next: str
    prev: str


class SpaceStatusCode422(TypedDict, total=False):
    """The standard validation error body.

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


class SpaceUnverifiedError(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    message: str


class TopUpMessageError(TypedDict, total=False):
    """Open shape: extra server keys permitted; not validated at runtime."""

    message: str


class TopUpDeclinedError(TypedDict, total=False):
    """The card was declined. This is not the standard validation error body: it carries the payment processor's stable decline code.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    message: str | None
    decline_code: str


class TopUpDepositFailedError(TypedDict, total=False):
    """An upstream billing service was unavailable and the deposit to the space balance could not be completed.

    Open shape: extra server keys are permitted and partial payloads are valid;
    not validated at runtime (a TypedDict is a plain ``dict``).
    """

    message: str
    code: Literal["deposit_failed"]


GetSpaceResponse: TypeAlias = "Space"
UpdateSpaceRequest: TypeAlias = "SpaceUpdate"
UpdateSpaceResponse: TypeAlias = "Space"
GetGeographicPermissionsResponse: TypeAlias = "GeographicPermission"
UpdateGeographicPermissionsRequest: TypeAlias = "GeographicPermissionUpdate"
UpdateGeographicPermissionsResponse: TypeAlias = "GeographicPermission"
GetBillingProfileResponse: TypeAlias = "BillingProfile"
UpdateBillingProfileRequest: TypeAlias = "BillingProfileUpdate"
UpdateBillingProfileResponse: TypeAlias = "BillingProfile"
ListBillingStatementPeriodsResponse: TypeAlias = "BillingStatementPeriodList"
GetBillingStatementResponse: TypeAlias = "BillingStatement"
GetBillingStatementCsvResponse: TypeAlias = "str"
GetUsageResponse: TypeAlias = "Usage"
ListPaymentHistoryResponse: TypeAlias = "PaymentHistoryList"
ListMembersResponse: TypeAlias = "MemberList"
CreateMemberRequest: TypeAlias = "MemberCreate"
CreateMemberResponse: TypeAlias = "Member"
GetMemberResponse: TypeAlias = "Member"
UpdateMemberRequest: TypeAlias = "MemberUpdate"
UpdateMemberResponse: TypeAlias = "Member"
ListMemberProjectsResponse: TypeAlias = "MemberProjectList"
EnableMemberProjectResponse: TypeAlias = "MemberProject"
GetBalanceResponse: TypeAlias = "Balance"
CreateTopUpRequest: TypeAlias = "TopUpCreate"
CreateTopUpResponse: TypeAlias = "BalanceAdjustment"
GetLowBalanceSettingResponse: TypeAlias = "LowBalanceSetting"
UpdateLowBalanceSettingRequest: TypeAlias = "LowBalanceSettingUpdate"
UpdateLowBalanceSettingResponse: TypeAlias = "LowBalanceSetting"
ListPaymentMethodsResponse: TypeAlias = "list[PaymentMethod]"
