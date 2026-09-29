"""HandoffRouter: moving one conversation between voice and text.

The browser side of this contract is already shipped -- the address widget
hardcodes ``/handoff``, ``/escalate`` and ``/say`` against its gateway URL --
so these tests pin the server half against that fixed shape.

Three properties matter more than the happy path:

* **The nonce is proof of having placed a call.** It is never a call id, and an
  unknown nonce is answered exactly like an expired one so the route cannot be
  used to probe whether a given call is live.
* **Ordering.** A medium never starts until the one it replaces has finished
  and been recorded, or the new medium's config fetch races a record that is
  still seconds away and it opens knowing nothing.
* **Typing is repeatable but bounded.** Each injected message is a billable
  turn, so the cap is a spend guard as much as an abuse guard.
"""

import asyncio
import copy
import logging
import threading
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from signalwire.ai_chat import AIChatClient, ChatGateway, HandoffRouter
from signalwire.ai_chat.client import _warn_if_id_will_be_altered
from signalwire.ai_chat.gateway import MAX_MESSAGE_BYTES, MAX_REQUEST_BODY_BYTES

SECRET = "s" * 32


def _recording_sender(events: list[Any]) -> Any:
    """A send_message that records and always succeeds."""

    def _send(call_id: str, text: str) -> bool:
        events.append(("say", text))
        return True

    return _send


@pytest.fixture
def gateway() -> ChatGateway:
    client = AIChatClient(
        project="p",
        token="t",  # noqa: S106 - test fixture, not a credential
        url="https://service.example.invalid/aichat",
    )
    return ChatGateway(
        config_url="https://agent.example.com/swml",
        key="pk_test",
        secret=SECRET,
        client=client,
    )


@pytest.fixture
def events() -> list[tuple[Any, ...]]:
    return []


@pytest.fixture
def handoff(gateway: ChatGateway, events: list[Any]) -> HandoffRouter:
    async def capture(conversation_id: str, medium: str) -> bool:
        await asyncio.sleep(0)  # a real await, not a poll
        events.append(("capture", conversation_id, medium))
        return True

    def end_call(call_id: str) -> None:
        events.append(("end_call", call_id))

    def send_message(call_id: str, text: str) -> bool:
        events.append(("say", call_id, text))
        return True

    return HandoffRouter(
        gateway=gateway,
        capture_leg=capture,
        end_call=end_call,
        send_message=send_message,
    )


@pytest.fixture
def client(handoff: HandoffRouter) -> TestClient:
    app = FastAPI()
    app.include_router(handoff.router(), prefix="/chat")
    return TestClient(app)


class TestHandoffRedemption:
    def test_returns_a_handle_the_gateway_can_read(
        self, handoff: HandoffRouter, client: TestClient, gateway: ChatGateway
    ) -> None:
        handoff.register("n1", conversation_id="conv-root", call_id="call-9")
        response = client.post("/chat/handoff", json={"nonce": "n1"})
        assert response.status_code == 200
        assert gateway.read_handle(response.json()["handle"])

    def test_call_ends_before_the_leg_is_captured(
        self, handoff: HandoffRouter, client: TestClient, events: list[Any]
    ) -> None:
        """Ending first is what makes the record exist to be captured."""
        handoff.register("n1", conversation_id="conv-root", call_id="call-9")
        client.post("/chat/handoff", json={"nonce": "n1"})
        assert events == [
            ("end_call", "call-9"),
            ("capture", "conv-root", "voice"),
        ]

    def test_new_leg_gets_a_fresh_dotted_id(
        self, handoff: HandoffRouter, client: TestClient, gateway: ChatGateway
    ) -> None:
        """An ended conversation cannot be reopened, so the handle must name a
        new leg -- and '.' is the only separator the service preserves."""
        handoff.register("n1", conversation_id="conv-root", call_id="call-9")
        response = client.post("/chat/handoff", json={"nonce": "n1"})
        assert gateway.read_handle(response.json()["handle"]) == "conv-root.1"

    def test_leg_ids_increment(self, handoff: HandoffRouter) -> None:
        assert handoff.next_conversation_id("root.2") == "root.3"
        assert handoff.next_conversation_id("root") == "root.1"

    def test_a_nonce_is_single_use(
        self, handoff: HandoffRouter, client: TestClient
    ) -> None:
        handoff.register("n1", conversation_id="conv-root", call_id="call-9")
        assert client.post("/chat/handoff", json={"nonce": "n1"}).status_code == 200
        assert client.post("/chat/handoff", json={"nonce": "n1"}).status_code == 404

    def test_unknown_and_spent_nonces_are_indistinguishable(
        self, handoff: HandoffRouter, client: TestClient
    ) -> None:
        """Otherwise this route reports whether a given call is live."""
        handoff.register("n1", conversation_id="conv-root", call_id="call-9")
        client.post("/chat/handoff", json={"nonce": "n1"})
        spent = client.post("/chat/handoff", json={"nonce": "n1"})
        unknown = client.post("/chat/handoff", json={"nonce": "never-existed"})
        assert spent.status_code == unknown.status_code == 404
        assert spent.json() == unknown.json()

    def test_expired_nonces_are_not_redeemable(
        self, gateway: ChatGateway, client: TestClient
    ) -> None:
        expired = HandoffRouter(gateway=gateway, nonce_ttl=-1)
        expired.register("n1", conversation_id="conv-root", call_id="call-9")
        assert expired._lookup("n1") is None

    def test_missing_nonce_is_rejected(self, client: TestClient) -> None:
        assert client.post("/chat/handoff", json={}).status_code == 404


