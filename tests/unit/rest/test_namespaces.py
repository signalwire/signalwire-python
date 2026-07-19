"""Tests for remaining namespaces — phone_numbers, video, datasphere, etc."""

from .conftest import MockResponse
from signalwire.rest.client import RestClient
from signalwire.rest.namespaces.relay_rest_types_generated import (
    CreateCspBrandRequest,
)
from unittest.mock import MagicMock


class TestPhoneNumbers:
    def test_search(self, client: RestClient, mock_session: MagicMock) -> None:
        # spec wire key is `areacode` (relay-rest/openapi.yaml), NOT `area_code` — this
        # passthrough test previously enshrined the wrong key (round-4). Wire-truth is
        # proven by the strict-mock generated test, not this fake-transport shape test.
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.phone_numbers.search(areacode="512")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/relay/rest/phone_numbers/search",
            json=None, params={"areacode": "512"}, timeout=30.0,
        )

    def test_update_uses_put(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {})
        client.phone_numbers.update("pn-1", name="Main")
        mock_session.request.assert_called_with(
            "PUT", "https://test.signalwire.com/api/relay/rest/phone_numbers/pn-1",
            json={"name": "Main"}, params=None, timeout=30.0,
        )


class TestQueues:
    def test_list_members(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.queues.list_members("q-1")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/relay/rest/queues/q-1/members",
            json=None, params=None, timeout=30.0,
        )

    def test_get_next_member(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {})
        client.queues.get_next_member("q-1")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/relay/rest/queues/q-1/members/next",
            json=None, params=None, timeout=30.0,
        )


class TestNumberGroups:
    def test_add_membership(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(201, {})
        client.number_groups.add_membership("ng-1", phone_number_id="pn-1")
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/relay/rest/number_groups/ng-1/number_group_memberships",
            json={"phone_number_id": "pn-1"}, params=None, timeout=30.0,
        )

    def test_get_membership(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {})
        client.number_groups.get_membership("mem-1")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/relay/rest/number_group_memberships/mem-1",
            json=None, params=None, timeout=30.0,
        )


class TestVerifiedCallers:
    def test_redial_verification(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {})
        client.verified_callers.redial_verification("vc-1")
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/relay/rest/verified_caller_ids/vc-1/verification",
            json=None, params=None, timeout=30.0,
        )

    def test_submit_verification(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {})
        client.verified_callers.submit_verification("vc-1", verification_code="123456")
        mock_session.request.assert_called_with(
            "PUT", "https://test.signalwire.com/api/relay/rest/verified_caller_ids/vc-1/verification",
            json={"verification_code": "123456"}, params=None, timeout=30.0,
        )


class TestSipProfile:
    def test_get(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"sip_uri": "test"})
        client.sip_profile.get()
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/relay/rest/sip_profile",
            json=None, params=None, timeout=30.0,
        )


class TestLookup:
    def test_phone_number(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {})
        client.lookup.phone_number("+15551234567", include="carrier")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/relay/rest/lookup/phone_number/+15551234567",
            json=None, params={"include": "carrier"}, timeout=30.0,
        )


class TestMfa:
    def test_sms(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"id": "mfa-1"})
        client.mfa.sms(to="+15551234567", from_="+15559876543")
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/relay/rest/mfa/sms",
            json={"to": "+15551234567", "from": "+15559876543"}, params=None, timeout=30.0,
        )

    def test_verify(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"success": True})
        client.mfa.verify("mfa-1", token="123456")  # noqa: S106
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/relay/rest/mfa/mfa-1/verify",
            json={"token": "123456"}, params=None, timeout=30.0,
        )


class TestDatasphere:
    def test_search(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.datasphere.documents.search(query_string="billing")
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/datasphere/documents/search",
            json={"query_string": "billing"}, params=None, timeout=30.0,
        )

    def test_list_chunks(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.datasphere.documents.list_chunks("doc-1")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/datasphere/documents/doc-1/chunks",
            json=None, params=None, timeout=30.0,
        )

    def test_delete_chunk(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(204, None, content=b"")
        client.datasphere.documents.delete_chunk("doc-1", "chunk-1")
        mock_session.request.assert_called_with(
            "DELETE", "https://test.signalwire.com/api/datasphere/documents/doc-1/chunks/chunk-1",
            json=None, params=None, timeout=30.0,
        )


class TestVideo:
    def test_rooms_create(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(201, {"id": "room-1"})
        client.video.rooms.create(name="standup")
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/video/rooms",
            json={"name": "standup"}, params=None, timeout=30.0,
        )

    def test_room_tokens_create(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"token": "abc"})
        client.video.room_tokens.create(room_name="standup", user_name="alice")
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/video/room_tokens",
            json={"room_name": "standup", "user_name": "alice"}, params=None, timeout=30.0,
        )

    def test_session_members(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.video.room_sessions.list_members("sess-1")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/video/room_sessions/sess-1/members",
            json=None, params=None, timeout=30.0,
        )

    def test_conference_streams(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(201, {})
        client.video.conferences.create_stream("conf-1", url="rtmp://example.com/live")
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/video/conferences/conf-1/streams",
            json={"url": "rtmp://example.com/live"}, params=None, timeout=30.0,
        )


class TestLogs:
    def test_voice_events(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.logs.voice.list_events("log-1")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/voice/logs/log-1/events",
            json=None, params=None, timeout=30.0,
        )


class TestRegistry:
    def test_create_brand(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(201, {"id": "brand-1"})
        body: CreateCspBrandRequest = {
            "csp_self_registered": True,
            "name": "MyBrand",
            "csp_brand_reference": "B123456",
        }
        client.registry.brands.create(body)
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/relay/rest/registry/beta/brands",
            json=body, params=None, timeout=30.0,
        )

    def test_campaign_orders(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": []})
        client.registry.campaigns.list_orders("camp-1")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/relay/rest/registry/beta/campaigns/camp-1/orders",
            json=None, params=None, timeout=30.0,
        )


class TestProjectTokens:
    def test_create_token(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"id": "tok-1"})
        client.project.tokens.create(name="test-token", permissions=["calling"])
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/project/tokens",
            json={"name": "test-token", "permissions": ["calling"]}, params=None, timeout=30.0,
        )


class TestPubSubChat:
    def test_pubsub_token(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"token": "abc"})
        client.pubsub.create_token(ttl=60, channels={"room": {"read": True}})
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/pubsub/tokens",
            json={"ttl": 60, "channels": {"room": {"read": True}}}, params=None, timeout=30.0,
        )

    def test_chat_token(self, client: RestClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"token": "abc"})
        client.chat.create_token(ttl=60, channels={"room": {"read": True}})
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/chat/tokens",
            json={"ttl": 60, "channels": {"room": {"read": True}}}, params=None, timeout=30.0,
        )


class TestDeprecationShimPaths:
    """3-python-b: the 21 namespace deprecation shims must warn with the REAL installed
    import path (signalwire.rest.namespaces.X), not the doubled repo-layout path
    (signalwire.signalwire.…) they used to name — a user can't act on a path that
    doesn't exist."""

    def test_shim_warns_with_real_import_path(self) -> None:
        import importlib
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import signalwire.rest.namespaces.calling  # noqa: F401
            importlib.reload(signalwire.rest.namespaces.calling)
        dep = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert dep, "shim did not warn"
        msg = str(dep[-1].message)
        assert "signalwire.rest.namespaces.calling is deprecated" in msg
        assert "signalwire.signalwire" not in msg
