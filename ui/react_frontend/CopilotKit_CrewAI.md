# CopilotKit + CrewAI Integration Guide

CopilotKit + CrewAI lets you bring powerful multi-agent AI features into your React application. This enables:

- **Agentic Chat**: Chat with AI copilots and call frontend tools
- **Human-in-the-Loop**: Collaborate with the AI, plan tasks, and decide actions interactively
- **Agentic/Generative UI**: Assign long-running tasks to agents and see real-time progress
- **Collaborative State**: Edit documents or data collaboratively with AI agents
- **Tool-Based Workflows**: Integrate custom tool actions into agent-driven UIs

## Why Use CopilotKit + CrewAI?

The combination of CopilotKit and CrewAI provides several advantages for building AI-powered applications:

1. **Simplified Development**: Reduce the complexity of building AI-powered UIs with pre-built components
2. **Multi-Agent Orchestration**: Leverage CrewAI's agent orchestration capabilities for complex workflows
3. **Seamless Integration**: Connect frontend UI components directly to backend AI agents
4. **Extensibility**: Easily extend with custom tools, agents, and UI components
5. **Production-Ready**: Built for real-world applications with error handling and fallbacks

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

## Customization Options

### Styling the Chat Interface

You can customize the appearance of the CopilotChat component to match your application's design:

```jsx
import React from 'react';
import { CopilotKitProvider } from '@copilotkit/react-core';
import { CopilotChat } from '@copilotkit/react-ui';
import './CustomChatStyles.css'; // Import custom CSS

const CustomStyledCopilotChat = () => (
  <CopilotKitProvider>
    <div className="custom-chat-container">
      <h2>Custom Styled AI Assistant</h2>
      <CopilotChat
        instructions="You are a specialized assistant for our application. Help users with their tasks and answer their questions."
        className="custom-chat"
        messageClassName="custom-message"
        inputClassName="custom-input"
        buttonClassName="custom-button"
      />
    </div>
  </CopilotKitProvider>
);

export default CustomStyledCopilotChat;
```

Example CSS (`CustomChatStyles.css`):

```css
.custom-chat-container {
  max-width: 600px;
  margin: 2rem auto;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 24px;
  background-color: #f8f9fa;
}

.custom-chat {
  border-radius: 8px;
  background-color: white;
}

.custom-message {
  padding: 12px;
  margin: 8px 0;
  border-radius: 8px;
}

.custom-input {
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #e0e0e0;
}

.custom-button {
  background-color: #4a6cf7;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
}
```

### Connecting to Backend Services

To connect your CopilotKit chat to backend services:

```jsx
import React from 'react';
import { CopilotKitProvider } from '@copilotkit/react-core';
import { CopilotChat } from '@copilotkit/react-ui';

const BackendConnectedChat = () => (
  <CopilotKitProvider
    apiKey="your-api-key"
    baseURL="/api/copilot" // Your backend API endpoint
  >
    <div style={{ maxWidth: 480, margin: "2rem auto" }}>
      <h2>AI Assistant with Backend Connection</h2>
      <CopilotChat
        instructions="You can help users by connecting to our backend services."
        onMessageSubmit={async (message) => {
          // Log messages to your backend
          await fetch('/api/chat-logs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
          });
        }}
      />
    </div>
  </CopilotKitProvider>
);

export default BackendConnectedChat;
```

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

## Best Practices

1. **Start Simple**: Begin with the basic CopilotChat component before adding customizations
2. **Provide Clear Instructions**: Give specific instructions to guide the AI's behavior
3. **Use Fallbacks**: Implement fallbacks for when services are unavailable
4. **Test Thoroughly**: Test with different inputs and edge cases
5. **Monitor Performance**: Keep an eye on response times and quality
6. **Iterate Based on Feedback**: Collect user feedback and improve the experience

---

**Note:**
- CrewAI + CopilotKit is best for apps that want agent-driven chat, collaboration, or tool-based automation in the frontend.
- Consider team needs before integrating—most features are opt-in and composable.

---

© 2025 CopilotKit + CrewAI. All rights reserved.