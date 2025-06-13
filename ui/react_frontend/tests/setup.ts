// Vitest global setup for React Testing Library
import '@testing-library/jest-dom';
import { vi, beforeEach, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Mock fetch API globally
global.fetch = vi.fn();

// Set up fetch mock default behavior
beforeEach(() => {
  global.fetch.mockReset();

  // Default mock implementation for fetch
  global.fetch.mockImplementation((url) => {
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