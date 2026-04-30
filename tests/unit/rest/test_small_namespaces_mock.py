"""Coverage for small REST namespaces against the live mock server.

Covers the gaps reported by ``audit_python_test_coverage.py`` for namespaces
that each had only a handful of uncovered methods:

- ``addresses`` — list / get / create / delete
- ``recordings`` — list / get / delete
- ``short_codes`` — list / get / update
- ``imported_numbers`` — create
- ``mfa`` — call
- ``sip_profile`` — update
- ``number_groups`` — list_memberships / delete_membership
- ``project.tokens`` — update / delete
- ``datasphere.documents`` — get_chunk
- ``queues`` — get_member

Each test:
1. Calls the SDK method against the in-process ``mock_signalwire`` server.
2. Asserts on the response body shape that the mock returns from the spec.
3. Asserts on ``mock.last_request()`` so we know the SDK sent the correct
   wire request — method, path, and body where applicable.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Addresses
# ---------------------------------------------------------------------------


class TestAddresses:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.addresses.list(page_size=10)
        assert isinstance(body, dict)
        assert "data" in body
        assert isinstance(body["data"], list)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/relay/rest/addresses"
        assert last.matched_route is not None
        assert last.query_params.get("page_size") == ["10"]

    def test_create(self, signalwire_client, mock):
        body = signalwire_client.addresses.create(
            address_type="commercial",
            first_name="Ada",
            last_name="Lovelace",
            country="US",
        )
        assert isinstance(body, dict)
        # An Address resource carries an 'id' field.
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/relay/rest/addresses"
        sent = last.body or {}
        assert sent.get("address_type") == "commercial"
        assert sent.get("first_name") == "Ada"
        assert sent.get("country") == "US"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.addresses.get("addr-123")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/relay/rest/addresses/addr-123"
        assert last.matched_route is not None

    def test_delete(self, signalwire_client, mock):
        body = signalwire_client.addresses.delete("addr-123")
        # 204 on delete returns {}.
        assert body == {} or isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/relay/rest/addresses/addr-123"
        assert last.response_status in (200, 202, 204)


# ---------------------------------------------------------------------------
# Recordings
# ---------------------------------------------------------------------------


class TestRecordings:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.recordings.list(page_size=5)
        assert isinstance(body, dict)
        assert "data" in body
        assert isinstance(body["data"], list)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/relay/rest/recordings"
        assert last.query_params.get("page_size") == ["5"]

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.recordings.get("rec-123")
        assert isinstance(body, dict)
        # The Recording schema has an 'id' field.
        assert "id" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/relay/rest/recordings/rec-123"

    def test_delete(self, signalwire_client, mock):
        body = signalwire_client.recordings.delete("rec-123")
        assert body == {} or isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/relay/rest/recordings/rec-123"
        assert last.response_status in (200, 202, 204)


# ---------------------------------------------------------------------------
# Short Codes
# ---------------------------------------------------------------------------


class TestShortCodes:
    def test_list(self, signalwire_client, mock):
        body = signalwire_client.short_codes.list(page_size=20)
        assert isinstance(body, dict)
        assert "data" in body
        assert isinstance(body["data"], list)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/relay/rest/short_codes"

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.short_codes.get("sc-1")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/relay/rest/short_codes/sc-1"

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.short_codes.update("sc-1", name="Marketing SMS")
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        # short_codes uses PUT for update per CrudResource override.
        assert last.method == "PUT"
        assert last.path == "/api/relay/rest/short_codes/sc-1"
        sent = last.body or {}
        assert sent.get("name") == "Marketing SMS"


# ---------------------------------------------------------------------------
# Imported Numbers
# ---------------------------------------------------------------------------


class TestImportedNumbers:
    def test_create(self, signalwire_client, mock):
        body = signalwire_client.imported_numbers.create(
            number="+15551234567",
            sip_username="alice",
            sip_password="secret",
            sip_proxy="sip.example.com",
        )
        assert isinstance(body, dict)
        # The imported-number response has an 'id'.
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/relay/rest/imported_phone_numbers"
        sent = last.body or {}
        assert sent.get("number") == "+15551234567"
        assert sent.get("sip_username") == "alice"
        assert sent.get("sip_proxy") == "sip.example.com"


# ---------------------------------------------------------------------------
# MFA — voice channel
# ---------------------------------------------------------------------------


class TestMfa:
    def test_call(self, signalwire_client, mock):
        body = signalwire_client.mfa.call(
            to="+15551234567",
            from_="+15559876543",
            message="Your code is {code}",
        )
        assert isinstance(body, dict)
        # The mfa response has 'id', 'success', 'channel', 'to'.
        assert "id" in body
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/relay/rest/mfa/call"
        sent = last.body or {}
        assert sent.get("to") == "+15551234567"
        assert sent.get("from_") == "+15559876543"
        assert sent.get("message") == "Your code is {code}"


# ---------------------------------------------------------------------------
# SIP Profile
# ---------------------------------------------------------------------------


class TestSipProfile:
    def test_update(self, signalwire_client, mock):
        body = signalwire_client.sip_profile.update(
            domain="myco.sip.signalwire.com",
            default_codecs=["PCMU", "PCMA"],
        )
        assert isinstance(body, dict)
        # The SIP profile resource has a 'domain' field.
        assert "domain" in body or "default_codecs" in body
        last = mock.last_request()
        assert last.method == "PUT"
        assert last.path == "/api/relay/rest/sip_profile"
        sent = last.body or {}
        assert sent.get("domain") == "myco.sip.signalwire.com"
        assert sent.get("default_codecs") == ["PCMU", "PCMA"]


# ---------------------------------------------------------------------------
# Number Groups — membership operations
# ---------------------------------------------------------------------------


class TestNumberGroups:
    def test_list_memberships(self, signalwire_client, mock):
        body = signalwire_client.number_groups.list_memberships(
            "ng-1", page_size=10,
        )
        assert isinstance(body, dict)
        assert "data" in body
        assert isinstance(body["data"], list)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/relay/rest/number_groups/ng-1/number_group_memberships"
        assert last.query_params.get("page_size") == ["10"]

    def test_delete_membership(self, signalwire_client, mock):
        body = signalwire_client.number_groups.delete_membership("mem-1")
        assert body == {} or isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/relay/rest/number_group_memberships/mem-1"
        assert last.response_status in (200, 202, 204)


# ---------------------------------------------------------------------------
# Project tokens — update + delete
# ---------------------------------------------------------------------------


class TestProjectTokens:
    def test_update(self, signalwire_client, mock):
        body = signalwire_client.project.tokens.update(
            "tok-1", name="renamed-token",
        )
        assert isinstance(body, dict)
        assert "id" in body
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.path == "/api/project/tokens/tok-1"
        sent = last.body or {}
        assert sent.get("name") == "renamed-token"

    def test_delete(self, signalwire_client, mock):
        body = signalwire_client.project.tokens.delete("tok-1")
        assert body == {} or isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/project/tokens/tok-1"
        assert last.response_status in (200, 202, 204)


# ---------------------------------------------------------------------------
# Datasphere — get_chunk
# ---------------------------------------------------------------------------


class TestDatasphere:
    def test_get_chunk(self, signalwire_client, mock):
        body = signalwire_client.datasphere.documents.get_chunk(
            "doc-1", "chunk-99",
        )
        assert isinstance(body, dict)
        # The DatasphereChunk schema has an 'id'.
        assert "id" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/datasphere/documents/doc-1/chunks/chunk-99"


# ---------------------------------------------------------------------------
# Queues — get_member
# ---------------------------------------------------------------------------


class TestQueues:
    def test_get_member(self, signalwire_client, mock):
        body = signalwire_client.queues.get_member("q-1", "mem-7")
        assert isinstance(body, dict)
        # A queue member has 'queue_id' and 'call_id' per the spec example.
        assert "queue_id" in body or "call_id" in body
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/relay/rest/queues/q-1/members/mem-7"
