import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Context
import { AppProvider, useAppContext } from './context/AppContext';

// Layout
import Layout from './components/Layout/Layout';

// Components
import Notifications from './components/UI/Notifications';
import { ProtectedRoute } from './components/auth';

// Pages
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import NicheAnalysisPage from './pages/NicheAnalysisPage';
import DeveloperPage from './pages/DeveloperPage';
import MonetizationPage from './pages/MonetizationPage';
import MarketingPage from './pages/MarketingPage';
import UserEngagementPage from './pages/UserEngagementPage';
import AboutPage from './pages/AboutPage';
import NotFoundPage from './pages/NotFoundPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';

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
  const { darkMode, isAuthenticated } = useAppContext();

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
          {/* Public routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/about" element={<AboutPage />} />
          
          {/* Auth routes - redirect to dashboard if already logged in */}
          <Route 
            path="/login" 
            element={
              isAuthenticated ? 
                <Navigate to="/dashboard" replace /> : 
                <LoginPage />
            } 
          />
          <Route 
            path="/register" 
            element={
              isAuthenticated ? 
                <Navigate to="/dashboard" replace /> : 
                <RegisterPage />
            } 
          />
          
          {/* Protected routes - require authentication */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } />
          
          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } />
          
          <Route path="/niche-analysis" element={
            <ProtectedRoute requiredPermission="niche:view">
              <NicheAnalysisPage />
            </ProtectedRoute>
          } />
          
          <Route path="/developer" element={
            <ProtectedRoute requiredPermission="solution:view">
              <DeveloperPage />
            </ProtectedRoute>
          } />
          
          <Route path="/monetization" element={
            <ProtectedRoute requiredPermission="monetization:view">
              <MonetizationPage />
            </ProtectedRoute>
          } />
          
          <Route path="/marketing" element={
            <ProtectedRoute requiredPermission="marketing:view">
              <MarketingPage />
            </ProtectedRoute>
          } />
          
          <Route path="/user-engagement" element={
            <ProtectedRoute requiredPermission={['admin', 'creator']}>
              <UserEngagementPage />
            </ProtectedRoute>
          } />
          
          {/* Catch all route */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Layout>
      <Notifications />
    </ThemeProvider>
  );
}

export default AppWithProviders;