/**
 * Tests for the AppContext (AppProvider and useAppContext)
 */

import React from 'react';
import { render, screen, act, waitFor } from '@testing-library/react';
import { AppProvider, useAppContext, ActionTypes } from './AppContext';

// Mock apiClient
jest.mock('../services/apiClient', () => ({
  user: {
    getCurrentUser: jest.fn(),
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn()
  },
  dashboard: {
    getProjectsOverview: jest.fn()
  }
}));

const apiClient = require('../services/apiClient');

const TestConsumer = ({ callback }) => {
  const ctx = useAppContext();
  if (callback) callback(ctx);
  return (
    <div>
      <div>user:{ctx.user ? ctx.user.username : ''}</div>
      <div>isAuthenticated:{ctx.isAuthenticated ? 'yes' : 'no'}</div>
      <div>notifications:{ctx.notifications.length}</div>
      <div>darkMode:{ctx.darkMode ? 'on' : 'off'}</div>
      <button onClick={() => ctx.dispatch({ type: ActionTypes.TOGGLE_DARK_MODE })}>Toggle Dark</button>
      <button onClick={() => ctx.addNotification({ message: 'Test', type: 'info', timeout: 100 })}>Add Notification</button>
    </div>
  );
};

describe('AppContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it('provides initial state and updates dark mode', () => {
    render(
      <AppProvider>
        <TestConsumer />
      </AppProvider>
    );
    expect(screen.getByText(/isAuthenticated:no/i)).toBeInTheDocument();
    expect(screen.getByText(/darkMode:off/i)).toBeInTheDocument();

    // Toggle dark mode
    act(() => {
      screen.getByText('Toggle Dark').click();
    });
    expect(screen.getByText(/darkMode:on/i)).toBeInTheDocument();
  });

  it('adds and auto-removes notifications', async () => {
    render(
      <AppProvider>
        <TestConsumer />
      </AppProvider>
    );
    expect(screen.getByText(/notifications:0/i)).toBeInTheDocument();
    act(() => {
      screen.getByText('Add Notification').click();
    });
    expect(screen.getByText(/notifications:1/i)).toBeInTheDocument();
    // Fast-forward timer for auto-removal
    act(() => {
      jest.advanceTimersByTime(200);
    });
    await waitFor(() => expect(screen.getByText(/notifications:0/i)).toBeInTheDocument());
  });

  it('useAppContext throws outside provider', () => {
    const ConsoleError = console.error;
    console.error = () => {}; // Silence error boundary output
    expect(() => render(<TestConsumer />)).toThrow(/useAppContext must be used within an AppProvider/i);
    console.error = ConsoleError;
  });

  it('login calls api and updates user, notifications', async () => {
    apiClient.user.login.mockResolvedValue({ username: 'tester' });
    let ctx;
    render(
      <AppProvider>
        <TestConsumer callback={c => (ctx = c)} />
      </AppProvider>
    );
    await act(async () => {
      await ctx.login({ username: 'tester', credential: 'pw' });
    });
    expect(apiClient.user.login).toHaveBeenCalledWith({ username: 'tester', credential: 'pw' });
    expect(ctx.user).toEqual({ username: 'tester' });
    expect(ctx.isAuthenticated).toBe(true);
    expect(ctx.notifications.some(n => n.message.includes('Login successful'))).toBe(true);
  });

  it('login handles error and adds error notification', async () => {
    apiClient.user.login.mockRejectedValue(new Error('fail'));
    let ctx;
    render(
      <AppProvider>
        <TestConsumer callback={c => (ctx = c)} />
      </AppProvider>
    );
    await expect(act(async () => {
      await ctx.login({ username: 'bad', credential: 'fail' });
    })).rejects.toThrow('fail');
    expect(ctx.isAuthenticated).toBe(false);
    expect(ctx.notifications.some(n => n.type === 'error')).toBe(true);
  });

  it('logout calls api and resets user/auth state', async () => {
    apiClient.user.logout.mockResolvedValue(undefined);
    let ctx;
    render(
      <AppProvider>
        <TestConsumer callback={c => (ctx = c)} />
      </AppProvider>
    );
    // Set user first
    act(() => {
      ctx.dispatch({ type: ActionTypes.SET_USER, payload: { username: 'x' } });
    });
    expect(ctx.isAuthenticated).toBe(true);

    await act(async () => {
      await ctx.logout();
    });
    expect(apiClient.user.logout).toHaveBeenCalled();
    expect(ctx.isAuthenticated).toBe(false);
    expect(ctx.user).toBe(null);
    expect(ctx.notifications.some(n => n.message.includes('logged out'))).toBe(true);
  });

  it('register calls api and updates user/notifications', async () => {
    apiClient.user.register.mockResolvedValue({ username: 'newuser' });
    let ctx;
    render(
      <AppProvider>
        <TestConsumer callback={c => (ctx = c)} />
      </AppProvider>
    );
    await act(async () => {
      await ctx.register({ username: 'newuser', email: 'a@b.com', credential: 'pw', name: 'Name' });
    });
    expect(apiClient.user.register).toHaveBeenCalled();
    expect(ctx.user).toEqual({ username: 'newuser' });
    expect(ctx.notifications.some(n => n.message.includes('Registration successful'))).toBe(true);
  });

  it('register handles error and adds error notification', async () => {
    apiClient.user.register.mockRejectedValue(new Error('fail'));
    let ctx;
    render(
      <AppProvider>
        <TestConsumer callback={c => (ctx = c)} />
      </AppProvider>
    );
    await expect(act(async () => {
      await ctx.register({ username: 'bad', email: 'fail@b.com', credential: 'fail', name: 'Name' });
    })).rejects.toThrow('fail');
    expect(ctx.isAuthenticated).toBe(false);
    expect(ctx.notifications.some(n => n.type === 'error')).toBe(true);
  });

  it('fetchDashboardData calls api and sets projectsData', async () => {
    apiClient.dashboard.getProjectsOverview.mockResolvedValue({ projects: [1, 2, 3] });
    let ctx;
    render(
      <AppProvider>
        <TestConsumer callback={c => (ctx = c)} />
      </AppProvider>
    );
    await act(async () => {
      await ctx.fetchDashboardData();
    });
    expect(apiClient.dashboard.getProjectsOverview).toHaveBeenCalled();
    expect(ctx.projectsData).toEqual({ projects: [1, 2, 3] });
  });
});