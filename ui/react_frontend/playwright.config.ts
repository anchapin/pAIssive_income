import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 120 * 1000, // Increase test timeout to 120 seconds
  expect: {
    timeout: 30000 // Increase default assertion timeout to 30 seconds
  },
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'] // Add list reporter for better CI output
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on', // Always capture traces for better debugging
    // Always capture screenshots for better debugging
    screenshot: 'on',
    // Always capture videos for better debugging
    video: 'on',
    // Increase navigation timeout
    navigationTimeout: 60000,
    // Increase action timeout
    actionTimeout: 30000,
    // Retry failed actions
    retries: 3,
  },
  // Retry failed tests
  retries: 2,
  // Increase worker timeout
  workers: 1, // Use only one worker to avoid resource contention
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  // Create a directory for test artifacts
  outputDir: 'test-results/',
});
