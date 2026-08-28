"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.

Contract: a SWAIG tool registered with ``secure=True`` REQUIRES a ``__token``.

These are real-HTTP tests: a real ``AgentBase`` is mounted through FastAPI's
``TestClient`` and driven over the ASGI stack, with a real ``SessionManager``
minting genuine HMAC tokens. Nothing about the token path is stubbed.

The three cases the contract pins down, for a ``secure=True`` tool:

  (i)   valid token   -> accepted, the handler RUNS
  (ii)  invalid token -> REFUSED, the handler does NOT run
  (iii) ABSENT token  -> REFUSED, the handler does NOT run

Case (iii) is the security fix. Before it, an absent token skipped validation
entirely and a ``secure`` tool executed unauthenticated -- a flag named
``secure`` that permits anonymous calls is a trap.

The refusal SHAPE is deliberately identical for (ii) and (iii): HTTP 200 with a
``FunctionResult`` body carrying a ``response`` string. The engine (mod_openai)
has no special handling for a SWAIG refusal -- it has no notion of a 401/403
from a tool -- so the tool simply reports that it cannot execute and the model
relays that to the caller. Do not "improve" this into a status code.

A ``secure=False`` tool must still run with no token at all; that is the whole
point of the flag being a flag.
"""

import base64
from typing import Any

from fastapi.testclient import TestClient

from signalwire.core.agent_base import AgentBase
from signalwire.core.function_result import FunctionResult


CALL_ID = "call-abc-123"


class _ProbeAgent(AgentBase):
    """Agent exposing one secure and one insecure tool, each recording calls."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.secure_calls: list[dict[str, Any]] = []
        self.open_calls: list[dict[str, Any]] = []

        self.define_tool(
            name="vault_balance",
            description="Read the caller's vault balance.",
            parameters={"type": "object", "properties": {}},
            handler=self._secure_handler,
            secure=True,
        )
        self.define_tool(
            name="store_hours",
            description="Read the public store hours.",
            parameters={"type": "object", "properties": {}},
            handler=self._open_handler,
            secure=False,
        )

    def _secure_handler(self, args: dict[str, Any], raw_data: Any) -> FunctionResult:
        self.secure_calls.append(args)
        return FunctionResult("SECRET-BALANCE-9999")

    def _open_handler(self, args: dict[str, Any], raw_data: Any) -> FunctionResult:
        self.open_calls.append(args)
        return FunctionResult("open 9 to 5")


def _basic_auth_headers(agent: AgentBase) -> dict[str, str]:
    creds = agent.get_basic_auth_credentials()
    token = base64.b64encode(f"{creds[0]}:{creds[1]}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "content-type": "application/json",
    }


def _post_swaig(
    client: TestClient,
    agent: AgentBase,
    function_name: str,
    query: str = "",
) -> Any:
    """POST a SWAIG function call, optionally with a token in the query string."""
    return client.post(
        f"/swaig{query}",
        json={
            "function": function_name,
            "argument": {"parsed": [{}], "raw": "{}"},
            "call_id": CALL_ID,
        },
        headers=_basic_auth_headers(agent),
    )


def _agent_and_client() -> tuple[_ProbeAgent, TestClient]:
    agent = _ProbeAgent(name="secure-probe")
    return agent, TestClient(agent.get_app())


def _valid_token(agent: AgentBase, function_name: str) -> str:
    """Mint a genuine HMAC token from the agent's own live SessionManager."""
    return str(agent._session_manager.create_tool_token(function_name, CALL_ID))


def _is_refusal(payload: dict[str, Any]) -> bool:
    text = str(payload.get("response", "")).lower()
    return "security token" in text and "cannot execute" in text


# ---------------------------------------------------------------------------
# (i) valid token -> accepted
# ---------------------------------------------------------------------------


class TestSecureToolValidToken:
    def test_valid_token_runs_the_handler(self) -> None:
        agent, client = _agent_and_client()
        token = _valid_token(agent, "vault_balance")

        resp = _post_swaig(client, agent, "vault_balance", f"?__token={token}")

        assert resp.status_code == 200, resp.text
        assert resp.json()["response"] == "SECRET-BALANCE-9999", resp.text
        assert agent.secure_calls, "secure handler was not invoked with a valid token"


