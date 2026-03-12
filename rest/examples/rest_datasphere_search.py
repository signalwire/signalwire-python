"""Example: Upload a document to Datasphere and run a semantic search.

Set these env vars (or pass them directly to SignalWireClient):
  SIGNALWIRE_PROJECT_ID   - your SignalWire project ID
  SIGNALWIRE_API_TOKEN    - your SignalWire API token
  SIGNALWIRE_SPACE        - your SignalWire space (e.g. example.signalwire.com)

For full HTTP debug output:
  SIGNALWIRE_LOG_LEVEL=debug
"""

from signalwire_agents.rest import SignalWireClient

client = SignalWireClient()


def main():
    # 1. Upload a document
    print("Uploading document to Datasphere...")
    doc = client.datasphere.documents.create(
        url="https://example.com/support-docs.pdf",
        tags=["support", "billing"],
        chunking_strategy="paragraph",
    )
    doc_id = doc["id"]
    print(f"  Document created: {doc_id}")

    # 2. Wait for processing, then list chunks
    print(f"\nListing chunks for document {doc_id}...")
    chunks = client.datasphere.documents.list_chunks(doc_id)
    for chunk in chunks.get("data", []):
        print(f"  - Chunk {chunk['id']}: {chunk.get('text', '')[:80]}...")

    # 3. Semantic search across all documents
    print("\nSearching Datasphere...")
    results = client.datasphere.documents.search(
        query_string="How do I reset my password?",
        tags=["support"],
        count=3,
    )
    for result in results.get("data", []):
        print(f"  - Score {result.get('distance', 'N/A')}: {result.get('text', '')[:80]}...")

    # 4. Clean up
    print(f"\nDeleting document {doc_id}...")
    client.datasphere.documents.delete(doc_id)
    print("  Deleted.")


if __name__ == "__main__":
    main()
