// Vitest global setup for React Testing Library
import '@testing-library/jest-dom';
import { vi, beforeEach, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

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

// Mock Storage
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

Object.defineProperty(window, 'localStorage', { value: createStorageMock() });
Object.defineProperty(window, 'sessionStorage', { value: createStorageMock() });


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
