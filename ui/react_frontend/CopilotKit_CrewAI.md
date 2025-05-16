# CopilotKit + CrewAI Integration Guide

CopilotKit + CrewAI lets you bring powerful multi-agent AI features into your React application. This enables:

- **Agentic Chat**: Chat with AI copilots and call frontend tools
- **Human-in-the-Loop**: Collaborate with the AI, plan tasks, and decide actions interactively
- **Agentic/Generative UI**: Assign long-running tasks to agents and see real-time progress
- **Collaborative State**: Edit documents or data collaboratively with AI agents
- **Tool-Based Workflows**: Integrate custom tool actions into agent-driven UIs

## Implementation Details

### Dependencies

The following dependencies have been added to the React frontend:

```json
{
  "dependencies": {
    "@copilotkit/react-core": "^0.20.0",
    "@copilotkit/react-textarea": "^0.20.0",
    "@copilotkit/react-ui": "^0.20.0",
    "crewai-kit": "^0.1.0"
  }
}
```

### Components

#### CopilotChat

The `CopilotChat` component provides a chat interface for interacting with AI agents:

```jsx
import React from 'react';
import { CopilotKit, CopilotChat } from '@copilotkit/react-ui';
import { CrewAIProvider } from 'crewai-kit';

const CopilotChatDemo = () => {
  return (
    <CopilotKit>
      <CrewAIProvider>
        <div className="copilot-chat-container">
          <CopilotChat />
        </div>
      </CrewAIProvider>
    </CopilotKit>
  );
};

export default CopilotChatDemo;
```

## Quick Start

1. **Initialize CopilotKit + CrewAI**

Open a terminal in this directory and run:

```sh
npx copilotkit@latest init -m CrewAI
```

This sets up CopilotKit and CrewAI in your React app.

2. **Explore Examples and Docs**

- [CrewAI Quickstart Guide](https://docs.copilotkit.ai/crewai-crews)
- [CrewAI Flows Guide](https://docs.copilotkit.ai/crewai-flows)
- [CopilotKit Demo Viewer](https://demo-viewer-five.vercel.app/)
- [CrewAI + CopilotKit Land (Official Site)](https://v0-crew-land.vercel.app/)

3. **Build Agentic Features**

Integrate CopilotKit's React components and APIs to add agent chat, collaborative UIs, or custom agent flows in your app. See the docs and demo viewer for usage patterns.

## Testing

Unit tests have been added for the CopilotChat component to ensure proper functionality:

```jsx
import { render, screen } from '@testing-library/react';
import CopilotChatDemo from './CopilotChat';

test('renders CopilotChat component', () => {
  render(<CopilotChatDemo />);
  const chatElement = screen.getByTestId('copilot-chat');
  expect(chatElement).toBeInTheDocument();
});
```

---

**Note:**
- CrewAI + CopilotKit is best for apps that want agent-driven chat, collaboration, or tool-based automation in the frontend.
- Consider team needs before integrating—most features are opt-in and composable.

---

© 2025 CopilotKit + CrewAI. All rights reserved.