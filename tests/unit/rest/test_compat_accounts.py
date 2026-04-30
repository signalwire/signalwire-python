"""Compat (Twilio-compatible) Accounts resource tests.

Drives ``client.compat.accounts.*`` against the real ``mock_signalwire``
HTTP server.  Each test asserts on both the SDK return value and the
recorded request journal so neither half is allowed to drift.
"""

from __future__ import annotations

import pytest


class TestCompatAccountsCreate:
    """``CompatAccounts.create`` -> POST /api/laml/2010-04-01/Accounts."""

    def test_returns_account_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.accounts.create(FriendlyName="Sub-A")
        # Synthesised response for the Account resource carries an account
        # body with friendly_name and date timestamps.
        assert isinstance(result, dict), f"expected dict, got {type(result).__name__}"
        assert "friendly_name" in result, f"missing 'friendly_name' in {sorted(result)!r}"

    def test_journal_records_post_to_accounts(self, signalwire_client, mock):
        signalwire_client.compat.accounts.create(FriendlyName="Sub-B")
        j = mock.last_request()
        assert j.method == "POST", f"expected POST, got {j.method!r}"
        # Accounts.create lives at the top-level Accounts collection - no
        # AccountSid prefix.
        assert j.path == "/api/laml/2010-04-01/Accounts", f"unexpected path {j.path!r}"
        # The keyword argument surfaced in the wire body.
        assert isinstance(j.body, dict)
        assert j.body.get("FriendlyName") == "Sub-B"
        assert 200 <= (j.response_status or 0) < 400


class TestCompatAccountsGet:
    """``CompatAccounts.get(sid)`` -> GET /api/laml/2010-04-01/Accounts/{sid}."""

    def test_returns_account_for_sid(self, signalwire_client, mock):
        result = signalwire_client.compat.accounts.get("AC123")
        assert isinstance(result, dict)
        # The retrieve endpoint synthesizes a single Account body.
        assert "friendly_name" in result

    def test_journal_records_get_with_sid(self, signalwire_client, mock):
        signalwire_client.compat.accounts.get("AC_SAMPLE_SID")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == "/api/laml/2010-04-01/Accounts/AC_SAMPLE_SID"
        # GET should not carry a request body.
        assert j.body in (None, "", {})
        assert j.matched_route is not None, "spec gap: account-get should match a route"


class TestCompatAccountsUpdate:
    """``CompatAccounts.update(sid, **kwargs)`` -> POST /api/laml/.../Accounts/{sid}."""

    def test_returns_updated_account(self, signalwire_client, mock):
        result = signalwire_client.compat.accounts.update(
            "AC123", FriendlyName="Renamed"
        )
        assert isinstance(result, dict)
        assert "friendly_name" in result

    def test_journal_records_post_to_account_path(self, signalwire_client, mock):
        signalwire_client.compat.accounts.update("AC_X", FriendlyName="NewName")
        j = mock.last_request()
        # Twilio-compat update is POST (not PATCH/PUT).
        assert j.method == "POST"
        assert j.path == "/api/laml/2010-04-01/Accounts/AC_X"
        assert isinstance(j.body, dict)
        assert j.body.get("FriendlyName") == "NewName"
