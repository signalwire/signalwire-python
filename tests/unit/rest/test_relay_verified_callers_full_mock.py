"""Full success + error coverage for ``client.verified_callers`` (relay-rest).

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template.  Verified caller
IDs is a CRUD resource (PUT update) at ``/api/relay/rest/verified_caller_ids``
plus a verification flow: ``redial_verification`` (POST .../verification) and
``submit_verification`` (PUT .../verification).
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError

_BASE = "/api/relay/rest/verified_caller_ids"


class TestRelayVerifiedCallersSuccess:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.verified_callers.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == _BASE
        assert last.matched_route == "relay-rest.list_verified_caller_ids"

    def test_create(self, signalwire_client, mock):
        body = signalwire_client.verified_callers.create(number="+15551112222")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == _BASE
        assert last.matched_route == "relay-rest.create_verified_caller_id"
        assert last.body and last.body.get("number") == "+15551112222"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.verified_callers.get("vc-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{_BASE}/vc-1"
        assert last.matched_route == "relay-rest.retrieve_verified_caller_id"

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.verified_callers.update("vc-1", name="renamed")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == f"{_BASE}/vc-1"
        assert last.matched_route == "relay-rest.update_verified_caller_id"
        assert last.body and last.body.get("name") == "renamed"

    def test_delete(self, signalwire_client, mock):
        signalwire_client.verified_callers.delete("vc-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == f"{_BASE}/vc-1"
        assert last.matched_route == "relay-rest.delete_verified_caller_id"

    def test_redial_verification(self, signalwire_client, mock):
        body = signalwire_client.verified_callers.redial_verification("vc-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == f"{_BASE}/vc-1/verification"
        assert last.matched_route == "relay-rest.redial_verification_call"

    def test_submit_verification(self, signalwire_client, mock):
        body = signalwire_client.verified_callers.submit_verification(
            "vc-1", verification_code="123456"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == f"{_BASE}/vc-1/verification"
        assert last.matched_route == "relay-rest.validate_verification_code"
        assert last.body and last.body.get("verification_code") == "123456"


class TestRelayVerifiedCallersErrors:
    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.list_verified_caller_ids", 500, {"error": "internal"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_verified_caller_ids"
        assert last.response_status == 500

    def test_create_unprocessable(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.create_verified_caller_id", 422, {"error": "bad"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.create(number="+15551112222")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.create_verified_caller_id"
        assert last.response_status == 422

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.retrieve_verified_caller_id", 404, {"error": "nope"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.retrieve_verified_caller_id"
        assert last.response_status == 404

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.update_verified_caller_id", 404, {"error": "nope"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.update("missing", name="x")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.update_verified_caller_id"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.delete_verified_caller_id", 404, {"error": "nope"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.delete_verified_caller_id"
        assert last.response_status == 404

    def test_redial_verification_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.redial_verification_call", 404, {"error": "nope"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.redial_verification("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.redial_verification_call"
        assert last.response_status == 404

    def test_submit_verification_unprocessable(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.validate_verification_code", 422, {"error": "wrong code"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.verified_callers.submit_verification(
                "vc-1", verification_code="000000"
            )
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.validate_verification_code"
        assert last.response_status == 422
