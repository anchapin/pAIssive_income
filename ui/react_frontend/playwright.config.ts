import { defineConfig, devices } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

// Determine if we're running in CI
const isCI = process.env.CI === 'true';

// Create output directories if they don't exist
const outputDir = path.join(process.cwd(), 'test-results');
const reportDir = path.join(process.cwd(), 'playwright-report');

try {
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
    console.log(`Created test-results directory at ${outputDir}`);
  }

  if (!fs.existsSync(reportDir)) {
    fs.mkdirSync(reportDir, { recursive: true });
    console.log(`Created playwright-report directory at ${reportDir}`);
  }
} catch (error) {
  console.error(`Error creating output directories: ${error}`);
}

// Log configuration information
console.log(`Playwright configuration:`);
console.log(`- Running in CI: ${isCI ? 'Yes' : 'No'}`);
console.log(`- Platform: ${process.platform}`);
console.log(`- Output directory: ${outputDir}`);
console.log(`- Report directory: ${reportDir}`);

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 180 * 1000, // Increase test timeout to 3 minutes for CI environments
  expect: {
    timeout: 60000 // Increase default assertion timeout to 60 seconds
  },
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'], // Add list reporter for better CI output
    ['json', { outputFile: 'playwright-report/test-results.json' }] // Add JSON reporter for programmatic access
  ],
  use: {
    // Use environment variable for baseURL if available
    baseURL: process.env.REACT_APP_BASE_URL || 'http://localhost:3000',

    // Adjust trace settings based on environment
    trace: isCI ? 'on-first-retry' : 'on', // Only capture traces on retry in CI to save resources

    // Adjust screenshot settings based on environment
    screenshot: isCI ? 'only-on-failure' : 'on', // Only capture screenshots on failure in CI

    // Adjust video settings based on environment
    video: isCI ? 'off' : 'on', // Disable videos in CI to save resources

    // Increase timeouts for CI environments
    navigationTimeout: isCI ? 90000 : 60000,
    actionTimeout: isCI ? 45000 : 30000,

    // Retry failed actions
    retries: 3,
  },
  // Retry failed tests more times in CI
  retries: isCI ? 3 : 2,

  // Use fewer workers in CI to avoid resource contention
  workers: isCI ? 1 : 1,

  // Configure projects based on environment
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Use headless mode in CI
        headless: isCI ? true : false,
      },
    },
  ],

  // Create a directory for test artifacts
  outputDir: 'test-results/',

  // Allow browser installation in CI environments for proper testing
  // skipInstallBrowsers: isCI,
});
