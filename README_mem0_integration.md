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

## Documentation

For more detailed information about mem0, refer to the following documentation:

- `docs/README_mem0.md`: Overview of mem0 investigation
- `docs/mem0_investigation.md`: Comprehensive overview of mem0
- `docs/mem0_integration_options.md`: Analysis of integration approaches
- `docs/mem0_core_apis.md`: Documentation of mem0's core APIs

## Troubleshooting

If you encounter issues with mem0:

1. Ensure the OpenAI API key is set correctly
2. Check that all dependencies are installed
3. Verify that the vector database (Qdrant) is accessible
4. Check the logs for any error messages

## References

- [mem0 Official Website](https://mem0.ai)
- [mem0 GitHub Repository](https://github.com/mem0ai/mem0)
