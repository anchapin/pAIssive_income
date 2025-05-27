"""
Demo: Vector Database + RAG (Retrieval-Augmented Generation) using ChromaDB.

Steps:
 1. uv pip install chromadb sentence-transformers
 2. python demo_vector_rag.py

This script embeds example texts, stores them in a local vector DB,
then retrieves the most relevant context for a query.
"""

from __future__ import annotations

import logging
import sys  # Added for sys.exit

# Configure logging
logger = logging.getLogger(__name__)


# Configure logging


# Configure logging


try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("Error: chromadb module not found. Please install it with 'pip install chromadb'")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Error: sentence_transformers module not found. Please install it with 'pip install sentence-transformers'")
    sys.exit(1)



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

# 4. Create/get collection
collection = client.get_or_create_collection("demo_rag")


# 5. Embed and add documents
def embed_and_insert_documents(
    docs: list[dict[str, str]],
    embedder_model: SentenceTransformer,
    collection: chromadb.Collection,
) -> None:
    """
    Embed documents and insert them into the collection.

    Args:
        docs: List of document dictionaries with 'id' and 'content' keys
        embedder_model: SentenceTransformer model for embedding
        collection: ChromaDB collection to insert into

    """
    ids = [doc["id"] for doc in docs]
    contents = [doc["content"] for doc in docs]
    embeddings = embedder_model.encode(contents).tolist()

    collection.add(ids=ids, documents=contents, embeddings=embeddings)


# Call the function to embed and insert documents
def main():
    """Main function to run the RAG demo."""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    embed_and_insert_documents(documents, embedder, collection)

    logger.info("Documents stored in ChromaDB.")

    # 6. Demo query
    query = "What city is the Eiffel Tower located in?"

    query_embedding = embedder.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=2)

    logger.info("\nQuery: %s\n", query)
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

    # Cleanup for demo (optional): client.delete_collection("demo_rag")

if __name__ == "__main__":
    main()
