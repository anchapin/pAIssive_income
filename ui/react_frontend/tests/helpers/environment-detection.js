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
      console.log(`Wrote file at absolute path: ${absolutePath}`);
      return true;
    } catch (fallbackError) {
      console.error(`Failed to write file with absolute path: ${fallbackError.message}`);
      return false;
    }
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
    isGitHubActions: ci.providers.gitHubActions,
    isJenkins: ci.providers.jenkins,
    isGitLabCI: ci.providers.gitLabCI,
    isCircleCI: ci.providers.circleCI,
    isAzurePipelines: ci.providers.azure,
    isTravis: ci.providers.travis,
    isTeamCity: ci.providers.teamCity,
    isBitbucket: ci.providers.bitbucket,
    isAppVeyor: ci.providers.appVeyor,
    isDroneCI: ci.providers.drone,
    isBuddyCI: ci.providers.buddy,
    isBuildkite: ci.providers.buildkite,
    isCodeBuild: ci.providers.codeBuild,
    isVercel: ci.providers.vercel,
    isNetlify: ci.providers.netlify,
    isHeroku: ci.providers.heroku,
    isDocker: container.type.docker,
    isKubernetes: container.type.kubernetes,
    isDockerCompose: !!process.env.COMPOSE_PROJECT_NAME,
    isDockerSwarm: !!process.env.DOCKER_SWARM,
    isContainerized: container.isContainer,
    isAWS: !!process.env.AWS_REGION,
    isAWSLambda: !!process.env.AWS_LAMBDA_FUNCTION_NAME,
    isAzureFunctions: !!process.env.AZURE_FUNCTIONS_ENVIRONMENT,
    isGCP: !!process.env.GOOGLE_CLOUD_PROJECT,
    isGCPCloudFunctions: !!(process.env.FUNCTION_NAME && process.env.FUNCTION_REGION),
    isGKE: !!(process.env.KUBERNETES_SERVICE_HOST && process.env.GKE_CLUSTER_NAME),
    isCloudEnvironment: !!(process.env.AWS_REGION || process.env.AZURE_SUBSCRIPTION_ID || process.env.GOOGLE_CLOUD_PROJECT),
    isServerless: !!(process.env.AWS_LAMBDA_FUNCTION_NAME || process.env.AZURE_FUNCTIONS_ENVIRONMENT || (process.env.FUNCTION_NAME && process.env.FUNCTION_REGION)),
    isDevelopment: process.env.NODE_ENV === 'development',
    isProduction: process.env.NODE_ENV === 'production',
    isTest: process.env.NODE_ENV === 'test',
    isWSL: !!process.env.WSL_DISTRO_NAME,
    isWindows: process.platform === 'win32',
    isMacOS: process.platform === 'darwin',
    isLinux: process.platform === 'linux',
    platform: process.platform,
    ciProviders: ci.providers,
    container,
    directories: dirs,
    env: process.env.NODE_ENV || 'development'
  };
}

/**
 * Create a comprehensive environment report
 * @param {string} [filePath] - Optional file path to write the report to
 * @param {Object} [options] - Report options
 * @param {boolean} [options.formatJson=false] - Whether to format as JSON instead of text
 * @param {boolean} [options.includeEnvVars=false] - Whether to include environment variables
 * @returns {string} Environment report
 */
function createEnvironmentReport(filePath, options = {}) {
  const { formatJson = false, includeEnvVars = false } = options;
  const env = detectEnvironment();

  if (formatJson) {
    const reportObj = {
      timestamp: new Date().toISOString(),
      operatingSystem: {
        platform: env.platform,
        isWindows: env.isWindows,
        isMacOS: env.isMacOS,
        isLinux: env.isLinux,
        isWSL: env.isWSL
      },
      ciEnvironment: {
        isCI: env.isCI,
        isGitHubActions: env.isGitHubActions,
        isJenkins: env.isJenkins,
        isGitLabCI: env.isGitLabCI,
        isCircleCI: env.isCircleCI,
        isAzure: env.isAzure,
        isTravis: env.isTravis
      },
      containerEnvironment: {
        isContainerized: env.isContainerized,
        isDocker: env.isDocker,
        isKubernetes: env.isKubernetes,
        isDockerCompose: env.isDockerCompose,
        isDockerSwarm: env.isDockerSwarm
      },
      cloudEnvironment: {
        isCloudEnvironment: env.isCloudEnvironment,
        isAWS: env.isAWS,
        isAWSLambda: env.isAWSLambda,
        isAzure: env.isAzure,
        isAzureFunctions: env.isAzureFunctions,
        isGCP: env.isGCP,
        isGCPCloudFunctions: env.isGCPCloudFunctions,
        isServerless: env.isServerless
      },
      nodeEnvironment: {
        isDevelopment: env.isDevelopment,
        isProduction: env.isProduction,
        isTest: env.isTest,
        nodeVersion: process.version
      }
    };

    if (includeEnvVars) {
      reportObj.environmentVariables = process.env;
    }

    const report = JSON.stringify(reportObj, null, 2);

    if (filePath) {
      safelyWriteFile(filePath, report);
    }

    return report;
  }

  // Text format
  const report = `Environment Detection Report
============================
Generated at: ${new Date().toISOString()}

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
- Azure Pipelines: ${env.isAzure ? 'Yes' : 'No'}
- Travis CI: ${env.isTravis ? 'Yes' : 'No'}

Container Environment:
- Containerized: ${env.isContainerized ? 'Yes' : 'No'}
- Docker: ${env.isDocker ? 'Yes' : 'No'}
- Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}
- Docker Compose: ${env.isDockerCompose ? 'Yes' : 'No'}
- Docker Swarm: ${env.isDockerSwarm ? 'Yes' : 'No'}

Cloud Environment:
- Cloud Environment: ${env.isCloudEnvironment ? 'Yes' : 'No'}
- AWS: ${env.isAWS ? 'Yes' : 'No'}
- AWS Lambda: ${env.isAWSLambda ? 'Yes' : 'No'}
- Azure: ${env.isAzure ? 'Yes' : 'No'}
- Azure Functions: ${env.isAzureFunctions ? 'Yes' : 'No'}
- GCP: ${env.isGCP ? 'Yes' : 'No'}
- GCP Cloud Functions: ${env.isGCPCloudFunctions ? 'Yes' : 'No'}
- Serverless: ${env.isServerless ? 'Yes' : 'No'}

Node Environment:
- Development: ${env.isDevelopment ? 'Yes' : 'No'}
- Production: ${env.isProduction ? 'Yes' : 'No'}
- Test: ${env.isTest ? 'Yes' : 'No'}
- Node Version: ${process.version}
`;

  if (filePath) {
    safelyWriteFile(filePath, report);
  }

  return report;
}

// Export environment detection functions
module.exports = {
  detectEnvironment,
  detectCIEnvironment,
  detectContainerEnvironment,
  getWorkingDirs,
  createEnvironmentReport,
  safeFileExists,
  safeReadFile,
  safelyCreateDirectory,
  safelyWriteFile
};