class TestRegistration:
    """The per-call config callback registers the nonce on every SWML request
    for the call, and the browser chooses the nonce, so a repeat registration
    must not reset, move or revive an entry."""

    def test_a_repeat_registration_keeps_the_typing_count(
        self, gateway: ChatGateway, events: list[Any]
    ) -> None:
        router = HandoffRouter(
            gateway=gateway,
            send_message=_recording_sender(events),
            max_messages_per_call=1,
        )
        router.register("n", conversation_id="c", call_id="call-1")
        assert asyncio.run(router.say("n", "one"))
        assert not asyncio.run(router.say("n", "two"))
        router.register("n", conversation_id="c", call_id="call-1")
        assert not asyncio.run(router.say("n", "three"))
        assert events == [("say", "one")]

    def test_a_repeat_registration_keeps_the_registration_time(
        self, handoff: HandoffRouter
    ) -> None:
        handoff.register("n", conversation_id="c", call_id="call-1")
        first = handoff._nonces["n"].issued_at
        handoff.register("n", conversation_id="c", call_id="call-1")
        assert handoff._nonces["n"].issued_at == first

    def test_a_live_nonce_cannot_be_moved_to_another_call(
        self, handoff: HandoffRouter, client: TestClient, events: list[Any]
    ) -> None:
        handoff.register("n", conversation_id="conv-a", call_id="call-a")
        handoff.register("n", conversation_id="conv-b", call_id="call-b")
        assert (
            client.post("/chat/say", json={"nonce": "n", "text": "hi"}).status_code
            == 200
        )
        assert events == [("say", "call-a", "hi")]

    def test_a_redeemed_nonce_cannot_be_registered_and_redeemed_again(
        self, handoff: HandoffRouter, client: TestClient
    ) -> None:
        handoff.register("n", conversation_id="conv-root", call_id="call-9")
        assert client.post("/chat/handoff", json={"nonce": "n"}).status_code == 200
        handoff.register("n", conversation_id="conv-root", call_id="call-10")
        again = client.post("/chat/handoff", json={"nonce": "n"})
        assert again.status_code == 404
        assert again.json() == {"error": "not found"}

    def test_a_redeemed_nonce_cannot_type(
        self, handoff: HandoffRouter, client: TestClient, events: list[Any]
    ) -> None:
        handoff.register("n", conversation_id="conv-root", call_id="call-9")
        client.post("/chat/handoff", json={"nonce": "n"})
        events.clear()
        said = client.post("/chat/say", json={"nonce": "n", "text": "late"})
        assert said.status_code == 404
        assert events == []

    def test_redemption_is_kept_until_the_ttl_passes(
        self, handoff: HandoffRouter
    ) -> None:
        handoff.register("n", conversation_id="conv-root", call_id="call-9")
        assert asyncio.run(handoff.redeem("n")) is not None
        entry = handoff._nonces["n"]
        assert entry.redeemed is True
        # Once the entry would have expired it is pruned, and the nonce can be
        # registered afresh.
        entry.issued_at -= handoff.nonce_ttl + 1
        handoff.register("n", conversation_id="conv-new", call_id="call-11")
        assert handoff._nonces["n"].redeemed is False
        assert handoff._nonces["n"].conversation_id == "conv-new"

    def test_a_shared_registry_stores_the_redemption(
        self, gateway: ChatGateway
    ) -> None:
        """A registry backed by shared storage sees the change only when the
        entry is assigned back, so redemption must not rely on mutation."""

        class Recording(dict[str, Any]):
            def __init__(self) -> None:
                super().__init__()
                self.assigned: list[tuple[str, bool]] = []

            def __setitem__(self, key: str, value: Any) -> None:
                self.assigned.append((key, value.redeemed))
                super().__setitem__(key, value)

        registry = Recording()
        router = HandoffRouter(gateway=gateway, registry=registry)
        router.register("n", conversation_id="c", call_id="call-1")
        assert asyncio.run(router.redeem("n")) is not None
        assert registry.assigned == [("n", False), ("n", True)]


