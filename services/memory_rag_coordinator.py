"""
Module: memory_rag_coordinator

This module provides the MemoryRAGCoordinator class, which queries both the mem0 memory system and the ChromaDB RAG system,
aggregates and deduplicates their responses, and returns a unified response object with detailed provenance and metrics.

Usage:
    coordinator = MemoryRAGCoordinator()
    response = coordinator.query(query="What is the project deadline?", user_id="user123")
"""

import time
import logging
from typing import Any, Dict, List, Optional, Tuple

# Import mem0 and ChromaDB interfaces as used in the codebase

def mem0_query(query: str, user_id: str) -> List[Dict]:
    """
    Query the mem0 memory system for relevant memories given a query and user ID.

    Instantiates a mem0 Memory object and calls its `search` method.

    Parameters
    ----------
    query : str
        The query string to search for.
    user_id : str
        The user identifier.

    Returns
    -------
    List[Dict]
        A list of dictionaries representing relevant memories.

    Notes
    -----
    - Requires the `mem0ai` package to be installed.
    - If mem0 is unavailable or an exception occurs, returns an empty list.
    """
    try:
        from mem0 import Memory
    except ImportError:
        logging.warning("mem0ai package is not installed. Install with: uv pip install mem0ai")
        return []

    try:
        memory = Memory()
        results = memory.search(query=query, user_id=user_id)
        # Ensure results are a list of dicts
        if not isinstance(results, list):
            logging.error("mem0 Memory.search did not return a list.")
            return []
        return results
    except Exception as e:
        logging.error(f"Exception during mem0_query: {e}")
        return []

import os

def chroma_query(query: str, user_id: Optional[str] = None) -> List[Dict]:
    """
    Query the ChromaDB RAG system for relevant documents given a query and optional user ID.

    Instantiates a ChromaDB client and collection, embeds the query using SentenceTransformer,
    performs a vector similarity search, and returns results as a list of dicts.

    Parameters
    ----------
    query : str
        The query string to search for.
    user_id : Optional[str]
        The user identifier (currently unused; future extension: per-user collections).

    Returns
    -------
    List[Dict]
        A list of dictionaries representing relevant documents, with keys including:
            - 'text' or 'content': The matched document text.
            - 'score': Vector distance (smaller is more similar).
            - ... (other metadata as available)

    Notes
    -----
    - Requires the `chromadb` and `sentence-transformers` packages.
      Install with: uv pip install chromadb sentence-transformers
    - If ChromaDB or embedding model is unavailable or an exception occurs, returns an empty list.
    - This function creates or loads a collection named "demo_rag".
      For production, parameterize the collection name and persist directory as needed.
    """
    try:
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer
    except ImportError:
        logging.warning(
            "chromadb and/or sentence-transformers not installed. Install with: uv pip install chromadb sentence-transformers"
        )
        return []

    try:
        # Choose a persist directory for ChromaDB (avoid .gitignore-excluded locations)
        persist_dir = os.environ.get("CHROMADB_PERSIST_DIR", ".chromadb_demo")
        client = chromadb.Client(
            Settings(
                persist_directory=persist_dir,
                chroma_db_impl="duckdb+parquet",
            )
        )

        collection_name = "demo_rag"
        collection = client.get_or_create_collection(collection_name)

        # Load embedding model (can be cached between calls in production)
        embedder = SentenceTransformer("all-MiniLM-L6-v2")

        # Embed the query
        query_embedding = embedder.encode(query).tolist()

        # Query the collection for top 5 matches (customize as needed)
        results = collection.query(query_embeddings=[query_embedding], n_results=5)

        # results["documents"], results["distances"], results["ids"], results["metadatas"]
        # Each is a list of lists (one per query)
        docs = results.get("documents", [[]])[0]
        dists = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else [{} for _ in docs]

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

        return formatted
    except Exception as e:
        logging.error(f"Exception during chroma_query: {e}")
        return []


