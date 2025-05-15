import React, { useEffect, useState, useCallback } from 'react';
import { Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Try to import the external AgentUI package first, then fall back to local implementation
// This ensures we always have a working component even if the external package is not available
let AgentUI;
try {
  // Try to import from the external package
  AgentUI = require('@ag-ui-protocol/ag-ui').AgentUI;
  console.log('Using external @ag-ui-protocol/ag-ui package');
} catch (error) {
  // Fall back to local implementation
  AgentUI = require('./components/AgentUI').AgentUI;
  console.log('Using local AgentUI implementation');
}

// Context
import { AppProvider, useAppContext } from './context/AppContext';

// Layout
import Layout from './components/Layout/Layout';

// Components
import Notifications from './components/UI/Notifications';

// Pages
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import NicheAnalysisPage from './pages/NicheAnalysisPage';
import DeveloperPage from './pages/DeveloperPage';
import MonetizationPage from './pages/MonetizationPage';
import MarketingPage from './pages/MarketingPage';
import UserEngagementPage from './pages/UserEngagementPage';
import ApiAnalyticsPage from './pages/ApiAnalyticsPage';
import AboutPage from './pages/AboutPage';
import NotFoundPage from './pages/NotFoundPage';

// App wrapper with theme and context
function AppWithProviders() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

// App content with theme based on context
function AppContent() {
  const { darkMode } = useAppContext();
  const [agent, setAgent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch agent info from backend
  useEffect(() => {
    async function fetchAgent() {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('/api/agent');
        if (!response.ok) throw new Error('Failed to fetch agent data');
        const data = await response.json();
        setAgent(data);
      } catch (err) {
        setError(err.message || 'An error occurred');
        console.error('Error fetching agent data:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchAgent();
  }, []);

  // Handle actions from ag-ui and send to backend
  const onAction = useCallback(async (action) => {
    try {
      const response = await fetch('/api/agent/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action),
      });
      if (!response.ok) throw new Error('Failed to submit action');
      // Optionally, refetch agent data or update UI here
    } catch (err) {
      console.error('Error sending action:', err);
    }
  }, []);

  // Create a theme instance based on dark mode preference
  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#4e73df',
      },
      secondary: {
        main: '#858796',
      },
      success: {
        main: '#1cc88a',
      },
      info: {
        main: '#36b9cc',
      },
      warning: {
        main: '#f6c23e',
      },
      error: {
        main: '#e74a3b',
      },
      background: {
        default: darkMode ? '#121212' : '#f8f9fc',
        paper: darkMode ? '#1e1e1e' : '#ffffff',
      },
    },
    typography: {
      fontFamily: '"Nunito", "Helvetica", "Arial", sans-serif',
    },
  });

  // AgentUI theme configuration
  const agentTheme = {
    primaryColor: theme.palette.primary.main,
    secondaryColor: theme.palette.secondary.main,
    fontFamily: theme.typography.fontFamily,
    borderRadius: "8px",
    darkMode: darkMode,
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/niche-analysis" element={<NicheAnalysisPage />} />
          <Route path="/developer" element={<DeveloperPage />} />
          <Route path="/monetization" element={<MonetizationPage />} />
          <Route path="/marketing" element={<MarketingPage />} />
          <Route path="/user-engagement" element={<UserEngagementPage />} />
          <Route path="/api-analytics" element={<ApiAnalyticsPage />} />
          <Route path="/about" element={
            <div>
              <AboutPage />
              {agent && !loading && !error && (
                <div className="agent-ui-container" style={{ marginTop: '2rem' }}>
                  <h2>Agent UI Integration</h2>
                  <AgentUI
                    agent={agent}
                    theme={agentTheme}
                    onAction={onAction}
                  />
                </div>
              )}
              {loading && <div>Loading agent...</div>}
              {error && <div>Error loading agent: {error}</div>}
            </div>
          } />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Layout>
      <Notifications />
    </ThemeProvider>
  );
}

export default AppWithProviders;
