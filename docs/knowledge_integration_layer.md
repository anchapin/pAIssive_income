# Unified Knowledge Integration Layer (mem0 + Vector DB/RAG)

## Overview and Motivation

As intelligent applications increasingly rely on both structured memory (such as mem0) and unstructured knowledge retrieval (such as vector databases or Retrieval-Augmented Generation, RAG), there is a need for a unified layer that abstracts and orchestrates these diverse sources. The unified Knowledge Integration Layer provides:

- **A single interface** to access multiple knowledge backends (mem0, vector DBs, RAG, etc.).
- **Fallback and aggregation mechanisms** to ensure robust, high-quality knowledge retrieval.
- **Consistent extension points** for adding new sources of knowledge without modifying core logic.
- **Seamless usage** in agent workflows, pipelines, or applications.

This layer dramatically simplifies knowledge management, improves code maintainability, and accelerates the integration of new knowledge modalities.

---

## Architecture Summary

**Key Components:**

- **KnowledgeSource Interface**  
  An abstract contract for all knowledge providers (mem0, vector DB, RAG, etc.), enforcing a simple, consistent API.

- **KnowledgeStrategy Enum**  
  Defines strategies for querying, such as `FALLBACK`, `AGGREGATE`, `PREFER_MEM0`, etc., allowing flexible runtime behavior.

- **Integration Layer**  
  Orchestrates calls to all registered `KnowledgeSource` implementations according to the selected `KnowledgeStrategy`. Handles fallback, aggregation, and result normalization.

- **Extensibility**  
  New knowledge sources can be registered by implementing the `KnowledgeSource` interface and adding them to the orchestrator.

**High-Level Flow:**

```
User/Agent Query
      ↓
Knowledge Integration Layer
      ↓
+--------------------------+
|    KnowledgeStrategy     |
+--------------------------+
      ↓
+--------------------------+
|   [mem0]   [VectorDB]    |
|   [RAG]    [CustomSrc]   |
+--------------------------+
      ↓
Unified Results (fallback, aggregated, etc.)
```

---

## Usage Pattern

### Basic Usage

```python
from knowledge_integration_layer import KnowledgeOrchestrator, KnowledgeStrategy

# Create orchestrator instance (registers mem0, vector DB, etc.)
orchestrator = KnowledgeOrchestrator(
    strategy=KnowledgeStrategy.FALLBACK  # or AGGREGATE, PREFER_MEM0, etc.
)

# Query for information
results = orchestrator.query("What is the capital of France?")

for result in results:
    print(result['source'], ":", result['content'])
```

### Changing the Strategy

```python
orchestrator.set_strategy(KnowledgeStrategy.AGGREGATE)
results = orchestrator.query("Explain quantum entanglement in simple terms.")
```

### Adding/Extending with a New Knowledge Source

```python
from knowledge_integration_layer import KnowledgeSource

class MyCustomKnowledgeSource(KnowledgeSource):
    def query(self, question, **kwargs):
        # Implement retrieval logic here
        return [{"source": "my_custom", "content": "Custom answer"}]

# Register the new source
orchestrator.add_source(MyCustomKnowledgeSource())
```

---

## Example: Typical Usage

```python
from knowledge_integration_layer import KnowledgeOrchestrator, KnowledgeStrategy

# Instantiate with desired strategy
orchestrator = KnowledgeOrchestrator(strategy=KnowledgeStrategy.PREFER_MEM0)

# Query
response = orchestrator.query("Who wrote 'Le Petit Prince'?")

print(response[0]['content'])
```

---

## How to Add New Knowledge Sources

1. **Implement the KnowledgeSource Interface**

   ```python
   from knowledge_integration_layer import KnowledgeSource

   class WikiKnowledge(KnowledgeSource):
       def query(self, question, **kwargs):
           # Connect to Wikipedia API or local dump
           return [{"source": "wiki", "content": "..."}]
   ```

2. **Register Your Source with the Orchestrator**

   ```python
   orchestrator.add_source(WikiKnowledge())
   ```

3. **(Optional) Update Strategy or Fallback Ordering**

   Adjust via the `KnowledgeStrategy` enum or orchestrator options.

---

## Reference: Code Location

- **Integration Layer Source Code:**  
  See [`interfaces/knowledge_integration_layer.py`](../interfaces/knowledge_integration_layer.py)
- **KnowledgeSource Interface:**  
  See [`interfaces/knowledge_source.py`](../interfaces/knowledge_source.py)
- **Typical usage:**  
  Examples and demos: [`demo_vector_rag.py`](../demo_vector_rag.py) and [`main_demo_vector_rag.py`](../main_demo_vector_rag.py)

---

## Documentation and Tests

- Keep this documentation file up to date as new knowledge sources or strategies are added.
- Ensure that any new sources or orchestrator changes are accompanied by tests (see `tests/`).

---

## Summary

The unified Knowledge Integration Layer streamlines access to diverse knowledge sources, making it easier to build, extend, and maintain intelligent systems that combine the strengths of mem0, vector search, RAG, and beyond.