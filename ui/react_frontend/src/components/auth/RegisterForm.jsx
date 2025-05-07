import React, { useState } from 'react';
import {
  TextField,
  Button,
  Box,
  Typography,
  Paper,
  InputAdornment,
  IconButton,
  CircularProgress,
  Grid
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useFormValidation, validationSchemas } from '../../utils/validation';
import { useAppContext } from '../../context/AppContext';

/**
 * Registration form component with validation
 */
const RegisterForm = ({ onSuccess }) => {
  const { register } = useAppContext();
  const [showCredential, setShowCredential] = useState(false);
  const [showConfirmCredential, setShowConfirmCredential] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState('');

  // Initialize form validation with registration schema
  const {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
    isValid
  } = useFormValidation(
    {
      username: '',
      email: '',
      authCredential: '',
      confirmCredential: '',
      name: ''
    },
    validationSchemas.register
  );

  // Handle registration form submission
  const submitRegistration = async (formData) => {
    setServerError('');
    setIsSubmitting(true);

    try {
      // Call register function from context
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.authCredential, // API still expects 'password'
        name: formData.name
      });

      // Call onSuccess callback if provided
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      // Handle registration error
      setServerError(
        error.message || 'Registration failed. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Toggle credential visibility
  const handleToggleCredentialVisibility = () => {
    setShowCredential(!showCredential);
  };

  // Toggle confirm credential visibility
  const handleToggleConfirmCredentialVisibility = () => {
    setShowConfirmCredential(!showConfirmCredential);
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h5" component="h1" gutterBottom align="center">
        Create Account
      </Typography>

      {serverError && (
        <Typography color="error" variant="body2" sx={{ mb: 2 }} align="center">
          {serverError}
        </Typography>
      )}

      <Box component="form" onSubmit={handleSubmit(submitRegistration)} noValidate>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus
              value={values.username}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.username && Boolean(errors.username)}
              helperText={touched.username && errors.username}
              disabled={isSubmitting}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              value={values.email}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.email && Boolean(errors.email)}
              helperText={touched.email && errors.email}
              disabled={isSubmitting}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              id="name"
              label="Full Name"
              name="name"
              autoComplete="name"
              value={values.name}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.name && Boolean(errors.name)}
              helperText={touched.name && errors.name}
              disabled={isSubmitting}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              required
              fullWidth
              name="authCredential"
              label="Authentication Credential"
              type={showCredential ? "text" : "password"}
              id="authCredential"
              autoComplete="new-password"
              value={values.authCredential}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.authCredential && Boolean(errors.authCredential)}
              helperText={touched.authCredential && errors.authCredential}
              disabled={isSubmitting}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle credential visibility"
                      onClick={handleToggleCredentialVisibility}
                      edge="end"
                    >
                      {showCredential ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              required
              fullWidth
              name="confirmCredential"
              label="Confirm Credential"
              type={showConfirmCredential ? "text" : "password"}
              id="confirmCredential"
              autoComplete="new-password"
              value={values.confirmCredential}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.confirmCredential && Boolean(errors.confirmCredential)}
              helperText={touched.confirmCredential && errors.confirmCredential}
              disabled={isSubmitting}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle credential visibility"
                      onClick={handleToggleConfirmCredentialVisibility}
                      edge="end"
                    >
                      {showConfirmCredential ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
          </Grid>
        </Grid>

        <Button
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          sx={{ mt: 3, mb: 2 }}
          disabled={!isValid || isSubmitting}
        >
          {isSubmitting ? <CircularProgress size={24} /> : "Register"}
        </Button>
      </Box>
    </Paper>
  );
};

export default RegisterForm;
