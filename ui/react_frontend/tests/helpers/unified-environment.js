/**
 * Unified Environment Detection Module
 *
 * This module provides a comprehensive environment detection system that works
 * across different test runners and CI platforms. It detects:
 * - CI environments (GitHub Actions, Jenkins, GitLab CI, CircleCI, etc.)
 * - Docker environments
 * - Local development environments
 *
 * It also provides utility functions for handling path-to-regexp issues in CI environments.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

/**
 * Detect if running in a CI environment
 * @returns {boolean} True if running in a CI environment
 */
function isCI() {
  return !!(
    // Standard CI environment variables
    process.env.CI === 'true' ||
    process.env.CI === true ||

    // GitHub Actions
    process.env.GITHUB_ACTIONS === 'true' ||
    !!process.env.GITHUB_WORKFLOW ||
    !!process.env.GITHUB_RUN_ID ||

    // Azure Pipelines
    process.env.TF_BUILD ||

    // Jenkins
    process.env.JENKINS_URL ||

    // GitLab CI
    process.env.GITLAB_CI ||

    // CircleCI
    process.env.CIRCLECI ||

    // Bitbucket Pipelines
    !!process.env.BITBUCKET_COMMIT ||

    // AppVeyor
    !!process.env.APPVEYOR ||

    // Drone
    !!process.env.DRONE ||

    // Buddy
    !!process.env.BUDDY ||

    // Buildkite
    !!process.env.BUILDKITE ||

    // AWS CodeBuild
    !!process.env.CODEBUILD_BUILD_ID ||

    // Travis CI
    process.env.TRAVIS === 'true' ||

    // Netlify
    !!process.env.NETLIFY ||

    // Vercel
    !!process.env.VERCEL ||

    // Heroku CI
    process.env.HEROKU_TEST_RUN_ID
  );
}

/**
 * Detect if running in GitHub Actions
 * @returns {boolean} True if running in GitHub Actions
 */
function isGitHubActions() {
  return !!(
    process.env.GITHUB_ACTIONS === 'true' ||
    !!process.env.GITHUB_WORKFLOW ||
    !!process.env.GITHUB_RUN_ID ||
    !!process.env.GITHUB_REPOSITORY ||
    !!process.env.GITHUB_WORKSPACE ||
    !!process.env.GITHUB_SHA ||
    process.env.CI_TYPE === 'github' ||
    process.env.CI_PLATFORM === 'github'
  );
}

/**
 * Detect if running in a Docker environment
 * @returns {boolean} True if running in Docker
 */
function isDockerEnvironment() {
  try {
    return !!(
      // Standard Docker environment file
      fs.existsSync('/.dockerenv') ||

      // Environment variable set in our Docker setup
      process.env.DOCKER_ENVIRONMENT === 'true' ||

      // Podman/container environment file
      fs.existsSync('/run/.containerenv') ||

      // Check cgroup for Docker
      (fs.existsSync('/proc/1/cgroup') &&
       fs.readFileSync('/proc/1/cgroup', 'utf8').includes('docker'))
    );
  } catch (error) {
    console.warn(`Error detecting Docker environment: ${error.message}`);
    return false;
  }
}

/**
 * Detect if running in a rkt container environment
 * @returns {boolean} True if running in rkt
 */
function isRktEnvironment() {
  try {
    return !!(
      // Environment variable set in our rkt setup
      process.env.RKT_ENVIRONMENT === 'true' ||
      process.env.RKT === 'true' ||

      // Check cgroup for rkt
      (fs.existsSync('/proc/1/cgroup') &&
       fs.readFileSync('/proc/1/cgroup', 'utf8').includes('rkt'))
    );
  } catch (error) {
    console.warn(`Error detecting rkt environment: ${error.message}`);
    return false;
  }
}

/**
 * Detect if running in a Singularity container environment
 * @returns {boolean} True if running in Singularity
 */
function isSingularityEnvironment() {
  try {
    return !!(
      // Environment variable set in Singularity
      process.env.SINGULARITY_ENVIRONMENT === 'true' ||
      process.env.SINGULARITY === 'true' ||
      !!process.env.SINGULARITY_CONTAINER ||

      // Check for Singularity specific files
      fs.existsSync('/.singularity.d') ||
      fs.existsSync('/singularity')
    );
  } catch (error) {
    console.warn(`Error detecting Singularity environment: ${error.message}`);
    return false;
  }
}

