import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Alert } from '@mui/material';

const ForgotPasswordForm = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      // Simulate API call (replace with real API as needed)
      await new Promise((resolve) => setTimeout(resolve, 500));
      setSent(true);
      if (onSuccess) onSuccess();
    } catch (err) {
      setError('Failed to send password reset link. Try again later.');
    } finally {
      setSubmitting(false);
    }
  };

  if (sent) {
    return (
      <Alert severity="success" role="status">
        If an account with that email exists, a password reset link has been sent.
      </Alert>
    );
  }

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 400, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" component="h1" gutterBottom>
        Forgot Password
      </Typography>
      <Typography variant="body2" gutterBottom>
        Enter your email address and we'll send you a link to reset your password.
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      <TextField
        label="Email"
        type="email"
        required
        value={email}
        onChange={e => setEmail(e.target.value)}
        fullWidth
        margin="normal"
        autoComplete="email"
        inputProps={{ 'aria-label': 'email' }}
      />
      <Button type="submit" variant="contained" color="primary" fullWidth disabled={submitting}>
        {submitting ? 'Sending...' : 'Send Reset Link'}
      </Button>
    </Box>
  );
};

export default ForgotPasswordForm;