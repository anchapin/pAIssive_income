/**
 * Enhanced Environment Detection Helper
 * @version 2.3.0
 */

const fs = require('fs');
const os = require('os');
const path = require('path');

/**
 * Safely check if a file exists with error handling
 * @param {string} filePath - Path to check
 * @returns {boolean} True if file exists, false otherwise
 */
function safeFileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch (error) {
    console.warn(`Error checking if file exists at ${filePath}: ${error.message}`);
    return false;
  }
}

/**
 * Safely read a file with error handling
 * @param {string} filePath - Path to read
 * @param {string} [encoding='utf8'] - File encoding
 * @returns {string|null} File contents or null if error
 */
function safeReadFile(filePath, encoding = 'utf8') {
  try {
    return fs.readFileSync(filePath, encoding);
  } catch (error) {
    console.warn(`Error reading file at ${filePath}: ${error.message}`);
    return null;
  }
}

/**
 * Detect CI environment with comprehensive platform support
 * @returns {Object} CI environment details
 */
function detectCIEnvironment() {
  const envVars = process.env;
  
  // GitHub Actions
  const isGitHubActions = envVars.GITHUB_ACTIONS === 'true' || !!envVars.GITHUB_WORKFLOW;
  
  // Jenkins
  const isJenkins = !!envVars.JENKINS_URL || !!envVars.JENKINS_HOME;
  
  // GitLab CI
  const isGitLabCI = !!envVars.GITLAB_CI || !!envVars.CI_SERVER;
  
  // CircleCI
  const isCircleCI = !!envVars.CIRCLECI;
  
  // Azure Pipelines
  const isAzure = !!envVars.TF_BUILD || !!envVars.AZURE_HTTP_USER_AGENT;
  
  // Travis CI
  const isTravis = !!envVars.TRAVIS;
  
  // TeamCity
  const isTeamCity = !!envVars.TEAMCITY_VERSION;
  
  // Additional CI platforms
  const isBitbucket = !!envVars.BITBUCKET_BUILD_NUMBER;
  const isAppVeyor = !!envVars.APPVEYOR;
  const isDrone = !!envVars.DRONE;
  const isBuddy = !!envVars.BUDDY;
  const isBuildkite = !!envVars.BUILDKITE;
  const isCodeBuild = !!envVars.CODEBUILD_BUILD_ID;
  const isVercel = !!envVars.VERCEL;
  const isNetlify = !!envVars.NETLIFY;
  const isHeroku = !!envVars.HEROKU_TEST_RUN_ID;

  // Combined CI detection
  const isCI = envVars.CI === 'true' || envVars.CI === true ||
               isGitHubActions || isJenkins || isGitLabCI || isCircleCI ||
               isAzure || isTravis || isTeamCity || isBitbucket ||
               isAppVeyor || isDrone || isBuddy || isBuildkite ||
               isCodeBuild || isVercel || isNetlify || isHeroku;

  return {
    isCI,
    providers: {
      gitHubActions: isGitHubActions,
      jenkins: isJenkins,
      gitLabCI: isGitLabCI,
      circleCI: isCircleCI,
      azure: isAzure,
      travis: isTravis,
      teamCity: isTeamCity,
      bitbucket: isBitbucket,
      appVeyor: isAppVeyor,
      drone: isDrone,
      buddy: isBuddy,
      buildkite: isBuildkite,
      codeBuild: isCodeBuild,
      vercel: isVercel,
      netlify: isNetlify,
      heroku: isHeroku
    }
  };
}

/**
 * Detect container environment
 * @returns {Object} Container environment details
 */
function detectContainerEnvironment() {
  const isDocker = safeFileExists('/.dockerenv');
  const isPodman = safeFileExists('/run/.containerenv');
  const isKubernetes = !!process.env.KUBERNETES_SERVICE_HOST;
  
  // Check for container runtime
  const cgroupContent = safeReadFile('/proc/1/cgroup');
  const hasContainerRuntime = cgroupContent && (
    cgroupContent.includes('docker') ||
    cgroupContent.includes('kubepods') ||
    cgroupContent.includes('containerd')
  );

  return {
    isContainer: isDocker || isPodman || isKubernetes || hasContainerRuntime,
    type: {
      docker: isDocker,
      podman: isPodman,
      kubernetes: isKubernetes,
      containerd: hasContainerRuntime && cgroupContent?.includes('containerd')
    }
  };
}

/**
 * Get working directories for different environments
 * @returns {Object} Working directory paths
 */
function getWorkingDirs() {
  const cwd = process.cwd();
  const tmp = os.tmpdir();
  
  return {
    workspace: process.env.GITHUB_WORKSPACE ||
              process.env.JENKINS_HOME ||
              process.env.CI_PROJECT_DIR ||
              cwd,
    temp: process.env.RUNNER_TEMP ||
          process.env.TEMP ||
          process.env.TMP ||
          tmp,
    cache: process.env.RUNNER_TOOL_CACHE ||
           path.join(tmp, '.cache'),
    home: os.homedir()
  };
}

/**
 * Detect and return comprehensive environment information
 * @returns {Object} Complete environment details
 */
function detectEnvironment() {
  const ci = detectCIEnvironment();
  const container = detectContainerEnvironment();
  const dirs = getWorkingDirs();
  
  return {
    isCI: ci.isCI,
    ciProviders: ci.providers,
    container,
    platform: {
      type: os.type(),
      platform: process.platform,
      release: os.release(),
      arch: process.arch,
      nodeVersion: process.version,
      isWindows: process.platform === 'win32',
      isMac: process.platform === 'darwin',
      isLinux: process.platform === 'linux'
    },
    directories: dirs,
    env: process.env.NODE_ENV || 'development'
  };
}

// Export environment detection functions
module.exports = {
  detectEnvironment,
  detectCIEnvironment,
  detectContainerEnvironment,
  getWorkingDirs
};
