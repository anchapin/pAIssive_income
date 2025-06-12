/**
 * Environment-Specific Test Fixtures
 * 
 * This module provides Playwright test fixtures that are environment-aware.
 * These fixtures can be used in tests to adjust behavior based on the detected environment.
 * 
 * @version 1.0.0
 */

import { test as base, expect } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

// Import environment detection module using require since it's CommonJS
// We need to use dynamic import with eval to avoid TypeScript errors
const environmentDetection = eval('require')('../helpers/environment-detection');
const playwrightEnvironment = eval('require')('../helpers/playwright-environment');

// Detect the current environment
const env = environmentDetection.detectEnvironment();

// Create a new test object with environment-specific fixtures
export const test = base.extend({
  /**
   * Environment information fixture
   * Provides access to the detected environment in tests
   */
  environmentInfo: async ({}, use) => {
    await use(env);
  },

  /**
   * Environment-aware page fixture
   * Extends the standard page fixture with environment-specific behavior
   */
  page: async ({ page }, use) => {
    // Add environment-specific behavior to the page
    
    // Adjust timeouts based on environment
    if (env.isCI) {
      page.setDefaultTimeout(90000); // 90 seconds in CI
    } else if (env.isDocker || env.isKubernetes) {
      page.setDefaultTimeout(60000); // 60 seconds in containers
    } else {
      page.setDefaultTimeout(30000); // 30 seconds locally
    }
    
    // Add environment information to the page context for logging
    page.environmentInfo = env;
    
    // Add environment-specific helper methods
    page.logEnvironmentInfo = async () => {
      console.log('Test running in environment:');
      console.log(`- Platform: ${env.platform}`);
      console.log(`- CI: ${env.isCI ? 'Yes' : 'No'}`);
      console.log(`- Docker: ${env.isDocker ? 'Yes' : 'No'}`);
      console.log(`- Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}`);
      console.log(`- Cloud: ${env.isCloudEnvironment ? 'Yes' : 'No'}`);
    };
    
    // Create a screenshot with environment info in the filename
    page.screenshotWithEnvironmentInfo = async (options = {}) => {
      const { path: screenshotPath, ...otherOptions } = options;
      
      let finalPath = screenshotPath;
      if (finalPath) {
        // Add environment info to the filename
        const parsedPath = path.parse(finalPath);
        finalPath = path.join(
          parsedPath.dir,
          `${parsedPath.name}-${env.platform}${env.isCI ? '-ci' : ''}${parsedPath.ext}`
        );
      }
      
      return await page.screenshot({ path: finalPath, ...otherOptions });
    };
    
    await use(page);
  },

  /**
   * Environment-specific test artifacts fixture
   * Provides methods for creating and managing test artifacts
   */
  testArtifacts: async ({}, use) => {
    // Create artifacts directory
    const artifactsDir = path.join(process.cwd(), 'test-artifacts');
    if (!fs.existsSync(artifactsDir)) {
      fs.mkdirSync(artifactsDir, { recursive: true });
    }
    
    // Create environment-specific subdirectory
    const envDir = path.join(
      artifactsDir,
      env.isCI ? 'ci' : env.isDocker ? 'docker' : 'local'
    );
    if (!fs.existsSync(envDir)) {
      fs.mkdirSync(envDir, { recursive: true });
    }
    
    // Create test artifacts object
    const testArtifacts = {
      // Save a file to the artifacts directory
      saveFile: async (filename: string, content: string) => {
        const filePath = path.join(envDir, filename);
        fs.writeFileSync(filePath, content);
        return filePath;
      },
      
      // Save environment report
      saveEnvironmentReport: async (filename: string = 'environment-report.txt') => {
        const report = playwrightEnvironment.createPlaywrightEnvironmentReport();
        const filePath = path.join(envDir, filename);
        fs.writeFileSync(filePath, report);
        return filePath;
      },
      
      // Get path for an artifact
      getArtifactPath: (filename: string) => {
        return path.join(envDir, filename);
      },
      
      // Get the artifacts directory
      getArtifactsDir: () => envDir,
      
      // Get environment information
      getEnvironmentInfo: () => env
    };
    
    await use(testArtifacts);
  },

  /**
   * Environment-specific API configuration fixture
   * Provides API configuration based on the environment
   */
  apiConfig: async ({}, use) => {
    // Determine API URL based on environment
    let apiBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL || 'http://localhost:8000/api';
    
    // Adjust API URL based on environment
    if (env.isCI) {
      // In CI, use the mock API server
      apiBaseUrl = process.env.CI_API_URL || 'http://localhost:8000/api';
    } else if (env.isDocker) {
      // In Docker, use the Docker service name
      apiBaseUrl = process.env.DOCKER_API_URL || 'http://api:8000/api';
    } else if (env.isKubernetes) {
      // In Kubernetes, use the service name
      apiBaseUrl = process.env.K8S_API_URL || 'http://api-service:8000/api';
    }
    
    // Create API config object
    const apiConfig = {
      baseUrl: apiBaseUrl,
      timeout: env.isCI ? 30000 : 10000,
      retries: env.isCI ? 3 : 1,
      headers: {
        'Content-Type': 'application/json',
        'X-Test-Environment': env.isCI ? 'ci' : env.isDocker ? 'docker' : 'local'
      },
      
      // Helper method to create a full URL
      getUrl: (path: string) => {
        return `${apiBaseUrl}${path.startsWith('/') ? path : `/${path}`}`;
      }
    };
    
    await use(apiConfig);
  }
});

// Export the expect object for convenience
export { expect };

/**
 * Skip test based on environment conditions
 * @param condition Function that returns true if the test should be skipped
 * @param reason Reason for skipping
 */
export function skipByEnvironment(condition: (env: any) => boolean, reason: string) {
  return test.skip(({ environmentInfo }) => condition(environmentInfo), reason);
}

/**
 * Run test only in specific environments
 * @param condition Function that returns true if the test should run
 * @param reason Reason for conditional run
 */
export function runInEnvironment(condition: (env: any) => boolean, reason: string) {
  return test.runIf(({ environmentInfo }) => condition(environmentInfo), reason);
}

// Convenience exports for common environment-specific test conditions
export const skipInCI = skipByEnvironment(env => env.isCI, 'Test skipped in CI environment');
export const skipInDocker = skipByEnvironment(env => env.isDocker, 'Test skipped in Docker environment');
export const skipInWindows = skipByEnvironment(env => env.isWindows, 'Test skipped in Windows environment');
export const skipInMacOS = skipByEnvironment(env => env.isMacOS, 'Test skipped in macOS environment');
export const skipInLinux = skipByEnvironment(env => env.isLinux, 'Test skipped in Linux environment');

export const runInCI = runInEnvironment(env => env.isCI, 'Test runs only in CI environment');
export const runInDocker = runInEnvironment(env => env.isDocker, 'Test runs only in Docker environment');
export const runInWindows = runInEnvironment(env => env.isWindows, 'Test runs only in Windows environment');
export const runInMacOS = runInEnvironment(env => env.isMacOS, 'Test runs only in macOS environment');
export const runInLinux = runInEnvironment(env => env.isLinux, 'Test runs only in Linux environment');
