import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import PropTypes from 'prop-types';
import { useAppContext } from '../../context/AppContext';

/**
 * Protected Route component that restricts access based on authentication status
 * and optional permission requirements.
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components to render if access is allowed
 * @param {boolean} props.requireAuth - Whether authentication is required
 * @param {string} props.requiredPermission - Optional permission required to access this route
 * @param {string} props.redirectTo - Path to redirect to if access is denied
 * @returns {React.ReactNode} - The protected component or redirect
 */
const ProtectedRoute = ({ 
  children, 
  requireAuth = true, 
  requiredPermission = null,
  redirectTo = '/login'
}) => {
  const { isAuthenticated, hasPermission } = useAppContext();
  const location = useLocation();

  // Check if the user meets the authentication requirement
  const isAuthSatisfied = requireAuth ? isAuthenticated : true;
  
  // Check if the user meets the permission requirement (if any)
  const isPermissionSatisfied = requiredPermission 
    ? hasPermission(requiredPermission)
    : true;

  // If any requirement is not met, redirect to the specified path
  if (!isAuthSatisfied || !isPermissionSatisfied) {
    // Save the location the user was trying to access for potential redirect after login
    return (
      <Navigate 
        to={redirectTo} 
        state={{ from: location.pathname }} 
        replace 
      />
    );
  }

  // If all requirements are met, render the children
  return children;
};

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
  requireAuth: PropTypes.bool,
  requiredPermission: PropTypes.string,
  redirectTo: PropTypes.string
};

export default ProtectedRoute;