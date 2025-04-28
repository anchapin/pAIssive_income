import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Box, Typography, Paper, Link as MuiLink } from '@mui/material';
import { Link } from 'react-router-dom';
import { LoginForm } from '../components/auth';

/**
 * Login page component for user authentication
 */
const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get the redirect path from location state or default to homepage
  const from = location.state?.from || '/';
  
  // Handle successful login
  const handleLoginSuccess = () => {
    // Navigate to the page the user was trying to access, or home if none
    navigate(from, { replace: true });
  };
  
  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '80vh'
    }}>
      <Paper elevation={3} sx={{ p: 4, maxWidth: 500, width: '100%' }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Log In to pAIssive Income
        </Typography>
        
        <Typography variant="body2" color="text.secondary" paragraph align="center">
          Access your dashboard and tools to generate passive income with AI
        </Typography>
        
        <LoginForm onSuccess={handleLoginSuccess} />
        
        <Box mt={3} textAlign="center">
          <Typography variant="body2">
            Don't have an account?{' '}
            <MuiLink component={Link} to="/register">
              Register here
            </MuiLink>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default LoginPage;