# ---------------------------------------------------------------------------
# (ii) invalid token -> refused (pre-existing behaviour; guard against regression)
# ---------------------------------------------------------------------------


class TestSecureToolInvalidToken:
    def test_invalid_token_is_refused(self) -> None:
        agent, client = _agent_and_client()

        resp = _post_swaig(client, agent, "vault_balance", "?__token=not-a-real-token")

        assert resp.status_code == 200, resp.text
        assert _is_refusal(resp.json()), resp.text
        assert not agent.secure_calls, (
            "secure handler RAN despite an invalid token: " + resp.text
        )

    def test_invalid_legacy_token_param_is_refused(self) -> None:
        """The legacy ``token`` query param is honoured as a fallback."""
        agent, client = _agent_and_client()

        resp = _post_swaig(client, agent, "vault_balance", "?token=not-a-real-token")

        assert resp.status_code == 200, resp.text
        assert _is_refusal(resp.json()), resp.text
        assert not agent.secure_calls


# ---------------------------------------------------------------------------
# (iii) ABSENT token -> refused  <- the security fix
# ---------------------------------------------------------------------------


class TestSecureToolAbsentToken:
    def test_absent_token_is_refused(self) -> None:
        """A ``secure=True`` tool must NOT execute when no token is supplied.

        Previously the entire validation block sat inside ``if token:`` -- so a
        request with no token skipped validation and the secure tool ran
        unauthenticated. Omitting the credential must never be weaker than
        presenting a wrong one.
        """
        agent, client = _agent_and_client()

        resp = _post_swaig(client, agent, "vault_balance")

        assert resp.status_code == 200, resp.text
        assert _is_refusal(resp.json()), resp.text
        assert not agent.secure_calls, (
            "SECURITY: secure handler RAN with NO token at all: " + resp.text
        )

    def test_absent_token_does_not_leak_the_secure_payload(self) -> None:
        agent, client = _agent_and_client()

        resp = _post_swaig(client, agent, "vault_balance")

        assert "SECRET-BALANCE-9999" not in resp.text

    def test_empty_token_is_refused(self) -> None:
        """An empty ``__token=`` is absent, not present-and-valid."""
        agent, client = _agent_and_client()

        resp = _post_swaig(client, agent, "vault_balance", "?__token=")

        assert resp.status_code == 200, resp.text
        assert _is_refusal(resp.json()), resp.text
        assert not agent.secure_calls


# ---------------------------------------------------------------------------
# The flag must remain a flag: secure=False + no token must still run
# ---------------------------------------------------------------------------


class TestInsecureToolStillRuns:
    def test_non_secure_tool_runs_without_a_token(self) -> None:
        agent, client = _agent_and_client()

        resp = _post_swaig(client, agent, "store_hours")

        assert resp.status_code == 200, resp.text
        assert resp.json()["response"] == "open 9 to 5", resp.text
        assert agent.open_calls, "insecure handler must run with no token"

    def test_non_secure_tool_runs_with_an_invalid_token(self) -> None:
        agent, client = _agent_and_client()

        resp = _post_swaig(client, agent, "store_hours", "?__token=garbage")

        assert resp.status_code == 200, resp.text
        assert resp.json()["response"] == "open 9 to 5", resp.text
        assert agent.open_calls


# ---------------------------------------------------------------------------
# Refusal shape parity: absent and invalid must be indistinguishable
# ---------------------------------------------------------------------------


class TestRefusalShapeParity:
    def test_absent_and_invalid_refusals_are_the_same_shape(self) -> None:
        """The engine has no refusal protocol -- both must be a 200 + FunctionResult.

        If these ever diverge, a port could reasonably conclude that one of
        them is allowed to be an HTTP error, which the engine cannot consume.
        """
        agent_a, client_a = _agent_and_client()
        absent = _post_swaig(client_a, agent_a, "vault_balance")

        agent_b, client_b = _agent_and_client()
        invalid = _post_swaig(client_b, agent_b, "vault_balance", "?__token=bogus")

        assert absent.status_code == invalid.status_code == 200
        assert absent.json() == invalid.json(), (
            f"refusal shapes diverged: absent={absent.text} invalid={invalid.text}"
        )
