import React from 'react';

export const CopilotChat = ({ instructions, ...props }) => (
  <div data-testid="mock-copilot-chat" {...props}>
    <p>Mock CopilotChat Component</p>
    <p>Instructions: {instructions}</p>
  </div>
);

export const CopilotTextarea = ({ placeholder, ...props }) => (
  <textarea 
    data-testid="mock-copilot-textarea"
    placeholder={placeholder}
    {...props}
  />
);

export default {
  CopilotChat,
  CopilotTextarea
};