class TestConcurrency:
    """The per-call config callback registers nonces in worker threads, and
    /handoff and /say requests overlap, so the table's updates are atomic."""

    def test_a_registration_racing_a_redemption_cant_revive_the_nonce(
        self, gateway: ChatGateway
    ) -> None:
        router = HandoffRouter(gateway=gateway)
        handles: list[str | None] = []

        def register_and_redeem_elsewhere() -> None:
            router.register("n", conversation_id="late", call_id="call-2")
            handles.append(asyncio.run(router.redeem("n")))

        class Racing(dict[str, Any]):
            """Once the first registration has found the nonce absent, runs
            another registration and redemption in another thread, before the
            first one inserts its entry."""

            raced = False

            def get(self, key: Any, default: Any = None) -> Any:
                found = super().get(key, default)
                if not Racing.raced:
                    Racing.raced = True
                    other = threading.Thread(target=register_and_redeem_elsewhere)
                    other.start()
                    other.join(timeout=0.5)  # blocks on the lock if it's atomic
                    racers.append(other)
                return found

        racers: list[threading.Thread] = []
        router._nonces = Racing()
        router.register("n", conversation_id="first", call_id="call-1")
        racers[0].join(timeout=5)
        # One registration stands, and the nonce redeems once
        handles.append(asyncio.run(router.redeem("n")))
        assert sum(handle is not None for handle in handles) == 1

    def test_overlapping_says_cant_pass_the_cap(self, gateway: ChatGateway) -> None:
        delivered: list[str] = []

        async def send(call_id: str, text: str) -> bool:
            await asyncio.sleep(0.01)  # delivery takes a moment
            delivered.append(text)
            return True

        router = HandoffRouter(gateway=gateway, send_message=send, max_messages_per_call=1)
        router.register("n", conversation_id="c", call_id="call-1")

        async def three_at_once() -> list[bool]:
            return list(await asyncio.gather(*(router.say("n", f"m{i}") for i in range(3))))

        results = asyncio.run(three_at_once())
        assert results.count(True) == 1
        assert len(delivered) == 1

    def test_a_failed_delivery_gives_its_slot_back(self, gateway: ChatGateway) -> None:
        attempts: list[str] = []

        def send(call_id: str, text: str) -> bool:
            attempts.append(text)
            if len(attempts) == 1:
                raise ConnectionError("platform unavailable")
            return True

        router = HandoffRouter(gateway=gateway, send_message=send, max_messages_per_call=1)
        router.register("n", conversation_id="c", call_id="call-1")
        assert not asyncio.run(router.say("n", "first"))
        assert asyncio.run(router.say("n", "again"))
        assert not asyncio.run(router.say("n", "over the cap"))
        assert attempts == ["first", "again"]


class TestCopyingRegistry:
    """A shared registry, such as one backed by a cache, returns a copy of
    an entry rather than the stored object."""

    class Copying(dict[str, Any]):
        def get(self, key: Any, default: Any = None) -> Any:
            value = super().get(key, default)
            return copy.deepcopy(value)

        def __setitem__(self, key: str, value: Any) -> None:
            super().__setitem__(key, copy.deepcopy(value))

    def test_a_failed_delivery_gives_its_slot_back(self, gateway: ChatGateway) -> None:
        attempts: list[str] = []

        def send(call_id: str, text: str) -> bool:
            attempts.append(text)
            if len(attempts) == 1:
                raise ConnectionError("platform unavailable")
            return True

        router = HandoffRouter(
            gateway=gateway, send_message=send, max_messages_per_call=1,
            registry=self.Copying(),
        )
        router.register("n", conversation_id="c", call_id="call-1")
        assert not asyncio.run(router.say("n", "first"))
        assert asyncio.run(router.say("n", "again"))
        assert not asyncio.run(router.say("n", "over the cap"))
        assert attempts == ["first", "again"]

    def test_a_redeemed_nonce_stays_redeemed(self, gateway: ChatGateway) -> None:
        router = HandoffRouter(gateway=gateway, registry=self.Copying())
        router.register("n", conversation_id="c", call_id="call-1")
        assert asyncio.run(router.redeem("n")) is not None
        router.register("n", conversation_id="c", call_id="call-1")
        assert asyncio.run(router.redeem("n")) is None


