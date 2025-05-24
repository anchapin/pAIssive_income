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
 * Safely create a directory with error handling
 * @param {string} dirPath - Directory path to create
 * @returns {boolean} True if successful, false otherwise
 */
function safelyCreateDirectory(dirPath) {
  try {
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
    return true;
  } catch (error) {
    console.warn(`Error creating directory at ${dirPath}: ${error.message}`);
    return false;
  }
}

/**
 * Safely write a file with error handling
 * @param {string} filePath - File path to write
 * @param {string} content - Content to write
 * @param {string} [encoding='utf8'] - File encoding
 * @returns {boolean} True if successful, false otherwise
 */
function safelyWriteFile(filePath, content, encoding = 'utf8') {
  try {
    // Ensure directory exists
    const dir = path.dirname(filePath);
    safelyCreateDirectory(dir);

    fs.writeFileSync(filePath, content, encoding);
    return true;
  } catch (error) {
    console.warn(`Error writing file at ${filePath}: ${error.message}`);
    return false;
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
  
  // Additional CI platforms
  const isCodefresh = !!envVars.CF_BUILD_ID;
  const isSemaphore = !!envVars.SEMAPHORE;
  const isHarness = !!envVars.HARNESS_BUILD_ID;

  // Combined CI detection
  const isCI = envVars.CI === 'true' || envVars.CI === true ||
               isGitHubActions || isJenkins || isGitLabCI || isCircleCI ||
               isAzure || isTravis || isTeamCity || isBitbucket ||
               isAppVeyor || isDrone || isBuddy || isBuildkite ||
               isCodeBuild || isVercel || isNetlify || isHeroku ||
               isCodefresh || isSemaphore || isHarness;

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
      heroku: isHeroku,
      codefresh: isCodefresh,
      semaphore: isSemaphore,
      harness: isHarness
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

  // Check for container runtime - only on Linux platforms
  let hasContainerRuntime = false;
  if (process.platform === 'linux') {
    const cgroupContent = safeReadFile('/proc/1/cgroup');
    hasContainerRuntime = cgroupContent && (
      cgroupContent.includes('docker') ||
      cgroupContent.includes('kubepods') ||
      cgroupContent.includes('containerd')
    );
  }

  return {
    isContainer: isDocker || isPodman || isKubernetes || hasContainerRuntime,
    type: {
      docker: isDocker,
      podman: isPodman,
      kubernetes: isKubernetes,
      containerd: hasContainerRuntime && process.platform === 'linux'
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

  // Get system information
  let memory = { total: 0, free: 0 };
  let cpus = [];
  let hostname = 'localhost';
  let username = 'user';

  try {
    const os = require('os');
    memory = {
      total: os.totalmem(),
      free: os.freemem()
    };
    cpus = os.cpus();
    hostname = os.hostname();
    try {
      username = os.userInfo().username;
    } catch (userError) {
      // userInfo might not be available in some environments
      username = process.env.USER || process.env.USERNAME || 'user';
    }
  } catch (error) {
    console.warn(`Error getting system information: ${error.message}`);
  }

  return {
    isCI: ci.isCI,
    isGitHubActions: ci.providers.gitHubActions,
    isJenkins: ci.providers.jenkins,
    isGitLabCI: ci.providers.gitLabCI,
    isCircleCI: ci.providers.circleCI,
    isTravis: ci.providers.travis,
    isAzurePipelines: ci.providers.azure,
    isTeamCity: ci.providers.teamCity,
    isBitbucket: ci.providers.bitbucket,
    isAppVeyor: ci.providers.appVeyor,
    isDroneCI: ci.providers.drone,
    isBuddyCI: ci.providers.buddy,
    isBuildkite: ci.providers.buildkite,
    isCodeBuild: ci.providers.codeBuild,
    isCodefresh: ci.providers.codefresh,
    isSemaphore: ci.providers.semaphore,
    isHarness: ci.providers.harness,
    ciProviders: ci.providers,
    isDocker: container.type.docker,
    isPodman: container.type.podman,
    isKubernetes: container.type.kubernetes,
    isContainerized: container.isContainer,
    isRkt: false, // Add support for rkt if needed
    isContainerd: container.type.containerd,
    isCRIO: false, // Add support for CRI-O if needed
    isSingularity: false, // Add support for Singularity if needed
    isLXC: false, // Add support for LXC if needed
    isDockerCompose: !!process.env.COMPOSE_PROJECT_NAME,
    isDockerSwarm: !!process.env.DOCKER_SWARM,
    isAWS: !!process.env.AWS_REGION || !!process.env.AWS_LAMBDA_FUNCTION_NAME,
    isAzure: !!process.env.AZURE_FUNCTIONS_ENVIRONMENT || !!process.env.WEBSITE_SITE_NAME,
    isGCP: !!process.env.GOOGLE_CLOUD_PROJECT || !!process.env.GCLOUD_PROJECT,
    isAlibabaCloud: !!process.env.ALIBABA_CLOUD_REGION || !!process.env.ALIBABA_CLOUD_ACCESS_KEY_ID,
    isTencentCloud: !!process.env.TENCENTCLOUD_REGION || !!process.env.TENCENTCLOUD_SECRET_ID,
    isHuaweiCloud: !!process.env.HUAWEICLOUD_REGION || !!process.env.HUAWEICLOUD_ACCESS_KEY,
    isOracleCloud: !!process.env.OCI_REGION || !!process.env.OCI_TENANCY,
    isIBMCloud: !!process.env.IBM_CLOUD_REGION || !!process.env.IBMCLOUD_API_KEY,
    isCloudEnvironment: !!(process.env.AWS_REGION || process.env.AZURE_FUNCTIONS_ENVIRONMENT || process.env.GOOGLE_CLOUD_PROJECT || process.env.ALIBABA_CLOUD_REGION || process.env.TENCENTCLOUD_REGION || process.env.HUAWEICLOUD_REGION || process.env.OCI_REGION || process.env.IBM_CLOUD_REGION),
    isLambda: !!process.env.AWS_LAMBDA_FUNCTION_NAME,
    isAzureFunctions: !!process.env.AZURE_FUNCTIONS_ENVIRONMENT,
    isCloudFunctions: !!process.env.FUNCTION_NAME && !!process.env.FUNCTION_REGION,
    isServerless: !!(process.env.AWS_LAMBDA_FUNCTION_NAME || process.env.AZURE_FUNCTIONS_ENVIRONMENT || (process.env.FUNCTION_NAME && process.env.FUNCTION_REGION)),
    // Node.js environment detection
    isDevelopment: process.env.NODE_ENV === 'development',
    isProduction: process.env.NODE_ENV === 'production',
    isTest: process.env.NODE_ENV === 'test' || process.env.NODE_ENV === 'testing' || process.env.CI === 'true',
    isStaging: process.env.NODE_ENV === 'staging',
    container,
    platform: process.platform,
    isWindows: process.platform === 'win32',
    isMacOS: process.platform === 'darwin',
    isLinux: process.platform === 'linux',
    isWSL: process.env.WSL_DISTRO_NAME !== undefined,
    nodeVersion: process.version,
    architecture: process.arch,
    osType: require('os').type(),
    osRelease: require('os').release(),
    workingDir: process.cwd(),
    hostname,
    username,
    memory,
    cpus,
    directories: dirs,
    env: process.env.NODE_ENV || 'development'
  };
}

// Export environment detection functions
module.exports = {
  detectEnvironment,
  detectCIEnvironment,
  detectContainerEnvironment,
  getWorkingDirs,
  safeFileExists,
  safeReadFile,
  safelyCreateDirectory,
  safelyWriteFile
};
