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
  const [showPassword, setShowPassword] = useState(false);
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
    { username: '', password: '' },
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
        password: formData.password
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

  // Toggle password visibility
  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
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
          name="password"
          label="Password"
          type={showPassword ? "text" : "password"}
          id="password"
          autoComplete="current-password"
          value={values.password}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.password && Boolean(errors.password)}
          helperText={touched.password && errors.password}
          disabled={isSubmitting}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle password visibility"
                  onClick={handleTogglePasswordVisibility}
                  edge="end"
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
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
          Demo credentials: username "demo" / password "password"
        </FormHelperText>
      </Box>
    </Paper>
  );
};

export default LoginForm;
