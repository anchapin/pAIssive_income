/**
 * Authentication components index
 *
 * This file exports all authentication-related components and utilities
 * to make importing them elsewhere in the application easier.
 */

import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import ProtectedRoute from './ProtectedRoute';
import AuthGuard from './AuthGuard';

export {
  LoginForm,
  RegisterForm,
  ProtectedRoute,
  AuthGuard
};

// Default export as an object for named imports
export default {
  LoginForm,
  RegisterForm,
  ProtectedRoute,
  AuthGuard
};
