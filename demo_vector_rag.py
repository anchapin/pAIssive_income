"""
Demo: Vector Database + RAG (Retrieval-Augmented Generation) using ChromaDB.

with a Unified Schema and Best Practices for Interoperability.

Steps:
 1. uv pip install chromadb sentence-transformers
 2. python demo_vector_rag.py

This script embeds example texts, stores them in a local vector DB,
then retrieves the most relevant context for a query.
"""

from __future__ import annotations

import hashlib
import json
import logging
import unicodedata
from typing import Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Configure logging instead of print statements
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# 1. Initialize ChromaDB client (local, in-memory for demo)
client = chromadb.Client(
    Settings(
        persist_directory=".chromadb_demo",  # change or remove for pure in-memory
        chroma_db_impl="duckdb+parquet",
    )
)

# 2. Unified schema for all documents (id, content, user_id, metadata, embedding)
# Legacy demo content is adapted to this schema


def canonicalize_text(text: str) -> str:
    """
    Normalize and canonicalize text for deduplication.

    - Lowercase, strip, remove extra whitespace, apply NFC unicode normalization.
    """
    text = unicodedata.normalize("NFC", text.lower().strip())
    return " ".join(text.split())


def canonical_doc_hash(user_id: str, content: str, metadata: dict) -> str:
    """
    Create a canonical hash for deduplication.

    Uses user_id, canonicalized content, and metadata['source'] if present.
    """
    content_canon = canonicalize_text(content)
    source = metadata.get("source", "")
    hash_input = f"{user_id}|{content_canon}|{source}".encode()
    return hashlib.sha256(hash_input).hexdigest()


def prepare_document(
    doc: dict,
    user_id: Optional[str] = None,
    default_metadata: Optional[dict] = None,
    embedding: Optional[list[float]] = None,
) -> dict:
    """
    Ensure the document follows the unified schema.

    If fields are missing, fill with defaults.
    """
    doc_out = {}
    doc_out["id"] = (
        doc.get("id")
        or hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest()
    )
    doc_out["content"] = doc.get("content", "")
    doc_out["user_id"] = doc.get("user_id", user_id or "global")
    # Merge metadata: doc, then default_metadata, then ensure at least "source"
    doc_out["metadata"] = dict(default_metadata or {})
    doc_out["metadata"].update(doc.get("metadata", {}))
    if "source" not in doc_out["metadata"]:
        doc_out["metadata"]["source"] = "demo"
    doc_out["embedding"] = embedding or doc.get("embedding")
    return doc_out


# 3. Demo documents, now with schema fields (legacy content adapted)
demo_documents = [
    {
        "id": "1",
        "content": "The Eiffel Tower is in Paris.",
        "user_id": "global",
        "metadata": {"type": "fact", "source": "demo", "lang": "en"},
    },
    {
        "id": "2",
        "content": "The capital of Germany is Berlin.",
        "user_id": "global",
        "metadata": {"type": "fact", "source": "demo", "lang": "en"},
    },
    {
        "id": "3",
        "content": "The moon orbits the earth.",
        "user_id": "global",
        "metadata": {"type": "fact", "source": "demo", "lang": "en"},
    },
    {
        "id": "4",
        "content": "Python is a programming language.",
        "user_id": "global",
        "metadata": {"type": "fact", "source": "demo", "lang": "en"},
    },
    {
        "id": "5",
        "content": "Retrieval-Augmented Generation (RAG) enhances LLMs with external knowledge.",
        "user_id": "global",
        "metadata": {"type": "fact", "source": "demo", "lang": "en"},
    },
]

# 3. Load embedding model (Sentence Transformers)
embedder = SentenceTransformer("all-MiniLM-L6-v2")


# 4. Create/get collection
collection = client.get_or_create_collection("demo_rag")


# 6. Canonicalization and deduplication logic before inserting documents
def embed_and_insert_documents_with_dedup(
    docs: list[dict],
    embedder_model: SentenceTransformer,
    collection: chromadb.Collection,
    user_id_default: str = "global",
) -> tuple[list[dict], list[str]]:
    """
    Embed documents, canonicalize, deduplicate, and insert into collection.

    Returns: (inserted_docs, skipped_duplicate_ids).
    """
    stored_hashes = set()
    inserted_docs: list[dict] = []
    skipped_ids: list[str] = []

    # Retrieve all existing documents' canonical hashes (if any)
    # (In production: index this efficiently. For demo, we keep it simple.)
    try:
        # Attempt to fetch all docs (if API allows)
        existing = collection.get(include=["documents", "metadatas"])
        existing_docs = existing.get("documents")
        existing_metas = existing.get("metadatas")
        if existing_docs is not None and existing_metas is not None:
            for i, doc_content in enumerate(existing_docs):
                meta = existing_metas[i]
                uid = meta.get("user_id", user_id_default)
                content = doc_content
                doc_hash = canonical_doc_hash(uid, content, meta)
                stored_hashes.add(doc_hash)
    except (RuntimeError, ValueError, KeyError, TypeError) as e:
        logger.warning("Collection may be empty or error occurred: %s", e)

    for doc_in in docs:
        doc = prepare_document(doc_in, user_id=user_id_default)
        doc_hash = canonical_doc_hash(doc["user_id"], doc["content"], doc["metadata"])
        if doc_hash in stored_hashes:
            logger.info(
                "Deduplication: Skipping duplicate doc id=%s (hash=%s...)",
                doc["id"],
                doc_hash[:8],
            )
            skipped_ids.append(doc["id"])
            continue
        # Canonicalize content before embedding
        canon_content = canonicalize_text(doc["content"])
        embedding = embedder_model.encode([canon_content])[0].tolist()
        doc["embedding"] = embedding
        # Insert with all unified schema fields
        # ChromaDB: 'documents' is content, 'metadatas' is dict, 'ids' is id, 'embeddings' is vector
        collection.add(
            ids=[doc["id"]],
            documents=[doc["content"]],
            embeddings=[embedding],
            metadatas=[
                {
                    **doc["metadata"],
                    "user_id": doc[
                        "user_id"
                    ],  # Ensure user_id is in metadata for filtering
                    "canonical_hash": doc_hash,
                }
            ],
        )
        logger.info("Inserted doc id=%s (hash=%s...)", doc["id"], doc_hash[:8])
        inserted_docs.append(doc)
        stored_hashes.add(doc_hash)
    return inserted_docs, skipped_ids


