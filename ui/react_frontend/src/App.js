import React, { useCallback } from 'react';
import { AgentUI } from '@ag-ui-protocol/ag-ui';

// Example agent configuration
const agent = {
  id: "demo-agent",
  name: "Demo Agent",
  avatarUrl: "https://avatars.githubusercontent.com/u/1234567?v=4",
  description: "This is a sample agent powered by ag-ui.",
  // ...other agent properties as supported by ag-ui
};

// Example theme configuration
const theme = {
  primaryColor: "#007bff",
  secondaryColor: "#f5f5f5",
  fontFamily: "Roboto, Arial, sans-serif",
  borderRadius: "8px",
  darkMode: false,
  // ...other theme settings
};

// Example action handler
function handleAgentAction(action) {
  // Replace with real logic as needed
  alert(`Agent action triggered: ${JSON.stringify(action)}`);
}

function App() {
  // Optionally use useCallback if you want stable handler references
  const onAction = useCallback(handleAgentAction, []);

  return (
    <div className="App">
      {/* Enhanced ag-ui integration */}
      <AgentUI
        agent={agent}
        theme={theme}
        onAction={onAction}
        // Add other props as needed, e.g. session, messages, etc.
      />
      {/* Your existing code here */}
    </div>
  );
}

export default App;
import { Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

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
          <Route path="/about" element={<AboutPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Layout>
      <Notifications />
    </ThemeProvider>
  );
}

export default AppWithProviders;
