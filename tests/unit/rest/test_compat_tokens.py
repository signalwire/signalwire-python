"""Compat API tokens tests.

Covers ``CompatTokens.create / .update / .delete``.  Note: ``CompatTokens``
extends ``BaseResource`` (not ``CrudResource``), so its ``update`` uses
PATCH rather than POST.
"""

from __future__ import annotations


class TestCompatTokensCreate:
    def test_returns_token_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.tokens.create(Ttl=3600)
        assert isinstance(result, dict)
        # Token resources carry id + token + permissions.
        assert "token" in result or "id" in result

    def test_journal_records_post_with_ttl(self, signalwire_client, mock):
        signalwire_client.compat.tokens.create(Ttl=3600, Name="api-key")
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == "/api/laml/2010-04-01/Accounts/test_proj/tokens"
        assert isinstance(j.body, dict)
        assert j.body.get("Ttl") == 3600
        assert j.body.get("Name") == "api-key"


class TestCompatTokensUpdate:
    def test_returns_token_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.tokens.update("TK_U", Ttl=7200)
        assert isinstance(result, dict)
        assert "token" in result or "id" in result

    def test_journal_records_patch_with_ttl(self, signalwire_client, mock):
        signalwire_client.compat.tokens.update("TK_UU", Ttl=7200)
        j = mock.last_request()
        # CompatTokens.update uses PATCH (BaseResource.update -> http.patch).
        assert j.method == "PATCH"
        assert j.path == "/api/laml/2010-04-01/Accounts/test_proj/tokens/TK_UU"
        assert isinstance(j.body, dict)
        assert j.body.get("Ttl") == 7200


class TestCompatTokensDelete:
    def test_no_exception_on_delete(self, signalwire_client, mock):
        result = signalwire_client.compat.tokens.delete("TK_D")
        assert isinstance(result, dict)

    def test_journal_records_delete(self, signalwire_client, mock):
        signalwire_client.compat.tokens.delete("TK_DEL")
        j = mock.last_request()
        assert j.method == "DELETE"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/tokens/TK_DEL"
        )
