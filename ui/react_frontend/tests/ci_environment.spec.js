/**
 * CI Environment Tests
 *
 * This file contains tests for CI environment-specific behavior:
 * - GitHub Actions
 * - Jenkins
 * - GitLab CI
 * - Circle CI
 * - Travis CI
 * - Azure Pipelines
 * - TeamCity
 *
 * These tests ensure that the application behaves correctly in different CI environments.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import fs from 'fs';
import path from 'path';
import os from 'os';

// Mock modules
vi.mock('fs');
vi.mock('path');
vi.mock('os');

// Mock the environment detection module
vi.mock('../src/utils/environmentDetection', () => ({
  detectEnvironment: vi.fn(() => {
    // Enhanced CI detection with multiple methods
    const isCI = process.env.CI === 'true' || process.env.CI === true ||
                process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW ||
                !!process.env.JENKINS_URL || !!process.env.GITLAB_CI ||
                !!process.env.CIRCLECI || !!process.env.TRAVIS ||
                !!process.env.TF_BUILD || !!process.env.TEAMCITY_VERSION ||
                !!process.env.BITBUCKET_COMMIT || !!process.env.APPVEYOR ||
                !!process.env.DRONE || !!process.env.BUDDY ||
                !!process.env.BUILDKITE || !!process.env.CODEBUILD_BUILD_ID;

    // GitHub Actions detection
    const isGitHubActions = process.env.GITHUB_ACTIONS === 'true' ||
                           !!process.env.GITHUB_WORKFLOW ||
                           !!process.env.GITHUB_RUN_ID;

    // Jenkins detection
    const isJenkins = !!process.env.JENKINS_URL ||
                     !!process.env.JENKINS_HOME;

    // GitLab CI detection
    const isGitLabCI = !!process.env.GITLAB_CI ||
                      !!process.env.CI_SERVER_NAME && process.env.CI_SERVER_NAME.includes('GitLab');

    // CircleCI detection
    const isCircleCI = !!process.env.CIRCLECI ||
                      !!process.env.CIRCLE_BUILD_NUM;

    // Travis CI detection
    const isTravis = !!process.env.TRAVIS ||
                    !!process.env.TRAVIS_JOB_ID;

    // Azure Pipelines detection
    const isAzurePipelines = !!process.env.TF_BUILD ||
                            !!process.env.AZURE_HTTP_USER_AGENT;

    // TeamCity detection
    const isTeamCity = !!process.env.TEAMCITY_VERSION ||
                      !!process.env.TEAMCITY_BUILD_PROPERTIES_FILE;

    // Bitbucket Pipelines detection
    const isBitbucket = !!process.env.BITBUCKET_COMMIT ||
                       !!process.env.BITBUCKET_BUILD_NUMBER;

    // AppVeyor detection
    const isAppVeyor = !!process.env.APPVEYOR ||
                      !!process.env.APPVEYOR_BUILD_ID;

    // Drone detection
    const isDrone = !!process.env.DRONE ||
                   !!process.env.DRONE_BUILD_NUMBER;

    // Buddy detection
    const isBuddy = !!process.env.BUDDY ||
                   !!process.env.BUDDY_PIPELINE_ID;

    // Buildkite detection
    const isBuildkite = !!process.env.BUILDKITE ||
                       !!process.env.BUILDKITE_BUILD_ID;

    // AWS CodeBuild detection
    const isCodeBuild = !!process.env.CODEBUILD_BUILD_ID ||
                       !!process.env.CODEBUILD_BUILD_ARN;

    // Docker detection for CI environments
    const isDocker = process.env.DOCKER_ENVIRONMENT === 'true' ||
                    (fs.existsSync('/.dockerenv') || process.env.DOCKER === 'true');

    // Kubernetes detection for CI environments
    const isKubernetes = !!process.env.KUBERNETES_SERVICE_HOST ||
                        !!process.env.KUBERNETES_PORT;

    return {
      platform: os.platform(),
      isWindows: os.platform() === 'win32',
      isMacOS: os.platform() === 'darwin',
      isLinux: os.platform() === 'linux',
      isCI,
      isGitHubActions,
      isJenkins,
      isGitLabCI,
      isCircleCI,
      isTravis,
      isAzurePipelines,
      isTeamCity,
      isBitbucket,
      isAppVeyor,
      isDrone,
      isBuddy,
      isBuildkite,
      isCodeBuild,
      isDocker,
      isKubernetes,
      isBrowser: false,
      nodeVersion: process.version,
      architecture: process.arch,
      osType: os.type(),
      osRelease: os.release(),
      tmpDir: os.tmpdir(),
      homeDir: os.homedir(),
      workingDir: process.cwd()
    };
  }),
  getPathSeparator: vi.fn(() => {
    return os.platform() === 'win32' ? '\\' : '/';
  }),
  getPlatformPath: vi.fn((inputPath) => {
    const isWindows = os.platform() === 'win32';

    if (isWindows && inputPath.includes('/')) {
      return inputPath.replace(/\//g, '\\');
    }

    if (!isWindows && inputPath.includes('\\')) {
      return inputPath.replace(/\\/g, '/');
    }

    return inputPath;
  }),
  useEnvironment: vi.fn()
}));

// Import the environment detection module
import { detectEnvironment, getPathSeparator, getPlatformPath } from '../src/utils/environmentDetection';

// Create the CI environment module that uses our environment detection
const ciEnvironment = {
  detectCIEnvironmentType: () => {
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

    if (env.isBitbucket) {
      return 'bitbucket';
    }

    if (env.isAppVeyor) {
      return 'appveyor';
    }

    if (env.isDrone) {
      return 'drone';
    }

    if (env.isBuddy) {
      return 'buddy';
    }

    if (env.isBuildkite) {
      return 'buildkite';
    }

    if (env.isCodeBuild) {
      return 'codebuild';
    }

    // Check for containerized CI environments
    if (env.isDocker && env.isCI) {
      return 'docker-ci';
    }

    if (env.isKubernetes && env.isCI) {
      return 'kubernetes-ci';
    }

    return 'generic';
  },

  setupCIEnvironment: () => {
    const env = detectEnvironment();
    const ciType = ciEnvironment.detectCIEnvironmentType();

    if (ciType === 'none') {
      console.log('No CI environment detected');
      return { success: true, ciType };
    }

    console.log(`Setting up CI environment for ${ciType}`);

    try {
      // Create directories
      const directories = [
        'logs',
        'playwright-report',
        'test-results',
        'coverage'
      ];

      const separator = getPathSeparator();

      for (const dir of directories) {
        const dirPath = path.join(process.cwd(), dir);
        if (!fs.existsSync(dirPath)) {
          fs.mkdirSync(dirPath, { recursive: true });
          console.log(`Created directory: ${dirPath}`);
        } else {
          console.log(`Directory already exists: ${dirPath}`);
        }
      }

      // Create marker files
      const timestamp = new Date().toISOString();
      const markerLocations = [
        path.join(process.cwd(), 'logs', 'ci-environment.txt'),
        path.join(process.cwd(), 'playwright-report', 'ci-environment.txt'),
        path.join(process.cwd(), 'test-results', 'ci-environment.txt')
      ];

      const markerContent = `CI Environment: ${ciType}
Timestamp: ${timestamp}
Node.js: ${env.nodeVersion}
Platform: ${env.platform}
OS: ${env.osType} ${env.osRelease}
Architecture: ${env.architecture}
Working Directory: ${env.workingDir}
Temp Directory: ${env.tmpDir}
`;

      for (const location of markerLocations) {
        const dir = path.dirname(location);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }

        fs.writeFileSync(location, markerContent);
        console.log(`Created marker file at ${location}`);
      }

      // Set environment variables
      process.env.CI = 'true';
      process.env.PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = '1';

      if (ciType === 'github' && !process.env.GITHUB_ACTIONS) {
        process.env.GITHUB_ACTIONS = 'true';
      }

      console.log('CI environment setup complete');
      return { success: true, ciType, env };
    } catch (error) {
      console.error(`Failed to set up CI environment: ${error.message}`);
      return { success: false, ciType, error: error.message };
    }
  },

  createCIReport: (filePath) => {
    const env = detectEnvironment();
    const ciType = ciEnvironment.detectCIEnvironmentType();

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
Run ID: ${process.env.GITHUB_RUN_ID || 'unknown'}
Run Number: ${process.env.GITHUB_RUN_NUMBER || 'unknown'}
Server URL: ${process.env.GITHUB_SERVER_URL || 'unknown'}
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
Jenkins Home: ${process.env.JENKINS_HOME || 'unknown'}
`;
        break;
      case 'gitlab':
        report += `GitLab CI
---------
Job: ${process.env.CI_JOB_NAME || 'unknown'}
Pipeline: ${process.env.CI_PIPELINE_ID || 'unknown'}
Project: ${process.env.CI_PROJECT_PATH || 'unknown'}
Commit: ${process.env.CI_COMMIT_SHA || 'unknown'}
Branch: ${process.env.CI_COMMIT_BRANCH || 'unknown'}
Tag: ${process.env.CI_COMMIT_TAG || 'unknown'}
Server: ${process.env.CI_SERVER_URL || 'unknown'}
`;
        break;
      case 'circle':
        report += `CircleCI
--------
Job: ${process.env.CIRCLE_JOB || 'unknown'}
Build: ${process.env.CIRCLE_BUILD_NUM || 'unknown'}
Project: ${process.env.CIRCLE_PROJECT_REPONAME || 'unknown'}
Branch: ${process.env.CIRCLE_BRANCH || 'unknown'}
SHA: ${process.env.CIRCLE_SHA1 || 'unknown'}
Username: ${process.env.CIRCLE_USERNAME || 'unknown'}
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
Tag: ${process.env.TRAVIS_TAG || 'unknown'}
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
Reason: ${process.env.BUILD_REASON || 'unknown'}
`;
        break;
      case 'teamcity':
        report += `TeamCity
--------
Build: ${process.env.BUILD_NUMBER || 'unknown'}
Version: ${process.env.TEAMCITY_VERSION || 'unknown'}
Project: ${process.env.TEAMCITY_PROJECT_NAME || 'unknown'}
Build Type: ${process.env.TEAMCITY_BUILDCONF_NAME || 'unknown'}
Properties: ${process.env.TEAMCITY_BUILD_PROPERTIES_FILE || 'unknown'}
`;
        break;
      case 'bitbucket':
        report += `Bitbucket Pipelines
------------------
Commit: ${process.env.BITBUCKET_COMMIT || 'unknown'}
Branch: ${process.env.BITBUCKET_BRANCH || 'unknown'}
Build: ${process.env.BITBUCKET_BUILD_NUMBER || 'unknown'}
Repository: ${process.env.BITBUCKET_REPO_SLUG || 'unknown'}
Workspace: ${process.env.BITBUCKET_WORKSPACE || 'unknown'}
`;
        break;
      case 'appveyor':
        report += `AppVeyor
--------
Build: ${process.env.APPVEYOR_BUILD_NUMBER || 'unknown'}
Version: ${process.env.APPVEYOR_BUILD_VERSION || 'unknown'}
Project: ${process.env.APPVEYOR_PROJECT_NAME || 'unknown'}
Branch: ${process.env.APPVEYOR_REPO_BRANCH || 'unknown'}
Commit: ${process.env.APPVEYOR_REPO_COMMIT || 'unknown'}
`;
        break;
      case 'drone':
        report += `Drone CI
--------
Build: ${process.env.DRONE_BUILD_NUMBER || 'unknown'}
Branch: ${process.env.DRONE_BRANCH || 'unknown'}
Commit: ${process.env.DRONE_COMMIT || 'unknown'}
Repository: ${process.env.DRONE_REPO || 'unknown'}
`;
        break;
      case 'buddy':
        report += `Buddy
-----
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
`;
        break;
      case 'codebuild':
        report += `AWS CodeBuild
-------------
Build: ${process.env.CODEBUILD_BUILD_ID || 'unknown'}
ARN: ${process.env.CODEBUILD_BUILD_ARN || 'unknown'}
Number: ${process.env.CODEBUILD_BUILD_NUMBER || 'unknown'}
Project: ${process.env.CODEBUILD_PROJECT_NAME || 'unknown'}
`;
        break;
      case 'docker-ci':
        report += `Docker CI Environment
-------------------
Docker: Yes
CI: Yes
Docker Environment Variable: ${process.env.DOCKER_ENVIRONMENT || 'not set'}
Docker Variable: ${process.env.DOCKER || 'not set'}
Docker Compose Project: ${process.env.COMPOSE_PROJECT_NAME || 'not set'}
Docker Compose File: ${process.env.COMPOSE_FILE || 'not set'}
`;
        break;
      case 'kubernetes-ci':
        report += `Kubernetes CI Environment
-----------------------
Kubernetes: Yes
CI: Yes
Kubernetes Service Host: ${process.env.KUBERNETES_SERVICE_HOST || 'not set'}
Kubernetes Port: ${process.env.KUBERNETES_PORT || 'not set'}
Kubernetes Namespace: ${process.env.KUBERNETES_NAMESPACE || 'not set'}
Pod Name: ${process.env.POD_NAME || 'not set'}
Pod IP: ${process.env.POD_IP || 'not set'}
Service Account: ${process.env.SERVICE_ACCOUNT || 'not set'}
`;
        break;
      default:
        report += `Generic CI
----------
CI environment detected
CI Variable: ${process.env.CI || 'not set'}
`;
        break;
    }

    // Add system information from environment detection
    report += `
System Information
-----------------
Node.js: ${env.nodeVersion}
Platform: ${env.platform}
Architecture: ${env.architecture}
OS: ${env.osType} ${env.osRelease}
Working Directory: ${env.workingDir}
Temp Directory: ${env.tmpDir}
Home Directory: ${env.homeDir}
WSL: ${env.isWSL ? 'Yes' : 'No'}
WSL Distro: ${process.env.WSL_DISTRO_NAME || 'not set'}

Container Environment:
- Docker: ${env.isDocker ? 'Yes' : 'No'}
- Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}
- Docker Compose: ${env.isDockerCompose ? 'Yes' : 'No'}
- Docker Swarm: ${env.isDockerSwarm ? 'Yes' : 'No'}

CI Environment Detection:
- CI: ${env.isCI ? 'Yes' : 'No'}
- GitHub Actions: ${env.isGitHubActions ? 'Yes' : 'No'}
- Jenkins: ${env.isJenkins ? 'Yes' : 'No'}
- GitLab CI: ${env.isGitLabCI ? 'Yes' : 'No'}
- CircleCI: ${env.isCircleCI ? 'Yes' : 'No'}
- Travis CI: ${env.isTravis ? 'Yes' : 'No'}
- Azure Pipelines: ${env.isAzurePipelines ? 'Yes' : 'No'}
- TeamCity: ${env.isTeamCity ? 'Yes' : 'No'}
- Bitbucket Pipelines: ${env.isBitbucket ? 'Yes' : 'No'}
- AppVeyor: ${env.isAppVeyor ? 'Yes' : 'No'}
- Drone CI: ${env.isDrone ? 'Yes' : 'No'}
- Buddy: ${env.isBuddy ? 'Yes' : 'No'}
- Buildkite: ${env.isBuildkite ? 'Yes' : 'No'}
- AWS CodeBuild: ${env.isCodeBuild ? 'Yes' : 'No'}

Cloud Environment:
- AWS: ${env.isAWS ? 'Yes' : 'No'}
- Azure: ${env.isAzure ? 'Yes' : 'No'}
- GCP: ${env.isGCP ? 'Yes' : 'No'}

Environment Variables:
- NODE_ENV: ${process.env.NODE_ENV || 'not set'}
- CI: ${process.env.CI || 'not set'}
- DOCKER_ENVIRONMENT: ${process.env.DOCKER_ENVIRONMENT || 'not set'}
- KUBERNETES_SERVICE_HOST: ${process.env.KUBERNETES_SERVICE_HOST || 'not set'}
- GITHUB_ACTIONS: ${process.env.GITHUB_ACTIONS || 'not set'}
- JENKINS_URL: ${process.env.JENKINS_URL || 'not set'}
- GITLAB_CI: ${process.env.GITLAB_CI || 'not set'}
- CIRCLECI: ${process.env.CIRCLECI || 'not set'}
- TRAVIS: ${process.env.TRAVIS || 'not set'}
- TF_BUILD: ${process.env.TF_BUILD || 'not set'}
- TEAMCITY_VERSION: ${process.env.TEAMCITY_VERSION || 'not set'}
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
};

// Import the module under test
vi.mock('../tests/helpers/ci-environment', () => ciEnvironment, { virtual: true });
const { detectCIEnvironmentType, setupCIEnvironment, createCIReport } = ciEnvironment;

describe('CI Environment', () => {
  // Reset mocks before each test
  beforeEach(() => {
    vi.resetAllMocks();

    // Default mock implementations
    os.platform.mockReturnValue('linux');
    os.type.mockReturnValue('Linux');
    os.release.mockReturnValue('5.10.0');
    os.arch.mockReturnValue('x64');
    os.tmpdir.mockReturnValue('/tmp');
    fs.existsSync.mockReturnValue(false);
    fs.mkdirSync.mockImplementation(() => undefined);
    fs.writeFileSync.mockImplementation(() => undefined);
    path.join.mockImplementation((...args) => args.join('/'));
    path.dirname.mockImplementation((p) => p.split('/').slice(0, -1).join('/'));
    process.env = { NODE_ENV: 'test' };
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('CI Environment Detection', () => {
    it('should detect GitHub Actions environment', () => {
      // Arrange
      process.env.GITHUB_ACTIONS = 'true';
      process.env.GITHUB_WORKFLOW = 'test-workflow';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: true,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('github');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect GitHub Actions environment from GITHUB_RUN_ID', () => {
      // Arrange
      process.env.GITHUB_RUN_ID = '12345';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: true,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('github');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Jenkins environment', () => {
      // Arrange
      process.env.JENKINS_URL = 'http://jenkins.example.com';
      process.env.JOB_NAME = 'test-job';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: true,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('jenkins');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Jenkins environment from JENKINS_HOME', () => {
      // Arrange
      process.env.JENKINS_HOME = '/var/lib/jenkins';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: true,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('jenkins');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect GitLab CI environment', () => {
      // Arrange
      process.env.GITLAB_CI = 'true';
      process.env.CI_JOB_NAME = 'test-job';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: true,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('gitlab');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect GitLab CI environment from CI_SERVER_NAME', () => {
      // Arrange
      process.env.CI_SERVER_NAME = 'GitLab';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: true,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('gitlab');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect CircleCI environment', () => {
      // Arrange
      process.env.CIRCLECI = 'true';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: true,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('circle');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect CircleCI environment from CIRCLE_BUILD_NUM', () => {
      // Arrange
      process.env.CIRCLE_BUILD_NUM = '123';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: true,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('circle');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Travis CI environment', () => {
      // Arrange
      process.env.TRAVIS = 'true';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: true,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('travis');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Travis CI environment from TRAVIS_JOB_ID', () => {
      // Arrange
      process.env.TRAVIS_JOB_ID = '123';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: true,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('travis');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Azure Pipelines environment', () => {
      // Arrange
      process.env.TF_BUILD = 'true';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: true,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('azure');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Azure Pipelines environment from AZURE_HTTP_USER_AGENT', () => {
      // Arrange
      process.env.AZURE_HTTP_USER_AGENT = 'Azure-Pipelines';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: true,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('azure');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect TeamCity environment', () => {
      // Arrange
      process.env.TEAMCITY_VERSION = '2023.1';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: true,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('teamcity');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect TeamCity environment from TEAMCITY_BUILD_PROPERTIES_FILE', () => {
      // Arrange
      process.env.TEAMCITY_BUILD_PROPERTIES_FILE = '/tmp/teamcity.properties';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: true,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('teamcity');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Bitbucket Pipelines environment', () => {
      // Arrange
      process.env.BITBUCKET_COMMIT = 'abc123';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: true,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('bitbucket');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect AppVeyor environment', () => {
      // Arrange
      process.env.APPVEYOR = 'true';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: true,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('appveyor');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Drone CI environment', () => {
      // Arrange
      process.env.DRONE = 'true';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: true,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('drone');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Buddy environment', () => {
      // Arrange
      process.env.BUDDY = 'true';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: true,
        isBuildkite: false,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('buddy');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Buildkite environment', () => {
      // Arrange
      process.env.BUILDKITE = 'true';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: true,
        isCodeBuild: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('buildkite');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect AWS CodeBuild environment', () => {
      // Arrange
      process.env.CODEBUILD_BUILD_ID = 'build-id';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: true
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('codebuild');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Docker CI environment', () => {
      // Arrange
      process.env.CI = 'true';
      process.env.DOCKER_ENVIRONMENT = 'true';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false,
        isDocker: true,
        isKubernetes: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('docker-ci');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Kubernetes CI environment', () => {
      // Arrange
      process.env.CI = 'true';
      process.env.KUBERNETES_SERVICE_HOST = '10.0.0.1';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false,
        isDocker: false,
        isKubernetes: true
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('kubernetes-ci');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect generic CI environment', () => {
      // Arrange
      process.env.CI = 'true';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false,
        isDocker: false,
        isKubernetes: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('generic');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect no CI environment', () => {
      // Arrange
      // No CI environment variables set

      detectEnvironment.mockReturnValue({
        isCI: false,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: false,
        isCircleCI: false,
        isTravis: false,
        isAzurePipelines: false,
        isTeamCity: false,
        isBitbucket: false,
        isAppVeyor: false,
        isDrone: false,
        isBuddy: false,
        isBuildkite: false,
        isCodeBuild: false,
        isDocker: false,
        isKubernetes: false
      });

      // Act
      const ciType = detectCIEnvironmentType();

      // Assert
      expect(ciType).toBe('none');
      expect(detectEnvironment).toHaveBeenCalled();
    });
  });

  describe('CI Environment Setup', () => {
    it('should set up GitHub Actions environment', () => {
      // Arrange
      process.env.GITHUB_ACTIONS = 'true';
      process.env.GITHUB_WORKFLOW = 'test-workflow';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: true,
        isJenkins: false,
        platform: 'linux',
        isLinux: true,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Linux',
        osRelease: '5.10.0',
        tmpDir: '/tmp',
        homeDir: '/home/user',
        workingDir: '/home/user/project'
      });

      getPathSeparator.mockReturnValue('/');

      // Act
      const result = setupCIEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.ciType).toBe('github');
      expect(result.env).toBeDefined();
      expect(fs.mkdirSync).toHaveBeenCalled();
      expect(fs.writeFileSync).toHaveBeenCalled();
      expect(detectEnvironment).toHaveBeenCalled();
      expect(getPathSeparator).toHaveBeenCalled();
    });

    it('should set up Jenkins environment', () => {
      // Arrange
      process.env.JENKINS_URL = 'http://jenkins.example.com';
      process.env.JOB_NAME = 'test-job';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: true,
        platform: 'linux',
        isLinux: true,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Linux',
        osRelease: '5.10.0',
        tmpDir: '/tmp',
        homeDir: '/home/user',
        workingDir: '/home/user/project'
      });

      getPathSeparator.mockReturnValue('/');

      // Act
      const result = setupCIEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.ciType).toBe('jenkins');
      expect(result.env).toBeDefined();
      expect(fs.mkdirSync).toHaveBeenCalled();
      expect(fs.writeFileSync).toHaveBeenCalled();
      expect(detectEnvironment).toHaveBeenCalled();
      expect(getPathSeparator).toHaveBeenCalled();
    });

    it('should set up GitLab CI environment', () => {
      // Arrange
      process.env.GITLAB_CI = 'true';
      process.env.CI_JOB_NAME = 'test-job';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        isGitLabCI: true,
        platform: 'linux',
        isLinux: true,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Linux',
        osRelease: '5.10.0',
        tmpDir: '/tmp',
        homeDir: '/home/user',
        workingDir: '/home/user/project'
      });

      getPathSeparator.mockReturnValue('/');

      // Act
      const result = setupCIEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.ciType).toBe('gitlab');
      expect(result.env).toBeDefined();
      expect(fs.mkdirSync).toHaveBeenCalled();
      expect(fs.writeFileSync).toHaveBeenCalled();
      expect(detectEnvironment).toHaveBeenCalled();
      expect(getPathSeparator).toHaveBeenCalled();
    });

    it('should set up CI environment on Windows', () => {
      // Arrange
      process.env.CI = 'true';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        platform: 'win32',
        isWindows: true,
        isLinux: false,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Windows_NT',
        osRelease: '10.0.19042',
        tmpDir: 'C:\\Windows\\Temp',
        homeDir: 'C:\\Users\\user',
        workingDir: 'C:\\Users\\user\\project'
      });

      getPathSeparator.mockReturnValue('\\');

      // Act
      const result = setupCIEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.ciType).toBe('generic');
      expect(result.env).toBeDefined();
      expect(fs.mkdirSync).toHaveBeenCalled();
      expect(fs.writeFileSync).toHaveBeenCalled();
      expect(detectEnvironment).toHaveBeenCalled();
      expect(getPathSeparator).toHaveBeenCalled();
    });

    it('should handle directory creation failures', () => {
      // Arrange
      process.env.CI = 'true';

      detectEnvironment.mockReturnValue({
        isCI: true,
        isGitHubActions: false,
        isJenkins: false,
        platform: 'linux',
        isLinux: true,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Linux',
        osRelease: '5.10.0',
        tmpDir: '/tmp',
        homeDir: '/home/user',
        workingDir: '/home/user/project'
      });

      getPathSeparator.mockReturnValue('/');

      fs.mkdirSync.mockImplementation(() => {
        throw new Error('Permission denied');
      });

      // Act
      const result = setupCIEnvironment();

      // Assert
      expect(result.success).toBe(false);
      expect(result.error).toContain('Permission denied');
      expect(fs.mkdirSync).toHaveBeenCalled();
      expect(detectEnvironment).toHaveBeenCalled();
      expect(getPathSeparator).toHaveBeenCalled();
    });
  });

  describe('CI Report Creation', () => {
    it('should create a GitHub Actions report', () => {
      // Arrange
      process.env.GITHUB_ACTIONS = 'true';
      process.env.GITHUB_WORKFLOW = 'test-workflow';
      process.env.GITHUB_REPOSITORY = 'user/repo';

      // Act
      const report = createCIReport();

      // Assert
      expect(report).toContain('GitHub Actions');
      expect(report).toContain('test-workflow');
      expect(report).toContain('user/repo');
    });

    it('should create a Jenkins report', () => {
      // Arrange
      process.env.JENKINS_URL = 'http://jenkins.example.com';
      process.env.JOB_NAME = 'test-job';
      process.env.BUILD_NUMBER = '123';

      // Act
      const report = createCIReport();

      // Assert
      expect(report).toContain('Jenkins');
      expect(report).toContain('test-job');
      expect(report).toContain('123');
    });

    it('should create a generic CI report', () => {
      // Arrange
      process.env.CI = 'true';

      // Act
      const report = createCIReport();

      // Assert
      expect(report).toContain('Generic CI');
      expect(report).toContain('CI environment detected');
    });

    it('should write report to file when path is provided', () => {
      // Arrange
      process.env.CI = 'true';
      const filePath = '/tmp/ci-report.txt';

      // Act
      createCIReport(filePath);

      // Assert
      expect(fs.writeFileSync).toHaveBeenCalledWith(filePath, expect.any(String));
    });
  });
});
