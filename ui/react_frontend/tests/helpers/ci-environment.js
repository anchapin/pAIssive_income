/**
 * CI Environment Helper
 * 
 * This module provides functions to handle CI environment-specific behavior:
 * - GitHub Actions
 * - Jenkins
 * - GitLab CI
 * - Circle CI
 * - Travis CI
 * - Azure Pipelines
 * - TeamCity
 * 
 * It's designed to be used across the application to ensure consistent
 * CI environment handling.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { detectEnvironment } = require('./environment-detection');

/**
 * Detect the CI environment type
 * @returns {string} CI environment type ('github', 'jenkins', 'gitlab', 'circle', 'travis', 'azure', 'teamcity', 'generic', 'none')
 */
function detectCIEnvironmentType() {
  const env = detectEnvironment();
  
  if (!env.isCI) {
    return 'none';
  }
  
  if (env.isGitHubActions) {
    return 'github';
  }
  
  if (env.isJenkins) {
    return 'jenkins';
  }
  
  if (env.isGitLabCI) {
    return 'gitlab';
  }
  
  if (env.isCircleCI) {
    return 'circle';
  }
  
  if (env.isTravis) {
    return 'travis';
  }
  
  if (env.isAzurePipelines) {
    return 'azure';
  }
  
  if (env.isTeamCity) {
    return 'teamcity';
  }
  
  return 'generic';
}

/**
 * Create necessary directories for CI environment
 * @returns {Object} Result object with success status and error message
 */
