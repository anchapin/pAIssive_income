"""
Demo: Vector Database + RAG (Retrieval-Augmented Generation) using ChromaDB

Steps:
 1. pip install chromadb sentence-transformers
 2. python demo_vector_rag.py

This script embeds example texts, stores them in a local vector DB,
then retrieves the most relevant context for a query.
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging

# Configure logging instead of print statements
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

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


# 5. Define function to embed and insert documents
def embed_and_insert_documents(docs, embedder, collection):
    """Embed and insert documents into the collection.

    Args:
        docs: List of document dictionaries with 'id' and 'content' keys
        embedder: SentenceTransformer model for embedding
        collection: ChromaDB collection
    """
    ids = [doc["id"] for doc in docs]
    contents = [doc["content"] for doc in docs]
    embeddings = embedder.encode(contents).tolist()

    collection.add(ids=ids, documents=contents, embeddings=embeddings)


# Embed and add documents
embed_and_insert_documents(documents, embedder, collection)

logging.info("Documents stored in ChromaDB.")

# 6. Demo query
query = "What city is the Eiffel Tower located in?"

query_embedding = embedder.encode(query).tolist()
results = collection.query(query_embeddings=[query_embedding], n_results=2)

logging.info(f"Query: {query}")
logging.info("Top results:")
for doc, dist in zip(results["documents"][0], results["distances"][0]):
    logging.info(f"- {doc} (distance: {dist:.4f})")

"""
Expected output:

Query: What city is the Eiffel Tower located in?

Top results:
- The Eiffel Tower is in Paris. (distance: ...)
- The capital of Germany is Berlin. (distance: ...)
"""

# Cleanup for demo (optional): client.delete_collection("demo_rag")
