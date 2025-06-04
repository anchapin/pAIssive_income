import React, { useState } from 'react';

/**
 * Local implementation of the AgentUI component that mimics the interface
 * of the @ag-ui-protocol/ag-ui package. This serves as a fallback when
 * the external package is not available.
 */
export const AgentUI = ({ agent, theme, onAction }) => {
  const [expanded, setExpanded] = useState(false);
  const [message, setMessage] = useState('');

  // Default theme values if not provided
  const defaultTheme = {
    primaryColor: '#4e73df',
    secondaryColor: '#858796',
    fontFamily: '"Nunito", "Helvetica", "Arial", sans-serif',
    borderRadius: '8px',
    darkMode: false,
  };

  // Merge provided theme with defaults
  const mergedTheme = { ...defaultTheme, ...theme };

  // Generate styles based on theme
  const styles = {
    container: {
      fontFamily: mergedTheme.fontFamily,
      backgroundColor: mergedTheme.darkMode ? '#1e1e1e' : '#ffffff',
      color: mergedTheme.darkMode ? '#e0e0e0' : '#333333',
      border: `1px solid ${mergedTheme.darkMode ? '#444' : '#ddd'}`,
      borderRadius: mergedTheme.borderRadius,
      padding: '1rem',
      maxWidth: '600px',
      boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '1rem',
      borderBottom: `1px solid ${mergedTheme.darkMode ? '#444' : '#eee'}`,
      paddingBottom: '0.5rem',
    },
    title: {
      margin: 0,
      color: mergedTheme.primaryColor,
      fontSize: '1.2rem',
      fontWeight: 'bold',
    },
    expandButton: {
      background: 'none',
      border: 'none',
      color: mergedTheme.secondaryColor,
      cursor: 'pointer',
      fontSize: '1.2rem',
    },
    agentInfo: {
      marginBottom: '1rem',
    },
    infoItem: {
      margin: '0.5rem 0',
    },
    label: {
      fontWeight: 'bold',
      marginRight: '0.5rem',
    },
    actionButtons: {
      display: 'flex',
      gap: '0.5rem',
      marginBottom: '1rem',
    },
    button: {
      backgroundColor: mergedTheme.primaryColor,
      color: '#fff',
      border: 'none',
      borderRadius: '4px',
      padding: '0.5rem 1rem',
      cursor: 'pointer',
      fontFamily: mergedTheme.fontFamily,
      transition: 'background-color 0.2s',
    },
    secondaryButton: {
      backgroundColor: mergedTheme.secondaryColor,
      color: '#fff',
      border: 'none',
      borderRadius: '4px',
      padding: '0.5rem 1rem',
      cursor: 'pointer',
      fontFamily: mergedTheme.fontFamily,
      transition: 'background-color 0.2s',
    },
    messageInput: {
      width: '100%',
      padding: '0.5rem',
      borderRadius: '4px',
      border: `1px solid ${mergedTheme.darkMode ? '#444' : '#ddd'}`,
      backgroundColor: mergedTheme.darkMode ? '#333' : '#fff',
      color: mergedTheme.darkMode ? '#e0e0e0' : '#333',
      marginBottom: '0.5rem',
      fontFamily: mergedTheme.fontFamily,
    },
    footer: {
      fontSize: '0.8rem',
      color: mergedTheme.secondaryColor,
      textAlign: 'center',
      marginTop: '1rem',
      borderTop: `1px solid ${mergedTheme.darkMode ? '#444' : '#eee'}`,
      paddingTop: '0.5rem',
    },
  };

  // Handle button actions
  const handleAction = (actionType) => {
    if (onAction) {
      onAction({
        type: actionType,
        agentId: agent?.id,
        timestamp: new Date().toISOString(),
      });
    }
  };

  // Handle message submission
  const handleSubmitMessage = () => {
    if (message.trim() && onAction) {
      onAction({
        type: 'MESSAGE',
        agentId: agent?.id,
        content: message,
        timestamp: new Date().toISOString(),
      });
      setMessage('');
    }
  };

  return (
    <div style={styles.container} data-testid="agent-ui-component">
      <div style={styles.header}>
        <h3 style={styles.title}>Agent Interface</h3>
        <button
          style={styles.expandButton}
          onClick={() => setExpanded(!expanded)}
          aria-label={expanded ? "Collapse" : "Expand"}
        >
          {expanded ? '▲' : '▼'}
        </button>
      </div>

      {expanded && (
        <div style={styles.agentInfo}>
          <p style={styles.infoItem}>
            <span style={styles.label}>ID:</span>
            {agent?.id || 'N/A'}
          </p>
          <p style={styles.infoItem}>
            <span style={styles.label}>Name:</span>
            {agent?.name || 'Unknown Agent'}
          </p>
          <p style={styles.infoItem}>
            <span style={styles.label}>Status:</span>
            {agent?.status || 'Unknown'}
          </p>
          <p style={styles.infoItem}>
            <span style={styles.label}>Type:</span>
            {agent?.type || 'Standard'}
          </p>
          <p style={styles.infoItem}>
            <span style={styles.label}>Created:</span>
            {agent?.createdAt ? new Date(agent.createdAt).toLocaleString() : 'Unknown'}
          </p>
        </div>
      )}

      <div style={styles.actionButtons}>
        <button
          style={styles.button}
          onClick={() => handleAction('START')}
          disabled={agent?.status === 'running'}
        >
          Start
        </button>
        <button
          style={styles.button}
          onClick={() => handleAction('STOP')}
          disabled={agent?.status !== 'running'}
        >
          Stop
        </button>
        <button
          style={styles.secondaryButton}
          onClick={() => handleAction('HELP')}
        >
          Help
        </button>
      </div>

      <div>
        <textarea
          style={styles.messageInput}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Send a message to the agent..."
          rows={3}
        />
        <button
          style={styles.button}
          onClick={handleSubmitMessage}
          disabled={!message.trim()}
        >
          Send Message
        </button>
      </div>

      <div style={styles.footer}>
        <p>Local AgentUI Implementation v1.0</p>
      </div>
    </div>
  );
};

export default AgentUI;
