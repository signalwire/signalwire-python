"""AUTO-GENERATED REST wire tests for the `space` namespace — DO NOT EDIT.
Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py

Each route the SDK implements (captured from the real client by python_route_registry,
joined to the spec operationId) gets a SUCCESS test (call it, assert method/path/route on
the mock journal) and an ERROR test (arm a 5xx, assert SignalWireRestError). The assertion
oracle is the spec operationId — independent of the resource generator — so these catch
SDK-vs-contract drift, not just a generator self-snapshot. Full-mock harness fixtures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from signalwire.rest._base import SignalWireRestError

if TYPE_CHECKING:
    from signalwire.rest.client import RestClient

    from .conftest import _MockHarness


class TestSpaceWire:
    def test_balance_create_top_up(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.balance.create_top_up(
            idempotency_key="x", amount_in_microdollars=1, payment_method_id="x"
        )
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "space.create_top_up"

    def test_balance_create_top_up_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.create_top_up", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.balance.create_top_up(
                idempotency_key="x", amount_in_microdollars=1, payment_method_id="x"
            )
        assert exc.value.status_code == 500

    def test_balance_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.balance.get()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.get_balance"

    def test_balance_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.get_balance", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.balance.get()
        assert exc.value.status_code == 500

    def test_billing_profile_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.billing_profile.get()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.get_billing_profile"

    def test_billing_profile_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.get_billing_profile", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.billing_profile.get()
        assert exc.value.status_code == 500

    def test_billing_profile_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.billing_profile.update(
            address_line1="x",
            address_city="x",
            address_state="x",
            address_zip="x",
            address_country="x",
            company_name="x",
            contact_name="x",
            contact_email=["x"],
            contact_phone="x",
        )
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "space.update_billing_profile"

    def test_billing_profile_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.update_billing_profile", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.billing_profile.update(
                address_line1="x",
                address_city="x",
                address_state="x",
                address_zip="x",
                address_country="x",
                company_name="x",
                contact_name="x",
                contact_email=["x"],
                contact_phone="x",
            )
        assert exc.value.status_code == 500

    def test_billing_statements_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.billing_statements.get()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.get_billing_statement"

    def test_billing_statements_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.get_billing_statement", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.billing_statements.get()
        assert exc.value.status_code == 500

    def test_billing_statements_get_csv(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.billing_statements.get_csv()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.get_billing_statement_csv"

    def test_billing_statements_get_csv_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.get_billing_statement_csv", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.billing_statements.get_csv()
        assert exc.value.status_code == 500

    def test_billing_statements_get_pdf(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.billing_statements.get_pdf()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.get_billing_statement_pdf"

    def test_billing_statements_get_pdf_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.get_billing_statement_pdf", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.billing_statements.get_pdf()
        assert exc.value.status_code == 500

    def test_billing_statements_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.billing_statements.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.list_billing_statement_periods"

    def test_billing_statements_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.list_billing_statement_periods", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.billing_statements.list()
        assert exc.value.status_code == 500

    def test_geographic_permissions_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.geographic_permissions.get()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.get_geographic_permissions"

    def test_geographic_permissions_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.get_geographic_permissions", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.geographic_permissions.get()
        assert exc.value.status_code == 500

    def test_geographic_permissions_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.geographic_permissions.update(countries=["x"])
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "space.update_geographic_permissions"

    def test_geographic_permissions_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.update_geographic_permissions", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.geographic_permissions.update(countries=["x"])
        assert exc.value.status_code == 500

    def test_low_balance_setting_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.low_balance_setting.get()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.get_low_balance_setting"

    def test_low_balance_setting_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.get_low_balance_setting", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.low_balance_setting.get()
        assert exc.value.status_code == 500

    def test_low_balance_setting_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.low_balance_setting.update()
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "space.update_low_balance_setting"

    def test_low_balance_setting_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.update_low_balance_setting", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.low_balance_setting.update()
        assert exc.value.status_code == 500

    def test_members_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.members.create(email="x", role="admin")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "space.create_member"

    def test_members_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.create_member", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.members.create(email="x", role="admin")
        assert exc.value.status_code == 500

    def test_members_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.members.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "space.delete_member"

    def test_members_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.delete_member", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.members.delete("test-id")
        assert exc.value.status_code == 500

    def test_members_disable_project(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.members.disable_project("test-id", "test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "space.disable_member_project"

    def test_members_disable_project_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.disable_member_project", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.members.disable_project("test-id", "test-id")
        assert exc.value.status_code == 500

    def test_members_enable_project(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.members.enable_project("test-id", "test-id")
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "space.enable_member_project"

    def test_members_enable_project_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.enable_member_project", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.members.enable_project("test-id", "test-id")
        assert exc.value.status_code == 500

    def test_members_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.members.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.get_member"

    def test_members_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.get_member", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.members.get("test-id")
        assert exc.value.status_code == 500

    def test_members_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.members.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.list_members"

    def test_members_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.list_members", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.members.list()
        assert exc.value.status_code == 500

    def test_members_list_projects(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.members.list_projects("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.list_member_projects"

    def test_members_list_projects_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.list_member_projects", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.members.list_projects("test-id")
        assert exc.value.status_code == 500

    def test_members_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.members.update("test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "space.update_member"

    def test_members_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.update_member", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.members.update("test-id")
        assert exc.value.status_code == 500

    def test_payment_history_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.payment_history.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.list_payment_history"

    def test_payment_history_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.list_payment_history", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.payment_history.list()
        assert exc.value.status_code == 500

    def test_payment_methods_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.payment_methods.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "space.delete_payment_method"

    def test_payment_methods_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.delete_payment_method", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.payment_methods.delete("test-id")
        assert exc.value.status_code == 500

    def test_payment_methods_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.payment_methods.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.list_payment_methods"

    def test_payment_methods_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.list_payment_methods", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.payment_methods.list()
        assert exc.value.status_code == 500

    def test_settings_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.settings.get()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.get_space"

    def test_settings_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.get_space", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.settings.get()
        assert exc.value.status_code == 500

    def test_settings_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.settings.update()
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.matched_route == "space.update_space"

    def test_settings_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.update_space", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.settings.update()
        assert exc.value.status_code == 500

    def test_usage_get(self, signalwire_client: RestClient, mock: _MockHarness) -> None:
        signalwire_client.space.usage.get()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "space.get_usage"

    def test_usage_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.get_usage", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.usage.get()
        assert exc.value.status_code == 500
