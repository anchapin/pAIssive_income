# mem0 Integration Guide

This guide provides practical instructions for integrating [mem0](https://mem0.ai), a memory layer for AI agents, into the pAIssive_income project.

## Overview

mem0 enables AI agents to remember user preferences, past interactions, and important information across conversations, providing persistent, contextual memory capabilities.

## Installation

mem0 and its dependencies are included in the main `requirements.txt`. To install:

```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or with pip
pip install -r requirements.txt
```

### Required Dependencies

- `mem0ai>=0.1.100`
- `qdrant-client>=1.9.1`
- `openai>=1.33.0`
- `pytz>=2024.1`

## Environment Variables

Set your OpenAI API key for mem0 to function:

```bash
# Linux/macOS
export OPENAI_API_KEY='your-api-key'
# Windows (PowerShell)
$env:OPENAI_API_KEY='your-api-key'
# Windows (CMD)
set OPENAI_API_KEY=your-api-key
```

## Basic Usage Example

```python
from mem0 import Memory

memory = Memory()
memory.add("User prefers dark mode", user_id="user123")
results = memory.search("What are the user's preferences?", user_id="user123")
for result in results.get("results", []):
    print(result)
```

## Integration with Agents

- `agent_team/mem0_enhanced_agents.py`: Memory-enhanced CrewAI agents
- `adk_demo/mem0_enhanced_adk_agents.py`: Memory-enhanced ADK agents
- `examples/mem0_integration_example.py`: Example script

## Docker Support

mem0 and dependencies are included in the Dockerfile. Pass your API key as an environment variable (see `docker-compose.yml`).

## Testing

To test mem0 integration:

```bash
python test_mem0.py
```

## Troubleshooting

- Ensure your OpenAI API key is set
- All dependencies installed
- Qdrant (vector database) is accessible
- Check logs for errors

## References

- [mem0 Official Website](https://mem0.ai)
- [mem0 GitHub Repository](https://github.com/mem0ai/mem0)

## Further Reading

- [mem0 Investigation](../README_mem0.md)
- [mem0 Core APIs](../mem0_core_apis.md)
- [mem0 Integration Options](../mem0_integration_options.md)