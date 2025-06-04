# mem0 Integration

This document provides information about the integration of mem0, a memory layer for AI agents, into the pAIssive_income project.

## Overview

[mem0](https://mem0.ai) is a memory system that enables AI agents to remember user preferences, past interactions, and important information across conversations. It provides persistent, contextual memory capabilities that enhance the personalization and effectiveness of AI agents.

## Installation

mem0 and its dependencies are now included in the main `requirements.txt` file. To install them, use:

```bash
uv pip install -r requirements.txt
```

If you do not have 'uv' installed, you can install it one time with:

```bash
pip install uv
```

All subsequent dependency management should use 'uv' exclusively.

## Required Dependencies

The following dependencies are required for mem0:

- `mem0ai>=0.1.100`: The core mem0 package
- `qdrant-client>=1.9.1`: Vector database client for memory storage
- `openai>=1.33.0`: Required for memory embeddings
- `pytz>=2024.1`: Required for timezone handling

## Environment Variables

mem0 requires an OpenAI API key to function properly. Set it as an environment variable:

```bash
# Linux/macOS
export OPENAI_API_KEY='your-api-key'

# Windows (PowerShell)
$env:OPENAI_API_KEY='your-api-key'

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key
```

## Basic Usage

Here's a simple example of how to use mem0 in your code:

```python
from mem0 import Memory

# Initialize memory
memory = Memory()

# Add a memory
memory.add("User prefers dark mode", user_id="user123")

# Search for relevant memories
results = memory.search("What are the user's preferences?", user_id="user123")

# Process results
for result in results.get("results", []):
    print(result)
```

## Integration with Agents

The project includes example implementations of mem0-enhanced agents:

- `agent_team/mem0_enhanced_agents.py`: Memory-enhanced CrewAI agents
- `adk_demo/mem0_enhanced_adk_agents.py`: Memory-enhanced ADK agents
- `examples/mem0_integration_example.py`: Example script demonstrating mem0 integration

## Docker Support

The Dockerfile has been updated to include mem0 and its dependencies. When running with Docker, make sure to pass the OpenAI API key as an environment variable:

```bash
docker-compose up -d
```

The `docker-compose.yml` file includes the `OPENAI_API_KEY` environment variable, which you can set before running the containers.

## Testing

To verify that mem0 is working correctly, you can run the test script:

```bash
python test_mem0.py
```

## Best Practices: mem0 and RAG

For agents that require both persistent user memory and dynamic retrieval of external knowledge (Retrieval-Augmented Generation, or RAG), we recommend a combined approach:

- **Use mem0** for user-specific, long-term memory (preferences, interaction history).
- **Use RAG** for dynamic, up-to-date, or domain-specific knowledge and document retrieval.
- **Combine both** to enable agents that can personalize retrieval, re-rank responses, and learn from user feedback.

**Example combined workflow:**
1. Retrieve user context from mem0.
2. Retrieve relevant external documents with RAG.
3. Use both memory and retrieval results as context for the agent's generation.
4. Store user feedback or new insights back into mem0.

See [docs/mem0_rag_best_practices.md](docs/mem0_rag_best_practices.md) for a full guide, code examples, and recommendations.

---

## Documentation

For more detailed information about mem0 and advanced integration patterns, refer to:

- `docs/README_mem0.md`: Overview of mem0 investigation
- `docs/mem0_investigation.md`: Comprehensive overview of mem0
- `docs/mem0_integration_options.md`: Analysis of integration approaches
- `docs/mem0_core_apis.md`: Documentation of mem0's core APIs
- `docs/mem0_rag_best_practices.md`: Best practices for mem0 + RAG usage

## Troubleshooting

If you encounter issues with mem0:

1. Ensure the OpenAI API key is set correctly
2. Check that all dependencies are installed
3. Verify that the vector database (Qdrant) is accessible
4. Check the logs for any error messages

## References

- [mem0 Official Website](https://mem0.ai)
- [mem0 GitHub Repository](https://github.com/mem0ai/mem0)

---

## mem0, Vector DB, and RAG Interoperability: Schema, Standards, and Codebase Alignment

### Intersection and Differences: mem0 vs. Standalone Vector DB/RAG

**mem0** serves as an intelligent memory layer that abstracts vector database (e.g., Qdrant) usage for agent memory, focusing on contextual, per-user, and conversational storage/retrieval.  
**Standalone vector DB/RAG** (as in `demo_vector_rag.py` and related scripts) typically implement a lower-level, stateless chunking and retrieval pipeline for documents, with explicit index/query operations and less built-in notion of user/session.

**Key Differences:**
- **Contextualization:** mem0 tightly couples user/session/context with each memory fragment; typical RAG/vector DB pipelines treat context as metadata or ignore it.
- **APIs:** mem0 exposes high-level add/search/update APIs, handling embedding and storage internally; RAG/vector DB code interacts directly with DB CRUD and embedding APIs.
- **Deduplication/History:** mem0 supports history and versioning, while standard RAG pipelines require manual deduplication and canonicalization.
- **Metadata:** mem0 treats metadata as first-class, whereas in most RAG examples, metadata is optional or inconsistently structured.

**Intersection:**  
Both store embeddings and associated texts ("memories", "chunks", etc.) in a vector DB backend, and can benefit from a shared schema for storage, deduplication, and interoperability.

---

### Unified Schema for Vector DB Storage

Adopting a unified schema enables seamless interoperation between mem0 and standalone RAG pipelines.

**Recommended Unified Schema:**

| Field      | Type      | Description                                       |
| ---------- | --------- | ------------------------------------------------- |
| id         | string    | Unique identifier (UUID, hash, or composite key)  |
| content    | string    | The main textual content (memory, chunk, etc.)    |
| user_id    | string    | User/session identifier (required, even if "global") |
| metadata   | object    | Structured metadata (dict/JSON), for tags, type, timestamps, source, etc. |
| embedding  | array[float] | Dense vector embedding (for similarity search) |

**Schema Adoption Examples:**
- **mem0:** Store all memories using this schema; map mem0's internal fields to these names (e.g., `memory_id` → `id`, `memory` → `content`, etc.).
- **RAG/vector DB scripts:** When ingesting or querying, enforce this schema for all upserts, queries, and retrievals. For legacy data, add migration logic or adapters to conform.

---

### Identifier and Context Propagation Standards

To maximize interoperability and auditability, adhere to these standards across all pipelines:

- **Always set `user_id`:** Even for system/global data, use a reserved string (e.g., `"global"`) rather than null/empty.
- **Use `metadata` for categorization:** Store fields like `type` (e.g., "doc", "message", "summary"), `source`, `timestamp`, and any custom tags.
- **Support multi-message/contextual queries:** When querying for context, allow batch retrieval using user_id + metadata filters (e.g., all memories with `type:message` for a user).
- **Propagate identifiers:** Any message, chunk, or memory passed between systems should retain its `id` and `user_id`. Downstream consumers must maintain these when writing back or updating.

---

### Deduplication and Context Sharing Strategy

- **Canonicalization:** When ingesting, normalize whitespace, casing, and remove duplicate content before embedding.
- **Deduplication:** Before upserting, check for existing entries with the same (user_id, content, metadata["source"]) triple, or use a canonical hash of (content + user_id + source).
- **Context Sharing:** Use `metadata` to indicate shared or referenced context (e.g., `{"shared_from": "original_id"}`); allow agents to fetch related memories via metadata queries.
- **Update/History Support:** Prefer update APIs that create new versions while retaining history (mem0 supports this natively; for RAG, store previous versions in metadata or a parallel history collection/table).
- **Metadata Filtering:** Use metadata fields for fine-grained filtering (e.g., by type, date, source) during both upsert and search.

---

### Actionable Steps for Codebase Alignment

1. **Update Code to Unified Schema:**
   - Refactor `demo_vector_rag.py` and any related ingestion/query logic to use the unified schema fields.
   - Ensure all new memories/chunks include `id`, `content`, `user_id`, `metadata`, and `embedding` on insert.
   - Provide migration scripts or adapters for legacy data.

2. **Propagate Identifiers and Metadata:**
   - Audit code for places where `user_id` or `metadata` may be missing or inconsistently set.
   - Update function signatures and database calls to require `user_id` and structured `metadata`.

3. **Deduplication/Context Sharing:**
   - Implement canonicalization/deduplication logic in ingestion scripts.
   - Add support for context sharing via metadata references.

4. **Testing:**
   - Add/expand tests to verify interoperability:  
     - Test mem0 API and direct vector DB queries return consistent results using the unified schema.
     - Add tests for deduplication, metadata filtering, and context sharing.

5. **Documentation:**
   - Update this README and all related docs to reference the unified schema.
   - Optionally, add a new detailed doc: `docs/vector_db_schema_and_alignment.md` for technical details, migration steps, and code examples.

6. **Example Code Alignment:**
   - Update `demo_vector_rag.py` to:
     - Accept and store all unified schema fields.
     - Demonstrate context propagation and metadata usage.
     - Show deduplication in action.

---

For further technical details, see the draft doc [`docs/vector_db_schema_and_alignment.md`] if present, or create it using the above schema and practices.
