import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['**/*.{test,spec}.{js,jsx,ts,tsx}'],
    exclude: ['node_modules', 'dist', 'build'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportOnFailure: true,
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'dist/',
        'build/',
        'coverage/',
        '**/*.config.js',
        '**/*.config.ts',
        'tests/',
        'src/setupTests.js'
      ],
      thresholds: {
        global: {
          branches: 15,
          functions: 15,
          lines: 15,
          statements: 15
        },
        // Allow coverage generation to continue even if thresholds aren't met
        // This ensures CI can still upload coverage reports
        autoUpdate: false,
        perFile: false
      },
      // Force coverage generation even on test failures
      skipFull: false,
      all: true
    }
  },
});