function createCIDirectories() {
  try {
    const directories = [
      'logs',
      'playwright-report',
      'test-results',
      'coverage'
    ];
    
    for (const dir of directories) {
      const dirPath = path.join(process.cwd(), dir);
      if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
        console.log(`Created directory: ${dirPath}`);
      } else {
        console.log(`Directory already exists: ${dirPath}`);
      }
    }
    
    return { success: true };
  } catch (error) {
    console.error(`Failed to create directories: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Create marker files for CI environment
 * @param {string} ciType - CI environment type
 * @returns {Object} Result object with success status and error message
 */
function createCIMarkerFiles(ciType) {
  try {
    const env = detectEnvironment();
    const timestamp = new Date().toISOString();
    
    // Create marker files in multiple locations to ensure at least one succeeds
    const markerLocations = [
      path.join(process.cwd(), 'logs', 'ci-environment.txt'),
      path.join(process.cwd(), 'playwright-report', 'ci-environment.txt'),
      path.join(process.cwd(), 'test-results', 'ci-environment.txt')
    ];
    
    const markerContent = `CI Environment: ${ciType}
Timestamp: ${timestamp}
Node.js: ${env.nodeVersion}
Platform: ${env.platform}
Architecture: ${env.architecture}
OS: ${env.osType} ${env.osRelease}
Working Directory: ${env.workingDir}
`;
    
    for (const location of markerLocations) {
      try {
        const dir = path.dirname(location);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }
        
        fs.writeFileSync(location, markerContent);
        console.log(`Created marker file at ${location}`);
      } catch (error) {
        console.warn(`Failed to create marker file at ${location}: ${error.message}`);
        // Continue to the next location
      }
    }
    
    return { success: true };
  } catch (error) {
    console.error(`Failed to create marker files: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Set up CI environment
 * @returns {Object} Result object with success status, CI type, and error message
 */
function setupCIEnvironment() {
  try {
    const ciType = detectCIEnvironmentType();
    
    if (ciType === 'none') {
      console.log('No CI environment detected');
      return { success: true, ciType };
    }
    
    console.log(`Setting up CI environment for ${ciType}`);
    
    // Create directories
    const dirResult = createCIDirectories();
    if (!dirResult.success) {
      return { success: false, ciType, error: `Failed to create directories: ${dirResult.error}` };
    }
    
    // Create marker files
    const markerResult = createCIMarkerFiles(ciType);
    if (!markerResult.success) {
      return { success: false, ciType, error: `Failed to create marker files: ${markerResult.error}` };
    }
    
    // Set environment variables
    process.env.CI = 'true';
    process.env.PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = '1';
    
    if (ciType === 'github' && !process.env.GITHUB_ACTIONS) {
      process.env.GITHUB_ACTIONS = 'true';
    }
    
    console.log('CI environment setup complete');
    return { success: true, ciType };
  } catch (error) {
    console.error(`Failed to set up CI environment: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Create a CI environment report
 * @param {string} [filePath] - Optional file path to write the report to
 * @returns {string} CI environment report
 */
function createCIReport(filePath) {
  const env = detectEnvironment();
  const ciType = detectCIEnvironmentType();
  
  let report = `CI Environment Report
=====================
Generated at: ${new Date().toISOString()}

`;
  
  if (ciType === 'none') {
    report += 'No CI environment detected\n';
    return report;
  }
  
  // Add CI-specific information
  switch (ciType) {
    case 'github':
      report += `GitHub Actions
--------------
Workflow: ${process.env.GITHUB_WORKFLOW || 'unknown'}
Repository: ${process.env.GITHUB_REPOSITORY || 'unknown'}
Ref: ${process.env.GITHUB_REF || 'unknown'}
SHA: ${process.env.GITHUB_SHA || 'unknown'}
Actor: ${process.env.GITHUB_ACTOR || 'unknown'}
Event: ${process.env.GITHUB_EVENT_NAME || 'unknown'}
`;
      break;
    case 'jenkins':
      report += `Jenkins
-------
Job: ${process.env.JOB_NAME || 'unknown'}
Build: ${process.env.BUILD_NUMBER || 'unknown'}
URL: ${process.env.JENKINS_URL || 'unknown'}
Workspace: ${process.env.WORKSPACE || 'unknown'}
`;
      break;
    case 'gitlab':
      report += `GitLab CI
---------
Job: ${process.env.CI_JOB_NAME || 'unknown'}
Pipeline: ${process.env.CI_PIPELINE_ID || 'unknown'}
Project: ${process.env.CI_PROJECT_PATH || 'unknown'}
Commit: ${process.env.CI_COMMIT_SHA || 'unknown'}
Branch: ${process.env.CI_COMMIT_REF_NAME || 'unknown'}
`;
      break;
    case 'circle':
      report += `Circle CI
---------
Job: ${process.env.CIRCLE_JOB || 'unknown'}
Build: ${process.env.CIRCLE_BUILD_NUM || 'unknown'}
Project: ${process.env.CIRCLE_PROJECT_REPONAME || 'unknown'}
Branch: ${process.env.CIRCLE_BRANCH || 'unknown'}
`;
      break;
    case 'travis':
      report += `Travis CI
---------
Job: ${process.env.TRAVIS_JOB_NAME || 'unknown'}
Build: ${process.env.TRAVIS_BUILD_NUMBER || 'unknown'}
Repo: ${process.env.TRAVIS_REPO_SLUG || 'unknown'}
Branch: ${process.env.TRAVIS_BRANCH || 'unknown'}
`;
      break;
    case 'azure':
      report += `Azure Pipelines
--------------
Build: ${process.env.BUILD_BUILDNUMBER || 'unknown'}
Definition: ${process.env.BUILD_DEFINITIONNAME || 'unknown'}
Repository: ${process.env.BUILD_REPOSITORY_NAME || 'unknown'}
Branch: ${process.env.BUILD_SOURCEBRANCHNAME || 'unknown'}
`;
      break;
    case 'teamcity':
      report += `TeamCity
--------
Build: ${process.env.BUILD_NUMBER || 'unknown'}
Configuration: ${process.env.TEAMCITY_BUILDCONF_NAME || 'unknown'}
Project: ${process.env.TEAMCITY_PROJECT_NAME || 'unknown'}
`;
      break;
    default:
      report += `Generic CI
----------
CI environment detected
`;
      break;
  }
  
  // Add system information
  report += `
System Information
-----------------
Node.js: ${env.nodeVersion}
Platform: ${env.platform}
Architecture: ${env.architecture}
OS: ${env.osType} ${env.osRelease}
Working Directory: ${env.workingDir}
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
      console.error(`Failed to write CI report to ${filePath}: ${error.message}`);
    }
  }
  
  return report;
}

module.exports = {
  detectCIEnvironmentType,
  createCIDirectories,
  createCIMarkerFiles,
  setupCIEnvironment,
  createCIReport
};
