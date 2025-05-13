import React from "react";
import { CopilotKitProvider } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";

/**
 * Minimal CopilotKit + CrewAI Chat Demo
 * This component sets up a basic CopilotChat agent UI.
 * Customize or expand as needed.
 */
const CopilotChatDemo = () => (
  <CopilotKitProvider>
    <div style={{ maxWidth: 480, margin: "2rem auto", border: "1px solid #ccc", borderRadius: 8, padding: 24 }}>
      <h2>CopilotKit + CrewAI Chat</h2>
      <CopilotChat
        instructions="You are a helpful project assistant. Answer user questions, brainstorm ideas, and assist with task planning."
      />
    </div>
  </CopilotKitProvider>
);

export default CopilotChatDemo;