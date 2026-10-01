"""``client.space`` — the Space Administration API — against the live mock server.

prime-rails serves ``/api/space`` only to a user's Personal Access Token: HTTP Basic with an
EMPTY username and the PAT as the password (``API::Space::BaseController`` ->
``Authenticators::PersonalAccessToken``). The mock enforces the same credential on every
``space`` route (``mock_signalwire/auth.py``), so each test here proves the SDK sent it.

Also covers the three wire shapes only this namespace has: a ``text/csv`` success
(``billing_statement.csv``), a success that IS a redirect (``billing_statement.pdf`` -> 302
to the statement's URL), and a required request header (the top-up ``Idempotency-Key``).
"""

from __future__ import annotations

import base64

import pytest

from signalwire.rest._base import SignalWireRestError
from signalwire.rest.client import RestClient

from .conftest import _MockHarness


def _decoded_auth(entry_headers: dict[str, str]) -> str:
    value = entry_headers["authorization"]
    assert value.startswith("Basic ")
    return base64.b64decode(value.split(" ", 1)[1]).decode()


class TestSpaceCredential:
    def test_space_request_carries_the_pat_with_an_empty_username(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.members.list()
        last = mock.last_request()
        assert last.path == "/api/space/members"
        assert last.matched_route == "space.list_members"
        assert last.response_status == 200
        user, _, password = _decoded_auth(last.headers).partition(":")
        assert user == ""
        assert password.startswith("pat_")

    def test_project_resources_keep_the_project_credential(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.addresses.list()
        user, _, _token = _decoded_auth(mock.last_request().headers).partition(":")
        assert user == "test_proj"

    def test_space_error_surfaces_as_rest_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("space.get_space", 401, {"message": "Unauthorized"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.settings.get()
        assert exc.value.status_code == 401
        assert mock.last_request().matched_route == "space.get_space"


class TestSpaceWireShapes:
    def test_member_invite_body(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.members.create(
            email="ada@example.com", role="admin", name="Ada Lovelace"
        )
        last = mock.last_request()
        assert (last.method, last.path) == ("POST", "/api/space/members")
        assert last.body["email"] == "ada@example.com"
        assert last.body == {
            "email": "ada@example.com",
            "role": "admin",
            "name": "Ada Lovelace",
        }

    def test_billing_statement_csv_returns_the_text(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        body = signalwire_client.space.billing_statements.get_csv(month="2026-08")
        assert isinstance(body, str) and body
        last = mock.last_request()
        assert last.path == "/api/space/billing_statement.csv"
        assert last.query_params.get("month") == ["2026-08"]
        assert last.headers.get("accept") == "text/csv"

    def test_billing_statement_pdf_returns_the_redirect_location(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        url = signalwire_client.space.billing_statements.get_pdf(month="2026-08")
        assert url.startswith("https://")
        last = mock.last_request()
        assert last.path == "/api/space/billing_statement.pdf"
        assert last.response_status == 302

    def test_billing_statement_pdf_success_that_is_not_a_redirect_raises(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario(
            "space.get_billing_statement_pdf", 200, {"not": "a redirect"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.space.billing_statements.get_pdf(month="2026-08")
        assert exc.value.status_code == 200

    def test_top_up_sends_the_idempotency_key_header(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.balance.create_top_up(
            idempotency_key="key-123",
            amount_in_microdollars=10_000_000,
            payment_method_id="00000000-0000-4000-8000-000000000000",
        )
        last = mock.last_request()
        assert (last.method, last.path) == ("POST", "/api/space/balance/top_ups")
        assert last.headers.get("idempotency-key") == "key-123"
        assert last.body == {
            "amount_in_microdollars": 10_000_000,
            "payment_method_id": "00000000-0000-4000-8000-000000000000",
        }

    def test_member_project_enable(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.members.enable_project("m-1", "p-1")
        last = mock.last_request()
        assert (last.method, last.path) == (
            "PUT",
            "/api/space/members/m-1/projects/p-1",
        )
        assert last.matched_route == "space.enable_member_project"


class TestSpaceClientConstruction:
    def test_pat_only_client_reaches_space(self) -> None:
        c = RestClient(personal_access_token="pat_x", host="example.signalwire.com")
        assert c.space.members is not None

    def test_pat_only_client_refuses_project_resources(self) -> None:
        c = RestClient(personal_access_token="pat_x", host="example.signalwire.com")
        with pytest.raises(ValueError, match="project and token are required"):
            c.fabric.addresses.list()

    def test_project_only_client_refuses_space(self) -> None:
        c = RestClient(project="p", token="t", host="example.signalwire.com")
        with pytest.raises(ValueError, match="personal_access_token is required"):
            c.space.members.list()

    def test_pat_from_the_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for var in ("SIGNALWIRE_PROJECT_ID", "SIGNALWIRE_API_TOKEN"):
            monkeypatch.delenv(var, raising=False)
        monkeypatch.setenv("SIGNALWIRE_PERSONAL_ACCESS_TOKEN", "pat_env")
        monkeypatch.setenv("SIGNALWIRE_SPACE", "example.signalwire.com")
        c = RestClient()
        assert c._pat_http._session.auth == ("", "pat_env")

    def test_no_credential_at_all_still_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        for var in (
            "SIGNALWIRE_PROJECT_ID",
            "SIGNALWIRE_API_TOKEN",
            "SIGNALWIRE_PERSONAL_ACCESS_TOKEN",
        ):
            monkeypatch.delenv(var, raising=False)
        with pytest.raises(ValueError, match="project, token, and host are required"):
            RestClient(host="example.signalwire.com")