class TestEscalate:
    def test_captures_the_chat_leg_before_returning(
        self, client: TestClient, gateway: ChatGateway, events: list[Any]
    ) -> None:
        """The browser blocks on this, which is what makes the following dial
        safe."""
        handle = gateway.mint_handle("conv-root.5")
        assert client.post("/chat/escalate", json={"handle": handle}).status_code == 200
        assert events == [("capture", "conv-root.5", "chat")]

    def test_a_forged_handle_is_refused(self, client: TestClient) -> None:
        assert (
            client.post("/chat/escalate", json={"handle": "forged"}).status_code == 404
        )

    def test_a_missing_handle_is_a_bad_request(self, client: TestClient) -> None:
        assert client.post("/chat/escalate", json={}).status_code == 400


class TestSay:
    def test_delivers_trimmed_text_to_the_call_the_nonce_names(
        self, handoff: HandoffRouter, client: TestClient, events: list[Any]
    ) -> None:
        handoff.register("n2", conversation_id="conv-root", call_id="call-9")
        assert (
            client.post(
                "/chat/say", json={"nonce": "n2", "text": "  hello  "}
            ).status_code
            == 200
        )
        assert events == [("say", "call-9", "hello")]

    def test_is_repeatable(self, handoff: HandoffRouter, client: TestClient) -> None:
        """Unlike redemption, typing is repeatable until the nonce is redeemed
        or expires."""
        handoff.register("n2", conversation_id="conv-root", call_id="call-9")
        for _ in range(3):
            assert (
                client.post("/chat/say", json={"nonce": "n2", "text": "x"}).status_code
                == 200
            )

    def test_is_capped_per_call(self, gateway: ChatGateway, events: list[Any]) -> None:
        """Every injection is a billable turn."""
        router = HandoffRouter(
            gateway=gateway,
            send_message=_recording_sender(events),
            max_messages_per_call=2,
        )
        router.register("n", conversation_id="c", call_id="call-1")
        assert asyncio.run(router.say("n", "one"))
        assert asyncio.run(router.say("n", "two"))
        assert not asyncio.run(router.say("n", "three"))

    def test_empty_text_is_refused(
        self, handoff: HandoffRouter, client: TestClient
    ) -> None:
        handoff.register("n2", conversation_id="conv-root", call_id="call-9")
        assert (
            client.post("/chat/say", json={"nonce": "n2", "text": "   "}).status_code
            == 404
        )

    def test_an_unknown_nonce_cannot_inject(self, client: TestClient) -> None:
        """The whole point: a browser cannot name someone else's call."""
        assert (
            client.post(
                "/chat/say", json={"nonce": "guessed", "text": "hello"}
            ).status_code
            == 404
        )

    def test_disabled_when_no_sender_is_configured(self, gateway: ChatGateway) -> None:
        router = HandoffRouter(gateway=gateway)
        router.register("n", conversation_id="c", call_id="call-1")
        assert not asyncio.run(router.say("n", "hello"))


