"""REST fields and params the prime-rails code accepts, now in the spec (round 2) -- live mock.

porting-sdk corrected messages, fabric, video and space base facts from
prime-rails@61268748c7: WhatsApp message fields, subscriber-token binding fields, epoch
timestamps for video date fields, and update/create bodies that no longer require a field
the contract prefills or allows to be nil. Each test sends the request over the real mock
and asserts the mock recorded it with NO wire violation. The new-field tests fail against
the previous base (STRICT-MOCKS flags the undeclared body keys); the loosened/widened ones
guard the generated signatures (the previous SDK required ``enable_room_previews`` / ``url``
/ ``name`` and typed ``join_until`` as ``str``).
"""

from __future__ import annotations

from typing import Any

import requests

from signalwire.rest.client import RestClient

from .conftest import _MockHarness


def _last_raw(mock: _MockHarness) -> dict[str, Any]:
    """The most recent raw journal entry for this client (keeps ``wire_violations``)."""
    resp = requests.get(f"{mock.url}/__mock__/journal", timeout=5)
    resp.raise_for_status()
    mine = {mock.auth_header, mock.pat_auth_header} - {""}
    entries = [
        e for e in resp.json() if (e.get("headers") or {}).get("authorization") in mine
    ]
    assert entries, "no request recorded for this client"
    return dict(entries[-1])


def _clean(mock: _MockHarness, route: str) -> dict[str, Any]:
    entry = _last_raw(mock)
    assert entry.get("matched_route") == route, entry.get("matched_route")
    assert not entry.get("wire_violations"), entry.get("wire_violations")
    assert 200 <= int(entry.get("response_status") or 0) < 300, entry.get(
        "response_status"
    )
    return entry


class TestWhatsappMessages:
    def test_template_message_sends_template_id_and_parameters(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.messages.create(
            to="+15551234567",
            from_="whatsapp:+15559876543",
            template_id="order_update",
            body_template_parameters={"order": "12345"},
            button_template_parameters=["track"],
        )
        entry = _clean(mock, "messages.create_message")
        assert entry["body"]["template_id"] == "order_update"
        assert entry["body"]["body_template_parameters"] == {"order": "12345"}
        assert entry["body"]["button_template_parameters"] == ["track"]

    def test_content_message_sends_message_type_and_an_object_body(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.messages.create(
            to="+15551234567",
            from_="whatsapp:+15559876543",
            message_type="whatsapp_media_location",
            body={"latitude": 1.5, "longitude": 2.5},
        )
        entry = _clean(mock, "messages.create_message")
        assert entry["body"]["message_type"] == "whatsapp_media_location"
        assert entry["body"]["body"] == {"latitude": 1.5, "longitude": 2.5}


class TestFabricFields:
    def test_subscriber_token_binds_a_fingerprint_and_the_refresh_scope(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        fingerprint = "A" * 43
        signalwire_client.fabric.tokens.create_subscriber_token(
            reference="ada@example.com", scope="sat:refresh", fingerprint=fingerprint
        )
        entry = _clean(mock, "fabric.create_subscriber_token")
        assert entry["body"]["scope"] == "sat:refresh"
        assert entry["body"]["fingerprint"] == fingerprint

    def test_conference_room_create_without_enable_room_previews(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.conference_rooms.create(name="standup")
        entry = _clean(mock, "fabric.create_conference_room")
        assert "enable_room_previews" not in entry["body"]


class TestVideoFields:
    def test_room_create_takes_an_epoch_join_until(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.rooms.create(name="standup", join_until=1767225599)
        entry = _clean(mock, "video.create_room")
        assert entry["body"]["join_until"] == 1767225599

    def test_stream_update_without_url(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.video.streams.update("5c7ab86a-3ae4-4cf1-9da2-b6a11a5dc4a0")
        _clean(mock, "video.update_stream")


class TestSpaceFields:
    def test_space_update_without_name(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.space.settings.update()
        _clean(mock, "space.update_space")
