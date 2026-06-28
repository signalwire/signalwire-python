"""Full success + error coverage for ``client.fabric.tokens`` (FabricTokens).

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template: every canonical
route gets a SUCCESS test (call the real SDK method against the live mock, assert
the parsed body shape + the journal entry's method/path/matched_route) and an
ERROR test (arm a 4xx/5xx via ``mock.push_scenario``, assert the SDK raises
``SignalWireRestError`` with the right ``status_code`` and the journal recorded
the route hit with the error status).

``FabricTokens`` creates subscriber / guest / invite / embed tokens under
``/api/fabric`` (note the non-CRUD, irregular paths).
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError


class TestFabricTokensSuccess:
    """Happy-path: each token route hit with a 2xx on the exact canonical path."""

    def test_create_subscriber_token(self, signalwire_client, mock):
        body = signalwire_client.fabric.tokens.create_subscriber_token(
            reference="sub-1001"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/subscribers/tokens"
        assert last.matched_route == "fabric.create_subscriber_token", (
            f"expected fabric.create_subscriber_token, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("reference") == "sub-1001"

    def test_refresh_subscriber_token(self, signalwire_client, mock):
        body = signalwire_client.fabric.tokens.refresh_subscriber_token(
            refresh_token="t-1"  # noqa: S106 - test fixture value, not a real secret
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/subscribers/tokens/refresh"
        assert last.matched_route == "fabric.refresh_subscriber_token", (
            f"expected fabric.refresh_subscriber_token, got {last.matched_route!r}"
        )

    def test_create_invite_token(self, signalwire_client, mock):
        body = signalwire_client.fabric.tokens.create_invite_token(
            address_id="3fa85f64-5717-4562-b3fc-2c963f66afa6"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/subscriber/invites"
        assert last.matched_route == "fabric.create_subscriber_invite_token", (
            f"expected fabric.create_subscriber_invite_token, got {last.matched_route!r}"
        )

    def test_create_guest_token(self, signalwire_client, mock):
        body = signalwire_client.fabric.tokens.create_guest_token(
            allowed_addresses=["addr-1"]
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/guests/tokens"
        assert last.matched_route == "fabric.create_subscriber_guest_token", (
            f"expected fabric.create_subscriber_guest_token, got {last.matched_route!r}"
        )

    def test_create_embed_token(self, signalwire_client, mock):
        body = signalwire_client.fabric.tokens.create_embed_token(token="e-1")  # noqa: S106 - test fixture value, not a real secret
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/fabric/embeds/tokens"
        assert last.matched_route == "fabric.create_embeds_token", (
            f"expected fabric.create_embeds_token, got {last.matched_route!r}"
        )


class TestFabricTokensErrors:
    """Failure path: each token route surfaces a 4xx/5xx as SignalWireRestError."""

    def test_create_subscriber_token_unprocessable(self, signalwire_client, mock):
        mock.push_scenario(
            "fabric.create_subscriber_token", 422, {"error": "reference required"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.tokens.create_subscriber_token(reference="sub-1001")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "fabric.create_subscriber_token"
        assert last.response_status == 422

    def test_refresh_subscriber_token_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "fabric.refresh_subscriber_token", 404, {"error": "token not found"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.tokens.refresh_subscriber_token(
                refresh_token="missing"  # noqa: S106 - test fixture value, not a real secret
            )
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "fabric.refresh_subscriber_token"
        assert last.response_status == 404

    def test_create_invite_token_unprocessable(self, signalwire_client, mock):
        mock.push_scenario(
            "fabric.create_subscriber_invite_token", 422, {"error": "email required"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.tokens.create_invite_token(
                address_id="3fa85f64-5717-4562-b3fc-2c963f66afa6"
            )
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "fabric.create_subscriber_invite_token"
        assert last.response_status == 422

    def test_create_guest_token_unprocessable(self, signalwire_client, mock):
        mock.push_scenario(
            "fabric.create_subscriber_guest_token", 422, {"error": "bad input"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.tokens.create_guest_token(
                allowed_addresses=["addr-1"]
            )
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "fabric.create_subscriber_guest_token"
        assert last.response_status == 422

    def test_create_embed_token_server_error(self, signalwire_client, mock):
        mock.push_scenario("fabric.create_embeds_token", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.fabric.tokens.create_embed_token(token="e-1")  # noqa: S106 - test fixture value, not a real secret
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "fabric.create_embeds_token"
        assert last.response_status == 500
