# mem0 Core APIs and Classes

This document provides a detailed overview of mem0's core APIs, classes, and usage patterns.

## Main Classes

### `Memory` Class

The primary interface for interacting with mem0's memory system.

```python
from mem0 import Memory

# Basic initialization
memory = Memory()

# Advanced initialization with custom configuration
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": "your-api-key",
            "model": "gpt-4"
        }
    }
}
memory = Memory.from_config(config)
```

### `AsyncMemory` Class

Asynchronous version of the Memory class for use in async applications.

```python
from mem0 import AsyncMemory

# Basic initialization
memory = AsyncMemory()

# Usage in async context
async def example():
    result = await memory.add("Memory to store", user_id="user123")
    search_results = await memory.search("Query", user_id="user123")
```

### `MemoryClient` Class

Client for interacting with mem0's managed platform API.

```python
from mem0 import MemoryClient

# Initialize with API key
client = MemoryClient(api_key="your-api-key")

# Use the client
client.add("Memory to store", user_id="user123")
results = client.search("Query to search", user_id="user123")
```

## Core Methods

### Memory Addition

```python
# Add a simple memory
result = memory.add(
    "I prefer dark mode in my applications.",
    user_id="user123",
    metadata={"category": "preferences"}
)

# Add conversation messages
messages = [
    {"role": "user", "content": "I'm allergic to shellfish."},
    {"role": "assistant", "content": "I'll remember that you have a shellfish allergy."}
]
result = memory.add(messages, user_id="user123")

# Add with inference disabled (store raw text)
result = memory.add(
    "Raw text to store without inference.",
    user_id="user123",
    infer=False
)
```

### Memory Retrieval

```python
# Search for relevant memories
search_result = memory.search(
    query="What food allergies do I have?",
    user_id="user123",
    limit=5  # Optional: limit number of results
)

# Get all memories for a user
all_memories = memory.get_all(user_id="user123")

# Get a specific memory by ID
specific_memory = memory.get(memory_id="memory-uuid")
```

### Memory Management

```python
# Update a memory
update_result = memory.update(
    memory_id="memory-uuid",
    data="Updated memory content."
)

# Get memory history (versions)
history_result = memory.history(memory_id="memory-uuid")

# Delete a specific memory
delete_result = memory.delete(memory_id="memory-uuid")

# Delete all memories for a user
delete_all_result = memory.delete_all(user_id="user123")

# Reset all memories (caution: deletes everything)
memory.reset()
```

## Configuration Options

### Vector Store Configuration

```python
vector_store_config = {
    "provider": "qdrant",  # Vector database provider
    "config": {
        "host": "localhost",  # Database host
        "port": 6333,  # Database port
        # Additional provider-specific options
    }
}
```

Supported providers:
- `qdrant` (default): Qdrant vector database
- Others may be available in future versions

### LLM Configuration

```python
llm_config = {
    "provider": "openai",  # LLM provider
    "config": {
        "api_key": "your-api-key",  # API key
        "model": "gpt-4",  # Model name
        "temperature": 0.7,  # Optional: temperature
        "max_tokens": 500,  # Optional: max tokens
        # Additional provider-specific options
    }
}
```

Supported providers:
- `openai` (default): OpenAI API
- `anthropic`: Anthropic Claude API
- `ollama`: Ollama local models
- `azure`: Azure OpenAI
- Others may be available

### Embedder Configuration

```python
embedder_config = {
    "provider": "openai",  # Embedding provider
    "config": {
        "api_key": "your-api-key",  # API key
        "model": "text-embedding-3-small",  # Model name
        # Additional provider-specific options
    }
}
```

Supported providers:
- `openai` (default): OpenAI Embeddings API
- Others may be available

### Graph Store Configuration (Optional)

```python
graph_store_config = {
    "provider": "neo4j",  # Graph database provider
    "config": {
        "url": "neo4j+s://your-instance",  # Connection URL
        "username": "neo4j",  # Authentication username
        "password": "password",  # Authentication password
        # Additional provider-specific options
    }
}
```

Supported providers:
- `neo4j`: Neo4j graph database

## Advanced Usage

### Custom Prompts

mem0 allows customization of the prompts used for memory processing:

```python
config = {
    # Other configuration options...
    "custom_fact_extraction_prompt": "Custom prompt for extracting facts from conversations",
    "custom_update_memory_prompt": "Custom prompt for updating existing memories"
}
memory = Memory.from_config(config)
```

### Filtering Memories

When searching or retrieving memories, you can apply filters:

```python
# Search with filters
filters = {
    "AND": [
        {
            "user_id": "user123"
        },
        {
            "metadata.category": "preferences"
        }
    ]
}
results = memory.search(
    query="What are my preferences?",
    filters=filters,
    version="v2"  # Required for advanced filtering
)

# Get all with filters
all_filtered = memory.get_all(
    filters=filters,
    version="v2",
    page=1,
    page_size=50
)
```

### Pagination

For large result sets, pagination is supported:

```python
# Get page 2 with 20 items per page
results = memory.get_all(
    user_id="user123",
    page=2,
    page_size=20
)
```

## Error Handling

mem0 operations may raise exceptions that should be handled:

```python
try:
    result = memory.add("Memory to store", user_id="user123")
except Exception as e:
    print(f"Error adding memory: {e}")

try:
    results = memory.search("Query", user_id="user123")
except Exception as e:
    print(f"Error searching memories: {e}")
```

## Best Practices

1. **User IDs**: Use consistent user IDs across operations to maintain proper memory isolation
2. **Metadata**: Use metadata to categorize memories for better organization and filtering
3. **Error Handling**: Always implement proper error handling for production use
4. **Memory Management**: Implement policies for memory cleanup to prevent accumulation of outdated information
5. **Configuration**: Use appropriate configuration for your use case, especially for production deployments
