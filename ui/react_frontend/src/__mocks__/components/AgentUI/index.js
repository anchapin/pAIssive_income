// Mock for local AgentUI component
import React from 'react';

export const AgentUI = ({ agent, theme, onAction }) => {
  return (
    <div data-testid="mock-agent-ui" className="mock-agent-ui">
      <div>Mock AgentUI Component</div>
      <div>Agent: {agent ? JSON.stringify(agent) : 'No agent data'}</div>
      <button 
        onClick={() => onAction?.({ type: 'TEST_ACTION', payload: { test: true } })}
        data-testid="mock-action-button"
      >
        Trigger Action
      </button>
    </div>
  );
};
