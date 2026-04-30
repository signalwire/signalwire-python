"""Compat Messages & Faxes media + update tests.

Covers the gap entries for ``CompatMessages`` and ``CompatFaxes``:

  - Messages: update, get_media, delete_media
  - Faxes:    update, list_media, get_media, delete_media
"""

from __future__ import annotations


# ---- Messages ------------------------------------------------------------


class TestCompatMessagesUpdate:
    def test_returns_message_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.messages.update(
            "MM_TEST", Body="updated body"
        )
        assert isinstance(result, dict)
        # Message resources carry body + status + sid fields.
        assert "body" in result or "sid" in result

    def test_journal_records_post_to_message(self, signalwire_client, mock):
        signalwire_client.compat.messages.update("MM_U1", Body="x", Status="canceled")
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Messages/MM_U1"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("Body") == "x"
        assert j.body.get("Status") == "canceled"


class TestCompatMessagesGetMedia:
    def test_returns_media_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.messages.get_media("MM_GM", "ME_GM")
        assert isinstance(result, dict)
        # Media resources expose content_type + sid + parent_sid.
        assert "content_type" in result or "sid" in result

    def test_journal_records_get_to_media_path(self, signalwire_client, mock):
        signalwire_client.compat.messages.get_media("MM_X", "ME_X")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Messages/MM_X/Media/ME_X"
        )


class TestCompatMessagesDeleteMedia:
    def test_no_exception_on_delete(self, signalwire_client, mock):
        result = signalwire_client.compat.messages.delete_media("MM_DM", "ME_DM")
        # The SDK's DELETE handler returns {} on 204 or whatever the mock
        # body is for non-204 responses.  Either way we expect a dict.
        assert isinstance(result, dict)

    def test_journal_records_delete(self, signalwire_client, mock):
        signalwire_client.compat.messages.delete_media("MM_D", "ME_D")
        j = mock.last_request()
        assert j.method == "DELETE"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Messages/MM_D/Media/ME_D"
        )


# ---- Faxes ---------------------------------------------------------------


class TestCompatFaxesUpdate:
    def test_returns_fax_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.faxes.update("FX_U", Status="canceled")
        assert isinstance(result, dict)
        # Fax resources carry direction + status + duration.
        assert "status" in result or "direction" in result

    def test_journal_records_post_with_status(self, signalwire_client, mock):
        signalwire_client.compat.faxes.update("FX_U2", Status="canceled")
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == "/api/laml/2010-04-01/Accounts/test_proj/Faxes/FX_U2"
        assert isinstance(j.body, dict)
        assert j.body.get("Status") == "canceled"


class TestCompatFaxesListMedia:
    def test_returns_paginated_list(self, signalwire_client, mock):
        result = signalwire_client.compat.faxes.list_media("FX_LM")
        assert isinstance(result, dict)
        # Fax media listing uses 'media' or 'fax_media' as collection key.
        assert "media" in result or "fax_media" in result, (
            f"expected 'media' or 'fax_media' key, got {sorted(result)!r}"
        )

    def test_journal_records_get_to_fax_media(self, signalwire_client, mock):
        signalwire_client.compat.faxes.list_media("FX_LM_X")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Faxes/FX_LM_X/Media"
        )


class TestCompatFaxesGetMedia:
    def test_returns_fax_media_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.faxes.get_media("FX_GM", "ME_GM")
        assert isinstance(result, dict)
        # Fax media carries content_type + sid + fax_sid.
        assert "content_type" in result or "sid" in result

    def test_journal_records_get_to_specific_media(self, signalwire_client, mock):
        signalwire_client.compat.faxes.get_media("FX_G", "ME_G")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Faxes/FX_G/Media/ME_G"
        )


class TestCompatFaxesDeleteMedia:
    def test_no_exception_on_delete(self, signalwire_client, mock):
        result = signalwire_client.compat.faxes.delete_media("FX_DM", "ME_DM")
        assert isinstance(result, dict)

    def test_journal_records_delete(self, signalwire_client, mock):
        signalwire_client.compat.faxes.delete_media("FX_D", "ME_D")
        j = mock.last_request()
        assert j.method == "DELETE"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Faxes/FX_D/Media/ME_D"
        )
