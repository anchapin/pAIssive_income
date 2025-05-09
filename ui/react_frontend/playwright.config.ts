import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 60 * 1000, // Increase test timeout to 60 seconds
  expect: {
    timeout: 15000 // Increase default assertion timeout to 15 seconds
  },
  reporter: [
    ['html', { outputFolder: 'playwright-report' }]
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    // Add screenshot on failure
    screenshot: 'only-on-failure',
    // Add video recording for better debugging
    video: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
