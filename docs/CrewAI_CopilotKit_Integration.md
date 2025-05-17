# CrewAI + CopilotKit Integration Guide

This guide provides detailed information about the integration between CrewAI and CopilotKit in the pAIssive_income project.

## Overview

The integration between CrewAI and CopilotKit enables powerful multi-agent AI features in the React frontend, including:

- **Agentic Chat**: Chat with AI copilots and call frontend tools
- **Human-in-the-Loop**: Collaborate with the AI, plan tasks, and decide actions interactively
- **Agentic/Generative UI**: Assign long-running tasks to agents and see real-time progress
- **Collaborative State**: Edit documents or data collaboratively with AI agents
- **Tool-Based Workflows**: Integrate custom tool actions into agent-driven UIs

This integration creates a seamless connection between the backend AI agent capabilities (powered by CrewAI) and the frontend user interface (powered by CopilotKit), allowing for sophisticated AI-driven applications with minimal development effort.

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

## Advanced Usage Patterns

### Custom Agent Roles

You can create custom agent roles with specific expertise areas:

```python
from agent_team.crewai_agents import CrewAIAgentTeam

# Create a specialized team for content creation
content_team = CrewAIAgentTeam(llm_provider=your_llm_provider)

# Add specialized agents
content_team.add_agent(
    role="SEO Specialist",
    goal="Optimize content for search engines",
    backstory="Expert in SEO with 10 years of experience"
)

content_team.add_agent(
    role="Content Writer",
    goal="Create engaging and informative content",
    backstory="Professional writer with expertise in technical topics"
)

content_team.add_agent(
    role="Editor",
    goal="Ensure content quality and consistency",
    backstory="Experienced editor with attention to detail"
)

# Define specialized tasks
content_team.add_task(
    description="Research keywords for the article on AI agents",
    agent="SEO Specialist"
)

content_team.add_task(
    description="Write a 1500-word article on AI agents",
    agent="Content Writer"
)

content_team.add_task(
    description="Review and edit the article",
    agent="Editor"
)

# Run the workflow
result = content_team.run()
```

### Frontend Tool Integration

You can integrate custom tools with CopilotKit to enable AI agents to perform specific actions:

```jsx
import { CopilotKit, CopilotChat, useCopilotAction } from '@copilotkit/react-ui';

// Define a custom tool
function CustomTools() {
  // Register a tool that can be called by the AI
  useCopilotAction({
    name: "generate_report",
    description: "Generate a report based on the provided data",
    parameters: [
      {
        name: "topic",
        type: "string",
        description: "The topic of the report"
      },
      {
        name: "length",
        type: "number",
        description: "The desired length of the report in words"
      }
    ],
    handler: async ({ topic, length }) => {
      // Call your backend API to generate the report
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, length })
      });

      const data = await response.json();
      return data.report;
    }
  });

  return null;
}

// Use the custom tool in your app
function App() {
  return (
    <CopilotKit>
      <CustomTools />
      <CopilotChat
        instructions="You can help users generate reports using the generate_report tool."
      />
    </CopilotKit>
  );
}
```

## Resources

- [CrewAI Documentation](https://docs.crewai.com/)
- [CopilotKit Documentation](https://docs.copilotkit.ai/)
- [CrewAI + CopilotKit Integration Guide](https://docs.copilotkit.ai/crewai-crews)
- [CrewAI GitHub Repository](https://github.com/joaomdmoura/crewAI)
- [CopilotKit GitHub Repository](https://github.com/CopilotKit/CopilotKit)
- [CopilotKit Demo Viewer](https://demo-viewer-five.vercel.app/)
- [CrewAI + CopilotKit Land (Official Site)](https://v0-crew-land.vercel.app/)

## Troubleshooting

### CrewAI Not Available

If CrewAI is not available, the `CrewAIAgentTeam` class will use a fallback implementation that provides the same interface but does not require CrewAI to be installed. This allows the application to continue functioning even when CrewAI is not available.

To install CrewAI:

```bash
pip install '.[agents]'
```

Common issues with CrewAI installation:

1. **Dependency Conflicts**: If you encounter dependency conflicts, try creating a fresh virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install '.[agents]'
   ```

2. **Missing LLM Provider**: CrewAI requires an LLM provider. Make sure you have configured one:
   ```python
   from langchain.llms import OpenAI

   llm = OpenAI(api_key="your-api-key")
   agent_team = CrewAIAgentTeam(llm_provider=llm)
   ```

3. **Memory Issues**: For complex workflows, you might need to adjust memory settings:
   ```python
   import os
   os.environ["CREWAI_MEMORY"] = "1"  # Enable memory
   ```

### CopilotKit Not Available

If CopilotKit is not available, the `CopilotChat` component will use a fallback implementation that provides a basic chat interface without the advanced features of CopilotKit. This allows the application to continue functioning even when CopilotKit is not available.

To install CopilotKit:

```bash
cd ui/react_frontend
npm install @copilotkit/react-core @copilotkit/react-ui
```

Common issues with CopilotKit integration:

1. **Version Compatibility**: Make sure all CopilotKit packages have matching versions:
   ```bash
   npm install @copilotkit/react-core@0.20.0 @copilotkit/react-ui@0.20.0 @copilotkit/react-textarea@0.20.0
   ```

2. **API Key Configuration**: CopilotKit may require API keys for certain features:
   ```jsx
   <CopilotKitProvider apiKey="your-api-key">
     {/* Your components */}
   </CopilotKitProvider>
   ```

3. **CORS Issues**: If you're connecting to a backend API, you might encounter CORS issues. Make sure your backend allows requests from your frontend domain.

### Integration Issues

1. **Communication Between Frontend and Backend**: To connect CopilotKit with CrewAI, you'll need an API endpoint:
   ```python
   # In your Flask app
   @app.route('/api/crewai', methods=['POST'])
   def crewai_endpoint():
       data = request.json
       agent_team = CrewAIAgentTeam(llm_provider=your_llm_provider)
       # Configure the team based on the request
       result = agent_team.run()
       return jsonify({"result": result})
   ```

2. **Error Handling**: Implement proper error handling on both sides:
   ```jsx
   // Frontend
   const handleCrewAIRequest = async () => {
     try {
       const response = await fetch('/api/crewai', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ query: userQuery })
       });

       if (!response.ok) {
         throw new Error('Failed to connect to CrewAI');
       }

       const data = await response.json();
       setResult(data.result);
     } catch (error) {
       console.error('Error:', error);
       setError('Failed to process your request. Please try again.');
     }
   };
   ```