# Insert demo documents (deduplication and canonicalization applied)
inserted, skipped = embed_and_insert_documents_with_dedup(
    demo_documents, embedder, collection
)
logger.info(
    "\nInserted %d documents, skipped %d duplicates.", len(inserted), len(skipped)
)


# 7. Retrieval: Context propagation and metadata filtering example
def query_with_metadata_filter(
    collection: chromadb.Collection,
    query: str,
    user_id: Optional[str] = None,
    metadata_filter: Optional[dict] = None,
    n_results: int = 3,
) -> dict:
    """
    Query the vector DB with optional user_id and metadata filter.

    Returns the matching results.
    """
    query_embedding = embedder.encode([canonicalize_text(query)])[0].tolist()
    where = {}
    if user_id:
        where["user_id"] = user_id
    if metadata_filter:
        where.update(metadata_filter)
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where if where else None,
        include=["documents", "metadatas", "distances"],
    )


# 6. Demo query
query = "What city is the Eiffel Tower located in?"
metadata_filter = {"type": "fact"}  # Filter for fact-type documents

results = query_with_metadata_filter(
    collection, query, user_id="global", metadata_filter=metadata_filter
)
logger.info("\nQuery: %s\nFilter: %s\nResults:", query, metadata_filter)
docs = results.get("documents")
metas = results.get("metadatas")
dists = results.get("distances")
if docs is not None and metas is not None and dists is not None:
    for doc, meta, dist in zip(docs[0], metas[0], dists[0]):
        logger.info("- %s [meta: %s] (distance: %.4f)", doc, meta, dist)

# Show how context propagation works: fetch all 'fact' type for a user
logger.info("\n--- Context Propagation Demo: All 'fact' memories for user 'global' ---")
all_facts = collection.get(where={"user_id": "global", "type": "fact"})
docs = all_facts.get("documents")
metas = all_facts.get("metadatas")
if docs is not None and metas is not None:
    for i, doc in enumerate(docs):
        meta = metas[i]
        logger.info("Fact %d: %s [meta: %s]", i + 1, doc, meta)

"""
Expected output:
"""


def test_deduplication_and_metadata() -> None:
    """Test deduplication and metadata filtering logic."""
    # Try to re-insert a duplicate doc
    duplicate = {
        "id": "dup1",
        "content": "The Eiffel Tower is in Paris.",
        "user_id": "global",
        "metadata": {"type": "fact", "source": "demo", "lang": "en"},
    }
    inserted, skipped = embed_and_insert_documents_with_dedup(
        [duplicate], embedder, collection
    )
    if len(inserted) != 0:
        logger.error("Deduplication failed: duplicate was inserted.")
        msg = "Deduplication failed: duplicate was inserted."
        raise AssertionError(msg)
    if len(skipped) != 1:
        logger.error("Deduplication test: duplicate was not skipped.")
        msg = "Deduplication test: duplicate was not skipped."
        raise AssertionError(msg)
    logger.info("Deduplication test passed.")

    # Insert a new doc with different source
    new_doc = {
        "id": "new1",
        "content": "The Eiffel Tower is in Paris.",
        "user_id": "global",
        "metadata": {"type": "fact", "source": "wikipedia", "lang": "en"},
    }
    inserted, skipped = embed_and_insert_documents_with_dedup(
        [new_doc], embedder, collection
    )
    if len(inserted) != 1:
        logger.error("Unique document was not inserted.")
        msg = "Unique document was not inserted."
        raise AssertionError(msg)
    logger.info("Insertion of new doc with different source passed.")

    # Test metadata filtering
    filter_meta = {"source": "wikipedia"}
    results = collection.get(where={"user_id": "global", **filter_meta})
    docs = results.get("documents")
    if docs is not None and not any(doc == new_doc["content"] for doc in docs):
        logger.error("Metadata filtering failed.")
        msg = "Metadata filtering failed."
        raise AssertionError(msg)
    logger.info("Metadata filtering test passed.")


if __name__ == "__main__":
    logger.info("\n--- Running Test Block ---")
    test_deduplication_and_metadata()
    logger.info("All tests passed.")
