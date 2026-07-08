"""AUTO-GENERATED REST wire tests for the `datasphere` namespace — DO NOT EDIT.
Regenerate: python3 porting-sdk/scripts/generate_python_rest_types.py

Each route the SDK implements (captured from the real client by python_route_registry,
joined to the spec operationId) gets a SUCCESS test (call it, assert method/path/route on
the mock journal) and an ERROR test (arm a 5xx, assert SignalWireRestError). The assertion
oracle is the spec operationId — independent of the resource generator — so these catch
SDK-vs-contract drift, not just a generator self-snapshot. Full-mock harness fixtures.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from signalwire.rest._base import SignalWireRestError

if TYPE_CHECKING:
    from signalwire.rest.client import RestClient

    from .conftest import _MockHarness


class TestDatasphereWire:
    def test_documents_create(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.datasphere.documents.create({})
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "datasphere.create_document"

    def test_documents_create_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("datasphere.create_document", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.create({})
        assert exc.value.status_code == 500

    def test_documents_delete(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.datasphere.documents.delete("test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "datasphere.delete_document"

    def test_documents_delete_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("datasphere.delete_document", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.delete("test-id")
        assert exc.value.status_code == 500

    def test_documents_delete_chunk(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.datasphere.documents.delete_chunk("test-id", "test-id")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.matched_route == "datasphere.delete_document_chunk"

    def test_documents_delete_chunk_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("datasphere.delete_document_chunk", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.delete_chunk("test-id", "test-id")
        assert exc.value.status_code == 500

    def test_documents_get(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.datasphere.documents.get("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "datasphere.get_document"

    def test_documents_get_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("datasphere.get_document", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.get("test-id")
        assert exc.value.status_code == 500

    def test_documents_get_chunk(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.datasphere.documents.get_chunk("test-id", "test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "datasphere.get_document_chunk"

    def test_documents_get_chunk_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("datasphere.get_document_chunk", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.get_chunk("test-id", "test-id")
        assert exc.value.status_code == 500

    def test_documents_list(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.datasphere.documents.list()
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "datasphere.list_documents"

    def test_documents_list_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("datasphere.list_documents", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.list()
        assert exc.value.status_code == 500

    def test_documents_list_chunks(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.datasphere.documents.list_chunks("test-id")
        last = mock.last_request()
        assert last.method == "GET"
        assert last.matched_route == "datasphere.list_document_chunks"

    def test_documents_list_chunks_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("datasphere.list_document_chunks", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.list_chunks("test-id")
        assert exc.value.status_code == 500

    def test_documents_search(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.datasphere.documents.search(query_string="x")
        last = mock.last_request()
        assert last.method == "POST"
        assert last.matched_route == "datasphere.search_documents"

    def test_documents_search_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("datasphere.search_documents", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.search(query_string="x")
        assert exc.value.status_code == 500

    def test_documents_update(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        signalwire_client.datasphere.documents.update("test-id")
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.matched_route == "datasphere.update_document"

    def test_documents_update_error(
        self, signalwire_client: RestClient, mock: _MockHarness
    ) -> None:
        mock.push_scenario("datasphere.update_document", 500, {"error": "x"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.update("test-id")
        assert exc.value.status_code == 500
