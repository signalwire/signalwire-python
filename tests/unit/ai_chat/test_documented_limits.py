"""
The limits the ai_chat docstrings describe.

HandoffRouter said typing works "for the life of the call"; it works until the
nonce expires, nonce_ttl seconds after registration, or is redeemed.
GatewayRejection said its reason never discloses why a handle failed to
verify; the gateway tells a malformed, an invalid and an expired handle apart,
and the browser receives that reason.
"""

import asyncio
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from signalwire.ai_chat import AIChatClient, ChatGateway, HandoffRouter
from signalwire.ai_chat.gateway import GatewayRejection

SECRET = "s" * 32
KEY = "pk_test"


def _gateway(**kw: Any) -> ChatGateway:
    client = AIChatClient(
        project="p",
        token="t",
        url="https://service.example.invalid/aichat",
    )
    return ChatGateway(
        config_url="https://agent.example.com/swml",
        key=KEY,
        secret=SECRET,
        client=client,
        **kw,
    )


def _router(sent: list[str], **kw: Any) -> HandoffRouter:
    def send_message(call_id: str, text: str) -> bool:
        sent.append(text)
        return True

    return HandoffRouter(gateway=_gateway(), send_message=send_message, **kw)


class TestTypingLifetime:
    def test_typing_stops_when_the_nonce_expires(self) -> None:
        sent: list[str] = []
        router = _router(sent, nonce_ttl=600)
        router.register("n", conversation_id="c", call_id="call-1")
        assert asyncio.run(router.say("n", "before"))

        # Move the registration back past nonce_ttl, as if the call had run
        # longer than that
        router._nonces["n"].issued_at -= 601

        assert not asyncio.run(router.say("n", "after"))
        assert sent == ["before"]

    def test_typing_stops_once_the_nonce_is_redeemed(self) -> None:
        sent: list[str] = []
        router = _router(sent)
        router.register("n", conversation_id="c", call_id="call-1")
        assert asyncio.run(router.say("n", "before"))
        assert asyncio.run(router.redeem("n")) is not None
        assert not asyncio.run(router.say("n", "after"))
        assert sent == ["before"]


class TestHandleRejectionReasons:
    def test_malformed_handle(self) -> None:
        with pytest.raises(GatewayRejection) as err:
            _gateway().read_handle("not-a-handle")
        assert (err.value.status, err.value.reason) == (400, "malformed handle")

    def test_invalid_handle(self) -> None:
        gateway = _gateway()
        tampered = gateway.mint_handle().split(".")[0] + ".AAAA"
        with pytest.raises(GatewayRejection) as err:
            gateway.read_handle(tampered)
        assert (err.value.status, err.value.reason) == (403, "invalid handle")

    def test_expired_handle(self) -> None:
        gateway = _gateway(handle_ttl=-1)
        with pytest.raises(GatewayRejection) as err:
            gateway.read_handle(gateway.mint_handle())
        assert (err.value.status, err.value.reason) == (403, "expired handle")

    def test_the_browser_receives_the_reason(self) -> None:
        gateway = _gateway(handle_ttl=-1)
        app = FastAPI()
        app.include_router(gateway.router(), prefix="/chat")
        response = TestClient(app).post(
            "/chat/",
            json={"method": "chat", "message": "hi", "handle": gateway.mint_handle()},
            headers={"Authorization": f"Bearer {KEY}"},
        )
        assert response.status_code == 403
        assert response.json() == {"error": "expired handle"}
