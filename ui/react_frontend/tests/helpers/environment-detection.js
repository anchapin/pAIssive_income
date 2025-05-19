/**
 * Environment Detection Helper
 * 
 * This module provides functions to detect and handle different environments:
 * - Windows vs macOS/Linux
 * - CI environments (GitHub Actions, etc.)
 * - Docker containers
 * - Development vs Production
 * 
 * It's designed to be used across the application to ensure consistent
 * environment detection and handling.
 */

const fs = require('fs');
const os = require('os');
const path = require('path');

/**
 * Detect the current environment
 * @returns {Object} Environment information
 */
function detectEnvironment() {
  // Operating System Detection
  const platform = os.platform();
  const isWindows = platform === 'win32';
  const isMacOS = platform === 'darwin';
  const isLinux = platform === 'linux';

  // CI Environment Detection
  const isCI = process.env.CI === 'true' || process.env.CI === true ||
               process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW ||
               !!process.env.JENKINS_URL || !!process.env.GITLAB_CI || 
               !!process.env.CIRCLECI || !!process.env.TRAVIS ||
               !!process.env.TF_BUILD || !!process.env.TEAMCITY_VERSION;
  
  const isGitHubActions = process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW;
  const isJenkins = !!process.env.JENKINS_URL;
  const isGitLabCI = !!process.env.GITLAB_CI;
  const isCircleCI = !!process.env.CIRCLECI;
  const isTravis = !!process.env.TRAVIS;
  const isAzurePipelines = !!process.env.TF_BUILD;
  const isTeamCity = !!process.env.TEAMCITY_VERSION;

  // Docker Environment Detection
  const isDocker = process.env.DOCKER_ENVIRONMENT === 'true' ||
                  (fs.existsSync('/.dockerenv') || process.env.DOCKER === 'true');

  // Node Environment Detection
  const isDevelopment = process.env.NODE_ENV === 'development';
  const isProduction = process.env.NODE_ENV === 'production';
  const isTest = process.env.NODE_ENV === 'test';

  // Browser Detection (only valid in browser environment)
  const isBrowser = typeof window !== 'undefined' && typeof window.document !== 'undefined';
  
  // Verbose Logging
  const verboseLogging = process.env.VERBOSE_LOGGING === 'true' || isCI;

  return {
    // Operating System
    platform,
    isWindows,
    isMacOS,
    isLinux,
    
    // CI Environment
    isCI,
    isGitHubActions,
    isJenkins,
    isGitLabCI,
    isCircleCI,
    isTravis,
    isAzurePipelines,
    isTeamCity,
    
    // Docker Environment
    isDocker,
    
    // Node Environment
    isDevelopment,
    isProduction,
    isTest,
    
    // Browser Environment
    isBrowser,
    
    // Logging
    verboseLogging,
    
    // System Info
    nodeVersion: process.version,
    architecture: process.arch,
    osType: os.type(),
    osRelease: os.release(),
    tmpDir: os.tmpdir(),
    homeDir: os.homedir(),
    workingDir: process.cwd()
  };
}

/**
 * Create a detailed environment report
 * @param {string} [filePath] - Optional file path to write the report to
 * @returns {string} Environment report
 */
function createEnvironmentReport(filePath) {
  const env = detectEnvironment();
  
  // Create report content
  const report = `Environment Report
=================
Generated at: ${new Date().toISOString()}

Operating System:
- Platform: ${env.platform}
- Type: ${env.osType}
- Release: ${env.osRelease}
- Windows: ${env.isWindows ? 'Yes' : 'No'}
- macOS: ${env.isMacOS ? 'Yes' : 'No'}
- Linux: ${env.isLinux ? 'Yes' : 'No'}

CI Environment:
- CI: ${env.isCI ? 'Yes' : 'No'}
- GitHub Actions: ${env.isGitHubActions ? 'Yes' : 'No'}
- Jenkins: ${env.isJenkins ? 'Yes' : 'No'}
- GitLab CI: ${env.isGitLabCI ? 'Yes' : 'No'}
- Circle CI: ${env.isCircleCI ? 'Yes' : 'No'}
- Travis CI: ${env.isTravis ? 'Yes' : 'No'}
- Azure Pipelines: ${env.isAzurePipelines ? 'Yes' : 'No'}
- TeamCity: ${env.isTeamCity ? 'Yes' : 'No'}

Docker Environment:
- Docker: ${env.isDocker ? 'Yes' : 'No'}

Node Environment:
- Node Version: ${env.nodeVersion}
- Architecture: ${env.architecture}
- Development: ${env.isDevelopment ? 'Yes' : 'No'}
- Production: ${env.isProduction ? 'Yes' : 'No'}
- Test: ${env.isTest ? 'Yes' : 'No'}

Paths:
- Working Directory: ${env.workingDir}
- Temp Directory: ${env.tmpDir}
- Home Directory: ${env.homeDir}

Environment Variables:
- NODE_ENV: ${process.env.NODE_ENV || 'not set'}
- CI: ${process.env.CI || 'not set'}
- GITHUB_ACTIONS: ${process.env.GITHUB_ACTIONS || 'not set'}
- DOCKER_ENVIRONMENT: ${process.env.DOCKER_ENVIRONMENT || 'not set'}
`;

  // Write report to file if path is provided
  if (filePath) {
    try {
      const dir = path.dirname(filePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(filePath, report);
    } catch (error) {
      console.error(`Failed to write environment report to ${filePath}: ${error.message}`);
    }
  }
  
  return report;
}

module.exports = {
  detectEnvironment,
  createEnvironmentReport
};
