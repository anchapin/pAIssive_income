import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Paper, Link as MuiLink } from '@mui/material';
import { Link } from 'react-router-dom';
import { RegisterForm } from '../components/auth';

/**
 * Registration page component for new user signups
 */
const RegisterPage = () => {
  const navigate = useNavigate();

  // Handle successful registration
  const handleRegisterSuccess = () => {
    // Navigate to the dashboard after successful registration
    navigate('/dashboard', { replace: true });
  };

  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '80vh'
    }}>
      <Paper elevation={3} sx={{ p: 4, maxWidth: 600, width: '100%' }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Create Your Account
        </Typography>

        <Typography variant="body2" color="text.secondary" paragraph align="center">
          Join pAIssive Income and start creating AI-powered passive income streams
        </Typography>

        <RegisterForm onSuccess={handleRegisterSuccess} />

        <Box mt={3} textAlign="center">
          <Typography variant="body2">
            Already have an account?{' '}
            <MuiLink component={Link} to="/login">
              Log in here
            </MuiLink>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default RegisterPage;
