# mem0 Integration Points in pAIssive_income

This document identifies the key integration points for adding mem0 memory capabilities to the pAIssive_income codebase. It maps out where AI agents are defined, existing memory implementations, and potential lifecycle hooks for memory recall/write operations.

## 1. Agent Definitions

### 1.1 CrewAI Agents

The primary agent implementation in the codebase is based on CrewAI, located in:

- `agent_team/crewai_agents.py`: Contains the main CrewAI agent definitions and team implementation
- `main_crewai_agents.py`: Contains example CrewAI agent roles and workflows

Key classes:
- `CrewAIAgentTeam`: High-level interface for working with CrewAI agents, tasks, and crews
- Example agent roles: `data_gatherer`, `analyzer`, `writer`

### 1.2 ADK Agents

The codebase also includes Google's Agent Development Kit (ADK) implementations:

- `adk_demo/agents.py`: Contains ADK agent implementations
- `main_agents.py`: Contains example ADK agent implementations

Key classes:
- `DataGathererAgent`: Agent for handling data gathering requests
- `SummarizerAgent`: Agent for summarizing gathered data

### 1.3 Agent Team Service

The architecture includes an Agent Team Service design:

- `docs/architecture/services/agent-team-service.md`: Design document for the Agent Team Service
- `docs/agent-team.md`: Documentation for the Agent Team module

## 2. Existing Memory Implementations

### 2.1 SimpleMemory in ADK

The ADK agents use a simple memory implementation:

```python
# From adk_demo/agents.py and main_agents.py
class DataGathererAgent(Agent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.memory = SimpleMemory()
        self.add_skill("gather", DataGathererSkill())
```

### 2.2 CrewAI Memory Flag

CrewAI has a memory flag that can be enabled:

```python
# From docs/CrewAI_CopilotKit_Integration.md
import os
os.environ["CREWAI_MEMORY"] = "1"  # Enable memory
```

### 2.3 Example mem0 Integration

There's an example mem0 integration in:

- `examples/mem0_integration_example.py`: Example script demonstrating mem0 integration
- `examples/test_mem0_local.py`: Script for testing mem0 locally

Key class:
```python
class MemoryEnhancedAgent(MockAgent):
    def __init__(self, name: str, user_id: str):
        super().__init__(name)
        
        # Initialize mem0 memory
        if Memory is not None:
            self.memory = Memory()
        else:
            self.memory = None
            
        self.user_id = user_id
    
    def process_message(self, message: str) -> str:
        # Retrieve relevant memories
        relevant_memories = self.memory.search(
            query=message,
            user_id=self.user_id,
            limit=5
        )
        
        # Process with enhanced context
        # Store the interaction in memory
        # ...
```

## 3. Lifecycle Hooks for Memory Integration

### 3.1 CrewAI Agent Lifecycle

Potential hooks in the CrewAI agent lifecycle:

1. **Agent Initialization**: When agents are created in `CrewAIAgentTeam.add_agent()`
2. **Task Execution**: Before/after task execution in `crew.kickoff()`
3. **Agent Communication**: During agent-to-agent communication

### 3.2 ADK Agent Lifecycle

Potential hooks in the ADK agent lifecycle:

1. **Message Processing**: In the message handling methods
2. **Skill Execution**: Before/after skill execution
3. **Agent Communication**: During message sending/receiving

### 3.3 General Agent Lifecycle Hooks

Common lifecycle hooks across agent implementations:

1. **Initialization**: When an agent is created
2. **Task Assignment**: When a task is assigned to an agent
3. **Context Building**: When building context for agent operations
4. **Response Generation**: Before/after generating responses
5. **Task Completion**: When a task is completed
6. **Team Interaction**: During agent-to-agent communication

## 4. Integration Recommendations

### 4.1 CrewAI Integration

For CrewAI agents, we recommend:

1. Extend the `CrewAIAgentTeam` class to include mem0 memory:

```python
class MemoryEnhancedCrewAIAgentTeam(CrewAIAgentTeam):
    def __init__(self, llm_provider=None, user_id=None):
        super().__init__(llm_provider)
        self.memory = Memory()
        self.user_id = user_id or "default_user"
        
    def add_agent(self, role, goal, backstory):
        agent = super().add_agent(role, goal, backstory)
        # Store agent information in memory
        self.memory.add(
            f"Agent {role} has goal: {goal} and backstory: {backstory}",
            user_id=self.user_id,
            metadata={"agent_role": role}
        )
        return agent
        
    def run(self):
        # Retrieve relevant memories before running
        # Enhance context with memories
        result = super().run()
        # Store results in memory
        return result
```

2. Add memory hooks to the task execution process

### 4.2 ADK Integration

For ADK agents, we recommend:

1. Create a `MemoryEnhancedAgent` base class:

```python
from adk.agent import Agent
from adk.memory import SimpleMemory
from mem0 import Memory

class Mem0EnhancedAgent(Agent):
    def __init__(self, name, user_id):
        super().__init__(name)
        self.memory = Memory()
        self.user_id = user_id
        
    def handle_message(self, message):
        # Retrieve relevant memories
        relevant_memories = self.memory.search(
            query=message.content,
            user_id=self.user_id,
            limit=5
        )
        
        # Enhance context with memories
        enhanced_message = self._enhance_with_memories(message, relevant_memories)
        
        # Process with enhanced context
        response = super().handle_message(enhanced_message)
        
        # Store the interaction in memory
        self.memory.add(
            [
                {"role": "user", "content": message.content},
                {"role": "assistant", "content": response.content}
            ],
            user_id=self.user_id
        )
        
        return response
```

## 5. Implementation Steps

1. Add mem0 as a dependency:
   ```bash
   pip install mem0ai
   ```

2. Create memory-enhanced versions of the agent classes

3. Add memory hooks to key lifecycle points:
   - Agent initialization
   - Task/message processing
   - Response generation
   - Task completion

4. Update the agent team implementations to use memory-enhanced agents

5. Add configuration options for memory capabilities

## 6. Conclusion

The pAIssive_income codebase has multiple integration points for mem0 memory capabilities. The most promising approaches are:

1. Enhancing the CrewAI agent implementation with memory capabilities
2. Creating memory-enhanced versions of the ADK agents
3. Adding memory hooks to the agent lifecycle

By implementing these integration points, we can add persistent memory capabilities to the AI agents, making them more effective and personalized.
