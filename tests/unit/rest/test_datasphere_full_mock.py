"""Full success + error coverage for ``client.datasphere.documents`` (#56).

Mirrors the micro-template ``test_fabric_ai_agents_full_mock.py`` EXACTLY: each
canonical datasphere route gets a SUCCESS test (call the real SDK method against
the live mock, assert the parsed body shape AND the journal entry's method +
exact canonical path + matched_route) and an ERROR test (arm a 4xx/5xx via
``mock.push_scenario(endpoint_id, status, body)``, assert the SDK raises
``SignalWireRestError`` with the right ``status_code``, and that the journal
recorded the route with the error status).

``datasphere.documents`` is a CRUD resource at /api/datasphere/documents with
extra ``search`` and chunk sub-resources:
  list / create / get / update (PATCH) / delete, search (POST /search),
  list_chunks / get_chunk / delete_chunk under {id}/chunks.
"""

from __future__ import annotations

import pytest

from signalwire.rest._base import SignalWireRestError


class TestDatasphereSuccess:
    """Happy-path: each route hit with a 2xx on the exact canonical path."""

    def test_list(self, signalwire_client, mock):
        body = signalwire_client.datasphere.documents.list()
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/datasphere/documents"
        assert last.matched_route == "datasphere.list_documents", (
            f"expected datasphere.list_documents, got {last.matched_route!r}"
        )

    def test_create(self, signalwire_client, mock):
        body = signalwire_client.datasphere.documents.create(
            url="https://example.com/doc.pdf",
        )
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/datasphere/documents"
        assert last.matched_route == "datasphere.create_document", (
            f"expected datasphere.create_document, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("url") == "https://example.com/doc.pdf"

    def test_search(self, signalwire_client, mock):
        body = signalwire_client.datasphere.documents.search(query_string="hello")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "POST"
        assert last.path == "/api/datasphere/documents/search"
        assert last.matched_route == "datasphere.search_documents", (
            f"expected datasphere.search_documents, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("query_string") == "hello"

    def test_list_chunks(self, signalwire_client, mock):
        body = signalwire_client.datasphere.documents.list_chunks("doc-1001")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/datasphere/documents/doc-1001/chunks"
        assert last.matched_route == "datasphere.list_document_chunks", (
            f"expected datasphere.list_document_chunks, got {last.matched_route!r}"
        )

    def test_get_chunk(self, signalwire_client, mock):
        body = signalwire_client.datasphere.documents.get_chunk("doc-1001", "ch-1")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/datasphere/documents/doc-1001/chunks/ch-1"
        assert last.matched_route == "datasphere.get_document_chunk", (
            f"expected datasphere.get_document_chunk, got {last.matched_route!r}"
        )

    def test_delete_chunk(self, signalwire_client, mock):
        signalwire_client.datasphere.documents.delete_chunk("doc-1001", "ch-1")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/datasphere/documents/doc-1001/chunks/ch-1"
        assert last.matched_route == "datasphere.delete_document_chunk", (
            f"expected datasphere.delete_document_chunk, got {last.matched_route!r}"
        )

    def test_get(self, signalwire_client, mock):
        body = signalwire_client.datasphere.documents.get("doc-1001")
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "GET"
        assert last.path == "/api/datasphere/documents/doc-1001"
        assert last.matched_route == "datasphere.get_document", (
            f"expected datasphere.get_document, got {last.matched_route!r}"
        )

    def test_update(self, signalwire_client, mock):
        body = signalwire_client.datasphere.documents.update("doc-1001", tags=["x"])
        assert isinstance(body, dict)
        last = mock.last_request()
        assert last.method == "PATCH"
        assert last.path == "/api/datasphere/documents/doc-1001"
        assert last.matched_route == "datasphere.update_document", (
            f"expected datasphere.update_document, got {last.matched_route!r}"
        )
        assert last.body and last.body.get("tags") == ["x"]

    def test_delete(self, signalwire_client, mock):
        signalwire_client.datasphere.documents.delete("doc-1001")
        last = mock.last_request()
        assert last.method == "DELETE"
        assert last.path == "/api/datasphere/documents/doc-1001"
        assert last.matched_route == "datasphere.delete_document", (
            f"expected datasphere.delete_document, got {last.matched_route!r}"
        )


class TestDatasphereErrors:
    """Failure path: each route exercised with a 4xx/5xx the SDK must surface."""

    def test_list_server_error(self, signalwire_client, mock):
        mock.push_scenario("datasphere.list_documents", 500, {"error": "internal"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.list()
        assert exc.value.status_code == 500
        last = mock.last_request()
        assert last.matched_route == "datasphere.list_documents"
        assert last.response_status == 500

    def test_create_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("datasphere.create_document", 422, {"error": "url required"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.create()
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "datasphere.create_document"
        assert last.response_status == 422

    def test_search_unprocessable(self, signalwire_client, mock):
        mock.push_scenario("datasphere.search_documents", 422, {"error": "bad query"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.search()
        assert exc.value.status_code == 422
        last = mock.last_request()
        assert last.matched_route == "datasphere.search_documents"
        assert last.response_status == 422

    def test_list_chunks_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "datasphere.list_document_chunks", 404, {"error": "not found"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.list_chunks("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "datasphere.list_document_chunks"
        assert last.response_status == 404

    def test_get_chunk_not_found(self, signalwire_client, mock):
        mock.push_scenario("datasphere.get_document_chunk", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.get_chunk("doc-1001", "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "datasphere.get_document_chunk"
        assert last.response_status == 404

    def test_delete_chunk_not_found(self, signalwire_client, mock):
        mock.push_scenario(
            "datasphere.delete_document_chunk", 404, {"error": "not found"}
        )
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.delete_chunk("doc-1001", "missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "datasphere.delete_document_chunk"
        assert last.response_status == 404

    def test_get_not_found(self, signalwire_client, mock):
        mock.push_scenario("datasphere.get_document", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.get("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "datasphere.get_document"
        assert last.response_status == 404

    def test_update_not_found(self, signalwire_client, mock):
        mock.push_scenario("datasphere.update_document", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.update("missing", tags=["x"])
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "datasphere.update_document"
        assert last.response_status == 404

    def test_delete_not_found(self, signalwire_client, mock):
        mock.push_scenario("datasphere.delete_document", 404, {"error": "not found"})
        with pytest.raises(SignalWireRestError) as exc:
            signalwire_client.datasphere.documents.delete("missing")
        assert exc.value.status_code == 404
        last = mock.last_request()
        assert last.matched_route == "datasphere.delete_document"
        assert last.response_status == 404
