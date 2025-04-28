import React from 'react';
import PropTypes from 'prop-types';
import { useAppContext } from '../../context/AppContext';

/**
 * AuthGuard component for conditionally rendering content based on authentication
 * and permission requirements.
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Content to render if conditions are met
 * @param {boolean} props.requireAuth - Whether authentication is required
 * @param {string|string[]} props.requiredPermission - Permission(s) required (any one of array)
 * @param {React.ReactNode} props.fallback - Content to render if conditions are not met
 * @returns {React.ReactNode} - Either children or fallback based on conditions
 */
const AuthGuard = ({ 
  children, 
  requireAuth = true, 
  requiredPermission = null,
  fallback = null
}) => {
  const { isAuthenticated, hasPermission } = useAppContext();

  // Check if the user meets the authentication requirement
  const isAuthSatisfied = requireAuth ? isAuthenticated : true;
  
  // Check if the user meets the permission requirement (if any)
  let isPermissionSatisfied = true;
  
  if (requiredPermission) {
    if (Array.isArray(requiredPermission)) {
      // If array provided, check if user has ANY of the permissions
      isPermissionSatisfied = requiredPermission.some(perm => hasPermission(perm));
    } else {
      // Single permission check
      isPermissionSatisfied = hasPermission(requiredPermission);
    }
  }

  // If all requirements are met, render children
  if (isAuthSatisfied && isPermissionSatisfied) {
    return <>{children}</>;
  }
  
  // Otherwise render fallback or null
  return fallback ? <>{fallback}</> : null;
};

AuthGuard.propTypes = {
  children: PropTypes.node.isRequired,
  requireAuth: PropTypes.bool,
  requiredPermission: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string)
  ]),
  fallback: PropTypes.node
};

export default AuthGuard;