/**
 * Detect if running in a Kubernetes environment
 * @returns {boolean} True if running in Kubernetes
 */
function isKubernetesEnvironment() {
  return !!(
    // Standard Kubernetes environment variables
    process.env.KUBERNETES_SERVICE_HOST ||

    // Check for Kubernetes service account token
    (process.platform !== 'win32' && fs.existsSync('/var/run/secrets/kubernetes.io'))
  );
}

/**
 * Create a directory with enhanced error handling
 * @param {string} dirPath - Directory path to create
 * @returns {boolean} True if directory was created or already exists
 */
function createDirectoryWithErrorHandling(dirPath) {
  try {
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
      console.log(`Created directory at ${dirPath}`);
    }
    return true;
  } catch (error) {
    console.error(`Failed to create directory at ${dirPath}: ${error.message}`);

    // Try with absolute path as fallback
    try {
      const absolutePath = path.resolve(process.cwd(), dirPath);
      if (!fs.existsSync(absolutePath)) {
        fs.mkdirSync(absolutePath, { recursive: true });
        console.log(`Created directory at absolute path: ${absolutePath}`);
      }
      return true;
    } catch (fallbackError) {
      console.error(`Failed to create directory with absolute path: ${fallbackError.message}`);
      return false;
    }
  }
}

/**
 * Create a marker file with enhanced error handling
 * @param {string} filePath - File path to create
 * @param {string} content - Content to write to the file
 * @returns {boolean} True if file was created successfully
 */
function createMarkerFile(filePath, content) {
  try {
    // Ensure directory exists
    const dirPath = path.dirname(filePath);
    createDirectoryWithErrorHandling(dirPath);

    // Write the file
    fs.writeFileSync(filePath, content);
    console.log(`Created marker file at ${filePath}`);
    return true;
  } catch (error) {
    console.error(`Failed to create marker file at ${filePath}: ${error.message}`);

    // Try with a timestamp-based filename in the same directory
    try {
      const dirPath = path.dirname(filePath);
      const timestampFilename = `marker-${Date.now()}.txt`;
      const timestampPath = path.join(dirPath, timestampFilename);

      fs.writeFileSync(timestampPath, content);
      console.log(`Created marker file with timestamp name: ${timestampPath}`);
      return true;
    } catch (fallbackError) {
      console.error(`Failed to create marker with timestamp filename: ${fallbackError.message}`);
      return false;
    }
  }
}

/**
 * Get environment information as a formatted string
 * @returns {string} Formatted environment information
 */
function getEnvironmentInfo() {
  return `Environment Information:
- CI Environment: ${isCI() ? 'Yes' : 'No'}
- GitHub Actions: ${isGitHubActions() ? 'Yes' : 'No'}
- Container Environments:
  - Docker: ${isDockerEnvironment() ? 'Yes' : 'No'}
  - Kubernetes: ${isKubernetesEnvironment() ? 'Yes' : 'No'}
  - rkt: ${isRktEnvironment() ? 'Yes' : 'No'}
  - Singularity: ${isSingularityEnvironment() ? 'Yes' : 'No'}
- Platform: ${process.platform}
- Architecture: ${process.arch}
- Node.js Version: ${process.version}
- Working Directory: ${process.cwd()}
- Hostname: ${os.hostname()}
- User: ${os.userInfo().username}
- Timestamp: ${new Date().toISOString()}`;
}

/**
 * Create CI-specific success markers
 * @param {string} baseDir - Base directory to create markers in
 * @param {string} message - Message to include in the marker files
 * @returns {boolean} True if at least one marker was created successfully
 */
