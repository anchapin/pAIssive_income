/**
 * Tests for the ProtectedRoute component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route, useLocation } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';

// Mock useAppContext
jest.mock('../../context/AppContext', () => ({
  useAppContext: jest.fn()
}));

const { useAppContext } = require('../../context/AppContext');

describe('ProtectedRoute', () => {
  const TestChild = () => <div>Protected Content</div>;

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders children if authenticated and no permission required', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: true,
      hasPermission: () => true
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route
            path="/protected"
            element={
              <ProtectedRoute>
                <TestChild />
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/Protected Content/i)).toBeInTheDocument();
  });

  it('redirects to login if not authenticated', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: false,
      hasPermission: () => true
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route
            path="/protected"
            element={
              <ProtectedRoute>
                <div>Protected Content</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/Login Page/i)).toBeInTheDocument();
  });

  it('redirects to custom path if not authenticated', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: false,
      hasPermission: () => true
    });

    render(
      <MemoryRouter initialEntries={['/secret']}>
        <Routes>
          <Route
            path="/secret"
            element={
              <ProtectedRoute redirectTo="/custom-login">
                <div>Secret Page</div>
              </ProtectedRoute>
            }
          />
          <Route path="/custom-login" element={<div>Custom Login</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/Custom Login/i)).toBeInTheDocument();
  });

  it('redirects if requiredPermission is not satisfied', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: true,
      hasPermission: (perm) => perm !== 'admin'
    });

    render(
      <MemoryRouter initialEntries={['/admin']}>
        <Routes>
          <Route
            path="/admin"
            element={
              <ProtectedRoute requiredPermission="admin">
                <div>Admin Panel</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/Login Page/i)).toBeInTheDocument();
  });

  it('renders children if requiredPermission is satisfied', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: true,
      hasPermission: (perm) => perm === 'admin'
    });

    render(
      <MemoryRouter initialEntries={['/admin']}>
        <Routes>
          <Route
            path="/admin"
            element={
              <ProtectedRoute requiredPermission="admin">
                <div>Admin Panel</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/Admin Panel/i)).toBeInTheDocument();
  });

  it('redirects with correct "from" state', () => {
    useAppContext.mockReturnValue({
      isAuthenticated: false,
      hasPermission: () => true
    });

    // Custom component to check redirect state
    const LocationState = () => {
      const location = useLocation();
      return (
        <div>
          Redirected from: {location.state?.from}
        </div>
      );
    };

    render(
      <MemoryRouter initialEntries={['/foo/bar']}>
        <Routes>
          <Route
            path="/foo/bar"
            element={
              <ProtectedRoute>
                <div>Should not see</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<LocationState />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/Redirected from: \/foo\/bar/i)).toBeInTheDocument();
  });
});