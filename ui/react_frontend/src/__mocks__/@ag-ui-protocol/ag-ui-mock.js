/**
 * Mock implementation of @ag-ui-protocol/ag-ui
 * 
 * This file provides a mock implementation of the @ag-ui-protocol/ag-ui package
 * for testing and development purposes.
 */

import React from 'react';

/**
 * AgentUI component - mock implementation
 * 
 * @param {Object} props - Component props
 * @param {Object} props.agent - Agent data
 * @param {Object} props.theme - Theme configuration
 * @param {Function} props.onAction - Action handler function
 * @returns {JSX.Element} AgentUI component
 */
export const AgentUI = ({ agent = {}, theme = {}, onAction = () => {} }) => {
  // Create a default agent object if none is provided
  const safeAgent = {
    id: agent?.id || 1,
    name: agent?.name || 'Agent',
    description: agent?.description || 'No description available'
  };

  // Create a default theme object if none is provided
  const safeTheme = {
    darkMode: theme?.darkMode || false,
    primaryColor: theme?.primaryColor || '#007bff',
    secondaryColor: theme?.secondaryColor || '#f5f5f5',
    fontFamily: theme?.fontFamily || 'Arial, sans-serif',
    borderRadius: theme?.borderRadius || '4px'
  };

  // Safe action handler
  const handleAction = (actionType) => {
    try {
      onAction({
        type: actionType,
        agentId: safeAgent.id,
        payload: {}
      });
    } catch (error) {
      console.error(`Error handling ${actionType} action:`, error);
    }
  };

  return (
    <div
      className="agent-ui-component mock"
      data-testid="agent-ui-component-mock"
      style={{
        backgroundColor: safeTheme.darkMode ? '#1e1e1e' : '#ffffff',
        color: safeTheme.darkMode ? '#ffffff' : '#000000',
        fontFamily: safeTheme.fontFamily,
        padding: '1rem',
        borderRadius: safeTheme.borderRadius,
        border: `1px solid ${safeTheme.primaryColor}`,
      }}
    >
      <div style={{ marginBottom: '0.5rem', fontSize: '0.8rem', color: '#888' }}>
        Mock Implementation
      </div>
      <h3 style={{ color: safeTheme.primaryColor }}>
        {safeAgent.name}
      </h3>

      <div className="agent-description" data-testid="agent-description">
        {safeAgent.description}
      </div>

      <div className="agent-actions" style={{ marginTop: '1rem' }}>
        <button
          data-testid="help-button"
          onClick={() => handleAction('HELP')}
          style={{
            backgroundColor: safeTheme.primaryColor,
            color: '#ffffff',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            cursor: 'pointer',
            marginRight: '0.5rem',
          }}
        >
          Help
        </button>

        <button
          data-testid="start-button"
          onClick={() => handleAction('START')}
          style={{
            backgroundColor: safeTheme.secondaryColor,
            color: '#000000',
            border: `1px solid ${safeTheme.primaryColor}`,
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Start
        </button>
      </div>
    </div>
  );
};

// Also export as default for compatibility
export default { AgentUI };
