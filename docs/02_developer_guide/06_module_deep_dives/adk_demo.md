# ADK Demo Module — Deep Dive

This document provides a detailed guide to the ADK (Agent Development Kit) demo module, including the mem0 memory enhancement.

---

## Overview

The ADK demo module showcases the implementation of AI agents using the Agent Development Kit framework. It includes examples of different agent types and demonstrates how to use them in various scenarios.

## Setup

1. **Install dependencies**

   Ensure you've installed project dependencies, including ADK, by running:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys**

   ADK relies on LLM providers (e.g., OpenAI).
   - Set your API key as an environment variable, for example:
     ```
     export OPENAI_API_KEY=your-key-here
     ```

---

## Usage

- The module in `adk_demo/` defines example agent implementations.
- To run the included examples:

  ```bash
  python adk_demo/example_agent.py
  ```

- You should see log output indicating the sample agents have run.

---

## Agent Types

The ADK demo module includes several agent types:

1. **Base Agent**: A foundational agent implementation
2. **Data Gatherer Agent**: Specialized for collecting and processing data
3. **Summarizer Agent**: Specialized for summarizing information
4. **Memory-Enhanced Agents**: Agents with persistent memory capabilities

---

## Memory-Enhanced Agents with mem0

The ADK demo module includes memory-enhanced versions of ADK agents using the mem0 memory layer.

### Overview

Memory-enhanced agents can remember information across conversations and sessions, making them more effective for long-running tasks and personalized interactions.

### Implementation

The memory enhancement is implemented in `adk_demo/mem0_enhanced_adk_agents.py`, which provides:

- `MemoryEnhancedAgent`: Base class for memory-enhanced ADK agents
- `MemoryEnhancedDataGathererAgent`: Data gatherer agent with memory capabilities
- `MemoryEnhancedSummarizerAgent`: Summarizer agent with memory capabilities

### Usage

```python
from adk_demo.mem0_enhanced_adk_agents import MemoryEnhancedDataGathererAgent

# Create a memory-enhanced agent
agent = MemoryEnhancedDataGathererAgent(name="DataGatherer", user_id="user123")

# Process a message with memory enhancement
response = agent.handle_message("What data do we have on renewable energy?")

# The agent will remember this interaction for future reference
```

### Memory Operations

Memory-enhanced agents can:

1. **Store memories**: Save important information for future reference
2. **Retrieve memories**: Access previously stored information when needed
3. **Update memories**: Modify existing memories with new information
4. **Delete memories**: Remove outdated or irrelevant memories

### Memory Integration Points

Memory is integrated at several points in the agent lifecycle:

1. **Message Processing**: When handling incoming messages
2. **Skill Execution**: When executing agent skills
3. **Response Generation**: When generating responses to users

### Configuration

Memory-enhanced agents require:

1. **OpenAI API key**: For generating embeddings
2. **User ID**: To isolate memories by user
3. **Optional storage configuration**: To customize where memories are stored

For more details on mem0 integration, see [docs/04_security_and_compliance/05_mem0_integration.md](../../04_security_and_compliance/05_mem0_integration.md).

---

## Extending ADK Agents

- **Define new agents:** Create new agent classes by extending the base agent classes.
- **Add skills:** Implement new skills for agents to use.
- **Customize behavior:** Override methods to customize agent behavior.
- **Integration:** Import and use agents from your services, API endpoints, CLI commands, or other application modules as needed.

---

## Testing

Tests for ADK agents are provided in the `tests/` directory to verify functionality.

---

## References

- [ADK Documentation](https://docs.example.com/adk) (placeholder)
- [mem0 Documentation](https://mem0.ai)

---

## Support

For troubleshooting ADK integration:
- Check the ADK documentation
- Ask in your project's communication channels
