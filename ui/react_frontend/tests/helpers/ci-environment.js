/**
 * Enhanced CI Environment Helper
 *
 * This module provides comprehensive functions to handle CI environment-specific behavior:
 * - GitHub Actions
 * - Jenkins
 * - GitLab CI
 * - Circle CI
 * - Travis CI
 * - Azure Pipelines
 * - TeamCity
 * - Bitbucket Pipelines
 * - AppVeyor
 * - Drone CI
 * - Buddy CI
 * - Buildkite
 * - AWS CodeBuild
 * - Vercel
 * - Netlify
 * - Heroku CI
 * - Semaphore CI
 * - Codefresh
 * - Woodpecker CI
 * - Harness CI
 * - Render
 * - Railway
 * - Fly.io
 *
 * It's designed to be used across the application to ensure consistent
 * CI environment handling with proper fallbacks and error handling.
 *
 * @version 2.1.0
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
 * Detect the CI environment type with enhanced detection for more CI platforms
 * @param {Object} options - Options for detection
 * @param {boolean} options.verbose - Whether to log verbose information
 * @param {boolean} options.includeContainers - Whether to include container environments as CI types
 * @param {string} options.forceCIType - Force a specific CI type
 * @returns {string} CI environment type ('github', 'jenkins', 'gitlab', 'circle', 'travis', 'azure', 'teamcity', 'bitbucket', 'appveyor', 'drone', 'buddy', 'buildkite', 'codebuild', 'vercel', 'netlify', 'heroku', 'semaphore', 'codefresh', 'woodpecker', 'harness', 'render', 'railway', 'flyio', 'generic', 'none')
 */
function detectCIEnvironmentType(options = {}) {
  const { verbose = false, includeContainers = false, forceCIType = null } = options;

  try {
    // If a specific CI type is forced, return it
    if (forceCIType) {
      if (verbose) console.log(`Forced CI type: ${forceCIType}`);
      return forceCIType.toLowerCase();
    }

    // Check if CI_TYPE environment variable is set
    if (process.env.CI_TYPE) {
      if (verbose) console.log(`CI_TYPE environment variable set to: ${process.env.CI_TYPE}`);
      return process.env.CI_TYPE.toLowerCase();
    }

    const env = detectEnvironment();

    // Check if we're in a CI environment
    if (!env.isCI && !process.env.CI_ENVIRONMENT) {
      if (verbose) console.log('No CI environment detected');
      return 'none';
    }

    // Check for GitHub Actions
    if (env.isGitHubActions) {
      if (verbose) console.log('GitHub Actions CI detected');
      return 'github';
    }

    // Check for Jenkins
    if (env.isJenkins) {
      if (verbose) console.log('Jenkins CI detected');
      return 'jenkins';
    }

    // Check for GitLab CI
    if (env.isGitLabCI) {
      if (verbose) console.log('GitLab CI detected');
      return 'gitlab';
    }

    // Check for Circle CI
    if (env.isCircleCI) {
      if (verbose) console.log('CircleCI detected');
      return 'circle';
    }

    // Check for Travis CI
    if (env.isTravis) {
      if (verbose) console.log('Travis CI detected');
      return 'travis';
    }

    // Check for Azure Pipelines
    if (env.isAzurePipelines) {
      if (verbose) console.log('Azure Pipelines detected');
      return 'azure';
    }

    // Check for TeamCity
    if (env.isTeamCity) {
      if (verbose) console.log('TeamCity CI detected');
      return 'teamcity';
    }

    // Check for Bitbucket Pipelines
    if (env.isBitbucket) {
      if (verbose) console.log('Bitbucket Pipelines detected');
      return 'bitbucket';
    }

    // Check for AppVeyor
    if (env.isAppVeyor) {
      if (verbose) console.log('AppVeyor CI detected');
      return 'appveyor';
    }

    // Check for Drone CI
    if (env.isDroneCI) {
      if (verbose) console.log('Drone CI detected');
      return 'drone';
    }

    // Check for Buddy CI
    if (env.isBuddyCI) {
      if (verbose) console.log('Buddy CI detected');
      return 'buddy';
    }

    // Check for Buildkite
    if (env.isBuildkite) {
      if (verbose) console.log('Buildkite CI detected');
      return 'buildkite';
    }

    // Check for AWS CodeBuild
    if (env.isCodeBuild) {
      if (verbose) console.log('AWS CodeBuild detected');
      return 'codebuild';
    }

    // Check for Vercel
    if (process.env.VERCEL || process.env.NOW_BUILDER) {
      if (verbose) console.log('Vercel CI detected');
      return 'vercel';
    }

    // Check for Netlify
    if (process.env.NETLIFY) {
      if (verbose) console.log('Netlify CI detected');
      return 'netlify';
    }

    // Check for Heroku CI
    if (process.env.HEROKU_TEST_RUN_ID) {
      if (verbose) console.log('Heroku CI detected');
      return 'heroku';
    }

    // Check for Semaphore CI
    if (process.env.SEMAPHORE) {
      if (verbose) console.log('Semaphore CI detected');
      return 'semaphore';
    }

    // Check for Codefresh
    if (process.env.CF_BUILD_ID) {
      if (verbose) console.log('Codefresh CI detected');
      return 'codefresh';
    }

    // Check for Woodpecker CI
    if (process.env.CI_PIPELINE_ID && process.env.CI_REPO) {
      if (verbose) console.log('Woodpecker CI detected');
      return 'woodpecker';
    }

    // Check for Harness CI
    if (process.env.HARNESS_BUILD_ID) {
      if (verbose) console.log('Harness CI detected');
      return 'harness';
    }

    // Check for Render
    if (process.env.RENDER) {
      if (verbose) console.log('Render CI detected');
      return 'render';
    }

    // Check for Railway
    if (process.env.RAILWAY_ENVIRONMENT_ID) {
      if (verbose) console.log('Railway CI detected');
      return 'railway';
    }

    // Check for Fly.io
    if (process.env.FLY_APP_NAME) {
      if (verbose) console.log('Fly.io CI detected');
      return 'flyio';
    }

    // Check for container environments if includeContainers is true
    if (includeContainers) {
      // Docker environment
      if (env.isDocker) {
        if (verbose) console.log('Docker environment detected');
        return 'docker';
      }

      // Kubernetes environment
      if (env.isKubernetes) {
        if (verbose) console.log('Kubernetes environment detected');
        return 'kubernetes';
      }
    }

    // If no specific CI platform is detected, but CI is true
    if (verbose) console.log('Generic CI environment detected');
    return 'generic';
  } catch (error) {
    console.error(`Error detecting CI environment: ${error.message}`);
    return 'unknown';
  }
}

/**
 * Create necessary directories for CI environment with enhanced error handling
 * @param {string} [ciType='generic'] - CI environment type
 * @returns {Object} Result object with success status and error message
 */
