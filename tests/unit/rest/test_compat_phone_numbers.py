"""Compat IncomingPhoneNumbers + AvailablePhoneNumbers tests.

Covers the 8 uncovered ``CompatPhoneNumbers`` symbols:

  - list, get, update, delete (basic CRUD over IncomingPhoneNumbers)
  - purchase, import_number (phone-number provisioning)
  - list_available_countries, search_toll_free
"""

from __future__ import annotations


class TestCompatPhoneNumbersList:
    def test_returns_paginated_list(self, signalwire_client, mock):
        result = signalwire_client.compat.phone_numbers.list()
        assert isinstance(result, dict)
        assert "incoming_phone_numbers" in result, (
            f"expected 'incoming_phone_numbers' key, got {sorted(result)!r}"
        )
        assert isinstance(result["incoming_phone_numbers"], list)

    def test_journal_records_get_to_incoming_phone_numbers(
        self, signalwire_client, mock
    ):
        signalwire_client.compat.phone_numbers.list()
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/IncomingPhoneNumbers"
        )


class TestCompatPhoneNumbersGet:
    def test_returns_phone_number_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.phone_numbers.get("PN_TEST")
        assert isinstance(result, dict)
        # Incoming phone-number resources carry phone_number + sid + capabilities.
        assert "phone_number" in result or "sid" in result

    def test_journal_records_get_with_sid(self, signalwire_client, mock):
        signalwire_client.compat.phone_numbers.get("PN_GET")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/IncomingPhoneNumbers/PN_GET"
        )


class TestCompatPhoneNumbersUpdate:
    def test_returns_phone_number_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.phone_numbers.update(
            "PN_U", FriendlyName="updated"
        )
        assert isinstance(result, dict)
        assert "phone_number" in result or "sid" in result

    def test_journal_records_post_with_friendly_name(self, signalwire_client, mock):
        signalwire_client.compat.phone_numbers.update(
            "PN_UU", FriendlyName="updated", VoiceUrl="https://a.b/v"
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/IncomingPhoneNumbers/PN_UU"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("FriendlyName") == "updated"
        assert j.body.get("VoiceUrl") == "https://a.b/v"


class TestCompatPhoneNumbersDelete:
    def test_no_exception_on_delete(self, signalwire_client, mock):
        result = signalwire_client.compat.phone_numbers.delete("PN_D")
        assert isinstance(result, dict)

    def test_journal_records_delete_at_phone_number_path(
        self, signalwire_client, mock
    ):
        signalwire_client.compat.phone_numbers.delete("PN_DEL")
        j = mock.last_request()
        assert j.method == "DELETE"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/IncomingPhoneNumbers/PN_DEL"
        )


class TestCompatPhoneNumbersPurchase:
    """Purchase = POST /IncomingPhoneNumbers (the same path as list, but POST)."""

    def test_returns_purchased_number(self, signalwire_client, mock):
        result = signalwire_client.compat.phone_numbers.purchase(
            PhoneNumber="+15555550100"
        )
        assert isinstance(result, dict)
        # Purchase returns the newly created IncomingPhoneNumber.
        assert "phone_number" in result or "sid" in result

    def test_journal_records_post_with_phone_number(self, signalwire_client, mock):
        signalwire_client.compat.phone_numbers.purchase(
            PhoneNumber="+15555550100", FriendlyName="Main"
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/IncomingPhoneNumbers"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("PhoneNumber") == "+15555550100"
        assert j.body.get("FriendlyName") == "Main"


class TestCompatPhoneNumbersImportNumber:
    """Import = POST /ImportedPhoneNumbers (different path from purchase)."""

    def test_returns_imported_number(self, signalwire_client, mock):
        result = signalwire_client.compat.phone_numbers.import_number(
            PhoneNumber="+15555550111"
        )
        assert isinstance(result, dict)
        # Imported numbers also synthesise to IncomingPhoneNumber-shaped.
        assert "phone_number" in result or "sid" in result

    def test_journal_records_post_to_imported_phone_numbers(
        self, signalwire_client, mock
    ):
        signalwire_client.compat.phone_numbers.import_number(
            PhoneNumber="+15555550111", VoiceUrl="https://a.b/v"
        )
        j = mock.last_request()
        assert j.method == "POST"
        # Note the path is ImportedPhoneNumbers, not IncomingPhoneNumbers.
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/ImportedPhoneNumbers"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("PhoneNumber") == "+15555550111"


class TestCompatPhoneNumbersListAvailableCountries:
    """list_available_countries = GET /AvailablePhoneNumbers."""

    def test_returns_countries_collection(self, signalwire_client, mock):
        result = signalwire_client.compat.phone_numbers.list_available_countries()
        assert isinstance(result, dict)
        # Available countries response wraps a 'countries' list.
        assert "countries" in result, (
            f"expected 'countries' key, got {sorted(result)!r}"
        )
        assert isinstance(result["countries"], list)

    def test_journal_records_get_to_available_phone_numbers(
        self, signalwire_client, mock
    ):
        signalwire_client.compat.phone_numbers.list_available_countries()
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/AvailablePhoneNumbers"
        )


class TestCompatPhoneNumbersSearchTollFree:
    """search_toll_free(country, **) = GET /AvailablePhoneNumbers/{c}/TollFree."""

    def test_returns_available_numbers(self, signalwire_client, mock):
        result = signalwire_client.compat.phone_numbers.search_toll_free(
            "US", AreaCode="800"
        )
        assert isinstance(result, dict)
        assert "available_phone_numbers" in result, (
            f"expected 'available_phone_numbers' key, got {sorted(result)!r}"
        )
        assert isinstance(result["available_phone_numbers"], list)

    def test_journal_records_get_with_country_in_path(
        self, signalwire_client, mock
    ):
        signalwire_client.compat.phone_numbers.search_toll_free(
            "US", AreaCode="888"
        )
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/AvailablePhoneNumbers/US/TollFree"
        )
        # The AreaCode should be on the query string, not body.
        assert "AreaCode" in j.query_params
        assert j.query_params["AreaCode"] == ["888"]
