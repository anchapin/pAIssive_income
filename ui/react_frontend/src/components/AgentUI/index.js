// Local implementation of AgentUI component
import React from 'react';

/**
 * AgentUI component - local implementation to replace the external dependency
 * 
 * @param {Object} props - Component props
 * @param {Object} props.agent - Agent data
 * @param {Object} props.theme - Theme configuration
 * @param {Function} props.onAction - Action handler function
 * @returns {JSX.Element} AgentUI component
 */
export const AgentUI = ({ agent, theme, onAction }) => {
  return (
    <div 
      className="agent-ui-component"
      style={{
        backgroundColor: theme?.darkMode ? '#1e1e1e' : '#ffffff',
        color: theme?.darkMode ? '#ffffff' : '#000000',
        fontFamily: theme?.fontFamily || 'Arial, sans-serif',
        padding: '1rem',
        borderRadius: theme?.borderRadius || '4px',
        border: `1px solid ${theme?.primaryColor || '#007bff'}`,
      }}
    >
      <h3 style={{ color: theme?.primaryColor || '#007bff' }}>
        {agent?.name || 'Agent'}
      </h3>
      
      <div className="agent-description">
        {agent?.description || 'No description available'}
      </div>
      
      <div className="agent-actions" style={{ marginTop: '1rem' }}>
        <button
          onClick={() => onAction?.({ type: 'HELP', payload: {} })}
          style={{
            backgroundColor: theme?.primaryColor || '#007bff',
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
          onClick={() => onAction?.({ type: 'START', payload: {} })}
          style={{
            backgroundColor: theme?.secondaryColor || '#f5f5f5',
            color: '#000000',
            border: `1px solid ${theme?.primaryColor || '#007bff'}`,
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
