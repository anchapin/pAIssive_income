# CopilotKit + CrewAI Integration

This document provides an overview of the CopilotKit and CrewAI integration added to the project.

## Overview

CopilotKit + CrewAI integration enables powerful multi-agent AI features in the React frontend, including:

- **Agentic Chat**: Chat with AI copilots and call frontend tools
- **Human-in-the-Loop**: Collaborate with the AI, plan tasks, and decide actions interactively
- **Agentic/Generative UI**: Assign long-running tasks to agents and see real-time progress
- **Collaborative State**: Edit documents or data collaboratively with AI agents
- **Tool-Based Workflows**: Integrate custom tool actions into agent-driven UIs

## Implementation Details

The integration has been added to the React frontend in the `ui/react_frontend` directory:

- Added CopilotKit dependencies to `package.json`
- Created a `CopilotChat` component for basic chat functionality
- Added unit tests for the CopilotChat component
- Updated documentation with usage instructions

## Usage

To use the CopilotKit + CrewAI integration in your application:

1. Import the CopilotChat component:
   ```jsx
   import CopilotChatDemo from './components/CopilotChat';
   ```

2. Add the component to your application:
   ```jsx
   <CopilotChatDemo />
   ```

## Resources

- [CopilotKit + CrewAI Docs](https://docs.copilotkit.ai/crewai-crews)
- [Main Integration Guide](./docs/CrewAI_CopilotKit_Integration.md)
- [Frontend Implementation Guide](./ui/react_frontend/CopilotKit_CrewAI.md)
- [Advanced Usage Examples](./docs/examples/CrewAI_CopilotKit_Advanced_Examples.md)
