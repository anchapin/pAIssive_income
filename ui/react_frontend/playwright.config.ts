import { defineConfig, devices } from '@playwright/test';
import * as path from 'path';
import * as fs from 'fs';

/**
 * Enhanced Playwright Configuration
 *
 * This configuration uses the enhanced environment detection functionality
 * to adjust Playwright behavior based on the detected environment.
 */

// Import environment detection modules using require since they're CommonJS
// We need to use dynamic import with eval to avoid TypeScript errors
const environmentDetection = eval('require')('./tests/helpers/environment-detection');
const playwrightEnvironment = eval('require')('./tests/helpers/playwright-environment');

// Detect the current environment
const env = environmentDetection.detectEnvironment();

// Create a Playwright environment report
const reportPath = path.join(process.cwd(), 'playwright-report', 'environment-report.txt');
playwrightEnvironment.createPlaywrightEnvironmentReport({ filePath: reportPath });

// Log configuration information
console.log(`Playwright configuration:`);
console.log(`- Platform: ${env.platform}`);
console.log(`- CI: ${env.isCI ? 'Yes' : 'No'}`);
console.log(`- Docker: ${env.isDocker ? 'Yes' : 'No'}`);
console.log(`- Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}`);
console.log(`- Cloud: ${env.isCloudEnvironment ? 'Yes' : 'No'}`);
console.log(`- Node Environment: ${process.env.NODE_ENV || 'not set'}`);

// Get Playwright configuration based on the detected environment
const playwrightConfig = playwrightEnvironment.configurePlaywright({ verbose: true });

// Export the configuration
export default defineConfig(playwrightConfig);