function createCIDirectories(ciType = 'generic') {
  try {
    // Base directories needed for all CI environments
    const baseDirectories = [
      'logs',
      'playwright-report',
      'test-results',
      'coverage',
      'ci-reports'
    ];

    // CI-specific directories
    const ciSpecificDirectories = {
      github: [
        path.join('ci-reports', 'github'),
        path.join('playwright-report', 'github'),
        path.join('test-results', 'github')
      ],
      jenkins: [
        path.join('ci-reports', 'jenkins'),
        path.join('playwright-report', 'jenkins'),
        path.join('test-results', 'jenkins')
      ],
      gitlab: [
        path.join('ci-reports', 'gitlab'),
        path.join('playwright-report', 'gitlab'),
        path.join('test-results', 'gitlab')
      ],
      circle: [
        path.join('ci-reports', 'circle'),
        path.join('playwright-report', 'circle'),
        path.join('test-results', 'circle')
      ],
      travis: [
        path.join('ci-reports', 'travis'),
        path.join('playwright-report', 'travis'),
        path.join('test-results', 'travis')
      ],
      azure: [
        path.join('ci-reports', 'azure'),
        path.join('playwright-report', 'azure'),
        path.join('test-results', 'azure')
      ],
      teamcity: [
        path.join('ci-reports', 'teamcity'),
        path.join('playwright-report', 'teamcity'),
        path.join('test-results', 'teamcity')
      ],
      bitbucket: [
        path.join('ci-reports', 'bitbucket'),
        path.join('playwright-report', 'bitbucket'),
        path.join('test-results', 'bitbucket')
      ],
      appveyor: [
        path.join('ci-reports', 'appveyor'),
        path.join('playwright-report', 'appveyor'),
        path.join('test-results', 'appveyor')
      ],
      drone: [
        path.join('ci-reports', 'drone'),
        path.join('playwright-report', 'drone'),
        path.join('test-results', 'drone')
      ],
      buddy: [
        path.join('ci-reports', 'buddy'),
        path.join('playwright-report', 'buddy'),
        path.join('test-results', 'buddy')
      ],
      buildkite: [
        path.join('ci-reports', 'buildkite'),
        path.join('playwright-report', 'buildkite'),
        path.join('test-results', 'buildkite')
      ],
      codebuild: [
        path.join('ci-reports', 'codebuild'),
        path.join('playwright-report', 'codebuild'),
        path.join('test-results', 'codebuild')
      ],
      vercel: [
        path.join('ci-reports', 'vercel'),
        path.join('playwright-report', 'vercel'),
        path.join('test-results', 'vercel')
      ],
      netlify: [
        path.join('ci-reports', 'netlify'),
        path.join('playwright-report', 'netlify'),
        path.join('test-results', 'netlify')
      ],
      heroku: [
        path.join('ci-reports', 'heroku'),
        path.join('playwright-report', 'heroku'),
        path.join('test-results', 'heroku')
      ],
      semaphore: [
        path.join('ci-reports', 'semaphore'),
        path.join('playwright-report', 'semaphore'),
        path.join('test-results', 'semaphore')
      ],
      codefresh: [
        path.join('ci-reports', 'codefresh'),
        path.join('playwright-report', 'codefresh'),
        path.join('test-results', 'codefresh')
      ],
      woodpecker: [
        path.join('ci-reports', 'woodpecker'),
        path.join('playwright-report', 'woodpecker'),
        path.join('test-results', 'woodpecker')
      ],
      harness: [
        path.join('ci-reports', 'harness'),
        path.join('playwright-report', 'harness'),
        path.join('test-results', 'harness')
      ],
      render: [
        path.join('ci-reports', 'render'),
        path.join('playwright-report', 'render'),
        path.join('test-results', 'render')
      ],
      railway: [
        path.join('ci-reports', 'railway'),
        path.join('playwright-report', 'railway'),
        path.join('test-results', 'railway')
      ],
      flyio: [
        path.join('ci-reports', 'flyio'),
        path.join('playwright-report', 'flyio'),
        path.join('test-results', 'flyio')
      ],
      docker: [
        path.join('ci-reports', 'docker'),
        path.join('playwright-report', 'docker'),
        path.join('test-results', 'docker')
      ],
      kubernetes: [
        path.join('ci-reports', 'kubernetes'),
        path.join('playwright-report', 'kubernetes'),
        path.join('test-results', 'kubernetes')
      ],
      generic: [
        path.join('ci-reports', 'generic'),
        path.join('playwright-report', 'generic'),
        path.join('test-results', 'generic')
      ]
    };

    // Combine base directories with CI-specific directories
    const directories = [
      ...baseDirectories,
      ...(ciSpecificDirectories[ciType] || ciSpecificDirectories.generic)
    ];

    const results = [];

    for (const dir of directories) {
      const dirPath = path.join(process.cwd(), dir);
      const success = safelyCreateDirectory(dirPath);
      results.push({ path: dirPath, success });

      if (success) {
        console.log(`Created/verified directory: ${dirPath}`);
      } else {
        console.warn(`Failed to create directory: ${dirPath}`);
      }
    }

    // Check if at least the critical directories were created
    const criticalDirs = ['logs', 'playwright-report', 'test-results'];
    const criticalSuccess = criticalDirs.every(dir =>
      results.find(r => r.path.includes(dir) && r.success)
    );

    if (!criticalSuccess) {
      return {
        success: false,
        error: 'Failed to create critical directories',
        results
      };
    }

    return { success: true, results };
  } catch (error) {
    console.error(`Failed to create directories: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Create marker files for CI environment with enhanced information
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
      path.join(process.cwd(), 'test-results', 'ci-environment.txt'),
      path.join(process.cwd(), 'ci-reports', `${ciType}-environment.txt`),
      path.join(process.cwd(), 'ci-reports', ciType, 'environment.txt'),
      path.join(process.cwd(), 'playwright-report', ciType, 'environment.txt'),
      path.join(process.cwd(), 'test-results', ciType, 'environment.txt')
    ];

    // Create enhanced marker content with more CI information
    const markerContent = `CI Environment: ${ciType}
=================
Timestamp: ${timestamp}

CI Detection:
- CI: ${env.isCI ? 'Yes' : 'No'}
- CI Type: ${ciType}
- GitHub Actions: ${env.isGitHubActions ? 'Yes' : 'No'}
- Jenkins: ${env.isJenkins ? 'Yes' : 'No'}
- GitLab CI: ${env.isGitLabCI ? 'Yes' : 'No'}
- Circle CI: ${env.isCircleCI ? 'Yes' : 'No'}
- Travis CI: ${env.isTravis ? 'Yes' : 'No'}
- Azure Pipelines: ${env.isAzurePipelines ? 'Yes' : 'No'}
- TeamCity: ${env.isTeamCity ? 'Yes' : 'No'}
- Bitbucket: ${env.isBitbucket ? 'Yes' : 'No'}
- AppVeyor: ${env.isAppVeyor ? 'Yes' : 'No'}
- Drone CI: ${env.isDroneCI ? 'Yes' : 'No'}
- Buddy CI: ${env.isBuddyCI ? 'Yes' : 'No'}
- Buildkite: ${env.isBuildkite ? 'Yes' : 'No'}
- CodeBuild: ${env.isCodeBuild ? 'Yes' : 'No'}

System Information:
- Node.js: ${env.nodeVersion}
- Platform: ${env.platform}
- Architecture: ${env.architecture}
- OS: ${env.osType} ${env.osRelease}
- Working Directory: ${env.workingDir}
- Hostname: ${env.hostname || 'unknown'}

Environment Variables:
- NODE_ENV: ${process.env.NODE_ENV || 'not set'}
- CI: ${process.env.CI || 'not set'}
- GITHUB_ACTIONS: ${process.env.GITHUB_ACTIONS || 'not set'}
- GITHUB_WORKFLOW: ${process.env.GITHUB_WORKFLOW || 'not set'}
- JENKINS_URL: ${process.env.JENKINS_URL || 'not set'}
- GITLAB_CI: ${process.env.GITLAB_CI || 'not set'}
- CIRCLECI: ${process.env.CIRCLECI || 'not set'}
- TRAVIS: ${process.env.TRAVIS || 'not set'}
- TF_BUILD: ${process.env.TF_BUILD || 'not set'}
- TEAMCITY_VERSION: ${process.env.TEAMCITY_VERSION || 'not set'}
`;

    const results = [];

    for (const location of markerLocations) {
      const success = safelyWriteFile(location, markerContent);
      results.push({ path: location, success });

      if (success) {
        console.log(`Created marker file at ${location}`);
      } else {
        console.warn(`Failed to create marker file at ${location}`);
      }
    }

    // Check if at least one marker file was created
    const anySuccess = results.some(r => r.success);

    if (!anySuccess) {
      return {
        success: false,
        error: 'Failed to create any marker files',
        results
      };
    }

    // Create a JSON version of the marker file
    const jsonMarkerPath = path.join(process.cwd(), 'ci-reports', `${ciType}-environment.json`);
    const jsonContent = JSON.stringify({
      timestamp,
      ciType,
      ciDetection: {
        isCI: env.isCI,
        isGitHubActions: env.isGitHubActions,
        isJenkins: env.isJenkins,
        isGitLabCI: env.isGitLabCI,
        isCircleCI: env.isCircleCI,
        isTravis: env.isTravis,
        isAzurePipelines: env.isAzurePipelines,
        isTeamCity: env.isTeamCity,
        isBitbucket: env.isBitbucket,
        isAppVeyor: env.isAppVeyor,
        isDroneCI: env.isDroneCI,
        isBuddyCI: env.isBuddyCI,
        isBuildkite: env.isBuildkite,
        isCodeBuild: env.isCodeBuild
      },
      systemInfo: {
        nodeVersion: env.nodeVersion,
        platform: env.platform,
        architecture: env.architecture,
        osType: env.osType,
        osRelease: env.osRelease,
        workingDirectory: env.workingDir,
        hostname: env.hostname || 'unknown'
      },
      environmentVariables: {
        NODE_ENV: process.env.NODE_ENV || 'not set',
        CI: process.env.CI || 'not set',
        GITHUB_ACTIONS: process.env.GITHUB_ACTIONS || 'not set',
        GITHUB_WORKFLOW: process.env.GITHUB_WORKFLOW || 'not set',
        JENKINS_URL: process.env.JENKINS_URL || 'not set',
        GITLAB_CI: process.env.GITLAB_CI || 'not set',
        CIRCLECI: process.env.CIRCLECI || 'not set',
        TRAVIS: process.env.TRAVIS || 'not set',
        TF_BUILD: process.env.TF_BUILD || 'not set',
        TEAMCITY_VERSION: process.env.TEAMCITY_VERSION || 'not set'
      }
    }, null, 2);

    const jsonSuccess = safelyWriteFile(jsonMarkerPath, jsonContent);
    if (jsonSuccess) {
      console.log(`Created JSON marker file at ${jsonMarkerPath}`);
    }

    return { success: true, results };
  } catch (error) {
    console.error(`Failed to create marker files: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Set up CI environment with enhanced detection and error handling
 * @param {Object} [options] - Setup options
 * @param {boolean} [options.forceCI=false] - Force CI environment setup even if not detected
 * @param {string} [options.forceCIType=null] - Force a specific CI type
 * @returns {Object} Result object with success status, CI type, and error message
 */
function setupCIEnvironment(options = {}) {
  try {
    const {
      forceCI = false,
      forceCIType = null
    } = options;

    // Detect or force CI type
    let ciType = forceCIType || detectCIEnvironmentType();

    // Check if CI environment is detected or forced
    if (ciType === 'none' && !forceCI) {
      console.log('No CI environment detected');
      return { success: true, ciType: 'none', isCI: false };
    }

    // If forcing CI but no type specified, use generic
    if (forceCI && ciType === 'none') {
      ciType = 'generic';
    }

    console.log(`Setting up CI environment for ${ciType}`);

    // Create directories specific to the CI type
    const dirResult = createCIDirectories(ciType);
    if (!dirResult.success) {
      return {
        success: false,
        ciType,
        isCI: true,
        error: `Failed to create directories: ${dirResult.error}`,
        details: dirResult
      };
    }

    // Create marker files
    const markerResult = createCIMarkerFiles(ciType);
    if (!markerResult.success) {
      return {
        success: false,
        ciType,
        isCI: true,
        error: `Failed to create marker files: ${markerResult.error}`,
        details: markerResult
      };
    }

    // Set environment variables
    process.env.CI = 'true';
    process.env.CI_ENVIRONMENT = 'true';
    process.env.CI_TYPE = ciType;
    process.env.PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = '1';

    // Set CI-specific environment variables if not already set
    switch (ciType) {
      case 'github':
        if (!process.env.GITHUB_ACTIONS) process.env.GITHUB_ACTIONS = 'true';
        if (!process.env.GITHUB_WORKFLOW) process.env.GITHUB_WORKFLOW = 'local';
        break;
      case 'jenkins':
        if (!process.env.JENKINS_URL) process.env.JENKINS_URL = 'http://localhost:8080/';
        if (!process.env.JENKINS_HOME) process.env.JENKINS_HOME = process.cwd();
        break;
      case 'gitlab':
        if (!process.env.GITLAB_CI) process.env.GITLAB_CI = 'true';
        if (!process.env.CI_PROJECT_NAME) process.env.CI_PROJECT_NAME = 'local-project';
        break;
      case 'circle':
        if (!process.env.CIRCLECI) process.env.CIRCLECI = 'true';
        if (!process.env.CIRCLE_JOB) process.env.CIRCLE_JOB = 'local-job';
        break;
      case 'travis':
        if (!process.env.TRAVIS) process.env.TRAVIS = 'true';
        if (!process.env.TRAVIS_JOB_ID) process.env.TRAVIS_JOB_ID = 'local-job';
        break;
      case 'azure':
        if (!process.env.TF_BUILD) process.env.TF_BUILD = 'true';
        if (!process.env.BUILD_BUILDNUMBER) process.env.BUILD_BUILDNUMBER = 'local-build';
        break;
      case 'teamcity':
        if (!process.env.TEAMCITY_VERSION) process.env.TEAMCITY_VERSION = '2023.1';
        if (!process.env.TEAMCITY_PROJECT_NAME) process.env.TEAMCITY_PROJECT_NAME = 'local-project';
        break;
      case 'bitbucket':
        if (!process.env.BITBUCKET_BUILD_NUMBER) process.env.BITBUCKET_BUILD_NUMBER = '1';
        if (!process.env.BITBUCKET_COMMIT) process.env.BITBUCKET_COMMIT = 'local-commit';
        break;
      case 'appveyor':
        if (!process.env.APPVEYOR) process.env.APPVEYOR = 'true';
        if (!process.env.APPVEYOR_BUILD_ID) process.env.APPVEYOR_BUILD_ID = 'local-build';
        break;
      case 'drone':
        if (!process.env.DRONE) process.env.DRONE = 'true';
        if (!process.env.DRONE_BUILD_NUMBER) process.env.DRONE_BUILD_NUMBER = '1';
        break;
      case 'buddy':
        if (!process.env.BUDDY) process.env.BUDDY = 'true';
        if (!process.env.BUDDY_PIPELINE_ID) process.env.BUDDY_PIPELINE_ID = 'local-pipeline';
        break;
      case 'buildkite':
        if (!process.env.BUILDKITE) process.env.BUILDKITE = 'true';
        if (!process.env.BUILDKITE_BUILD_ID) process.env.BUILDKITE_BUILD_ID = 'local-build';
        break;
      case 'codebuild':
        if (!process.env.CODEBUILD_BUILD_ID) process.env.CODEBUILD_BUILD_ID = 'local-build';
        if (!process.env.CODEBUILD_BUILD_ARN) process.env.CODEBUILD_BUILD_ARN = 'local-arn';
        break;
      case 'vercel':
        if (!process.env.VERCEL) process.env.VERCEL = 'true';
        if (!process.env.VERCEL_ENV) process.env.VERCEL_ENV = 'development';
        break;
      case 'netlify':
        if (!process.env.NETLIFY) process.env.NETLIFY = 'true';
        if (!process.env.NETLIFY_LOCAL) process.env.NETLIFY_LOCAL = 'true';
        break;
      case 'heroku':
        if (!process.env.HEROKU_TEST_RUN_ID) process.env.HEROKU_TEST_RUN_ID = 'local-test-run';
        if (!process.env.HEROKU_APP_ID) process.env.HEROKU_APP_ID = 'local-app';
        break;
      case 'semaphore':
        if (!process.env.SEMAPHORE) process.env.SEMAPHORE = 'true';
        if (!process.env.SEMAPHORE_WORKFLOW_ID) process.env.SEMAPHORE_WORKFLOW_ID = 'local-workflow';
        break;
      case 'codefresh':
        if (!process.env.CF_BUILD_ID) process.env.CF_BUILD_ID = 'local-build';
        if (!process.env.CF_BUILD_URL) process.env.CF_BUILD_URL = 'http://localhost/build';
        break;
      case 'woodpecker':
        if (!process.env.CI_PIPELINE_ID) process.env.CI_PIPELINE_ID = 'local-pipeline';
        if (!process.env.CI_REPO) process.env.CI_REPO = 'local-repo';
        break;
      case 'harness':
        if (!process.env.HARNESS_BUILD_ID) process.env.HARNESS_BUILD_ID = 'local-build';
        if (!process.env.HARNESS_ACCOUNT_ID) process.env.HARNESS_ACCOUNT_ID = 'local-account';
        break;
      case 'render':
        if (!process.env.RENDER) process.env.RENDER = 'true';
        if (!process.env.RENDER_SERVICE_ID) process.env.RENDER_SERVICE_ID = 'local-service';
        break;
      case 'railway':
        if (!process.env.RAILWAY_ENVIRONMENT_ID) process.env.RAILWAY_ENVIRONMENT_ID = 'local-env';
        if (!process.env.RAILWAY_PROJECT_ID) process.env.RAILWAY_PROJECT_ID = 'local-project';
        break;
      case 'flyio':
        if (!process.env.FLY_APP_NAME) process.env.FLY_APP_NAME = 'local-app';
        if (!process.env.FLY_REGION) process.env.FLY_REGION = 'local';
        break;
      case 'docker':
        if (!process.env.DOCKER_ENVIRONMENT) process.env.DOCKER_ENVIRONMENT = 'true';
        break;
      case 'kubernetes':
        if (!process.env.KUBERNETES_SERVICE_HOST) process.env.KUBERNETES_SERVICE_HOST = 'localhost';
        break;
      case 'generic':
        // Generic CI already has CI=true set above
        break;
    }

    console.log(`CI environment setup complete for ${ciType}`);
    return {
      success: true,
      ciType,
      isCI: true,
      directories: dirResult.results,
      markerFiles: markerResult.results
    };
  } catch (error) {
    console.error(`Failed to set up CI environment: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Create a comprehensive CI environment report
 * @param {string} [filePath] - Optional file path to write the report to
 * @param {Object} [options] - Report options
 * @param {boolean} [options.includeEnvVars=false] - Whether to include all environment variables
 * @param {boolean} [options.includeSystemInfo=true] - Whether to include detailed system info
 * @param {boolean} [options.formatJson=false] - Whether to format as JSON instead of text
 * @param {boolean} [options.includeContainers=true] - Whether to include container environment information
 * @param {boolean} [options.includeCloud=true] - Whether to include cloud environment information
 * @param {boolean} [options.verbose=false] - Whether to log verbose information during report creation
 * @returns {string} CI environment report
 */
function createCIReport(filePath, options = {}) {
  const env = detectEnvironment();
  const ciType = detectCIEnvironmentType({ verbose: options.verbose });
  const {
    includeEnvVars = false,
    includeSystemInfo = true,
    formatJson = false,
    includeContainers = true,
    includeCloud = true,
    verbose = false
  } = options;

  // If JSON format is requested, return JSON
  if (formatJson) {
    const reportObj = {
      timestamp: new Date().toISOString(),
      ciType,
      ciDetection: {
        isCI: env.isCI,
        isGitHubActions: env.isGitHubActions,
        isJenkins: env.isJenkins,
        isGitLabCI: env.isGitLabCI,
        isCircleCI: env.isCircleCI,
        isTravis: env.isTravis,
        isAzurePipelines: env.isAzurePipelines,
        isTeamCity: env.isTeamCity,
        isBitbucket: env.isBitbucket,
        isAppVeyor: env.isAppVeyor,
        isDroneCI: env.isDroneCI,
        isBuddyCI: env.isBuddyCI,
        isBuildkite: env.isBuildkite,
        isCodeBuild: env.isCodeBuild,
        isVercel: process.env.VERCEL || process.env.NOW_BUILDER ? true : false,
        isNetlify: process.env.NETLIFY ? true : false,
        isHeroku: process.env.HEROKU_TEST_RUN_ID ? true : false,
        isSemaphore: process.env.SEMAPHORE ? true : false,
        isCodefresh: process.env.CF_BUILD_ID ? true : false,
        isWoodpecker: process.env.CI_PIPELINE_ID && process.env.CI_REPO ? true : false,
        isHarness: process.env.HARNESS_BUILD_ID ? true : false,
        isRender: process.env.RENDER ? true : false,
        isRailway: process.env.RAILWAY_ENVIRONMENT_ID ? true : false,
        isFlyio: process.env.FLY_APP_NAME ? true : false
      },
      systemInfo: {
        nodeVersion: env.nodeVersion,
        platform: env.platform,
        architecture: env.architecture,
        osType: env.osType,
        osRelease: env.osRelease,
        workingDirectory: env.workingDir
      }
    };

    // Add container environment information if requested
    if (includeContainers) {
      reportObj.containerEnvironment = {
        isDocker: env.isDocker || false,
        isKubernetes: env.isKubernetes || false,
        isDockerCompose: env.isDockerCompose || false,
        isDockerSwarm: env.isDockerSwarm || false,
        isContainerized: env.isContainerized || false
      };
    }

    // Add cloud environment information if requested
    if (includeCloud) {
      reportObj.cloudEnvironment = {
        isAWS: env.isAWS || false,
        isAzure: env.isAzure || false,
        isGCP: env.isGCP || false,
        isCloudEnvironment: env.isCloudEnvironment || false,
        isLambda: env.isLambda || false,
        isAzureFunctions: env.isAzureFunctions || false,
        isCloudFunctions: env.isCloudFunctions || false,
        isServerless: env.isServerless || false
      };
    }

    // Add CI-specific information
    switch (ciType) {
      case 'github':
        reportObj.github = {
          workflow: process.env.GITHUB_WORKFLOW || 'unknown',
          repository: process.env.GITHUB_REPOSITORY || 'unknown',
          ref: process.env.GITHUB_REF || 'unknown',
          sha: process.env.GITHUB_SHA || 'unknown',
          actor: process.env.GITHUB_ACTOR || 'unknown',
          event: process.env.GITHUB_EVENT_NAME || 'unknown',
          runId: process.env.GITHUB_RUN_ID || 'unknown',
          runNumber: process.env.GITHUB_RUN_NUMBER || 'unknown'
        };
        break;
      case 'jenkins':
        reportObj.jenkins = {
          job: process.env.JOB_NAME || 'unknown',
          build: process.env.BUILD_NUMBER || 'unknown',
          url: process.env.JENKINS_URL || 'unknown',
          workspace: process.env.WORKSPACE || 'unknown',
          nodeName: process.env.NODE_NAME || 'unknown',
          buildUrl: process.env.BUILD_URL || 'unknown'
        };
        break;
      case 'gitlab':
        reportObj.gitlab = {
          job: process.env.CI_JOB_NAME || 'unknown',
          pipeline: process.env.CI_PIPELINE_ID || 'unknown',
          project: process.env.CI_PROJECT_PATH || 'unknown',
          commit: process.env.CI_COMMIT_SHA || 'unknown',
          branch: process.env.CI_COMMIT_REF_NAME || 'unknown',
          jobUrl: process.env.CI_JOB_URL || 'unknown',
          pipelineUrl: process.env.CI_PIPELINE_URL || 'unknown'
        };
        break;
      case 'circle':
        reportObj.circle = {
          job: process.env.CIRCLE_JOB || 'unknown',
          build: process.env.CIRCLE_BUILD_NUM || 'unknown',
          project: process.env.CIRCLE_PROJECT_REPONAME || 'unknown',
          branch: process.env.CIRCLE_BRANCH || 'unknown',
          sha: process.env.CIRCLE_SHA1 || 'unknown',
          username: process.env.CIRCLE_USERNAME || 'unknown',
          buildUrl: process.env.CIRCLE_BUILD_URL || 'unknown'
        };
        break;
      case 'travis':
        reportObj.travis = {
          job: process.env.TRAVIS_JOB_NAME || 'unknown',
          build: process.env.TRAVIS_BUILD_NUMBER || 'unknown',
          repo: process.env.TRAVIS_REPO_SLUG || 'unknown',
          branch: process.env.TRAVIS_BRANCH || 'unknown',
          commit: process.env.TRAVIS_COMMIT || 'unknown',
          buildId: process.env.TRAVIS_BUILD_ID || 'unknown',
          jobId: process.env.TRAVIS_JOB_ID || 'unknown'
        };
        break;
      case 'azure':
        reportObj.azure = {
          build: process.env.BUILD_BUILDNUMBER || 'unknown',
          definition: process.env.BUILD_DEFINITIONNAME || 'unknown',
          repository: process.env.BUILD_REPOSITORY_NAME || 'unknown',
          branch: process.env.BUILD_SOURCEBRANCHNAME || 'unknown',
          commit: process.env.BUILD_SOURCEVERSION || 'unknown',
          buildId: process.env.BUILD_BUILDID || 'unknown',
          buildUrl: process.env.SYSTEM_TEAMFOUNDATIONCOLLECTIONURI
            ? `${process.env.SYSTEM_TEAMFOUNDATIONCOLLECTIONURI}${process.env.SYSTEM_TEAMPROJECT}/_build/results?buildId=${process.env.BUILD_BUILDID}`
            : 'unknown'
        };
        break;
      case 'teamcity':
        reportObj.teamcity = {
          build: process.env.BUILD_NUMBER || 'unknown',
          configuration: process.env.TEAMCITY_BUILDCONF_NAME || 'unknown',
          project: process.env.TEAMCITY_PROJECT_NAME || 'unknown',
          version: process.env.TEAMCITY_VERSION || 'unknown',
          buildType: process.env.TEAMCITY_BUILD_PROPERTIES_FILE || 'unknown'
        };
        break;
      case 'bitbucket':
        reportObj.bitbucket = {
          build: process.env.BITBUCKET_BUILD_NUMBER || 'unknown',
          commit: process.env.BITBUCKET_COMMIT || 'unknown',
          branch: process.env.BITBUCKET_BRANCH || 'unknown',
          repo: process.env.BITBUCKET_REPO_SLUG || 'unknown',
          workspace: process.env.BITBUCKET_WORKSPACE || 'unknown'
        };
        break;
      case 'appveyor':
        reportObj.appveyor = {
          build: process.env.APPVEYOR_BUILD_NUMBER || 'unknown',
          job: process.env.APPVEYOR_JOB_ID || 'unknown',
          project: process.env.APPVEYOR_PROJECT_SLUG || 'unknown',
          branch: process.env.APPVEYOR_REPO_BRANCH || 'unknown',
          commit: process.env.APPVEYOR_REPO_COMMIT || 'unknown'
        };
        break;
      case 'drone':
        reportObj.drone = {
          build: process.env.DRONE_BUILD_NUMBER || 'unknown',
          repo: process.env.DRONE_REPO || 'unknown',
          branch: process.env.DRONE_BRANCH || 'unknown',
          commit: process.env.DRONE_COMMIT || 'unknown',
          buildLink: process.env.DRONE_BUILD_LINK || 'unknown'
        };
        break;
      case 'buddy':
        reportObj.buddy = {
          pipeline: process.env.BUDDY_PIPELINE_ID || 'unknown',
          execution: process.env.BUDDY_EXECUTION_ID || 'unknown',
          workspace: process.env.BUDDY_WORKSPACE_ID || 'unknown',
          project: process.env.BUDDY_PROJECT_NAME || 'unknown'
        };
        break;
      case 'buildkite':
        reportObj.buildkite = {
          build: process.env.BUILDKITE_BUILD_NUMBER || 'unknown',
          branch: process.env.BUILDKITE_BRANCH || 'unknown',
          commit: process.env.BUILDKITE_COMMIT || 'unknown',
          pipeline: process.env.BUILDKITE_PIPELINE_SLUG || 'unknown',
          buildUrl: process.env.BUILDKITE_BUILD_URL || 'unknown'
        };
        break;
      case 'codebuild':
        reportObj.codebuild = {
          build: process.env.CODEBUILD_BUILD_ID || 'unknown',
          arn: process.env.CODEBUILD_BUILD_ARN || 'unknown',
          initiator: process.env.CODEBUILD_INITIATOR || 'unknown',
          region: process.env.AWS_REGION || 'unknown'
        };
        break;
      case 'vercel':
        reportObj.vercel = {
          environment: process.env.VERCEL_ENV || 'unknown',
          region: process.env.VERCEL_REGION || 'unknown',
          url: process.env.VERCEL_URL || 'unknown',
          gitCommitSha: process.env.VERCEL_GIT_COMMIT_SHA || 'unknown',
          gitCommitMessage: process.env.VERCEL_GIT_COMMIT_MESSAGE || 'unknown'
        };
        break;
      case 'netlify':
        reportObj.netlify = {
          buildId: process.env.NETLIFY_BUILD_ID || 'unknown',
          site: process.env.NETLIFY_SITE_NAME || 'unknown',
          deployUrl: process.env.DEPLOY_URL || 'unknown',
          context: process.env.CONTEXT || 'unknown'
        };
        break;
      case 'heroku':
        reportObj.heroku = {
          appId: process.env.HEROKU_APP_ID || 'unknown',
          appName: process.env.HEROKU_APP_NAME || 'unknown',
          dynoId: process.env.HEROKU_DYNO_ID || 'unknown',
          releaseVersion: process.env.HEROKU_RELEASE_VERSION || 'unknown'
        };
        break;
      case 'semaphore':
        reportObj.semaphore = {
          workflowId: process.env.SEMAPHORE_WORKFLOW_ID || 'unknown',
          pipelineId: process.env.SEMAPHORE_PIPELINE_ID || 'unknown',
          jobId: process.env.SEMAPHORE_JOB_ID || 'unknown',
          projectName: process.env.SEMAPHORE_PROJECT_NAME || 'unknown'
        };
        break;
      case 'codefresh':
        reportObj.codefresh = {
          buildId: process.env.CF_BUILD_ID || 'unknown',
          buildUrl: process.env.CF_BUILD_URL || 'unknown',
          branch: process.env.CF_BRANCH || 'unknown',
          commit: process.env.CF_REVISION || 'unknown'
        };
        break;
      case 'woodpecker':
        reportObj.woodpecker = {
          pipelineId: process.env.CI_PIPELINE_ID || 'unknown',
          repo: process.env.CI_REPO || 'unknown',
          branch: process.env.CI_BRANCH || 'unknown',
          commit: process.env.CI_COMMIT || 'unknown'
        };
        break;
      case 'harness':
        reportObj.harness = {
          buildId: process.env.HARNESS_BUILD_ID || 'unknown',
          accountId: process.env.HARNESS_ACCOUNT_ID || 'unknown',
          pipelineId: process.env.HARNESS_PIPELINE_ID || 'unknown',
          stageName: process.env.HARNESS_STAGE_NAME || 'unknown'
        };
        break;
      case 'render':
        reportObj.render = {
          serviceId: process.env.RENDER_SERVICE_ID || 'unknown',
          instanceId: process.env.RENDER_INSTANCE_ID || 'unknown',
          gitBranch: process.env.RENDER_GIT_BRANCH || 'unknown',
          gitCommit: process.env.RENDER_GIT_COMMIT || 'unknown'
        };
        break;
      case 'railway':
        reportObj.railway = {
          environmentId: process.env.RAILWAY_ENVIRONMENT_ID || 'unknown',
          projectId: process.env.RAILWAY_PROJECT_ID || 'unknown',
          serviceId: process.env.RAILWAY_SERVICE_ID || 'unknown',
          deploymentId: process.env.RAILWAY_DEPLOYMENT_ID || 'unknown'
        };
        break;
      case 'flyio':
        reportObj.flyio = {
          appName: process.env.FLY_APP_NAME || 'unknown',
          region: process.env.FLY_REGION || 'unknown',
          allocationId: process.env.FLY_ALLOC_ID || 'unknown',
          instanceId: process.env.FLY_INSTANCE_ID || 'unknown'
        };
        break;
      default:
        reportObj.generic = {
          ci: process.env.CI || 'true'
        };
        break;
    }

    // Include detailed system info if requested
    if (includeSystemInfo) {
      reportObj.detailedSystemInfo = {
        hostname: env.hostname,
        username: env.username,
        memory: {
          total: env.memory.total,
          free: env.memory.free,
          totalFormatted: formatBytes(env.memory.total),
          freeFormatted: formatBytes(env.memory.free)
        },
        cpus: env.cpus.length,
        cpuInfo: env.cpus.map(cpu => ({
          model: cpu.model,
          speed: cpu.speed
        }))
      };
    }

    // Include environment variables if requested
    if (includeEnvVars) {
      reportObj.environmentVariables = process.env;
    } else {
      // Include only relevant environment variables
      reportObj.environmentVariables = {
        NODE_ENV: process.env.NODE_ENV || 'not set',
        CI: process.env.CI || 'not set',
        CI_ENVIRONMENT: process.env.CI_ENVIRONMENT || 'not set',
        CI_TYPE: process.env.CI_TYPE || 'not set'
      };
    }

    const jsonReport = JSON.stringify(reportObj, null, 2);

    // Write report to file if path is provided
    if (filePath) {
      safelyWriteFile(filePath, jsonReport);
    }

    return jsonReport;
  }

  // Create text report
  let report = `CI Environment Report
=====================
Generated at: ${new Date().toISOString()}

`;

  if (ciType === 'none') {
    report += 'No CI environment detected\n';

    // Write report to file if path is provided
    if (filePath) {
      safelyWriteFile(filePath, report);
    }

    return report;
  }

  // Add CI detection information
  report += `CI Detection:
- CI: ${env.isCI ? 'Yes' : 'No'}
- CI Type: ${ciType}
- GitHub Actions: ${env.isGitHubActions ? 'Yes' : 'No'}
- Jenkins: ${env.isJenkins ? 'Yes' : 'No'}
- GitLab CI: ${env.isGitLabCI ? 'Yes' : 'No'}
- Circle CI: ${env.isCircleCI ? 'Yes' : 'No'}
- Travis CI: ${env.isTravis ? 'Yes' : 'No'}
- Azure Pipelines: ${env.isAzurePipelines ? 'Yes' : 'No'}
- TeamCity: ${env.isTeamCity ? 'Yes' : 'No'}
- Bitbucket: ${env.isBitbucket ? 'Yes' : 'No'}
- AppVeyor: ${env.isAppVeyor ? 'Yes' : 'No'}
- Drone CI: ${env.isDroneCI ? 'Yes' : 'No'}
- Buddy CI: ${env.isBuddyCI ? 'Yes' : 'No'}
- Buildkite: ${env.isBuildkite ? 'Yes' : 'No'}
- CodeBuild: ${env.isCodeBuild ? 'Yes' : 'No'}
- Vercel: ${process.env.VERCEL || process.env.NOW_BUILDER ? 'Yes' : 'No'}
- Netlify: ${process.env.NETLIFY ? 'Yes' : 'No'}
- Heroku: ${process.env.HEROKU_TEST_RUN_ID ? 'Yes' : 'No'}
- Semaphore: ${process.env.SEMAPHORE ? 'Yes' : 'No'}
- Codefresh: ${process.env.CF_BUILD_ID ? 'Yes' : 'No'}
- Woodpecker: ${process.env.CI_PIPELINE_ID && process.env.CI_REPO ? 'Yes' : 'No'}
- Harness: ${process.env.HARNESS_BUILD_ID ? 'Yes' : 'No'}
- Render: ${process.env.RENDER ? 'Yes' : 'No'}
- Railway: ${process.env.RAILWAY_ENVIRONMENT_ID ? 'Yes' : 'No'}
- Fly.io: ${process.env.FLY_APP_NAME ? 'Yes' : 'No'}

`;

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
Run ID: ${process.env.GITHUB_RUN_ID || 'unknown'}
Run Number: ${process.env.GITHUB_RUN_NUMBER || 'unknown'}
`;
      break;
    case 'jenkins':
      report += `Jenkins
-------
Job: ${process.env.JOB_NAME || 'unknown'}
Build: ${process.env.BUILD_NUMBER || 'unknown'}
URL: ${process.env.JENKINS_URL || 'unknown'}
Workspace: ${process.env.WORKSPACE || 'unknown'}
Node Name: ${process.env.NODE_NAME || 'unknown'}
Build URL: ${process.env.BUILD_URL || 'unknown'}
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
Job URL: ${process.env.CI_JOB_URL || 'unknown'}
Pipeline URL: ${process.env.CI_PIPELINE_URL || 'unknown'}
`;
      break;
    case 'circle':
      report += `Circle CI
---------
Job: ${process.env.CIRCLE_JOB || 'unknown'}
Build: ${process.env.CIRCLE_BUILD_NUM || 'unknown'}
Project: ${process.env.CIRCLE_PROJECT_REPONAME || 'unknown'}
Branch: ${process.env.CIRCLE_BRANCH || 'unknown'}
SHA: ${process.env.CIRCLE_SHA1 || 'unknown'}
Username: ${process.env.CIRCLE_USERNAME || 'unknown'}
Build URL: ${process.env.CIRCLE_BUILD_URL || 'unknown'}
`;
      break;
    case 'travis':
      report += `Travis CI
---------
Job: ${process.env.TRAVIS_JOB_NAME || 'unknown'}
Build: ${process.env.TRAVIS_BUILD_NUMBER || 'unknown'}
Repo: ${process.env.TRAVIS_REPO_SLUG || 'unknown'}
Branch: ${process.env.TRAVIS_BRANCH || 'unknown'}
Commit: ${process.env.TRAVIS_COMMIT || 'unknown'}
Build ID: ${process.env.TRAVIS_BUILD_ID || 'unknown'}
Job ID: ${process.env.TRAVIS_JOB_ID || 'unknown'}
`;
      break;
    case 'azure':
      report += `Azure Pipelines
--------------
Build: ${process.env.BUILD_BUILDNUMBER || 'unknown'}
Definition: ${process.env.BUILD_DEFINITIONNAME || 'unknown'}
Repository: ${process.env.BUILD_REPOSITORY_NAME || 'unknown'}
Branch: ${process.env.BUILD_SOURCEBRANCHNAME || 'unknown'}
Commit: ${process.env.BUILD_SOURCEVERSION || 'unknown'}
Build ID: ${process.env.BUILD_BUILDID || 'unknown'}
`;
      break;
    case 'teamcity':
      report += `TeamCity
--------
Build: ${process.env.BUILD_NUMBER || 'unknown'}
Configuration: ${process.env.TEAMCITY_BUILDCONF_NAME || 'unknown'}
Project: ${process.env.TEAMCITY_PROJECT_NAME || 'unknown'}
Version: ${process.env.TEAMCITY_VERSION || 'unknown'}
`;
      break;
    case 'bitbucket':
      report += `Bitbucket Pipelines
------------------
Build: ${process.env.BITBUCKET_BUILD_NUMBER || 'unknown'}
Commit: ${process.env.BITBUCKET_COMMIT || 'unknown'}
Branch: ${process.env.BITBUCKET_BRANCH || 'unknown'}
Repo: ${process.env.BITBUCKET_REPO_SLUG || 'unknown'}
Workspace: ${process.env.BITBUCKET_WORKSPACE || 'unknown'}
`;
      break;
    case 'appveyor':
      report += `AppVeyor
--------
Build: ${process.env.APPVEYOR_BUILD_NUMBER || 'unknown'}
Job: ${process.env.APPVEYOR_JOB_ID || 'unknown'}
Project: ${process.env.APPVEYOR_PROJECT_SLUG || 'unknown'}
Branch: ${process.env.APPVEYOR_REPO_BRANCH || 'unknown'}
Commit: ${process.env.APPVEYOR_REPO_COMMIT || 'unknown'}
`;
      break;
    case 'drone':
      report += `Drone CI
--------
Build: ${process.env.DRONE_BUILD_NUMBER || 'unknown'}
Repo: ${process.env.DRONE_REPO || 'unknown'}
Branch: ${process.env.DRONE_BRANCH || 'unknown'}
Commit: ${process.env.DRONE_COMMIT || 'unknown'}
Build Link: ${process.env.DRONE_BUILD_LINK || 'unknown'}
`;
      break;
    case 'buddy':
      report += `Buddy CI
--------
Pipeline: ${process.env.BUDDY_PIPELINE_ID || 'unknown'}
Execution: ${process.env.BUDDY_EXECUTION_ID || 'unknown'}
Workspace: ${process.env.BUDDY_WORKSPACE_ID || 'unknown'}
Project: ${process.env.BUDDY_PROJECT_NAME || 'unknown'}
`;
      break;
    case 'buildkite':
      report += `Buildkite
---------
Build: ${process.env.BUILDKITE_BUILD_NUMBER || 'unknown'}
Branch: ${process.env.BUILDKITE_BRANCH || 'unknown'}
Commit: ${process.env.BUILDKITE_COMMIT || 'unknown'}
Pipeline: ${process.env.BUILDKITE_PIPELINE_SLUG || 'unknown'}
Build URL: ${process.env.BUILDKITE_BUILD_URL || 'unknown'}
`;
      break;
    case 'codebuild':
      report += `AWS CodeBuild
-------------
Build: ${process.env.CODEBUILD_BUILD_ID || 'unknown'}
ARN: ${process.env.CODEBUILD_BUILD_ARN || 'unknown'}
Initiator: ${process.env.CODEBUILD_INITIATOR || 'unknown'}
Region: ${process.env.AWS_REGION || 'unknown'}
`;
      break;
    case 'vercel':
      report += `Vercel
------
Environment: ${process.env.VERCEL_ENV || 'unknown'}
Region: ${process.env.VERCEL_REGION || 'unknown'}
URL: ${process.env.VERCEL_URL || 'unknown'}
Git Commit SHA: ${process.env.VERCEL_GIT_COMMIT_SHA || 'unknown'}
Git Commit Message: ${process.env.VERCEL_GIT_COMMIT_MESSAGE || 'unknown'}
`;
      break;
    case 'netlify':
      report += `Netlify
-------
Build ID: ${process.env.NETLIFY_BUILD_ID || 'unknown'}
Site: ${process.env.NETLIFY_SITE_NAME || 'unknown'}
Deploy URL: ${process.env.DEPLOY_URL || 'unknown'}
Context: ${process.env.CONTEXT || 'unknown'}
`;
      break;
    case 'heroku':
      report += `Heroku
------
App ID: ${process.env.HEROKU_APP_ID || 'unknown'}
App Name: ${process.env.HEROKU_APP_NAME || 'unknown'}
Dyno ID: ${process.env.HEROKU_DYNO_ID || 'unknown'}
Release Version: ${process.env.HEROKU_RELEASE_VERSION || 'unknown'}
`;
      break;
    case 'semaphore':
      report += `Semaphore CI
-----------
Workflow ID: ${process.env.SEMAPHORE_WORKFLOW_ID || 'unknown'}
Pipeline ID: ${process.env.SEMAPHORE_PIPELINE_ID || 'unknown'}
Job ID: ${process.env.SEMAPHORE_JOB_ID || 'unknown'}
Project Name: ${process.env.SEMAPHORE_PROJECT_NAME || 'unknown'}
`;
      break;
    case 'codefresh':
      report += `Codefresh
---------
Build ID: ${process.env.CF_BUILD_ID || 'unknown'}
Build URL: ${process.env.CF_BUILD_URL || 'unknown'}
Branch: ${process.env.CF_BRANCH || 'unknown'}
Commit: ${process.env.CF_REVISION || 'unknown'}
`;
      break;
    case 'woodpecker':
      report += `Woodpecker CI
-------------
Pipeline ID: ${process.env.CI_PIPELINE_ID || 'unknown'}
Repo: ${process.env.CI_REPO || 'unknown'}
Branch: ${process.env.CI_BRANCH || 'unknown'}
Commit: ${process.env.CI_COMMIT || 'unknown'}
`;
      break;
    case 'harness':
      report += `Harness CI
---------
Build ID: ${process.env.HARNESS_BUILD_ID || 'unknown'}
Account ID: ${process.env.HARNESS_ACCOUNT_ID || 'unknown'}
Pipeline ID: ${process.env.HARNESS_PIPELINE_ID || 'unknown'}
Stage Name: ${process.env.HARNESS_STAGE_NAME || 'unknown'}
`;
      break;
    case 'render':
      report += `Render
------
Service ID: ${process.env.RENDER_SERVICE_ID || 'unknown'}
Instance ID: ${process.env.RENDER_INSTANCE_ID || 'unknown'}
Git Branch: ${process.env.RENDER_GIT_BRANCH || 'unknown'}
Git Commit: ${process.env.RENDER_GIT_COMMIT || 'unknown'}
`;
      break;
    case 'railway':
      report += `Railway
-------
Environment ID: ${process.env.RAILWAY_ENVIRONMENT_ID || 'unknown'}
Project ID: ${process.env.RAILWAY_PROJECT_ID || 'unknown'}
Service ID: ${process.env.RAILWAY_SERVICE_ID || 'unknown'}
Deployment ID: ${process.env.RAILWAY_DEPLOYMENT_ID || 'unknown'}
`;
      break;
    case 'flyio':
      report += `Fly.io
------
App Name: ${process.env.FLY_APP_NAME || 'unknown'}
Region: ${process.env.FLY_REGION || 'unknown'}
Allocation ID: ${process.env.FLY_ALLOC_ID || 'unknown'}
Instance ID: ${process.env.FLY_INSTANCE_ID || 'unknown'}
`;
      break;
    default:
      report += `Generic CI
----------
CI environment detected
`;
      break;
  }

  // Add container environment information if requested
  if (includeContainers) {
    report += `
Container Environment
-------------------
Docker: ${env.isDocker ? 'Yes' : 'No'}
Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}
Docker Compose: ${env.isDockerCompose ? 'Yes' : 'No'}
Docker Swarm: ${env.isDockerSwarm ? 'Yes' : 'No'}
Containerized: ${env.isContainerized ? 'Yes' : 'No'}
`;
  }

  // Add cloud environment information if requested
  if (includeCloud) {
    report += `
Cloud Environment
---------------
AWS: ${env.isAWS ? 'Yes' : 'No'}
Azure: ${env.isAzure ? 'Yes' : 'No'}
GCP: ${env.isGCP ? 'Yes' : 'No'}
Cloud Environment: ${env.isCloudEnvironment ? 'Yes' : 'No'}
Lambda: ${env.isLambda ? 'Yes' : 'No'}
Azure Functions: ${env.isAzureFunctions ? 'Yes' : 'No'}
Cloud Functions: ${env.isCloudFunctions ? 'Yes' : 'No'}
Serverless: ${env.isServerless ? 'Yes' : 'No'}
`;
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

  // Add detailed system information if requested
  if (includeSystemInfo) {
    report += `
Detailed System Information
-------------------------
Hostname: ${env.hostname || 'unknown'}
Username: ${env.username || 'unknown'}
Memory Total: ${formatBytes(env.memory.total)}
Memory Free: ${formatBytes(env.memory.free)}
CPUs: ${env.cpus.length}
`;
  }

  // Add environment variables
  report += `
Environment Variables
-------------------
NODE_ENV: ${process.env.NODE_ENV || 'not set'}
CI: ${process.env.CI || 'not set'}
CI_ENVIRONMENT: ${process.env.CI_ENVIRONMENT || 'not set'}
CI_TYPE: ${process.env.CI_TYPE || 'not set'}
`;

  // Add all environment variables if requested
  if (includeEnvVars) {
    report += formatEnvironmentVariables();
  }

  // Write report to file if path is provided
  if (filePath) {
    safelyWriteFile(filePath, report);
  }

  return report;
}

/**
 * Format bytes to a human-readable string
 * @param {number} bytes - Bytes to format
 * @returns {string} Formatted string
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format environment variables for the report
 * @returns {string} Formatted environment variables
 */
function formatEnvironmentVariables() {
  let result = '\nAll Environment Variables:\n';

  // Get all environment variables and sort them
  const envVars = Object.keys(process.env).sort();

  // Format each variable
  for (const key of envVars) {
    // Skip sensitive variables
    if (key.includes('KEY') || key.includes('SECRET') || key.includes('TOKEN') || key.includes('PASSWORD')) {
      result += `- ${key}: [REDACTED]\n`;
    } else {
      result += `- ${key}: ${process.env[key]}\n`;
    }
  }

  return result;
}

module.exports = {
  detectCIEnvironmentType,
  createCIDirectories,
  createCIMarkerFiles,
  setupCIEnvironment,
  createCIReport,
  formatBytes,
  formatEnvironmentVariables
};