class MemoryRAGCoordinator:
    """
    MemoryRAGCoordinator coordinates queries to both mem0 and ChromaDB retrieval systems,
    aggregates and deduplicates their results, and returns a unified, provenance-rich response.

    Methods
    -------
    query(query: str, user_id: str) -> Dict:
        Query both memory systems, aggregate results, and return a unified response.

    The response object includes:
        - merged_results: List of unique hits, each with text, source, timestamp, and relevance
        - subsystem_metrics: Timing and cost for each subsystem
        - raw_mem0_results: Original mem0 results
        - raw_chroma_results: Original ChromaDB results
    """

    def __init__(self):
        """
        Initialize the MemoryRAGCoordinator.

        Any shared state or resource initialization can be done here.
        """
        pass

    def query(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Query both mem0 and ChromaDB, aggregate and deduplicate their responses,
        and return a unified response.

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
        # Query mem0
        start = time.time()
        mem0_results = mem0_query(query, user_id)
        mem0_time = time.time() - start
        metrics['mem0'] = {'time_sec': mem0_time, 'cost': self._estimate_cost(mem0_results)}

        # Query ChromaDB
        start = time.time()
        chroma_results = chroma_query(query, user_id=user_id)
        chroma_time = time.time() - start
        metrics['chroma'] = {'time_sec': chroma_time, 'cost': self._estimate_cost(chroma_results)}

        # Aggregate and deduplicate
        merged_results = self._merge_results(mem0_results, chroma_results)

        return {
            'merged_results': merged_results,
            'subsystem_metrics': metrics,
            'raw_mem0_results': mem0_results,
            'raw_chroma_results': chroma_results,
        }

    def _merge_results(self, mem0_results: List[Dict], chroma_results: List[Dict]) -> List[Dict]:
        """
        Merge, deduplicate, and resolve conflicts between mem0 and ChromaDB results.

        Preference is given to more recent or more relevant information when duplicates/conflicts arise.

        Parameters
        ----------
        mem0_results : List[Dict]
            Results returned from mem0_query.
        chroma_results : List[Dict]
            Results returned from chroma_query.

        Returns
        -------
        List[Dict]
            Merged, deduplicated, and resolved results.
        """
        # Normalize results to a canonical form: text, source, timestamp, relevance
        def norm_result(r: Dict, source: str) -> Dict:
            return {
                'text': r.get('text') or r.get('content') or "",
                'source': source,
                'timestamp': r.get('timestamp'),
                'relevance': r.get('score') or r.get('relevance') or 0.0,
                **{k: v for k, v in r.items() if k not in ('text', 'content', 'timestamp', 'score', 'relevance')}
            }

        canonical_mem0 = [norm_result(r, "mem0") for r in mem0_results]
        canonical_chroma = [norm_result(r, "chroma") for r in chroma_results]

        # Deduplicate: Use text as key; prefer more relevant, then more recent
        combined = canonical_mem0 + canonical_chroma
        deduped = {}
        for r in combined:
            key = r['text'].strip()
            if not key:
                continue
            if key in deduped:
                existing = deduped[key]
                # Prefer higher relevance, then more recent timestamp
                if r['relevance'] > existing['relevance']:
                    deduped[key] = r
                elif r['relevance'] == existing['relevance']:
                    ts_r = r.get('timestamp') or 0
                    ts_e = existing.get('timestamp') or 0
                    if ts_r > ts_e:
                        deduped[key] = r
            else:
                deduped[key] = r

        # Sort by descending relevance, then most recent timestamp
        merged = list(deduped.values())
        merged.sort(key=lambda x: (-x.get('relevance', 0.0), -(x.get('timestamp') or 0)))
        return merged

    def _estimate_cost(self, results: List[Dict]) -> float:
        """
        Estimate the 'cost' of a query to a subsystem (stub implementation).

        Parameters
        ----------
        results : List[Dict]
            Results returned by a subsystem.

        Returns
        -------
        float
            Estimated cost (for extension/future use; currently returns 0.0)
        """
        # TODO: Implement true cost estimation if available (API usage, tokens, etc.)
        return 0.0