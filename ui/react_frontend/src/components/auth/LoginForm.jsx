import React, { useState } from 'react';
import {
  TextField,
  Button,
  Box,
  Typography,
  Paper,
  FormHelperText,
  InputAdornment,
  IconButton,
  CircularProgress
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useFormValidation, validationSchemas } from '../../utils/validation';
import { useAppContext } from '../../context/AppContext';

/**
 * Login form component with validation
 */
const LoginForm = ({ onSuccess }) => {
  const { login } = useAppContext();
  const [showCredential, setShowCredential] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState('');

  // Initialize form validation with login schema
  const {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
    isValid
  } = useFormValidation(
    { username: '', credentials: '' },
    validationSchemas.login
  );

  // Handle login form submission
  const submitLogin = async (formData) => {
    setServerError('');
    setIsSubmitting(true);

    try {
      // Call login function from context
      await login({
        username: formData.username,
        password: formData.credentials
      });

      // Call onSuccess callback if provided
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      // Handle login error
      setServerError(
        error.message || 'Login failed. Please check your credentials and try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Toggle credentials visibility
  const handleToggleCredentialVisibility = () => {
    setShowCredential(!showCredential);
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 400, mx: 'auto' }}>
      <Typography variant="h5" component="h1" gutterBottom align="center">
        Log In
      </Typography>

      {serverError && (
        <Typography color="error" variant="body2" sx={{ mb: 2 }} align="center">
          {serverError}
        </Typography>
      )}

      <Box component="form" onSubmit={handleSubmit(submitLogin)} noValidate>
        <TextField
          margin="normal"
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

        <TextField
          margin="normal"
          required
          fullWidth
          name="credentials"
          label="Credentials"
          type={showCredential ? "text" : "password"}
          id="credentials"
          autoComplete="current-password"
          value={values.credentials}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.credentials && Boolean(errors.credentials)}
          helperText={touched.credentials && errors.credentials}
          disabled={isSubmitting}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle credentials visibility"
                  onClick={handleToggleCredentialVisibility}
                  edge="end"
                >
                  {showCredential ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            )
          }}
        />

        <Button
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          sx={{ mt: 3, mb: 2 }}
          disabled={!isValid || isSubmitting}
        >
          {isSubmitting ? <CircularProgress size={24} /> : "Log In"}
        </Button>

        <FormHelperText>
          {/* 
            Demo credentials: username "demo" / authKey "demo123"
            NOTE: These are non-functional, non-sensitive demo values for UI demonstration only.
            No real credentials are exposed or used here.
          */}
          Demo credentials: username "demo" / authKey "demo123"
        </FormHelperText>
      </Box>
    </Paper>
  );
};

export default LoginForm;
