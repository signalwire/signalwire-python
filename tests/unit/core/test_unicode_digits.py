"""
Digits such as "²" pass str.isdigit(), and int() refuses them.

Each of these checked a string with isdigit() and then passed it to int(), so
a header, an environment variable or an argument holding such a digit raised
int()'s ValueError instead of getting the intended handling.
"""

import io
from typing import Any, ClassVar
from unittest.mock import patch

import pytest

from signalwire.ai_chat.gateway import GatewayRejection, _read_json_body
from signalwire.ai_chat.handoff import HandoffRouter
from signalwire.core.config_loader import ConfigLoader
from signalwire.core.function_result import _swml_int
from signalwire.core.mixins.serverless_mixin import _cgi_request

SUPERSCRIPT_TWO = "²"


class _Request:
    """A request with the given headers and body, as the gateway reads it."""

    def __init__(self, headers: dict[str, str], body: bytes) -> None:
        self.headers = headers
        self._body = body

    async def stream(self) -> Any:
        yield self._body


def test_swml_int_gives_its_own_message() -> None:
    with pytest.raises(
        ValueError, match="max_participants must be an integer of at least 2"
    ):
        _swml_int("max_participants", SUPERSCRIPT_TWO, minimum=2)


async def test_the_gateway_reads_the_body_whatever_content_length_says() -> None:
    request = _Request({"content-length": SUPERSCRIPT_TWO}, b'{"a": 1}')
    assert await _read_json_body(request, limit=1024) == {"a": 1}  # type: ignore[arg-type]  # a stand-in request


async def test_the_gateway_still_refuses_a_large_declared_body() -> None:
    request = _Request({"content-length": "2048"}, b"{}")
    with pytest.raises(GatewayRejection):
        await _read_json_body(request, limit=1024)  # type: ignore[arg-type]  # a stand-in request


def test_a_conversation_id_ending_in_such_a_digit_gets_a_suffix() -> None:
    assert (
        HandoffRouter._default_next_id(f"conv.{SUPERSCRIPT_TWO}")
        == f"conv.{SUPERSCRIPT_TWO}.1"
    )
    assert HandoffRouter._default_next_id("conv.2") == "conv.3"


def test_cgi_ignores_such_a_content_length(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTENT_LENGTH", SUPERSCRIPT_TWO)
    monkeypatch.setenv("REQUEST_METHOD", "POST")
    with patch("sys.stdin", io.StringIO('{"a": 1}')):
        request = _cgi_request()
    # Not a length, so nothing is read, as with no CONTENT_LENGTH at all
    assert request.body == ""
    assert request.method == "POST"


def test_config_substitution_keeps_such_a_value_as_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SW_TEST_DIGIT", SUPERSCRIPT_TWO)
    assert ConfigLoader([]).substitute_vars("${SW_TEST_DIGIT}") == SUPERSCRIPT_TWO
    monkeypatch.setenv("SW_TEST_DIGIT", "42")
    assert ConfigLoader([]).substitute_vars("${SW_TEST_DIGIT}") == 42


async def test_swml_service_reads_the_body_whatever_content_length_says() -> None:
    from signalwire.core.swml_service import SWMLService

    class _BodyRequest:
        headers: ClassVar[dict[str, str]] = {"content-length": SUPERSCRIPT_TWO}

        async def body(self) -> bytes:
            return b"{}"

    service = SWMLService(name="svc", route="/svc", basic_auth=("u", "p"))
    assert await service._read_body_with_limit(_BodyRequest()) == b"{}"  # type: ignore[arg-type]  # a stand-in request
