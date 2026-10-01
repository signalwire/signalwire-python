"""REST fields and params the prime-rails code accepts, now in the spec -- against the live mock.

porting-sdk corrected fabric and relay-rest base facts from prime-rails@29d6dce4b5 (routes,
contracts, serializers): list params the index contracts read (cursor pagination, the queue
name filter), request fields the create/update contracts accept, and update bodies that no
longer require fields the stored record already has. Each test sends the newly declared
field over the real mock and asserts the mock recorded it with NO wire violation: the mock's
STRICT-MOCKS check flags an undeclared query param or body key, so before the spec fix
every one of these requests was a violation.
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


class TestRelayListPagination:
    def test_queues_list_takes_cursor_pagination_and_the_name_filter(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.queues.list(page_size=5, page_number=0, filter_name="support")
        entry = _clean(mock, "relay-rest.list_queues")
        assert entry["query_params"]["page_size"] == ["5"]
        assert entry["query_params"]["filter_name"] == ["support"]

    def test_registry_brands_list_takes_cursor_pagination(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.brands.list(page_size=10)
        entry = _clean(mock, "relay-rest.list_brands")
        assert entry["query_params"]["page_size"] == ["10"]


class TestRelayRequestFields:
    def test_address_create_sends_the_e911_validation_switches(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.addresses.create(
            label="HQ",
            country="US",
            first_name="Ada",
            last_name="Lovelace",
            street_number="1",
            street_name="Main St",
            city="Hill Valley",
            state="CA",
            postal_code="91905",
            emergency_enabled=True,
            auto_correct_address=False,
        )
        entry = _clean(mock, "relay-rest.create_address")
        assert entry["body"]["emergency_enabled"] is True
        assert entry["body"]["auto_correct_address"] is False

    def test_campaign_update_sends_status_callback_and_contact_emails(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.registry.campaigns.update(
            "c1",
            status_callback_url="https://example.com/cb",
            signalwire_contact_emails=["ops@example.com"],
        )
        entry = _clean(mock, "relay-rest.update_campaign")
        assert entry["body"] == {
            "status_callback_url": "https://example.com/cb",
            "signalwire_contact_emails": ["ops@example.com"],
        }

    def test_short_code_update_needs_no_stored_fields(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.short_codes.update(
            "sc1", message_request_url="https://example.com/m"
        )
        entry = _clean(mock, "relay-rest.update_short_code")
        assert entry["body"] == {"message_request_url": "https://example.com/m"}

    def test_sip_profile_update_sends_the_outbound_policy(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.sip_profile.update(default_outbound_policy="block-pstn")
        entry = _clean(mock, "relay-rest.update_sip_profile")
        assert entry["body"]["default_outbound_policy"] == "block-pstn"


class TestFabricRequestFields:
    def test_subscriber_update_sends_time_zone_without_email(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.subscribers.update("s1", time_zone="America/New_York")
        entry = _clean(mock, "fabric.update_subscriber")
        assert entry["body"] == {"time_zone": "America/New_York"}

    def test_cxml_application_update_sends_the_contract_field_names(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.cxml_applications.update(
            "a1",
            name="IVR",
            call_request_url="https://example.com/voice",
            call_request_method="GET",
        )
        entry = _clean(mock, "fabric.update_cxml_application")
        assert entry["body"] == {
            "name": "IVR",
            "call_request_url": "https://example.com/voice",
            "call_request_method": "GET",
        }

    def test_sip_endpoint_create_needs_only_username_and_password(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.sip_endpoints.create(
            username="alice", password="s3cret-pass"
        )
        entry = _clean(mock, "fabric.create_sip_endpoint")
        assert entry["body"] == {"username": "alice", "password": "s3cret-pass"}
        assert entry["response_status"] == 201

    def test_guest_token_needs_no_allowed_addresses(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.fabric.tokens.create_guest_token(
            first_name="Guest", time_zone="UTC"
        )
        entry = _clean(mock, "fabric.create_subscriber_guest_token")
        assert entry["body"] == {"first_name": "Guest", "time_zone": "UTC"}
