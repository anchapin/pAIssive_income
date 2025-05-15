import React from 'react';
import PropTypes from 'prop-types';
import { Box, Typography, Button, Paper } from '@mui/material';

/**
 * Mock implementation of the AgentUI component from @ag-ui-protocol/ag-ui
 * This is used for testing purposes when the actual package is not available
 */
export const AgentUI = ({ agent, theme, onAction }) => {
  const handleHelp = () => {
    onAction({ type: 'help', agentId: agent.id });
  };

  const handleStart = () => {
    onAction({ type: 'start', agentId: agent.id });
  };

  const styles = {
    container: {
      padding: '16px',
      borderRadius: theme?.borderRadius || '8px',
      backgroundColor: theme?.secondaryColor || '#f5f5f5',
      color: '#333',
      fontFamily: theme?.fontFamily || 'Arial, sans-serif',
    },
    header: {
      color: theme?.primaryColor || '#007bff',
      marginBottom: '8px',
      fontWeight: 'bold',
    },
    description: {
      marginBottom: '16px',
    },
    buttonContainer: {
      display: 'flex',
      gap: '8px',
      marginTop: '16px',
    },
    button: {
      backgroundColor: theme?.primaryColor || '#007bff',
      color: '#fff',
      '&:hover': {
        backgroundColor: theme?.primaryColor ? `${theme.primaryColor}dd` : '#0069d9',
      },
    },
  };

  return (
    <Paper elevation={2} sx={styles.container}>
      <Typography variant="h6" sx={styles.header}>
        {agent.name}
      </Typography>
      <Typography variant="body2" sx={styles.description}>
        {agent.description}
      </Typography>
      <Box sx={styles.buttonContainer}>
        <Button 
          variant="contained" 
          size="small" 
          sx={styles.button}
          onClick={handleHelp}
        >
          Help
        </Button>
        <Button 
          variant="contained" 
          size="small" 
          sx={styles.button}
          onClick={handleStart}
        >
          Start
        </Button>
      </Box>
    </Paper>
  );
};

AgentUI.propTypes = {
  agent: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
  }).isRequired,
  theme: PropTypes.object,
  onAction: PropTypes.func.isRequired,
};

export default AgentUI;
