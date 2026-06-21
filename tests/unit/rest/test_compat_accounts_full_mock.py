"""Full success + error coverage for ``client.compat.accounts`` /
``client.compat.applications`` / ``client.compat.tokens`` — the LaML
(Twilio-compatible) 2010-04-01 Accounts API.

Mirrors the proven micro-template ``test_fabric_ai_agents_full_mock.py``:
every canonical route gets BOTH a SUCCESS test (call the real SDK method
against the live mock, assert the parsed body shape AND the journal entry —
method + exact resolved path + ``matched_route == endpoint_id``) and an ERROR
test (arm the mock for a 4xx/5xx via ``mock.push_scenario``, call the method,
assert the SDK raises ``SignalWireRestError`` with the right ``status_code`` and
the journal recorded the route hit with that status).

The SDK fills ``{AccountSid}`` from the client's configured project, which the
conftest pins to the constant ``test_proj`` — so the paths asserted here are the
concrete ``/api/laml/2010-04-01/Accounts/test_proj/...`` URLs the mock records.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

ACCOUNTS = "/api/laml/2010-04-01/Accounts"
BASE = "/api/laml/2010-04-01/Accounts/test_proj"


class TestCompatAccountsSuccess:
    def test_list_accounts(self, signalwire_client, mock):
        body = signalwire_client.compat.accounts.list()
        assert isinstance(body, dict)
        assert "accounts" in body, f"missing 'accounts' in {sorted(body)!r}"
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == ACCOUNTS
        assert last.matched_route == "compatibility.list_accounts"

    def test_create_subprojects(self, signalwire_client, mock):
        body = signalwire_client.compat.accounts.create(FriendlyName="Sub-A")
        assert isinstance(body, dict)
        assert "friendly_name" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == ACCOUNTS
        assert last.matched_route == "compatibility.create_subprojects"
        assert last.body and last.body.get("FriendlyName") == "Sub-A"

    def test_get_account(self, signalwire_client, mock):
        body = signalwire_client.compat.accounts.get("AC123")
        assert isinstance(body, dict)
        assert "friendly_name" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{ACCOUNTS}/AC123"
        assert last.matched_route == "compatibility.get_account"

    def test_update_account(self, signalwire_client, mock):
        body = signalwire_client.compat.accounts.update("AC123", FriendlyName="Renamed")
        assert isinstance(body, dict)
        assert "friendly_name" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{ACCOUNTS}/AC123"
        assert last.matched_route == "compatibility.update_account"
        assert last.body and last.body.get("FriendlyName") == "Renamed"


class TestCompatAccountsErrors:
    def test_list_accounts_server_error(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_accounts", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.accounts.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_accounts"
        assert last.response_status == 500

    def test_create_subprojects_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("compatibility.create_subprojects", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.accounts.create(FriendlyName="x")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "compatibility.create_subprojects"
        assert last.response_status == 422

    def test_get_account_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.get_account", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.accounts.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.get_account"
        assert last.response_status == 404

    def test_update_account_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_account", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.accounts.update("missing", FriendlyName="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_account"
        assert last.response_status == 404


class TestCompatApplicationsSuccess:
    def test_list_applications(self, signalwire_client, mock):
        body = signalwire_client.compat.applications.list()
        assert isinstance(body, dict)
        assert "applications" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{BASE}/Applications"
        assert last.matched_route == "compatibility.list_applications"

    def test_create_application(self, signalwire_client, mock):
        body = signalwire_client.compat.applications.create(FriendlyName="App-A")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{BASE}/Applications"
        assert last.matched_route == "compatibility.create_application"
        assert last.body and last.body.get("FriendlyName") == "App-A"

    def test_get_application(self, signalwire_client, mock):
        body = signalwire_client.compat.applications.get("AP1")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{BASE}/Applications/AP1"
        assert last.matched_route == "compatibility.get_application"

    def test_update_application(self, signalwire_client, mock):
        body = signalwire_client.compat.applications.update("AP1", FriendlyName="renamed")
        assert isinstance(body, dict)
        assert "sid" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{BASE}/Applications/AP1"
        assert last.matched_route == "compatibility.update_application"
        assert last.body and last.body.get("FriendlyName") == "renamed"

    def test_delete_application(self, signalwire_client, mock):
        signalwire_client.compat.applications.delete("AP1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{BASE}/Applications/AP1"
        assert last.matched_route == "compatibility.delete_application"


class TestCompatApplicationsErrors:
    def test_list_applications_server_error(self, signalwire_client, mock):
        mock.push_scenario("compatibility.list_applications", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.applications.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "compatibility.list_applications"
        assert last.response_status == 500

    def test_create_application_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("compatibility.create_application", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.applications.create(FriendlyName="x")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "compatibility.create_application"
        assert last.response_status == 422

    def test_get_application_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.get_application", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.applications.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.get_application"
        assert last.response_status == 404

    def test_update_application_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_application", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.applications.update("missing", FriendlyName="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_application"
        assert last.response_status == 404

    def test_delete_application_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_application", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.applications.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_application"
        assert last.response_status == 404


class TestCompatTokensSuccess:
    def test_create_token(self, signalwire_client, mock):
        body = signalwire_client.compat.tokens.create(name="tok-a")
        assert isinstance(body, dict)
        assert "token" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{BASE}/tokens"
        assert last.matched_route == "compatibility.create_token"
        assert last.body and last.body.get("name") == "tok-a"

    def test_update_token(self, signalwire_client, mock):
        body = signalwire_client.compat.tokens.update("tok1", name="renamed")
        assert isinstance(body, dict)
        assert "token" in body
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.path == f"{BASE}/tokens/tok1"
        assert last.matched_route == "compatibility.update_token"
        assert last.body and last.body.get("name") == "renamed"

    def test_delete_token(self, signalwire_client, mock):
        signalwire_client.compat.tokens.delete("tok1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{BASE}/tokens/tok1"
        assert last.matched_route == "compatibility.delete_token"


class TestCompatTokensErrors:
    def test_create_token_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("compatibility.create_token", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.tokens.create(name="x")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "compatibility.create_token"
        assert last.response_status == 422

    def test_update_token_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.update_token", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.tokens.update("missing", name="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.update_token"
        assert last.response_status == 404

    def test_delete_token_not_found(self, signalwire_client, mock):
        mock.push_scenario("compatibility.delete_token", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.compat.tokens.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "compatibility.delete_token"
        assert last.response_status == 404
