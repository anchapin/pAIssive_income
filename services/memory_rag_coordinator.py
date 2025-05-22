"""
Module: memory_rag_coordinator

This module provides the MemoryRAGCoordinator class, which queries both the mem0 memory system and the ChromaDB RAG system,
aggregates and deduplicates their responses, and returns a unified response object with detailed provenance and metrics.

Usage:
    coordinator = MemoryRAGCoordinator()
    response = coordinator.query(query="What is the project deadline?", user_id="user123")
"""

import time
from typing import Any, Dict, List, Optional, Tuple

# Import mem0 and ChromaDB interfaces as used in the codebase
import logging

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

try:
    from demo_vector_rag import chroma_query  # function: chroma_query(query: str, user_id: Optional[str] = None) -> List[Dict]
except ImportError:
    # Fallback stub for dev/CI if chroma_query is not available
    def chroma_query(query: str, user_id: Optional[str] = None) -> List[Dict]:
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