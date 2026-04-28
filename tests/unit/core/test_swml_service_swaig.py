"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests proving SWMLService can host SWAIG functions and serve a non-agent
SWML doc (e.g. ai_sidecar) without subclassing AgentBase. This is the
contract that lets sidecar / non-agent verbs reuse the SWAIG dispatch surface
that previously lived only on AgentBase.
"""

import asyncio
import base64
import json
from unittest.mock import MagicMock

from signalwire.core.swml_service import SWMLService
from signalwire.core.function_result import FunctionResult


def _make_request(method="POST", headers=None, body=None, query_params=None, url_path="/swaig"):
    """Build a minimal request object that the SWAIG handler can consume."""
    request = MagicMock()
    request.method = method
    request.url.path = url_path
    request.headers = headers or {"content-type": "application/json"}
    request.query_params = query_params or {}
    body_bytes = json.dumps(body).encode() if body is not None else b""

    async def _body():
        return body_bytes

    async def _json():
        return body if body is not None else {}

    request.body = _body
    request.json = _json
    request.state = MagicMock()
    return request


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _service(**kwargs):
    """Build a SWMLService instance with schema validation disabled for fast tests."""
    return SWMLService(name="t", schema_validation=False, **kwargs)


# ---------------------------------------------------------------------------
# SWMLService-only SWAIG hosting
# ---------------------------------------------------------------------------

class TestSWMLServiceHasSWAIGCapability:
    """The lift gives plain SWMLService instances SWAIG-hosting capability."""

    def test_define_tool_resolves_on_swml_service(self):
        svc = _service()
        assert hasattr(svc, "define_tool")
        assert hasattr(svc, "register_swaig_function")
        assert hasattr(svc, "on_function_call")
        assert hasattr(svc, "_handle_swaig_request")

    def test_tool_registry_is_initialized(self):
        svc = _service()
        assert svc._tool_registry is not None
        assert svc._tool_registry._swaig_functions == {}

    def test_define_tool_registers_function(self):
        svc = _service()
        svc.define_tool(
            name="lookup",
            description="Look something up.",
            parameters={"type": "object", "properties": {}},
            handler=lambda args, raw: FunctionResult("ok"),
        )
        assert "lookup" in svc._tool_registry._swaig_functions

    def test_as_router_mounts_swaig_endpoint(self):
        svc = _service()
        router = svc.as_router()
        paths = [r.path for r in router.routes if hasattr(r, "path")]
        assert "/swaig" in paths
        assert "/swaig/" in paths


class TestSWMLServiceSWAIGDispatch:
    """End-to-end dispatch tests: POST /swaig hits the registered handler."""

    def test_post_dispatches_to_registered_handler(self):
        svc = _service()
        called_with = {}

        def lookup(args, raw_data):
            called_with["args"] = args
            called_with["raw"] = raw_data
            return FunctionResult("found it")

        svc.define_tool(
            name="lookup",
            description="lookup",
            parameters={"type": "object", "properties": {"q": {"type": "string"}}},
            handler=lookup,
        )

        # Auth: SWMLService uses _check_basic_auth from its own definition. With
        # no _basic_auth credentials configured to require, the default flow
        # lets this through. We patch it to avoid environmental ambiguity.
        svc._check_basic_auth = MagicMock(return_value=True)

        request = _make_request(
            method="POST",
            body={
                "function": "lookup",
                "argument": {"raw": json.dumps({"q": "ACME"})},
                "call_id": "c-123",
            },
        )
        result = _run(svc._handle_swaig_request(request, MagicMock()))
        assert called_with["args"] == {"q": "ACME"}
        assert isinstance(result, dict)
        assert result.get("response") == "found it"

    def test_get_returns_swml_document_via_render_document(self):
        """Default _swaig_render_get_response uses render_document() — i.e. the
        currently-built SWML doc, not a dynamically rebuilt one. This is the
        non-agent path."""
        svc = _service()
        svc.add_section("main")
        svc.add_verb_to_section("main", "answer", {})
        svc._check_basic_auth = MagicMock(return_value=True)

        request = _make_request(method="GET")
        response = _run(svc._handle_swaig_request(request, MagicMock()))
        assert response.status_code == 200
        body = json.loads(response.body)
        assert "sections" in body
        assert "main" in body["sections"]

    def test_post_unknown_function_returns_error_response(self):
        svc = _service()
        svc._check_basic_auth = MagicMock(return_value=True)
        request = _make_request(method="POST", body={"function": "no_such_fn"})
        result = _run(svc._handle_swaig_request(request, MagicMock()))
        assert isinstance(result, dict)
        # on_function_call returns a `response` field for unknown funcs
        assert "no_such_fn" in result.get("response", "")

    def test_post_invalid_function_name_returns_400(self):
        svc = _service()
        svc._check_basic_auth = MagicMock(return_value=True)
        request = _make_request(method="POST", body={"function": "../etc/passwd"})
        response = _run(svc._handle_swaig_request(request, MagicMock()))
        assert response.status_code == 400

    def test_post_missing_function_returns_400(self):
        svc = _service()
        svc._check_basic_auth = MagicMock(return_value=True)
        request = _make_request(method="POST", body={})
        response = _run(svc._handle_swaig_request(request, MagicMock()))
        assert response.status_code == 400

    def test_unauthorized_returns_401(self):
        svc = _service()
        svc._check_basic_auth = MagicMock(return_value=False)
        request = _make_request(method="POST", body={"function": "x"})
        response = _run(svc._handle_swaig_request(request, MagicMock()))
        assert response.status_code == 401

    def test_swmlservice_has_no_token_validation_by_default(self):
        """A plain SWMLService does NOT do session-token validation. That's an
        AgentBase-specific extension. A token in query params is ignored."""
        svc = _service()
        svc._check_basic_auth = MagicMock(return_value=True)

        called = {}

        def lookup(args, raw_data):
            called["yes"] = True
            return FunctionResult("ok")

        svc.define_tool(
            name="lookup",
            description="d",
            parameters={"type": "object", "properties": {}},
            handler=lookup,
        )

        request = _make_request(
            method="POST",
            body={"function": "lookup", "argument": {"raw": "{}"}, "call_id": "c1"},
            query_params={"token": "obviously-bogus"},
        )
        result = _run(svc._handle_swaig_request(request, MagicMock()))
        assert called.get("yes") is True
        assert result.get("response") == "ok"


# ---------------------------------------------------------------------------
# Sidecar usage pattern
# ---------------------------------------------------------------------------

class TestSidecarPatternViaSWMLService:
    """Sidecar-flavored SWML services need three things from SWMLService:
    1. arbitrary verb emission (already supported via add_verb / add_section),
    2. SWAIG callback hosting (lifted-down here),
    3. an event-sink endpoint (already supported via register_routing_callback).

    These tests verify the full pattern works without any SidecarBase class.
    """

    def test_can_emit_ai_sidecar_verb(self):
        """SWMLService.add_verb accepts arbitrary verb dicts; ai_sidecar is
        just data, schema permitting."""
        svc = _service()
        svc.add_section("main")
        ok = svc.add_verb_to_section("main", "answer", {})
        assert ok
        # ai_sidecar isn't in the live SWML schema yet — bypass via raw doc.
        # Once the schema lands, callers will use add_verb_to_section directly.
        svc._current_document["sections"]["main"].append({"ai_sidecar": {
            "prompt": "real-time copilot",
            "lang": "en-US",
            "direction": ["remote-caller", "local-caller"],
        }})
        rendered = json.loads(svc.render_document())
        verbs = [list(v.keys())[0] for v in rendered["sections"]["main"]]
        assert "answer" in verbs
        assert "ai_sidecar" in verbs

    def test_full_sidecar_pattern_emit_swml_register_tool_register_event_sink(self):
        svc = _service()

        # 1. Build the SWML doc.
        svc.add_section("main")
        svc.add_verb_to_section("main", "answer", {})

        # 2. Register a SWAIG tool the sidecar's LLM can call.
        def lookup_competitor(args, raw_data):
            return FunctionResult(f"{args['competitor']} is $99/seat; we're $79.")

        svc.define_tool(
            name="lookup_competitor",
            description="Look up competitor pricing.",
            parameters={
                "type": "object",
                "properties": {"competitor": {"type": "string"}},
                "required": ["competitor"],
            },
            handler=lookup_competitor,
        )

        # 3. Register an event-sink endpoint via routing callback.
        events_seen = []

        def on_event(request, body):
            events_seen.append(body.get("type"))
            return None

        svc.register_routing_callback(on_event, path="/events")

        # Verify the router has both /swaig and /events paths.
        router = svc.as_router()
        paths = [r.path for r in router.routes if hasattr(r, "path")]
        assert "/swaig" in paths
        assert "/events" in paths or any(p.endswith("/events") for p in paths)

        # Verify the SWAIG dispatch works end-to-end.
        svc._check_basic_auth = MagicMock(return_value=True)
        request = _make_request(
            method="POST",
            body={
                "function": "lookup_competitor",
                "argument": {"raw": json.dumps({"competitor": "ACME"})},
            },
        )
        result = _run(svc._handle_swaig_request(request, MagicMock()))
        assert "ACME" in result.get("response", "")
        assert "$79" in result.get("response", "")
