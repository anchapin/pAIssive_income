import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react({
    jsxRuntime: 'automatic'
  })],
  esbuild: {
    jsx: 'automatic'
  },
  test: {
    environment: 'jsdom',
    include: [
      'src/**/*.test.js',
      'ui/**/*.test.js',
      'sdk/javascript/**/*.test.js'
    ],
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/cypress/**',
      '**/.{idea,git,cache,output,temp}/**',
      '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build}.config.*',
      '.venv*/**',
      'venv*/**',
      '__pycache__/**',
      '*.pyc'
    ],
    globals: true,
    setupFiles: ['./vitest.setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      include: [
        'src/**/*.js',
        'ui/**/*.js',
        'sdk/javascript/**/*.js'
      ],
      exclude: [
        '**/*.test.js',
        '**/test/**',
        'tests/**',
        '**/__mocks__/**',
        '**/mocks/**',
        '**/mock*/**',
        '**/testUtils.js',
        '**/test_utils.js',
        '**/test-utils.js',
        '**/setupTests.js',
        '.venv*/**',
        'venv*/**',
        '__pycache__/**',
        '*.pyc',
        'node_modules/**',
        '.git/**'
      ],
      thresholds: {
        statements: 80,
        branches: 80,
        functions: 80,
        lines: 80
      }
    }
  },
});
