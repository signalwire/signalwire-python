"""Compat Queues tests.

Covers ``CompatQueues.update``, ``list_members``, ``get_member``, and
``dequeue_member``.
"""

from __future__ import annotations


class TestCompatQueuesUpdate:
    def test_returns_queue_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.queues.update(
            "QU_U", FriendlyName="updated"
        )
        assert isinstance(result, dict)
        # Queue resources expose friendly_name + sid + max_size.
        assert "friendly_name" in result or "sid" in result

    def test_journal_records_post_with_friendly_name(self, signalwire_client, mock):
        signalwire_client.compat.queues.update(
            "QU_UU", FriendlyName="renamed", MaxSize=200
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == "/api/laml/2010-04-01/Accounts/test_proj/Queues/QU_UU"
        assert isinstance(j.body, dict)
        assert j.body.get("FriendlyName") == "renamed"
        assert j.body.get("MaxSize") == 200


class TestCompatQueuesListMembers:
    def test_returns_paginated_members(self, signalwire_client, mock):
        result = signalwire_client.compat.queues.list_members("QU_LM")
        assert isinstance(result, dict)
        assert "queue_members" in result, (
            f"expected 'queue_members' key, got {sorted(result)!r}"
        )
        assert isinstance(result["queue_members"], list)

    def test_journal_records_get_to_members(self, signalwire_client, mock):
        signalwire_client.compat.queues.list_members("QU_LMX")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Queues/QU_LMX/Members"
        )


class TestCompatQueuesGetMember:
    def test_returns_member_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.queues.get_member("QU_GM", "CA_GM")
        assert isinstance(result, dict)
        # Member resources expose call_sid + queue_sid + position.
        assert "call_sid" in result or "queue_sid" in result

    def test_journal_records_get_to_specific_member(self, signalwire_client, mock):
        signalwire_client.compat.queues.get_member("QU_GMX", "CA_GMX")
        j = mock.last_request()
        assert j.method == "GET"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Queues/QU_GMX/Members/CA_GMX"
        )


class TestCompatQueuesDequeueMember:
    def test_returns_member_resource(self, signalwire_client, mock):
        result = signalwire_client.compat.queues.dequeue_member(
            "QU_DM", "CA_DM", Url="https://a.b"
        )
        assert isinstance(result, dict)
        assert "call_sid" in result or "queue_sid" in result

    def test_journal_records_post_with_url(self, signalwire_client, mock):
        signalwire_client.compat.queues.dequeue_member(
            "QU_DMX", "CA_DMX", Url="https://a.b/url", Method="POST"
        )
        j = mock.last_request()
        assert j.method == "POST"
        assert j.path == (
            "/api/laml/2010-04-01/Accounts/test_proj/Queues/QU_DMX/Members/CA_DMX"
        )
        assert isinstance(j.body, dict)
        assert j.body.get("Url") == "https://a.b/url"
        assert j.body.get("Method") == "POST"
