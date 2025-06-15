# MemoryRAGCoordinator Documentation

## Overview

The `MemoryRAGCoordinator` is a unified middleware component that coordinates queries between the mem0 memory system and ChromaDB vector database. It provides a single interface for retrieving, aggregating, and deduplicating results from both systems, ensuring consistent scoring and optimal performance.

## Key Features

### 1. Unified Query Interface
- Single method to query both mem0 and ChromaDB systems
- Automatic fallback when dependencies are not available
- Consistent response format with detailed provenance

### 2. Score Normalization
The coordinator implements sophisticated score normalization to ensure consistent ranking across different systems:

#### ChromaDB Scores (Distance-based)
- **Input**: Distance scores where lower values indicate higher similarity
- **Range**: Typically 0 to ~2 for L2 distance, 0 to 1 for cosine distance
- **Normalization**: Converted to relevance using `1.0 / (1.0 + distance)`
- **Output**: Relevance scores where higher values indicate better matches

#### mem0 Scores (Relevance-based)
- **Input**: Relevance/similarity scores where higher values indicate better matches
- **Range**: Typically 0 to 1, but may vary by implementation
- **Normalization**: Ensures scores are in 0-1 range, handles different scales
- **Output**: Standardized relevance scores

### 3. Performance Optimizations
- **Lazy Initialization**: ChromaDB client and SentenceTransformer are initialized once in `__init__`
- **Cached Components**: Reuses embedder and collection objects across queries
- **Efficient Memory Management**: Pre-initialized mem0 Memory object

### 4. Deduplication and Merging
- **Text-based Deduplication**: Uses content text as the primary deduplication key
- **Preference Logic**: Prioritizes higher relevance scores, then more recent timestamps
- **Metadata Preservation**: Maintains original metadata while adding source information

## Usage

### Basic Usage

```python
from services.memory_rag_coordinator import MemoryRAGCoordinator

# Initialize coordinator
coordinator = MemoryRAGCoordinator()

# Query both systems
response = coordinator.query(
    query="What is the project deadline?",
    user_id="user123"
)

# Access results
merged_results = response["merged_results"]
metrics = response["subsystem_metrics"]
```

### Configuration Options

```python
# Custom configuration
coordinator = MemoryRAGCoordinator(
    chroma_collection_name="my_collection",
    chroma_n_results=10,
    chroma_persist_dir="/path/to/chroma/data"
)
```

### Response Format

```python
{
    "merged_results": [
        {
            "text": "Content text",
            "source": "mem0" | "chroma",
            "relevance": 0.95,  # Normalized score (0-1)
            "timestamp": 1234567890,
            # ... other metadata
        }
    ],
    "subsystem_metrics": {
        "mem0": {
            "time_sec": 0.1,
            "cost": 0.0
        },
        "chroma": {
            "time_sec": 0.2,
            "cost": 0.0
        }
    },
    "raw_mem0_results": [...],
    "raw_chroma_results": [...]
}
```

## Integration with Memory-Enhanced Agents

The coordinator is automatically integrated into memory-enhanced agent classes:

```python
from agent_team.mem0_enhanced_agents import MemoryEnhancedCrewAIAgentTeam

# The team automatically uses MemoryRAGCoordinator
team = MemoryEnhancedCrewAIAgentTeam(user_id="user123")

# Retrieve memories (uses coordinator internally)
memories = team.retrieve_relevant_memories(
    query="project information",
    limit=5
)
```

## Dependencies

### Required
- Python 3.8+
- `logging` (standard library)
- `time` (standard library)
- `typing` (standard library)

### Optional
- `mem0ai`: For mem0 memory system integration
- `chromadb`: For vector database functionality
- `sentence-transformers`: For text embeddings

### Graceful Degradation
The coordinator works even when optional dependencies are missing:
- Without `mem0ai`: Only ChromaDB results are returned
- Without `chromadb`/`sentence-transformers`: Only mem0 results are returned
- Without both: Returns empty results with appropriate logging

## Performance Considerations

### Initialization Overhead
- ChromaDB client and embedder are initialized once during `__init__`
- Subsequent queries reuse these components for better performance
- mem0 Memory object is also pre-initialized

### Query Performance
- Parallel execution of mem0 and ChromaDB queries
- Efficient deduplication using dictionary-based lookups
- Minimal memory overhead for result processing

### Scaling Recommendations
- For high-volume applications, consider connection pooling
- Monitor memory usage with large result sets
- Implement caching for frequently accessed queries

## Error Handling

The coordinator implements comprehensive error handling:
- Graceful degradation when dependencies are missing
- Exception logging without breaking the query flow
- Empty result fallbacks for failed subsystem queries

## Testing

Comprehensive test suite available in `tests/tests_memory_rag_coordinator.py`:
- Score normalization validation
- Deduplication logic verification
- Integration testing with mock systems
- Performance benchmarking

## Changelog

### Recent Improvements
- **Score Normalization**: Fixed critical issue where ChromaDB distances and mem0 relevance scores were not properly normalized
- **Performance Optimization**: Moved initialization to `__init__` method for better performance
- **Code Quality**: Improved error handling and logging throughout the module
- **Test Coverage**: Added comprehensive test suite for all functionality

## Future Enhancements

- **Caching Layer**: Add query result caching for improved performance
- **Advanced Scoring**: Implement more sophisticated relevance scoring algorithms
- **Batch Processing**: Support for batch queries across multiple users
- **Monitoring**: Add detailed metrics and monitoring capabilities
