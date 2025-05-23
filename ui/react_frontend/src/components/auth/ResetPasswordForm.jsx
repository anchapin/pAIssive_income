import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Alert, Link as MuiLink } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
// import { useParams } from 'react-router-dom';

const ResetPasswordForm = ({ onSuccess }) => {
  // The token would be used in a real API call: 
  // const { token } = useParams();
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [done, setDone] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    setSubmitting(true);
    try {
      // Simulate API call (replace with real API as needed)
      await new Promise((resolve) => setTimeout(resolve, 500));
      setDone(true);
      if (onSuccess) onSuccess();
    } catch (err) {
      setError('Failed to reset password. Link may be invalid or expired.');
    } finally {
      setSubmitting(false);
    }
  };

  if (done) {
    return (
      <Alert severity="success" role="status">
        Your password has been reset. You may now log in with your new password.
      </Alert>
    );
  }

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 400, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" component="h1" gutterBottom>
        Reset Password
      </Typography>
      <Typography variant="body2" gutterBottom>
        Please enter your new password below.
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <TextField
        label="New Password"
        type="password"
        required
        value={password}
        onChange={e => setPassword(e.target.value)}
        fullWidth
        margin="normal"
        inputProps={{ 'aria-label': 'new password' }}
      />
      <TextField
        label="Confirm Password"
        type="password"
        required
        value={confirm}
        onChange={e => setConfirm(e.target.value)}
        fullWidth
        margin="normal"
        inputProps={{ 'aria-label': 'confirm password' }}
      />
      <Button type="submit" variant="contained" color="primary" fullWidth disabled={submitting} sx={{ mb: 2 }}>
        {submitting ? 'Resetting...' : 'Reset Password'}
      </Button>
      <Box sx={{ textAlign: 'right' }}>
        <MuiLink component={RouterLink} to="/login" underline="hover" tabIndex={0}>
          Back to login
        </MuiLink>
      </Box>
    </Box>
  );
};

export default ResetPasswordForm;