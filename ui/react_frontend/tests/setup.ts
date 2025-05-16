// Vitest global setup for React Testing Library
import '@testing-library/jest-dom';
import { vi } from 'vitest';

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