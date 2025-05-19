/**
 * Enhanced Playwright Environment Helper
 *
 * This module provides comprehensive functions to handle environment-specific behavior
 * for Playwright tests. It integrates with the existing environment detection functionality
 * but is tailored specifically for E2E testing needs.
 *
 * Features:
 * - Detects and configures Playwright based on the current environment
 * - Provides environment-specific test utilities
 * - Handles different CI platforms, container environments, and cloud environments
 * - Creates environment-specific test reports
 *
 * @version 1.0.0
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const {
  detectEnvironment,
  safeFileExists,
  safeReadFile,
  safelyCreateDirectory,
  safelyWriteFile
} = require('./environment-detection');

/**
 * Configure Playwright based on the detected environment
 * @param {Object} options - Configuration options
 * @param {boolean} options.verbose - Whether to log verbose information
 * @param {boolean} options.createReportDirs - Whether to create report directories
 * @returns {Object} Playwright configuration object
 */
function configurePlaywright(options = {}) {
  const { verbose = false, createReportDirs = true } = options;

  // Detect the current environment
  const env = detectEnvironment();

  if (verbose) {
    console.log('Configuring Playwright for detected environment:');
    console.log(`- Platform: ${env.platform}`);
    console.log(`- CI: ${env.isCI ? 'Yes' : 'No'}`);
    console.log(`- Docker: ${env.isDocker ? 'Yes' : 'No'}`);
    console.log(`- Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}`);
    console.log(`- Cloud: ${env.isCloudEnvironment ? 'Yes' : 'No'}`);
    console.log(`- Node Environment: ${process.env.NODE_ENV || 'not set'}`);
  }

  // Create report directories if needed
  if (createReportDirs) {
    createPlaywrightDirectories(env);
  }

  // Base configuration
  const config = {
    testDir: './tests/e2e',
    timeout: env.isCI ? 180000 : 60000, // Longer timeout in CI
    expect: {
      timeout: env.isCI ? 60000 : 30000 // Longer expect timeout in CI
    },
    reporter: determineReporters(env),
    use: {
      baseURL: process.env.REACT_APP_BASE_URL || 'http://localhost:3000',
      trace: env.isCI ? 'on-first-retry' : 'on',
      screenshot: env.isCI ? 'only-on-failure' : 'on',
      video: env.isCI ? 'off' : 'on',
      navigationTimeout: env.isCI ? 90000 : 60000,
      actionTimeout: env.isCI ? 45000 : 30000,
      retries: 3,
    },
    retries: env.isCI ? 3 : 2,
    workers: determineWorkers(env),
    projects: determineProjects(env),
    outputDir: 'test-results/',
    skipInstallBrowsers: env.isCI,
  };

  return config;
}

/**
 * Determine appropriate reporters based on the environment
 * @param {Object} env - Environment object from detectEnvironment()
 * @returns {Array} Array of reporter configurations
 */
function determineReporters(env) {
  const reporters = [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ];

  // Add JSON reporter for all environments
  reporters.push(['json', { outputFile: 'playwright-report/test-results.json' }]);

  // Add CI-specific reporters
  if (env.isCI) {
    if (env.isGitHubActions) {
      reporters.push(['github']);
    } else if (env.isJenkins || env.isGitLabCI || env.isAzurePipelines) {
      reporters.push(['junit', { outputFile: 'test-results/junit-results.xml' }]);
    }
  }

  return reporters;
}

/**
 * Determine appropriate number of workers based on the environment
 * @param {Object} env - Environment object from detectEnvironment()
 * @returns {number} Number of workers
 */
function determineWorkers(env) {
  if (env.isCI) {
    // Use fewer workers in CI to avoid resource contention
    return 1;
  } else if (env.isDocker || env.isKubernetes) {
    // Use fewer workers in container environments
    return Math.max(1, Math.floor(os.cpus().length / 2));
  } else {
    // Use more workers in local development but ensure it's a number
    return Math.max(1, Math.floor(os.cpus().length * 0.75));
  }
}

/**
 * Determine appropriate projects based on the environment
 * @param {Object} env - Environment object from detectEnvironment()
 * @returns {Array} Array of project configurations
 */
function determineProjects(env) {
  const { devices } = require('@playwright/test');

  // Base project configuration
  const projects = [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        headless: env.isCI ? true : false,
      },
    }
  ];

  // Add more browsers for local development
  if (!env.isCI && !env.isDocker && !env.isKubernetes) {
    projects.push({
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        headless: false,
      },
    });
  }

  return projects;
}

/**
 * Create necessary directories for Playwright tests
 * @param {Object} env - Environment object from detectEnvironment()
 * @returns {boolean} Whether the directories were created successfully
 */
function createPlaywrightDirectories(env) {
  try {
    // Base directories
    const baseDirectories = [
      'playwright-report',
      'test-results',
      'test-artifacts',
      path.join('playwright-report', 'screenshots'),
      path.join('playwright-report', 'videos'),
      path.join('playwright-report', 'traces')
    ];

    // Environment-specific directories
    if (env.isCI) {
      baseDirectories.push(
        path.join('playwright-report', 'ci'),
        path.join('test-results', 'ci')
      );

      // CI platform-specific directories
      if (env.isGitHubActions) {
        baseDirectories.push(
          path.join('playwright-report', 'github-actions'),
          path.join('test-results', 'github-actions')
        );
      } else if (env.isJenkins) {
        baseDirectories.push(
          path.join('playwright-report', 'jenkins'),
          path.join('test-results', 'jenkins')
        );
      }
    }

    if (env.isDocker || env.isKubernetes) {
      baseDirectories.push(
        path.join('playwright-report', 'container'),
        path.join('test-results', 'container')
      );
    }

    // Create all directories
    for (const dir of baseDirectories) {
      const dirPath = path.join(process.cwd(), dir);
      safelyCreateDirectory(dirPath);
    }

    return true;
  } catch (error) {
    console.error(`Failed to create Playwright directories: ${error.message}`);
    return false;
  }
}

