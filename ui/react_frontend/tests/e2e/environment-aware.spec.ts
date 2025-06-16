/**
 * Environment-Aware E2E Tests
 * 
 * This file contains E2E tests that demonstrate how to use the environment detection
 * functionality to adjust test behavior based on the detected environment.
 * 
 * @version 1.0.0
 */

import { test, expect, skipInCI, runInCI } from '../fixtures/environment-fixtures';

// Test that runs in all environments
test('basic test that runs in all environments', async ({ page, environmentInfo }) => {
  // Log the detected environment
  console.log('Running test in environment:');
  console.log(`- Platform: ${environmentInfo.platform}`);
  console.log(`- CI: ${environmentInfo.isCI ? 'Yes' : 'No'}`);
  console.log(`- Docker: ${environmentInfo.isDocker ? 'Yes' : 'No'}`);
  
  // Navigate to the home page
  await page.goto('/');
  
  // Take a screenshot with environment info in the filename
  await page.screenshotWithEnvironmentInfo({
    path: `test-results/home-page.png`,
    fullPage: true
  });
  
  // Basic assertion that works in all environments
  expect(true).toBeTruthy();
});

// Test that runs only in CI environments
runInCI('CI-only test', async ({ page, environmentInfo, testArtifacts }) => {
  // This test only runs in CI environments
  expect(environmentInfo.isCI).toBeTruthy();
  
  // Save environment report
  await testArtifacts.saveEnvironmentReport('ci-test-report.txt');
  
  // Navigate to the home page
  await page.goto('/');
  
  // Take a screenshot
  await page.screenshot({
    path: testArtifacts.getArtifactPath('ci-home-page.png'),
    fullPage: true
  });
  
  // Basic assertion
  expect(true).toBeTruthy();
});

// Test that skips in CI environments
skipInCI('test that skips in CI environments', async ({ page, environmentInfo }) => {
  // This test will not run in CI environments
  expect(environmentInfo.isCI).toBeFalsy();
  
  // Navigate to the home page
  await page.goto('/');
  
  // Basic assertion
  expect(true).toBeTruthy();
});

// Test that demonstrates environment-specific API configuration
test('API configuration test', async ({ apiConfig }) => {
  // Log the API configuration
  console.log('API Configuration:');
  console.log(`- Base URL: ${apiConfig.baseUrl}`);
  console.log(`- Timeout: ${apiConfig.timeout}`);
  console.log(`- Retries: ${apiConfig.retries}`);
  
  // Test the URL helper
  const usersUrl = apiConfig.getUrl('/users');
  expect(usersUrl).toContain('/api/users');
  
  // Basic assertion
  expect(apiConfig.headers['Content-Type']).toBe('application/json');
});

// Test that demonstrates environment-specific behavior
test('environment-specific behavior test', async ({ page, environmentInfo }) => {
  // Navigate to the home page
  await page.goto('/');
  
  // Adjust test behavior based on environment
  if (environmentInfo.isCI) {
    // In CI, we might want to skip certain interactions or use simplified assertions
    console.log('Running in CI environment - using simplified assertions');
    expect(page.url()).toContain('localhost');
  } else if (environmentInfo.isDocker) {
    // In Docker, we might want to use different selectors or endpoints
    console.log('Running in Docker environment - using container-specific selectors');
    expect(page.url()).toContain('localhost');
  } else {
    // In local development, we might want to do more thorough testing
    console.log('Running in local environment - using full test suite');
    expect(page.url()).toContain('localhost');
    
    // Additional assertions for local environment
    expect(await page.title()).not.toBe('');
  }
});

// Test that demonstrates platform-specific behavior
test('platform-specific behavior test', async ({ page, environmentInfo }) => {
  // Navigate to the home page
  await page.goto('/');
  
  // Adjust test behavior based on platform
  if (environmentInfo.isWindows) {
    console.log('Running on Windows - using Windows-specific behavior');
    // Windows-specific test logic
    expect(environmentInfo.platform).toBe('win32');
  } else if (environmentInfo.isMacOS) {
    console.log('Running on macOS - using macOS-specific behavior');
    // macOS-specific test logic
    expect(environmentInfo.platform).toBe('darwin');
  } else if (environmentInfo.isLinux) {
    console.log('Running on Linux - using Linux-specific behavior');
    // Linux-specific test logic
    expect(environmentInfo.platform).toBe('linux');
  }
  
  // Common assertions
  expect(true).toBeTruthy();
});

// Test that demonstrates test artifacts
test('test artifacts test', async ({ testArtifacts, environmentInfo }) => {
  // Save a test artifact
  const filePath = await testArtifacts.saveFile(
    'test-info.txt',
    `Test run at ${new Date().toISOString()}\n` +
    `Platform: ${environmentInfo.platform}\n` +
    `CI: ${environmentInfo.isCI ? 'Yes' : 'No'}\n` +
    `Docker: ${environmentInfo.isDocker ? 'Yes' : 'No'}\n`
  );
  
  // Log the file path
  console.log(`Saved test artifact to ${filePath}`);
  
  // Save environment report
  const reportPath = await testArtifacts.saveEnvironmentReport();
  console.log(`Saved environment report to ${reportPath}`);
  
  // Basic assertion
  expect(filePath).toContain('test-info.txt');
  expect(reportPath).toContain('environment-report.txt');
});
