# CrewAI + CopilotKit Integration Guide

This guide provides detailed information about the integration between CrewAI and CopilotKit in the pAIssive_income project.

## Overview

The integration between CrewAI and CopilotKit enables powerful multi-agent AI features in the React frontend, including:

- **Agentic Chat**: Chat with AI copilots and call frontend tools
- **Human-in-the-Loop**: Collaborate with the AI, plan tasks, and decide actions interactively
- **Agentic/Generative UI**: Assign long-running tasks to agents and see real-time progress
- **Collaborative State**: Edit documents or data collaboratively with AI agents
- **Tool-Based Workflows**: Integrate custom tool actions into agent-driven UIs

## Implementation Details

### Backend (CrewAI)

The CrewAI integration is implemented in the `agent_team/crewai_agents.py` module. This module provides the `CrewAIAgentTeam` class, which is responsible for creating and managing CrewAI agents, tasks, and crews.

Key features of the `CrewAIAgentTeam` class:

- **Agent Creation**: Create CrewAI agents with specific roles, goals, and backstories
- **Task Assignment**: Assign tasks to agents
- **Workflow Execution**: Execute workflows using CrewAI's crew system
- **Error Handling**: Gracefully handle errors and provide fallbacks when CrewAI is not available

### Frontend (CopilotKit)

The CopilotKit integration is implemented in the `ui/react_frontend/src/components/CopilotChat.jsx` component. This component provides a chat interface for interacting with AI agents.

Key features of the CopilotKit integration:

- **Chat Interface**: Provides a user-friendly chat interface for interacting with AI agents
- **Agent Instructions**: Configurable instructions for the AI agents
- **Styling**: Customizable styling to match the application's design
- **Error Handling**: Gracefully handles errors and provides fallbacks when CopilotKit is not available

## Usage

### Backend (CrewAI)

To use the CrewAI integration in your Python code:

```python
from agent_team.crewai_agents import CrewAIAgentTeam

# Create a CrewAIAgentTeam instance
agent_team = CrewAIAgentTeam(llm_provider=your_llm_provider)

# Add agents to the team
agent_team.add_agent(
    role="Researcher",
    goal="Research the topic",
    backstory="Expert researcher"
)

agent_team.add_agent(
    role="Writer",
    goal="Write the report",
    backstory="Expert writer"
)

# Add tasks to the team
agent_team.add_task(
    description="Research the topic",
    agent="Researcher"
)

agent_team.add_task(
    description="Write the report",
    agent="Writer"
)

# Run the workflow
result = agent_team.run()
```

### Frontend (CopilotKit)

To use the CopilotKit integration in your React code:

```jsx
import React from 'react';
import CopilotChatDemo from './components/CopilotChat';

function App() {
  return (
    <div className="App">
      <CopilotChatDemo />
    </div>
  );
}

export default App;
```

## Testing

### Backend (CrewAI)

The CrewAI integration is tested in the `tests/test_crewai_agents.py` and `tests/test_crewai_integration.py` modules. These tests verify that the CrewAI integration works correctly, even when CrewAI is not available.

To run the CrewAI tests:

```bash
python -m pytest tests/test_crewai_agents.py tests/test_crewai_integration.py
```

### Frontend (CopilotKit)

The CopilotKit integration is tested in the `ui/react_frontend/src/components/CopilotChat.test.jsx` and `ui/react_frontend/src/components/CopilotKitIntegration.test.jsx` files. These tests verify that the CopilotKit integration works correctly, even when CopilotKit is not available.

To run the CopilotKit tests:

```bash
cd ui/react_frontend
npm test
```

## Resources

- [CrewAI Documentation](https://docs.crewai.com/)
- [CopilotKit Documentation](https://docs.copilotkit.ai/)
- [CrewAI + CopilotKit Integration Guide](https://docs.copilotkit.ai/crewai-crews)
- [CrewAI GitHub Repository](https://github.com/joaomdmoura/crewAI)
- [CopilotKit GitHub Repository](https://github.com/CopilotKit/CopilotKit)

## Troubleshooting

### CrewAI Not Available

If CrewAI is not available, the `CrewAIAgentTeam` class will use a fallback implementation that provides the same interface but does not require CrewAI to be installed. This allows the application to continue functioning even when CrewAI is not available.

To install CrewAI:

```bash
pip install '.[agents]'
```

### CopilotKit Not Available

If CopilotKit is not available, the `CopilotChat` component will use a fallback implementation that provides a basic chat interface without the advanced features of CopilotKit. This allows the application to continue functioning even when CopilotKit is not available.

To install CopilotKit:

```bash
cd ui/react_frontend
npm install @copilotkit/react-core @copilotkit/react-ui
```
