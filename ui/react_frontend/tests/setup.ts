// Vitest global setup for React Testing Library
import '@testing-library/jest-dom';
import { vi, beforeEach, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import React from 'react';

// Mock Emotion React to prevent context errors
vi.mock('@emotion/react', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => children,
  useTheme: () => ({
    palette: {
      mode: 'light',
      primary: { main: '#1976d2' },
    },
  }),
  jsx: vi.fn(),
  css: vi.fn(),
}));

// Mock Material-UI components and hooks
vi.mock('@mui/material/styles', () => ({
  createTheme: vi.fn(() => ({
    palette: {
      mode: 'light',
      primary: { main: '#1976d2' },
      secondary: { main: '#dc004e' },
      error: { main: '#f44336' },
      warning: { main: '#ff9800' },
      info: { main: '#2196f3' },
      success: { main: '#4caf50' },
    },
    spacing: (factor: number) => factor * 8,
    breakpoints: {
      up: () => '',
      down: () => '',
      values: { xs: 0, sm: 600, md: 900, lg: 1200, xl: 1536 }
    },
  })),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => children,
  useTheme: () => ({
    palette: {
      mode: 'light',
      primary: { main: '#1976d2' },
    },
    spacing: (factor: number) => factor * 8,
  }),
}));

// Mock Material-UI components 
vi.mock('@mui/material', () => ({
  Box: ({ children, component = 'div', sx, ...props }: any) => {
    const { sx: _sx, ...cleanProps } = props;
    return React.createElement(component, cleanProps, children);
  },
  TextField: ({ label, fullWidth, margin, inputProps, ...props }: any) => {
    const { fullWidth: _fw, margin: _m, inputProps: ip, ...cleanProps } = props;
    return React.createElement('input', { 'aria-label': label?.toLowerCase(), ...ip, ...cleanProps });
  },
  Button: ({ children, variant, color, fullWidth, sx, disabled, ...props }: any) => {
    const { variant: _v, color: _c, fullWidth: _fw, sx: _sx, ...cleanProps } = props;
    return React.createElement('button', { disabled, ...cleanProps }, children);
  },
  Typography: ({ children, component = 'div', variant, gutterBottom, ...props }: any) => {
    const { variant: _v, gutterBottom: _gb, ...cleanProps } = props;
    return React.createElement(component, cleanProps, children);
  },
  Alert: ({ children, severity, role = 'alert', sx, ...props }: any) => {
    const { sx: _sx, ...cleanProps } = props;
    return React.createElement('div', { role, 'data-severity': severity, ...cleanProps }, children);
  },
  Link: ({ children, component, to, underline, tabIndex, ...props }: any) => {
    const { underline: _u, ...cleanProps } = props;
    return component ? React.createElement(component, { to, tabIndex, ...cleanProps }, children) : React.createElement('a', { tabIndex, ...cleanProps }, children);
  },
  Paper: ({ children, elevation, sx, variant, component = 'div', ...props }: any) => {
    const { elevation: _e, sx: _sx, variant: _v, ...cleanProps } = props;
    return React.createElement(component, { 'data-elevation': elevation, 'data-variant': variant, ...cleanProps }, children);
  },
  Grid: ({ children, container, item, xs, sm, md, lg, xl, spacing, sx, ...props }: any) => {
    const { container: _c, item: _i, xs: _xs, sm: _sm, md: _md, lg: _lg, xl: _xl, spacing: _s, sx: _sx, ...cleanProps } = props;
    return React.createElement('div', { 'data-grid': 'true', ...cleanProps }, children);
  },
  InputAdornment: ({ children, position, ...props }: any) => {
    const { position: _p, ...cleanProps } = props;
    return React.createElement('div', { 'data-input-adornment': position, ...cleanProps }, children);
  },
  IconButton: ({ children, size, edge, color, sx, ...props }: any) => {
    const { size: _s, edge: _e, color: _c, sx: _sx, ...cleanProps } = props;
    return React.createElement('button', { 'data-icon-button': 'true', ...cleanProps }, children);
  },
  FormHelperText: ({ children, error, sx, ...props }: any) => {
    const { error: _e, sx: _sx, ...cleanProps } = props;
    return React.createElement('div', { 'data-helper-text': error ? 'error' : 'normal', ...cleanProps }, children);
  },
}));

// Mock localStorage and sessionStorage
const createStorageMock = () => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value.toString();
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
    key: vi.fn((index: number) => Object.keys(store)[index] || null),
    get length() {
      return Object.keys(store).length;
    },
  };
};

Object.defineProperty(window, 'localStorage', {
  value: createStorageMock(),
});

Object.defineProperty(window, 'sessionStorage', {
  value: createStorageMock(),
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});


// Mock fetch API globally
global.fetch = vi.fn();

// Set up fetch mock default behavior
beforeEach(() => {
  (global.fetch as import('vitest').Mock).mockReset();

  // Default mock implementation for fetch
  (global.fetch as import('vitest').Mock).mockImplementation((url: string | URL | Request) => {
    if (url === '/api/agent') {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ name: 'Test Agent', id: 1 }),
      });
    }

    if (url === '/api/agent/action') {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ status: 'success' }),
      });
    }

    // Default response for other URLs
    return Promise.resolve({
      ok: false,
      json: () => Promise.resolve({ error: 'Not found' }),
    });
  });
});

// Automatically cleanup after each test
afterEach(() => {
  cleanup();
});

// Set up global mocks for environment variables
const originalEnv = { ...process.env };

beforeEach(() => {
  // Reset process.env before each test
  process.env = { ...originalEnv };

  // Set up mock platform if specified
  if (process.env.MOCK_PLATFORM) {
    // This will be used by tests to override os.platform() mocks
    console.log(`Using mock platform: ${process.env.MOCK_PLATFORM}`);
  }
});

afterEach(() => {
  // Restore process.env after each test
  process.env = originalEnv;
});
