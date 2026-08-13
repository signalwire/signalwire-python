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
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from signalwire.ai_chat import AIChatClient, ChatGateway, HandoffRouter
from signalwire.ai_chat.client import _warn_if_id_will_be_altered

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
        """Unlike redemption -- typing lasts the life of the call."""
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

    # structlog renders to stdout rather than through the stdlib handlers
    # `caplog` installs, so the warning is asserted via captured output.

    @pytest.mark.parametrize("safe", ["conv-abc", "root.2", "a_b-c.d:e"])
    def test_safe_ids_are_quiet(self, safe: str, capsys: Any) -> None:
        _warn_if_id_will_be_altered(safe)
        assert "conversation_id_will_be_sanitized" not in capsys.readouterr().out

    @pytest.mark.parametrize(
        ("unsafe", "stored_as"),
        [("root~2", "root2"), ("conv id", "convid"), ("x!", "x")],
    )
    def test_unsafe_ids_warn_with_what_will_actually_be_stored(
        self, unsafe: str, stored_as: str, capsys: Any
    ) -> None:
        _warn_if_id_will_be_altered(unsafe)
        out = capsys.readouterr().out
        assert "conversation_id_will_be_sanitized" in out
        # The warning must name the id the service will really use -- that is
        # the fact the caller needs, and the one nothing else reports.
        assert stored_as in out

    @pytest.mark.parametrize("junk", [None, "", 123, []])
    def test_junk_is_ignored_rather_than_warned_about(
        self, junk: Any, capsys: Any
    ) -> None:
        """Paired with the warning case above: this asserts the warning is
        absent, so it can fail, rather than merely asserting no exception."""
        _warn_if_id_will_be_altered(junk)
        assert "conversation_id_will_be_sanitized" not in capsys.readouterr().out
