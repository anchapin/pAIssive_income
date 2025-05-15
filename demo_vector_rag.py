"""
Demo: Vector Database + RAG (Retrieval-Augmented Generation) using ChromaDB

Steps:
 1. uv pip install chromadb sentence-transformers
 2. python demo_vector_rag.py

This script embeds example texts, stores them in a local vector DB,
then retrieves the most relevant context for a query.
"""

import chromadb
from chromadb.config import Settings
import logging
from sentence_transformers import SentenceTransformer

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
def embed_and_insert_documents(docs, embedder_model, collection):
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
embed_and_insert_documents(documents, embedder, collection)

logger.info("Documents stored in ChromaDB.")

# 6. Demo query
query = "What city is the Eiffel Tower located in?"

query_embedding = embedder.encode(query).tolist()
results = collection.query(query_embeddings=[query_embedding], n_results=2)

logger.info(f"\nQuery: {query}\n")
logger.info("Top results:")
for doc, dist in zip(results["documents"][0], results["distances"][0]):
    logger.info(f"- {doc} (distance: {dist:.4f})")

"""
Expected output:

Query: What city is the Eiffel Tower located in?

Top results:
- The Eiffel Tower is in Paris. (distance: ...)
- The capital of Germany is Berlin. (distance: ...)
"""

# Cleanup for demo (optional): client.delete_collection("demo_rag")
