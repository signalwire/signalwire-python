"""Full success + error coverage for the smaller relay-rest namespaces.

Mirrors the ``test_fabric_ai_agents_full_mock`` micro-template.  Covers:

* ``client.sip_profile`` — singleton get/update (``/api/relay/rest/sip_profile``)
* ``client.lookup`` — phone-number lookup (``/api/relay/rest/lookup/phone_number/{e164}``)
* ``client.short_codes`` — list/get/update (``/api/relay/rest/short_codes``)
* ``client.imported_numbers`` — create only (``/api/relay/rest/imported_phone_numbers``)
* ``client.mfa`` — call/sms request + verify (``/api/relay/rest/mfa/...``)
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError


class TestRelaySipProfileSuccess:
    _BASE = "/api/relay/rest/sip_profile"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.sip_profile.get()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == self._BASE
        assert last.matched_route == "relay-rest.retrieve_sip_profile"

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.sip_profile.update(domain_identifier="acme")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == self._BASE
        assert last.matched_route == "relay-rest.update_sip_profile"
        assert last.body and last.body.get("domain_identifier") == "acme"


class TestRelaySipProfileErrors:
    def test_get_server_error(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.retrieve_sip_profile", 500, {"error": "boom"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.sip_profile.get()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "relay-rest.retrieve_sip_profile"
        assert last.response_status == 500

    def test_update_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.update_sip_profile", 422, {"error": "bad"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.sip_profile.update(domain_identifier="")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.update_sip_profile"
        assert last.response_status == 422


class TestRelayLookupSuccess:
    def test_phone_number(self, signalwire_client, mock):
        body = signalwire_client.lookup.phone_number("+15551230000")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/relay/rest/lookup/phone_number/+15551230000"
        assert last.matched_route == "relay-rest.lookup_phone_number"


class TestRelayLookupErrors:
    def test_phone_number_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.lookup_phone_number", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.lookup.phone_number("+19999999999")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.lookup_phone_number"
        assert last.response_status == 404


class TestRelayShortCodesSuccess:
    _BASE = "/api/relay/rest/short_codes"

    def test_list(self, signalwire_client, mock):
        body = signalwire_client.short_codes.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == self._BASE
        assert last.matched_route == "relay-rest.list_short_codes"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.short_codes.get("sc-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == f"{self._BASE}/sc-1"
        assert last.matched_route == "relay-rest.retrieve_short_code"

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.short_codes.update(
            "sc-1", name="promo", message_handler="relay_context"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == f"{self._BASE}/sc-1"
        assert last.matched_route == "relay-rest.update_short_code"
        assert last.body and last.body.get("name") == "promo"


class TestRelayShortCodesErrors:
    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.list_short_codes", 500, {"error": "boom"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.short_codes.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "relay-rest.list_short_codes"
        assert last.response_status == 500

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.retrieve_short_code", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.short_codes.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.retrieve_short_code"
        assert last.response_status == 404

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.update_short_code", 404, {"error": "nope"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.short_codes.update(
                "missing", name="x", message_handler="relay_context"
            )
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "relay-rest.update_short_code"
        assert last.response_status == 404


class TestRelayImportedNumbersSuccess:
    _BASE = "/api/relay/rest/imported_phone_numbers"

    def test_create(self, signalwire_client, mock):
        body = signalwire_client.imported_numbers.create(
            number="+15551230000", number_type="longcode"
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == self._BASE
        assert last.matched_route == "relay-rest.create_imported_phone_number"
        assert last.body and last.body.get("number") == "+15551230000"


class TestRelayImportedNumbersErrors:
    def test_create_unprocessable(self, signalwire_client, mock):
        mock.push_scenario(
            "relay-rest.create_imported_phone_number", 422, {"error": "bad"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.imported_numbers.create(
                number="+15551230000", number_type="longcode"
            )
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.create_imported_phone_number"
        assert last.response_status == 422


class TestRelayMfaSuccess:
    def test_call(self, signalwire_client, mock):
        body = signalwire_client.mfa.call(to="+15551230000")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/relay/rest/mfa/call"
        assert last.matched_route == "relay-rest.request_mfa_call"
        assert last.body and last.body.get("to") == "+15551230000"

    def test_sms(self, signalwire_client, mock):
        body = signalwire_client.mfa.sms(to="+15551230000")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/relay/rest/mfa/sms"
        assert last.matched_route == "relay-rest.request_mfa_sms"
        assert last.body and last.body.get("to") == "+15551230000"

    def test_verify(self, signalwire_client, mock):
        otp = "123456"
        body = signalwire_client.mfa.verify("mfa-1", token=otp)
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/relay/rest/mfa/mfa-1/verify"
        assert last.matched_route == "relay-rest.verify_mfa_token"
        assert last.body and last.body.get("token") == otp


class TestRelayMfaErrors:
    def test_call_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.request_mfa_call", 422, {"error": "to required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.mfa.call(to="+15551230000")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.request_mfa_call"
        assert last.response_status == 422

    def test_sms_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.request_mfa_sms", 422, {"error": "to required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.mfa.sms(to="+15551230000")
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.request_mfa_sms"
        assert last.response_status == 422

    def test_verify_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("relay-rest.verify_mfa_token", 422, {"error": "bad token"})
        otp = "000000"
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.mfa.verify("mfa-1", token=otp)
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "relay-rest.verify_mfa_token"
        assert last.response_status == 422
