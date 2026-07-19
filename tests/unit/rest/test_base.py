"""Tests for _base.py — HttpClient, BaseResource, CrudResource, error handling."""

from typing import Any

import pytest
from signalwire.rest._base import (
    SignalWireRestError,
    SignalWireRestTransportError,
    CrudResource,
    CrudWithAddresses,
)
from .conftest import MockResponse
from signalwire.rest._base import HttpClient
from unittest.mock import MagicMock


class TestBaseUrlScheme:
    """§2.2: a loopback host (local mock/dev server) gets http://; a real space gets
    https://. Lets a shipped example run verbatim against the local mock without a
    separate URL knob. Pure _base_url construction — no transport mocked."""

    @pytest.mark.parametrize("host", [
        "127.0.0.1:8790", "127.0.0.1", "localhost:3000", "localhost",
    ])
    def test_loopback_host_uses_http(self, host: str) -> None:
        c = HttpClient("proj", "tok", host)
        assert c._base_url == f"http://{host}", c._base_url

    @pytest.mark.parametrize("host", [
        "example.signalwire.com", "myspace.signalwire.com",
    ])
    def test_real_space_uses_https(self, host: str) -> None:
        c = HttpClient("proj", "tok", host)
        assert c._base_url == f"https://{host}", c._base_url


class TestSignalWireRestError:
    def test_error_attributes(self) -> None:
        err = SignalWireRestError(404, {"error": "not found"}, "/api/test", "GET")
        assert err.status_code == 404
        assert err.body == {"error": "not found"}
        assert err.url == "/api/test"
        assert err.method == "GET"
        assert "404" in str(err)

    def test_default_method(self) -> None:
        err = SignalWireRestError(500, "server error", "/api/x")
        assert err.method == "GET"


class TestHttpClient:
    def test_get(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": [1, 2]})
        result = http.get("/api/test", params={"page": 1})
        mock_session.request.assert_called_once_with(
            "GET", "https://test.signalwire.com/api/test",
            json=None, params={"page": 1}, timeout=30.0,
        )
        assert result == {"data": [1, 2]}

    def test_post(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(201, {"id": "abc"})
        result = http.post("/api/test", body={"name": "x"})
        mock_session.request.assert_called_once_with(
            "POST", "https://test.signalwire.com/api/test",
            json={"name": "x"}, params=None, timeout=30.0,
        )
        assert result == {"id": "abc"}

    def test_put(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"ok": True})
        result = http.put("/api/test/1", body={"name": "y"})
        mock_session.request.assert_called_once_with(
            "PUT", "https://test.signalwire.com/api/test/1",
            json={"name": "y"}, params=None, timeout=30.0,
        )

    def test_patch(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"ok": True})
        http.patch("/api/test/1", body={"name": "z"})
        mock_session.request.assert_called_once_with(
            "PATCH", "https://test.signalwire.com/api/test/1",
            json={"name": "z"}, params=None, timeout=30.0,
        )

    def test_delete(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(204, None, content=b"")
        result = http.delete("/api/test/1")
        mock_session.request.assert_called_once_with(
            "DELETE", "https://test.signalwire.com/api/test/1",
            json=None, params=None, timeout=30.0,
        )
        assert result == {}

    def test_error_raises(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(
            404, {"error": "not found"}, content=b'{"error":"not found"}',
        )
        with pytest.raises(SignalWireRestError) as exc_info:
            http.get("/api/missing")
        assert exc_info.value.status_code == 404

    def test_transport_error_wrapped(
        self, http: HttpClient, mock_session: MagicMock
    ) -> None:
        # A transport failure (connection refused / reset / DNS) must surface as the
        # typed SignalWireRestTransportError (a SignalWireRestError-family member with
        # status_code=None), NOT a bare requests.ConnectionError.
        import requests

        mock_session.request.side_effect = requests.ConnectionError(
            "connection refused"
        )
        with pytest.raises(SignalWireRestTransportError) as exc_info:
            http.get("/api/anything")
        assert isinstance(exc_info.value, SignalWireRestError)  # one family
        assert exc_info.value.status_code is None
        assert exc_info.value.method == "GET"
        assert exc_info.value.url == "/api/anything"


class TestCrudResource:
    def test_list(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": []})
        res: CrudResource[Any, Any, Any, Any] = CrudResource(http, "/api/items")
        result = res.list(page=1)
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/items",
            json=None, params={"page": 1}, timeout=30.0,
        )

    def test_create(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(201, {"id": "new"})
        res: CrudResource[Any, Any, Any, Any] = CrudResource(http, "/api/items")
        result = res.create(name="test")
        mock_session.request.assert_called_with(
            "POST", "https://test.signalwire.com/api/items",
            json={"name": "test"}, params=None, timeout=30.0,
        )

    def test_get(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"id": "abc"})
        res: CrudResource[Any, Any, Any, Any] = CrudResource(http, "/api/items")
        result = res.get("abc")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/items/abc",
            json=None, params=None, timeout=30.0,
        )

    def test_update_patch(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"ok": True})
        res: CrudResource[Any, Any, Any, Any] = CrudResource(http, "/api/items")
        res.update("abc", name="updated")
        mock_session.request.assert_called_with(
            "PATCH", "https://test.signalwire.com/api/items/abc",
            json={"name": "updated"}, params=None, timeout=30.0,
        )

    def test_update_put(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"ok": True})

        class PutResource(CrudResource[Any, Any, Any, Any]):
            _update_method = "PUT"

        res = PutResource(http, "/api/items")
        res.update("abc", name="updated")
        mock_session.request.assert_called_with(
            "PUT", "https://test.signalwire.com/api/items/abc",
            json={"name": "updated"}, params=None, timeout=30.0,
        )

    def test_delete(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(204, None, content=b"")
        res: CrudResource[Any, Any, Any, Any] = CrudResource(http, "/api/items")
        res.delete("abc")
        mock_session.request.assert_called_with(
            "DELETE", "https://test.signalwire.com/api/items/abc",
            json=None, params=None, timeout=30.0,
        )


class TestCrudWithAddresses:
    def test_list_addresses(self, http: HttpClient, mock_session: MagicMock) -> None:
        mock_session.request.return_value = MockResponse(200, {"data": []})
        res: CrudWithAddresses[Any, Any, Any, Any] = CrudWithAddresses(http, "/api/fabric/resources/ai_agents")
        res.list_addresses("abc")
        mock_session.request.assert_called_with(
            "GET", "https://test.signalwire.com/api/fabric/resources/ai_agents/abc/addresses",
            json=None, params=None, timeout=30.0,
        )
