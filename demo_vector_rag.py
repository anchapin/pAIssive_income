"""
Demo: Vector Database + RAG (Retrieval-Augmented Generation) using ChromaDB.

Steps:
 1. pip install chromadb sentence-transformers
 2. python demo_vector_rag.py

This script embeds example texts, stores them in a local vector DB,
then retrieves the most relevant context for a query.
"""

from __future__ import annotations

import logging

# Type checking imports
from typing import TYPE_CHECKING

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Initialize ChromaDB client (local, in-memory for demo)
client = chromadb.Client(
    Settings(
        persist_directory=".chromadb_demo",  # change or remove for pure in-memory
        chroma_db_impl="duckdb+parquet",
    )
)

# 2. Prepare demo data (texts with metadata)
documents = [
    {"id": "1", "content": "The Eiffel Tower is in Paris."},
    {"id": "2", "content": "The capital of Germany is Berlin."},
    {"id": "3", "content": "The moon orbits the earth."},
    {"id": "4", "content": "Python is a programming language."},
    {
        "id": "5",
        "content": "Retrieval-Augmented Generation (RAG) enhances LLMs with external knowledge.",
    },
]

# 3. Load embedding model (Sentence Transformers)
embedder = SentenceTransformer("all-MiniLM-L6-v2")


# Define helper function
def embed_and_insert_documents(
    documents: list[dict], embedder: SentenceTransformer, collection: Collection
) -> None:
    """
    Embed documents and insert them into the ChromaDB collection.

    Args:
        documents: List of document dictionaries with 'id' and 'content' fields
        embedder: SentenceTransformer model for embedding generation
        collection: ChromaDB collection to insert into

    """
    # Extract document content and IDs
    texts = [doc["content"] for doc in documents]
    doc_ids = [doc["id"] for doc in documents]

    # Generate embeddings for all texts
    embeddings = embedder.encode(texts).tolist()

    # Add documents, IDs, and embeddings to collection
    collection.add(documents=texts, ids=doc_ids, embeddings=embeddings)


# 4. Create/get collection
collection = client.get_or_create_collection("demo_rag")

# 5. Embed and add documents
embed_and_insert_documents(documents, embedder, collection)

logger.info("Documents stored in ChromaDB.")

# 6. Demo query
query = "What city is the Eiffel Tower located in?"

query_embedding = embedder.encode(query).tolist()
results = collection.query(query_embeddings=[query_embedding], n_results=2)

logger.info("Query: %s", query)
logger.info("Top results:")
for doc, dist in zip(results["documents"][0], results["distances"][0]):
    logger.info("- %s (distance: %.4f)", doc, dist)

"""
Expected output:

Query: What city is the Eiffel Tower located in?

Top results:
- The Eiffel Tower is in Paris. (distance: ...)
- The capital of Germany is Berlin. (distance: ...)
"""

if __name__ == "__main__":
    # Only delete collection when running directly
    client.delete_collection("demo_rag")