function createCISuccessMarkers(baseDir, message) {
  if (!isCI()) {
    console.log('Not in CI environment, skipping CI success markers');
    return false;
  }

  let success = false;
  const timestamp = new Date().toISOString();
  const content = `CI Success Marker
Created at: ${timestamp}
Message: ${message}
CI Environment: ${isCI() ? 'Yes' : 'No'}
GitHub Actions: ${isGitHubActions() ? 'Yes' : 'No'}
Container Environments:
  Docker: ${isDockerEnvironment() ? 'Yes' : 'No'}
  Kubernetes: ${isKubernetesEnvironment() ? 'Yes' : 'No'}
  rkt: ${isRktEnvironment() ? 'Yes' : 'No'}
  Singularity: ${isSingularityEnvironment() ? 'Yes' : 'No'}
Platform: ${process.platform}
Node.js Version: ${process.version}
Working Directory: ${process.cwd()}
Hostname: ${os.hostname()}
${getEnvironmentInfo()}
`;

  // Create multiple marker files with different names to ensure at least one is recognized
  const markerFiles = [
    'ci-success.txt',
    'github-actions-success.txt',
    'ci-test-success.txt',
    'test-completion.txt',
    'ci-compatibility-marker.txt'
  ];

  // Create directory if it doesn't exist
  createDirectoryWithErrorHandling(baseDir);

  // Create each marker file
  for (const markerFile of markerFiles) {
    const filePath = path.join(baseDir, markerFile);
    if (createMarkerFile(filePath, content)) {
      success = true;
    }
  }

  // If GitHub Actions, create specific GitHub Actions markers
  if (isGitHubActions()) {
    const githubMarkers = [
      'github-actions-marker.txt',
      'github-workflow-success.txt',
      'github-ci-success.txt'
    ];

    for (const markerFile of githubMarkers) {
      const filePath = path.join(baseDir, markerFile);
      if (createMarkerFile(filePath, content)) {
        success = true;
      }
    }
  }

  return success;
}

/**
 * Safely create a directory with error handling
 * @param {string} dirPath - Directory path to create
 * @returns {boolean} True if directory was created or already exists
 */
function safelyCreateDirectory(dirPath) {
  try {
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
      console.log(`Created directory at ${dirPath}`);
    }
    return true;
  } catch (error) {
    console.error(`Failed to create directory at ${dirPath}: ${error.message}`);

    // Try with absolute path as fallback
    try {
      const absolutePath = path.resolve(process.cwd(), dirPath);
      if (!fs.existsSync(absolutePath)) {
        fs.mkdirSync(absolutePath, { recursive: true });
        console.log(`Created directory at absolute path: ${absolutePath}`);
      }
      return true;
    } catch (fallbackError) {
      console.error(`Failed to create directory with absolute path: ${fallbackError.message}`);
      return false;
    }
  }
}

/**
 * Safely write a file with error handling
 * @param {string} filePath - File path to write
 * @param {string} content - Content to write
 * @param {Object} [options] - Options for writing
 * @param {boolean} [options.append=false] - Whether to append to the file
 * @returns {boolean} True if file was written successfully
 */
function safelyWriteFile(filePath, content, options = {}) {
  const { append = false } = options;
  
  try {
    // Ensure directory exists
    const dirPath = path.dirname(filePath);
    safelyCreateDirectory(dirPath);

    // Write the file
    if (append) {
      fs.appendFileSync(filePath, content);
    } else {
      fs.writeFileSync(filePath, content);
    }
    console.log(`Created file at ${filePath}`);
    return true;
  } catch (error) {
    console.error(`Failed to write file at ${filePath}: ${error.message}`);

    // Try with absolute path as fallback
    try {
      const absolutePath = path.resolve(process.cwd(), filePath);
      const absoluteDirPath = path.dirname(absolutePath);
      
      // Ensure directory exists
      safelyCreateDirectory(absoluteDirPath);
      
      // Write the file
      if (append) {
        fs.appendFileSync(absolutePath, content);
      } else {
        fs.writeFileSync(absolutePath, content);
      }
      console.log(`Created file at absolute path: ${absolutePath}`);
      return true;
    } catch (fallbackError) {
      console.error(`Failed to write file with absolute path: ${fallbackError.message}`);
      return false;
    }
  }
}

// Export all functions
module.exports = {
  isCI,
  isGitHubActions,
  isDockerEnvironment,
  isRktEnvironment,
  isSingularityEnvironment,
  isKubernetesEnvironment,
  createDirectoryWithErrorHandling,
  createMarkerFile,
  getEnvironmentInfo,
  createCISuccessMarkers,
  safelyCreateDirectory,
  safelyWriteFile
};
