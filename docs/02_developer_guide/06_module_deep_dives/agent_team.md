# Agent Team Module — Deep Dive

This document provides a detailed guide to the agent team module, including CrewAI integration and mem0 memory enhancement.

---

<!--
The content below was migrated from agent_team/README.md. For a summary, see the module directory.
-->

## Setup

1. **Install dependencies**

   Ensure you’ve installed project dependencies, including CrewAI, by running:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys**

   CrewAI relies on LLM providers (e.g., OpenAI).
   - Set your API key as an environment variable, for example:
     ```
     export OPENAI_API_KEY=your-key-here
     ```

---

## Usage

- The scaffold in `agent_team/crewai_agents.py` defines example agent roles and a simple workflow.
- To run the included workflow:

  ```bash
  python agent_team/crewai_agents.py
  ```

- You should see log output indicating the sample agents and tasks have run.

---

## Extending CrewAI Agents

- **Define new agents:** Edit or add to the `Agent` instances in `crewai_agents.py`.
- **Create tasks:** Define `Task` instances and assign them to agents.
- **Assemble your team:** Use the `Crew` class to group agents and tasks into a workflow.
- **Integration:** Import and trigger agent teams from your services, API endpoints, CLI commands, or other application modules as needed.

---

## References

- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI GitHub](https://github.com/VisionBlack/CrewAI)

---

## Testing

A minimal test scaffold is provided in `tests/test_crewai_agents.py` to verify CrewAI integration.

---

## Support

For troubleshooting CrewAI integration:
- Check [CrewAI docs](https://docs.crewai.com/)
- Ask in your project’s communication channels

---

## Memory-Enhanced Agents with mem0

The agent team module includes memory-enhanced versions of CrewAI agents using the mem0 memory layer.

### Overview

Memory-enhanced agents can remember information across conversations and sessions, making them more effective for long-running tasks and personalized interactions.

### Implementation

The memory enhancement is implemented in `agent_team/mem0_enhanced_agents.py`, which provides:

- `MemoryEnhancedCrewAIAgentTeam`: A CrewAI agent team with memory capabilities

### Usage

```python
from agent_team.mem0_enhanced_agents import MemoryEnhancedCrewAIAgentTeam

# Create a memory-enhanced agent team
team = MemoryEnhancedCrewAIAgentTeam(user_id="user123")

# Add agents with memory capabilities
researcher = team.add_agent(
    role="Researcher",
    goal="Find relevant information",
    backstory="Expert at gathering data"
)

# Run the team with memory enhancement
result = team.run()
```

### Memory Operations

Memory-enhanced agents can:

1. **Store memories**: Save important information for future reference
2. **Retrieve memories**: Access previously stored information when needed
3. **Update memories**: Modify existing memories with new information
4. **Delete memories**: Remove outdated or irrelevant memories

### Configuration

Memory-enhanced agents require:

1. **OpenAI API key**: For generating embeddings
2. **User ID**: To isolate memories by user
3. **Optional storage configuration**: To customize where memories are stored

For more details on mem0 integration, see [docs/04_security_and_compliance/05_mem0_integration.md](../../04_security_and_compliance/05_mem0_integration.md).