class TestSizeLimits:
    """Every route is reachable by anyone who can load the page, and /say
    text becomes a billed turn, so the body and the text are bounded."""

    def test_say_refuses_text_over_the_message_limit(
        self, handoff: HandoffRouter, client: TestClient, events: list[Any]
    ) -> None:
        handoff.register("n", conversation_id="conv-root", call_id="call-9")
        response = client.post(
            "/chat/say", json={"nonce": "n", "text": "x" * (MAX_MESSAGE_BYTES + 1)}
        )
        assert response.status_code == 413
        assert response.json() == {"error": "message too large"}
        assert events == []

    def test_the_size_answer_does_not_depend_on_the_nonce(
        self, client: TestClient
    ) -> None:
        """Checked before the lookup, so it can't be used to probe a nonce."""
        response = client.post(
            "/chat/say",
            json={"nonce": "never-existed", "text": "x" * (MAX_MESSAGE_BYTES + 1)},
        )
        assert response.status_code == 413
        assert response.json() == {"error": "message too large"}

    def test_say_accepts_text_at_the_limit(
        self, handoff: HandoffRouter, client: TestClient, events: list[Any]
    ) -> None:
        handoff.register("n", conversation_id="conv-root", call_id="call-9")
        text = "x" * MAX_MESSAGE_BYTES
        response = client.post("/chat/say", json={"nonce": "n", "text": text})
        assert response.status_code == 200
        assert events == [("say", "call-9", text)]

    def test_say_called_directly_refuses_oversized_text(
        self, gateway: ChatGateway, events: list[Any]
    ) -> None:
        router = HandoffRouter(gateway=gateway, send_message=_recording_sender(events))
        router.register("n", conversation_id="c", call_id="call-1")
        assert not asyncio.run(router.say("n", "x" * (MAX_MESSAGE_BYTES + 1)))
        assert events == []

    @pytest.mark.parametrize("path", ["/chat/handoff", "/chat/escalate", "/chat/say"])
    def test_an_oversized_body_is_refused(self, client: TestClient, path: str) -> None:
        response = client.post(
            path,
            content=b" " * (MAX_REQUEST_BODY_BYTES + 1),
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 413
        assert response.json() == {"error": "request too large"}

    def test_an_oversized_handoff_leaves_the_nonce_redeemable(
        self, handoff: HandoffRouter, client: TestClient
    ) -> None:
        handoff.register("n", conversation_id="conv-root", call_id="call-9")
        padded = b'{"nonce": "n", "pad": "' + b"x" * MAX_REQUEST_BODY_BYTES + b'"}'
        refused = client.post(
            "/chat/handoff", content=padded, headers={"Content-Type": "application/json"}
        )
        assert refused.status_code == 413
        assert client.post("/chat/handoff", json={"nonce": "n"}).status_code == 200


class TestCaptureFailures:
    def test_a_capture_timeout_does_not_block_the_switch(
        self, gateway: ChatGateway
    ) -> None:
        """Thin context beats refusing a switch the visitor asked for."""

        async def never_finishes(conversation_id: str, medium: str) -> bool:
            await asyncio.sleep(10)
            return True

        router = HandoffRouter(
            gateway=gateway, capture_leg=never_finishes, capture_timeout=0.05
        )
        router.register("n", conversation_id="c", call_id="call-1")
        handle = asyncio.run(router.redeem("n"))
        assert handle is not None
        assert gateway.read_handle(handle) == "c.1"

    def test_a_raising_capture_does_not_block_the_switch(
        self, gateway: ChatGateway
    ) -> None:
        def boom(conversation_id: str, medium: str) -> bool:
            raise RuntimeError("storage down")

        router = HandoffRouter(gateway=gateway, capture_leg=boom)
        router.register("n", conversation_id="c", call_id="call-1")
        handle = asyncio.run(router.redeem("n"))
        assert handle is not None
        assert gateway.read_handle(handle) == "c.1"


class TestConversationIdSanitization:
    """The service strips disallowed characters silently, so an id composed
    with the wrong separator is stored under a different, valid-looking id and
    everything filed under the original becomes unreachable.
    """

    # SDK loggers write through stdlib logging. The handler goes on the SDK's
    # own logger, because configure_logging() (run by other tests) turns off
    # propagation to the root logger, where caplog listens.

    @pytest.fixture
    def records(self) -> Iterator[list[logging.LogRecord]]:
        captured: list[logging.LogRecord] = []

        class Capture(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                captured.append(record)

        sdk_logger = logging.getLogger("signalwire.ai_chat.client")
        handler, level = Capture(), sdk_logger.level
        sdk_logger.addHandler(handler)
        sdk_logger.setLevel(logging.WARNING)
        try:
            yield captured
        finally:
            sdk_logger.removeHandler(handler)
            sdk_logger.setLevel(level)

    @pytest.mark.parametrize("safe", ["conv-abc", "root.2", "a_b-c.d:e"])
    def test_safe_ids_are_quiet(self, safe: str, records: list[logging.LogRecord]) -> None:
        _warn_if_id_will_be_altered(safe)
        assert records == []

    @pytest.mark.parametrize(
        ("unsafe", "stored_as"),
        [("root~2", "root2"), ("conv id", "convid"), ("x!", "x")],
    )
    def test_unsafe_ids_warn_with_what_will_actually_be_stored(
        self, unsafe: str, stored_as: str, records: list[logging.LogRecord]
    ) -> None:
        _warn_if_id_will_be_altered(unsafe)
        (record,) = records
        message = record.getMessage()
        assert "conversation_id_will_be_sanitized" in message
        # The warning must name the id the service will really use -- that is
        # the fact the caller needs, and the one nothing else reports.
        assert stored_as in message

    @pytest.mark.parametrize("junk", [None, "", 123, []])
    def test_junk_is_ignored_rather_than_warned_about(
        self, junk: Any, records: list[logging.LogRecord]
    ) -> None:
        """Paired with the warning case above: this asserts the warning is
        absent, so it can fail, rather than merely asserting no exception."""
        _warn_if_id_will_be_altered(junk)
        assert records == []
