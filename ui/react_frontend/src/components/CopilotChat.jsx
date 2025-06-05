import React from "react";
import { CopilotKitProvider } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "./CopilotChat.styles.css";

/**
 * Minimal CopilotKit + CrewAI Chat Demo
 * This component sets up a basic CopilotChat agent UI.
 * Customize or expand as needed.
 */
const CopilotChatDemo = () => (
  <CopilotKitProvider data-testid="mock-provider">
    <div className="copilot-chat-container" data-testid="mock-chat">
      <h2>CopilotKit + CrewAI Chat</h2>
      <div data-testid="chat-interface">
        <CopilotChat
          instructions="You are a helpful project assistant. Answer user questions, brainstorm ideas, and assist with task planning."
        />
      </div>
      <div data-testid="chat-instructions">
        <p>Instructions: You are a helpful project assistant. Answer user questions, brainstorm ideas, and assist with task planning.</p>
      </div>
    </div>
  </CopilotKitProvider>
);

export default CopilotChatDemo;