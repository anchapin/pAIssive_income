"""
Module: memory_rag_coordinator.

This module provides the MemoryRAGCoordinator class, which queries both the mem0 memory system and the ChromaDB RAG system,
aggregates and deduplicates their responses, and returns a unified response object with detailed provenance and metrics.

Usage:
    coordinator = MemoryRAGCoordinator()
    response = coordinator.query(query="What is the project deadline?", user_id="user123")
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)


class MemoryRAGCoordinator:
    """
    Coordinates queries to both mem0 and ChromaDB retrieval systems.

    Aggregates and deduplicates their results, and returns a unified, provenance-rich response.

    Parameters
    ----------
    chroma_collection_name : str
        Name of the ChromaDB collection (default: "demo_rag").
    chroma_n_results : int
        Number of top results to return from ChromaDB (default: 5).
    chroma_persist_dir : Optional[str]
        Directory for ChromaDB persistence (default: uses CHROMADB_PERSIST_DIR env or ".chromadb_demo").

    """

    def __init__(
        self,
        chroma_collection_name: str = "demo_rag",
        chroma_n_results: int = 5,
        chroma_persist_dir: str | None = None,
    ) -> None:
        """Initialize the MemoryRAGCoordinator."""
        # Setup ChromaDB client, collection, and embedder (can fail gracefully if not installed)
        self.chroma_collection_name = chroma_collection_name
        self.chroma_n_results = chroma_n_results
        self.chroma_persist_dir = chroma_persist_dir or os.environ.get(
            "CHROMADB_PERSIST_DIR", ".chromadb_demo"
        )
        self._chroma_client = None
        self._chroma_collection = None
        self._embedder = None

        try:
            import chromadb
            from chromadb.config import Settings
            from sentence_transformers import SentenceTransformer

            # Initialize client and collection
            self._chroma_client = chromadb.Client(
                Settings(
                    persist_directory=self.chroma_persist_dir,
                    chroma_db_impl="duckdb+parquet",
                )
            )
            self._chroma_collection = self._chroma_client.get_or_create_collection(
                self.chroma_collection_name
            )
            self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            logger.warning(
                "chromadb and/or sentence-transformers not installed. Install with: uv pip install chromadb sentence-transformers"
            )
        except Exception:
            logger.exception("Failed to initialize ChromaDB or embedder")

        # Initialize mem0 Memory object (reuse for performance)
        self._mem0_memory = None
        try:
            from mem0 import Memory
            self._mem0_memory = Memory()
        except ImportError:
            logger.warning("mem0ai package is not installed. Install with: uv pip install mem0ai")
        except Exception:
            logger.exception("Failed to initialize mem0 Memory")

    def query(self, query: str, user_id: str) -> dict[str, Any]:
        """
        Query both mem0 and ChromaDB, aggregate and deduplicate their responses, and return a unified response.

        Parameters
        ----------
        query : str
            The user's query string.
        user_id : str
            The user identifier.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing:
                - merged_results: List of merged and deduplicated results
                - subsystem_metrics: Dict with timing/cost per subsystem
                - raw_mem0_results: Raw mem0 results
                - raw_chroma_results: Raw ChromaDB results

        """
        metrics = {}
        try:
            # Query mem0
            start = time.time()
            mem0_results = self.mem0_query(query, user_id)
            mem0_time = time.time() - start
            metrics["mem0"] = {
                "time_sec": mem0_time,
                "cost": self._estimate_cost(mem0_results),
            }

            # Query ChromaDB
            start = time.time()
            chroma_results = self.chroma_query(query)
            chroma_time = time.time() - start
            metrics["chroma"] = {
                "time_sec": chroma_time,
                "cost": self._estimate_cost(chroma_results),
            }

            # Aggregate and deduplicate
            merged_results = self._merge_results(mem0_results, chroma_results)
        except Exception:
            logger.exception("Exception during query")
        else:
            return {
                "merged_results": merged_results,
                "subsystem_metrics": metrics,
                "raw_mem0_results": mem0_results,
                "raw_chroma_results": chroma_results,
            }
        return {}

    def mem0_query(self, query: str, user_id: str) -> list[dict]:
        """
        Query the mem0 memory system for relevant memories given a query and user ID.

        Uses the pre-initialized mem0 Memory object for better performance.

        Returns
        -------
        list[dict]
            A list of dictionaries representing relevant memories.

        """
        if self._mem0_memory is None:
            return []

        try:
            results = self._mem0_memory.search(query=query, user_id=user_id)
            if not isinstance(results, list):
                logger.error("mem0 Memory.search did not return a list.")
                return []
        except Exception:
            logger.exception("Exception during mem0_query")
            return []
        else:
            return results

    def chroma_query(self, query: str) -> list[dict]:
        """
        Query the ChromaDB RAG system for relevant documents given a query.

        Returns
        -------
        list[dict]
            A list of dictionaries representing relevant documents, with keys including:
                - 'text' or 'content': The matched document text.
                - 'score': Vector distance (smaller is more similar).
                - ... (other metadata as available)

        """
        if self._chroma_collection is None or self._embedder is None:
            return []

        try:
            query_embedding = self._embedder.encode(query).tolist()
            results = self._chroma_collection.query(
                query_embeddings=[query_embedding], n_results=self.chroma_n_results
            )
            docs = results.get("documents", [[]])[0]
            dists = results.get("distances", [[]])[0]
            ids = results.get("ids", [[]])[0]
            metadatas = (
                results.get("metadatas", [[]])[0]
                if results.get("metadatas")
                else [{} for _ in docs]
            )

            formatted = []
            for doc, dist, doc_id, meta in zip(docs, dists, ids, metadatas):
                entry = {
                    "content": doc,
                    "score": dist,
                    "id": doc_id,
                }
                if isinstance(meta, dict):
                    entry.update(meta)
                formatted.append(entry)
        except Exception:
            logger.exception("Exception during chroma_query")
            return []
        else:
            return formatted

    def _merge_results(
        self, mem0_results: list[dict], chroma_results: list[dict]
    ) -> list[dict]:
        """
        Merge, deduplicate, and resolve conflicts between mem0 and ChromaDB results.

        Preference is given to more recent or more relevant information when duplicates/conflicts arise.
        Normalizes scores so that higher is always better, regardless of source.
        """

        def norm_result(r: dict, source: str) -> dict:
            text_content = r.get("text") or r.get("content") or ""
            timestamp = r.get("timestamp")
            original_score = r.get("score")
            original_relevance = r.get("relevance")

            # Normalize scores to a consistent scale where 'higher is better' for all sources
            current_relevance_value = 0.0
            if source == "chroma":
                # ChromaDB typically returns distance scores where lower is better
                # Convert to relevance where higher is better
                if original_score is not None:
                    # For distance metrics (0 to ~2 for L2, 0 to 1 for cosine distance):
                    # Use 1/(1+distance) to convert to relevance (0 to 1 scale)
                    # This ensures that distance 0 -> relevance 1.0, and larger distances -> smaller relevance
                    current_relevance_value = 1.0 / (1.0 + original_score)
                else:
                    # If no score available, assign lowest relevance
                    current_relevance_value = 0.0
            elif source == "mem0":
                # mem0 typically returns relevance/similarity scores where higher is better
                # Use score first, then relevance, then default to 0.0
                current_relevance_value = (
                    original_score
                    if original_score is not None
                    else (original_relevance if original_relevance is not None else 0.0)
                )
                # Ensure mem0 scores are in 0-1 range for consistency
                # If score is already > 1, normalize it (some systems might use different scales)
                if current_relevance_value > 1.0:
                    current_relevance_value = min(current_relevance_value / 100.0, 1.0)  # Assume 0-100 scale
            else:
                # Unknown source, default to 0.0
                current_relevance_value = 0.0
            return {
                "text": text_content,
                "source": source,
                "timestamp": timestamp,
                "relevance": current_relevance_value,
                **{
                    k: v
                    for k, v in r.items()
                    if k not in ("text", "content", "timestamp", "score", "relevance")
                },
            }

        canonical_mem0 = [norm_result(r, "mem0") for r in mem0_results]
        canonical_chroma = [norm_result(r, "chroma") for r in chroma_results]

        # Deduplicate: Use text as key; prefer more relevant, then more recent
        combined = canonical_mem0 + canonical_chroma
        deduped = {}
        for r in combined:
            key = r["text"].strip()
            if not key:
                continue
            if key in deduped:
                existing = deduped[key]
                # Prefer higher relevance, then more recent timestamp
                if r["relevance"] > existing["relevance"]:
                    deduped[key] = r
                elif r["relevance"] == existing["relevance"]:
                    ts_r = r.get("timestamp") or 0
                    ts_e = existing.get("timestamp") or 0
                    if ts_r > ts_e:
                        deduped[key] = r
            else:
                deduped[key] = r

        # Sort by descending relevance, then most recent timestamp
        merged = list(deduped.values())
        merged.sort(
            key=lambda x: (-x.get("relevance", 0.0), -(x.get("timestamp") or 0))
        )
        return merged

    def _estimate_cost(self, results: list[dict]) -> float:  # noqa: ARG002
        """
        Estimate the 'cost' of a query to a subsystem (stub implementation).

        Returns
        -------
        float
            The estimated cost (currently always 0.0).

        """
        return 0.0
