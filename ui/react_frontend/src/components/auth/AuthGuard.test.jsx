/**
 * Tests for the AuthGuard component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import AuthGuard from './AuthGuard';

// Mock useAppContext
jest.mock('../../context/AppContext', () => ({
  useAppContext: jest.fn()
}));

const { useAppContext } = require('../../context/AppContext');

describe('AuthGuard', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders children if authenticated and no permission required', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: true,
      hasPermission: () => true
    });

    render(<AuthGuard><div>Secret Content</div></AuthGuard>);
    expect(screen.getByText(/Secret Content/i)).toBeInTheDocument();
  });

  it('renders fallback if not authenticated', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: false,
      hasPermission: () => true
    });

    render(<AuthGuard fallback={<div>Login Required</div>}><div>Secret</div></AuthGuard>);
    expect(screen.getByText(/Login Required/i)).toBeInTheDocument();
    expect(screen.queryByText(/Secret/i)).not.toBeInTheDocument();
  });

  it('renders fallback if requiredPermission is not satisfied', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: true,
      hasPermission: (perm) => perm !== 'admin'
    });

    render(
      <AuthGuard requiredPermission="admin" fallback={<div>No Access</div>}>
        <div>Admin Stuff</div>
      </AuthGuard>
    );
    expect(screen.getByText(/No Access/i)).toBeInTheDocument();
    expect(screen.queryByText(/Admin Stuff/i)).not.toBeInTheDocument();
  });

  it('renders children if requiredPermission is satisfied', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: true,
      hasPermission: (perm) => perm === 'admin'
    });

    render(
      <AuthGuard requiredPermission="admin">
        <div>Admin Stuff</div>
      </AuthGuard>
    );
    expect(screen.getByText(/Admin Stuff/i)).toBeInTheDocument();
  });

  it('renders children if any of requiredPermission array is satisfied', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: true,
      hasPermission: (perm) => perm === 'editor'
    });

    render(
      <AuthGuard requiredPermission={['admin', 'editor']}>
        <div>Editor Stuff</div>
      </AuthGuard>
    );
    expect(screen.getByText(/Editor Stuff/i)).toBeInTheDocument();
  });

  it('renders fallback if none of requiredPermission array is satisfied', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: true,
      hasPermission: (perm) => false
    });

    render(
      <AuthGuard requiredPermission={['admin', 'editor']} fallback={<div>No Permissions</div>}>
        <div>Content</div>
      </AuthGuard>
    );
    expect(screen.getByText(/No Permissions/i)).toBeInTheDocument();
    expect(screen.queryByText(/Content/i)).not.toBeInTheDocument();
  });

  it('renders children if requireAuth is false, even if not authenticated', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: false,
      hasPermission: () => true
    });

    render(
      <AuthGuard requireAuth={false}>
        <div>Public Content</div>
      </AuthGuard>
    );
    expect(screen.getByText(/Public Content/i)).toBeInTheDocument();
  });
});