/**
 * Create a Playwright environment report
 * @param {Object} options - Report options
 * @param {string} options.filePath - Path to write the report to
 * @param {boolean} options.formatJson - Whether to format as JSON
 * @param {boolean} options.includeEnvVars - Whether to include environment variables
 * @returns {string} The report content
 */
function createPlaywrightEnvironmentReport(options = {}) {
  const { filePath, formatJson = false, includeEnvVars = false } = options;

  // Detect the current environment
  const env = detectEnvironment();

  // Create report content
  const reportData = {
    timestamp: new Date().toISOString(),
    environment: {
      platform: env.platform,
      isWindows: env.isWindows,
      isMacOS: env.isMacOS,
      isLinux: env.isLinux,
      isWSL: env.isWSL
    },
    ci: {
      isCI: env.isCI,
      isGitHubActions: env.isGitHubActions,
      isJenkins: env.isJenkins,
      isGitLabCI: env.isGitLabCI,
      isCircleCI: env.isCircleCI,
      isTravis: env.isTravis,
      isAzurePipelines: env.isAzurePipelines
    },
    container: {
      isDocker: env.isDocker,
      isKubernetes: env.isKubernetes,
      isDockerCompose: env.isDockerCompose,
      isDockerSwarm: env.isDockerSwarm,
      isContainerized: env.isContainerized
    },
    cloud: {
      isAWS: env.isAWS,
      isAzure: env.isAzure,
      isGCP: env.isGCP,
      isCloudEnvironment: env.isCloudEnvironment
    },
    node: {
      isDevelopment: env.isDevelopment,
      isProduction: env.isProduction,
      isTest: env.isTest,
      isStaging: env.isStaging,
      nodeVersion: env.nodeVersion
    },
    playwright: {
      configuredWorkers: String(determineWorkers(env)),
      headless: env.isCI || env.isDocker || env.isKubernetes,
      browsers: env.isCI ? ['chromium'] : ['chromium', 'firefox'],
      retries: env.isCI ? 3 : 2
    }
  };

  // Format the report
  let report;
  if (formatJson) {
    report = JSON.stringify(reportData, null, 2);
  } else {
    report = `Playwright Environment Report
Generated: ${reportData.timestamp}

Operating System:
- Platform: ${env.platform}
- Windows: ${env.isWindows ? 'Yes' : 'No'}
- macOS: ${env.isMacOS ? 'Yes' : 'No'}
- Linux: ${env.isLinux ? 'Yes' : 'No'}
- WSL: ${env.isWSL ? 'Yes' : 'No'}

CI Environment:
- CI: ${env.isCI ? 'Yes' : 'No'}
- GitHub Actions: ${env.isGitHubActions ? 'Yes' : 'No'}
- Jenkins: ${env.isJenkins ? 'Yes' : 'No'}
- GitLab CI: ${env.isGitLabCI ? 'Yes' : 'No'}
- CircleCI: ${env.isCircleCI ? 'Yes' : 'No'}
- Travis: ${env.isTravis ? 'Yes' : 'No'}
- Azure Pipelines: ${env.isAzurePipelines ? 'Yes' : 'No'}

Container Environment:
- Docker: ${env.isDocker ? 'Yes' : 'No'}
- Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}
- Docker Compose: ${env.isDockerCompose ? 'Yes' : 'No'}
- Docker Swarm: ${env.isDockerSwarm ? 'Yes' : 'No'}
- Containerized: ${env.isContainerized ? 'Yes' : 'No'}

Cloud Environment:
- AWS: ${env.isAWS ? 'Yes' : 'No'}
- Azure: ${env.isAzure ? 'Yes' : 'No'}
- GCP: ${env.isGCP ? 'Yes' : 'No'}
- Cloud Environment: ${env.isCloudEnvironment ? 'Yes' : 'No'}

Node Environment:
- Development: ${env.isDevelopment ? 'Yes' : 'No'}
- Production: ${env.isProduction ? 'Yes' : 'No'}
- Test: ${env.isTest ? 'Yes' : 'No'}
- Staging: ${env.isStaging ? 'Yes' : 'No'}
- Node Version: ${env.nodeVersion}

Playwright Configuration:
- Workers: ${reportData.playwright.configuredWorkers}
- Headless: ${reportData.playwright.headless ? 'Yes' : 'No'}
- Browsers: ${reportData.playwright.browsers.join(', ')}
- Retries: ${reportData.playwright.retries}
`;
  }

  // Write report to file if path is provided
  if (filePath) {
    try {
      const dir = path.dirname(filePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(filePath, report);
    } catch (error) {
      console.error(`Failed to write Playwright environment report to ${filePath}: ${error.message}`);
    }
  }

  return report;
}

module.exports = {
  configurePlaywright,
  createPlaywrightEnvironmentReport,
  createPlaywrightDirectories,
  determineReporters,
  determineWorkers,
  determineProjects
};
