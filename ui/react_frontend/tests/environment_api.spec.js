/**
 * Environment-Specific API Tests
 *
 * This file contains tests for environment-specific API behavior:
 * - Windows vs macOS/Linux vs iOS vs Android API differences
 * - CI environment API behavior (GitHub Actions, Jenkins, GitLab CI, CircleCI, etc.)
 * - Container environment API behavior (Docker, Kubernetes)
 * - Cloud environment API behavior (AWS, Azure, GCP)
 * - Serverless environment API behavior (Lambda, Azure Functions, Cloud Functions)
 * - Development vs Production vs Test vs Staging API differences
 * - Browser vs Node.js API differences
 * - Mobile vs Desktop API differences
 * - Electron app API behavior
 * - WSL (Windows Subsystem for Linux) API behavior
 *
 * These tests ensure that the API behaves correctly in different environments.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import fs from 'fs';
import path from 'path';
import os from 'os';

// Mock modules
vi.mock('fs');
vi.mock('path');
vi.mock('os');
vi.mock('child_process');

// Create the environment detection module
const environmentDetection = {
  detectEnvironment: () => {
    // Operating System Detection
    const platform = os.platform();
    const isWindows = platform === 'win32';
    const isMacOS = platform === 'darwin';
    const isLinux = platform === 'linux';
    const isIOS = platform === 'ios';
    const isAndroid = platform === 'android';
    const isMobile = isIOS || isAndroid;
    const isBrowser = typeof window !== 'undefined';
    const isElectron = !!process.env.ELECTRON_RUN_AS_NODE;
    const isWSL = isLinux && (process.env.WSL_DISTRO_NAME || '').length > 0;

    // CI Environment Detection
    const isCI = process.env.CI === 'true' || process.env.CI === true ||
                process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW ||
                !!process.env.JENKINS_URL || !!process.env.GITLAB_CI ||
                !!process.env.CIRCLECI || !!process.env.TRAVIS ||
                !!process.env.TF_BUILD || !!process.env.TEAMCITY_VERSION ||
                !!process.env.BITBUCKET_BUILD_NUMBER || !!process.env.APPVEYOR;

    const isGitHubActions = process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW;
    const isJenkins = !!process.env.JENKINS_URL;
    const isGitLabCI = !!process.env.GITLAB_CI;
    const isCircleCI = !!process.env.CIRCLECI;
    const isTravis = !!process.env.TRAVIS;
    const isAzurePipelines = !!process.env.TF_BUILD;
    const isTeamCity = !!process.env.TEAMCITY_VERSION;
    const isBitbucket = !!process.env.BITBUCKET_BUILD_NUMBER;
    const isAppVeyor = !!process.env.APPVEYOR;

    // Container Environment Detection
    const isDocker = process.env.DOCKER_ENVIRONMENT === 'true' ||
                    process.env.DOCKER === 'true' ||
                    fs.existsSync('/.dockerenv') ||
                    fs.existsSync('/run/.containerenv');

    const isKubernetes = !!process.env.KUBERNETES_SERVICE_HOST ||
                        !!process.env.KUBERNETES_PORT;

    const isContainerized = isDocker || isKubernetes ||
                           process.env.CONTAINER === 'true' ||
                           process.env.CONTAINERIZED === 'true';

    // Cloud Environment Detection
    const isAWS = !!process.env.AWS_REGION ||
                 !!process.env.AWS_LAMBDA_FUNCTION_NAME ||
                 !!process.env.AWS_EXECUTION_ENV;

    const isAzure = !!process.env.AZURE_FUNCTIONS_ENVIRONMENT ||
                   !!process.env.WEBSITE_SITE_NAME ||
                   !!process.env.APPSETTING_WEBSITE_SITE_NAME;

    const isGCP = !!process.env.GOOGLE_CLOUD_PROJECT ||
                 !!process.env.GCLOUD_PROJECT ||
                 !!process.env.GCP_PROJECT ||
                 (!!process.env.FUNCTION_NAME && !!process.env.FUNCTION_REGION);

    const isCloudEnvironment = isAWS || isAzure || isGCP;

    // Serverless Environment Detection
    const isLambda = !!process.env.AWS_LAMBDA_FUNCTION_NAME;
    const isAzureFunctions = !!process.env.AZURE_FUNCTIONS_ENVIRONMENT;
    const isCloudFunctions = !!process.env.FUNCTION_NAME &&
                            !!process.env.FUNCTION_REGION;

    const isServerless = isLambda || isAzureFunctions || isCloudFunctions;

    // Node Environment Detection
    const isDevelopment = process.env.NODE_ENV === 'development';
    const isProduction = process.env.NODE_ENV === 'production';
    const isTest = process.env.NODE_ENV === 'test' ||
                  process.env.JEST_WORKER_ID !== undefined ||
                  process.env.VITEST !== undefined;
    const isStaging = process.env.NODE_ENV === 'staging';

    // Verbose Logging
    const verboseLogging = process.env.VERBOSE_LOGGING === 'true' ||
                          process.env.DEBUG === 'true' ||
                          process.env.DEBUG_LEVEL === 'verbose' ||
                          process.env.LOG_LEVEL === 'debug' ||
                          process.env.LOG_LEVEL === 'trace';

    return {
      // Operating System
      platform,
      isWindows,
      isMacOS,
      isLinux,
      isIOS,
      isAndroid,
      isMobile,
      isElectron,
      isWSL,

      // CI Environment
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

      // Container Environment
      isDocker,
      isKubernetes,
      isContainerized,

      // Cloud Environment
      isAWS,
      isAzure,
      isGCP,
      isCloudEnvironment,

      // Serverless Environment
      isLambda,
      isAzureFunctions,
      isCloudFunctions,
      isServerless,

      // Node Environment
      isDevelopment,
      isProduction,
      isTest,
      isStaging,

      // Browser Environment
      isBrowser,

      // Logging
      verboseLogging
    };
  },

  getBrowserInfo: () => {
    if (typeof window === 'undefined' || typeof navigator === 'undefined') {
      return {
        name: 'node',
        version: 'N/A',
        userAgent: 'N/A',
        isMobile: false,
        isTablet: false,
        isDesktop: true
      };
    }

    const userAgent = navigator.userAgent;
    const browsers = [
      { name: 'edge', regex: /Edge\/(\d+)/i },
      { name: 'edgeChromium', regex: /Edg\/(\d+)/i },
      { name: 'chrome', regex: /Chrome\/(\d+)/i },
      { name: 'firefox', regex: /Firefox\/(\d+)/i },
      { name: 'safari', regex: /Version\/(\d+).*Safari/i },
      { name: 'opera', regex: /OPR\/(\d+)/i },
      { name: 'ie', regex: /Trident.*rv:(\d+)/i }
    ];

    let name = 'unknown';
    let version = 'unknown';

    for (const browser of browsers) {
      const match = userAgent.match(browser.regex);
      if (match) {
        name = browser.name;
        version = match[1];
        break;
      }
    }

    // Mobile detection
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);

    // Tablet detection
    const isTablet = /iPad|Android(?!.*Mobile)/i.test(userAgent);

    // Desktop is neither mobile nor tablet
    const isDesktop = !isMobile && !isTablet;

    return {
      name,
      version,
      userAgent,
      isMobile,
      isTablet,
      isDesktop
    };
  },

  getNetworkInfo: () => {
    if (typeof navigator === 'undefined' || !navigator.connection) {
      return {
        online: typeof navigator !== 'undefined' ? navigator.onLine : false,
        effectiveType: '4g',
        downlink: 10,
        rtt: 50,
        saveData: false
      };
    }

    const connection = navigator.connection;

    return {
      online: navigator.onLine,
      effectiveType: connection.effectiveType || '4g',
      downlink: connection.downlink || 10,
      rtt: connection.rtt || 50,
      saveData: connection.saveData || false
    };
  }
};

// Create the platform-specific module
const platformSpecific = {
  getPlatformSpecificPath: (...pathSegments) => {
    const env = environmentDetection.detectEnvironment();

    // If only one segment is provided, it might be a path with separators
    if (pathSegments.length === 1 && typeof pathSegments[0] === 'string') {
      const inputPath = pathSegments[0];

      // Convert Windows paths to Unix paths on Unix platforms
      if (!env.isWindows && inputPath.includes('\\')) {
        return inputPath.replace(/\\/g, '/');
      }

      // Convert Unix paths to Windows paths on Windows
      if (env.isWindows && inputPath.includes('/')) {
        return inputPath.replace(/\//g, '\\');
      }

      return inputPath;
    }

    // Join path segments using platform-specific separator
    return path.join(...pathSegments);
  }
};

// Create a simple API client for testing
const createEnvironmentAwareApiClient = () => {
  const env = environmentDetection.detectEnvironment();
  const browserInfo = environmentDetection.getBrowserInfo();
  const networkInfo = environmentDetection.getNetworkInfo();

  return {
    getBaseUrl: () => {
      // Serverless environments
      if (env.isLambda) {
        return 'https://lambda-api.example.com';
      }
      if (env.isAzureFunctions) {
        return 'https://azure-functions-api.example.com';
      }
      if (env.isCloudFunctions) {
        return 'https://cloud-functions-api.example.com';
      }

      // Cloud environments
      if (env.isAWS) {
        return 'https://aws-api.example.com';
      }
      if (env.isAzure) {
        return 'https://azure-api.example.com';
      }
      if (env.isGCP) {
        return 'https://gcp-api.example.com';
      }

      // CI environments
      if (env.isGitHubActions) {
        return 'http://localhost:8000/api';
      }
      if (env.isJenkins || env.isGitLabCI || env.isCircleCI || env.isTravis) {
        return 'http://localhost:8080/api';
      }

      // Container environments
      if (env.isKubernetes) {
        return 'http://service.namespace.svc.cluster.local/api';
      }
      if (env.isDocker) {
        return 'http://host.docker.internal:5000/api';
      }

      // Mobile environments
      if (env.isMobile) {
        if (env.isIOS) {
          return 'https://ios-api.example.com';
        }
        if (env.isAndroid) {
          return 'https://android-api.example.com';
        }
        return 'https://mobile-api.example.com';
      }

      // Electron environment
      if (env.isElectron) {
        return 'http://localhost:3000/api';
      }

      // WSL environment
      if (env.isWSL) {
        return 'http://localhost:5000/api';
      }

      // Standard environments
      if (env.isProduction) {
        return 'https://api.example.com';
      }
      if (env.isStaging) {
        return 'https://staging-api.example.com';
      }
      if (env.isTest) {
        return 'http://localhost:9000/api';
      }
      if (env.isDevelopment) {
        return 'http://localhost:5000/api';
      }

      return 'http://localhost:5000/api';
    },

    getHeaders: () => {
      const headers = {
        'Content-Type': 'application/json'
      };

      // Environment headers
      if (env.isCI) {
        headers['X-CI-Environment'] = 'true';

        if (env.isGitHubActions) headers['X-GitHub-Actions'] = 'true';
        if (env.isJenkins) headers['X-Jenkins'] = 'true';
        if (env.isGitLabCI) headers['X-GitLab-CI'] = 'true';
        if (env.isCircleCI) headers['X-CircleCI'] = 'true';
        if (env.isTravis) headers['X-Travis'] = 'true';
      }

      if (env.isContainerized) {
        headers['X-Containerized'] = 'true';

        if (env.isDocker) headers['X-Docker-Environment'] = 'true';
        if (env.isKubernetes) headers['X-Kubernetes'] = 'true';
      }

      if (env.isCloudEnvironment) {
        headers['X-Cloud-Environment'] = 'true';

        if (env.isAWS) headers['X-AWS'] = 'true';
        if (env.isAzure) headers['X-Azure'] = 'true';
        if (env.isGCP) headers['X-GCP'] = 'true';
      }

      if (env.isServerless) {
        headers['X-Serverless'] = 'true';

        if (env.isLambda) headers['X-Lambda'] = 'true';
        if (env.isAzureFunctions) headers['X-Azure-Functions'] = 'true';
        if (env.isCloudFunctions) headers['X-Cloud-Functions'] = 'true';
      }

      // Platform headers
      if (env.isWindows) headers['X-Platform'] = 'windows';
      else if (env.isMacOS) headers['X-Platform'] = 'macos';
      else if (env.isLinux) headers['X-Platform'] = 'linux';
      else if (env.isIOS) headers['X-Platform'] = 'ios';
      else if (env.isAndroid) headers['X-Platform'] = 'android';

      if (env.isMobile) headers['X-Mobile'] = 'true';
      if (env.isElectron) headers['X-Electron'] = 'true';
      if (env.isWSL) headers['X-WSL'] = 'true';

      // Browser headers
      if (env.isBrowser) {
        headers['X-Browser-Name'] = browserInfo.name;
        headers['X-Browser-Version'] = browserInfo.version;

        if (browserInfo.isMobile) headers['X-Browser-Mobile'] = 'true';
        if (browserInfo.isTablet) headers['X-Browser-Tablet'] = 'true';
        if (browserInfo.isDesktop) headers['X-Browser-Desktop'] = 'true';

        // Network headers
        if (networkInfo.online) {
          headers['X-Network-Type'] = networkInfo.effectiveType;
          headers['X-Network-Downlink'] = String(networkInfo.downlink);
          headers['X-Network-RTT'] = String(networkInfo.rtt);

          if (networkInfo.saveData) {
            headers['X-Save-Data'] = 'true';
          }
        } else {
          headers['X-Offline'] = 'true';
        }
      }

      return headers;
    },

    getFilePath: (filename) => {
      if (env.isWindows) {
        return platformSpecific.getPlatformSpecificPath(`C:\\temp\\${filename}`);
      } else if (env.isMacOS) {
        return platformSpecific.getPlatformSpecificPath(`/Users/user/tmp/${filename}`);
      } else if (env.isLinux) {
        return platformSpecific.getPlatformSpecificPath(`/tmp/${filename}`);
      } else if (env.isIOS) {
        return platformSpecific.getPlatformSpecificPath(`/var/mobile/tmp/${filename}`);
      } else if (env.isAndroid) {
        return platformSpecific.getPlatformSpecificPath(`/data/local/tmp/${filename}`);
      } else if (env.isWSL) {
        return platformSpecific.getPlatformSpecificPath(`/mnt/c/temp/${filename}`);
      } else {
        return platformSpecific.getPlatformSpecificPath(`/tmp/${filename}`);
      }
    },

    getEnvironment: () => env,
    getBrowserInfo: () => browserInfo,
    getNetworkInfo: () => networkInfo
  };
};

// Mock the modules
vi.mock('../tests/helpers/environment-detection', () => environmentDetection, { virtual: true });
vi.mock('../tests/helpers/platform-specific', () => platformSpecific, { virtual: true });

describe('Environment-Specific API', () => {
  // Reset mocks before each test
  beforeEach(() => {
    vi.resetAllMocks();

    // Default mock implementations
    os.platform.mockReturnValue('linux');
    os.type.mockReturnValue('Linux');
    os.release.mockReturnValue('5.10.0');
    os.tmpdir.mockReturnValue('/tmp');
    fs.existsSync.mockReturnValue(false);
    path.join.mockImplementation((...args) => args.join('/'));
    path.resolve.mockImplementation((...args) => args.join('/'));
    process.env = { NODE_ENV: 'development' };
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('API Base URL', () => {
    it('should use development base URL in development environment', () => {
      // Arrange
      process.env.NODE_ENV = 'development';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('http://localhost:5000/api');
    });

    it('should use production base URL in production environment', () => {
      // Arrange
      process.env.NODE_ENV = 'production';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('https://api.example.com');
    });

    it('should use staging base URL in staging environment', () => {
      // Arrange
      process.env.NODE_ENV = 'staging';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('https://staging-api.example.com');
    });

    it('should use test base URL in test environment', () => {
      // Arrange
      process.env.NODE_ENV = 'test';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('http://localhost:9000/api');
    });

    it('should use GitHub Actions base URL in GitHub Actions environment', () => {
      // Arrange
      process.env.GITHUB_ACTIONS = 'true';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('http://localhost:8000/api');
    });

    it('should use Jenkins base URL in Jenkins environment', () => {
      // Arrange
      process.env.JENKINS_URL = 'http://jenkins.example.com';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('http://localhost:8080/api');
    });

    it('should use Docker base URL in Docker environment', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/.dockerenv');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('http://host.docker.internal:5000/api');
    });

    it('should use Kubernetes base URL in Kubernetes environment', () => {
      // Arrange
      process.env.KUBERNETES_SERVICE_HOST = 'kubernetes.default.svc.cluster.local';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('http://service.namespace.svc.cluster.local/api');
    });

    it('should use AWS base URL in AWS environment', () => {
      // Arrange
      process.env.AWS_REGION = 'us-west-2';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('https://aws-api.example.com');
    });

    it('should use Azure base URL in Azure environment', () => {
      // Arrange
      process.env.WEBSITE_SITE_NAME = 'my-azure-app';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('https://azure-api.example.com');
    });

    it('should use GCP base URL in GCP environment', () => {
      // Arrange
      process.env.GOOGLE_CLOUD_PROJECT = 'my-gcp-project';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('https://gcp-api.example.com');
    });

    it('should use Lambda base URL in Lambda environment', () => {
      // Arrange
      process.env.AWS_LAMBDA_FUNCTION_NAME = 'my-lambda-function';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('https://lambda-api.example.com');
    });

    it('should use Azure Functions base URL in Azure Functions environment', () => {
      // Arrange
      process.env.AZURE_FUNCTIONS_ENVIRONMENT = 'Production';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('https://azure-functions-api.example.com');
    });

    it('should use Cloud Functions base URL in Cloud Functions environment', () => {
      // Arrange
      process.env.FUNCTION_NAME = 'my-cloud-function';
      process.env.FUNCTION_REGION = 'us-central1';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('https://cloud-functions-api.example.com');
    });

    it('should use iOS base URL in iOS environment', () => {
      // Arrange
      os.platform.mockReturnValue('ios');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('https://ios-api.example.com');
    });

    it('should use Android base URL in Android environment', () => {
      // Arrange
      os.platform.mockReturnValue('android');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('https://android-api.example.com');
    });

    it('should use Electron base URL in Electron environment', () => {
      // Arrange
      process.env.ELECTRON_RUN_AS_NODE = 'true';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('http://localhost:3000/api');
    });

    it('should use WSL base URL in WSL environment', () => {
      // Arrange
      os.platform.mockReturnValue('linux');
      process.env.WSL_DISTRO_NAME = 'Ubuntu';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('http://localhost:5000/api');
    });
  });

  describe('API Headers', () => {
    it('should include CI header in CI environment', () => {
      // Arrange
      process.env.CI = 'true';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-CI-Environment', 'true');
    });

    it('should include GitHub Actions header in GitHub Actions environment', () => {
      // Arrange
      process.env.GITHUB_ACTIONS = 'true';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-GitHub-Actions', 'true');
    });

    it('should include Jenkins header in Jenkins environment', () => {
      // Arrange
      process.env.JENKINS_URL = 'http://jenkins.example.com';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-Jenkins', 'true');
    });

    it('should include Docker header in Docker environment', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/.dockerenv');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-Docker-Environment', 'true');
    });

    it('should include Kubernetes header in Kubernetes environment', () => {
      // Arrange
      process.env.KUBERNETES_SERVICE_HOST = 'kubernetes.default.svc.cluster.local';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-Kubernetes', 'true');
    });

    it('should include Containerized header in containerized environment', () => {
      // Arrange
      process.env.CONTAINER = 'true';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-Containerized', 'true');
    });

    it('should include Cloud Environment header in cloud environment', () => {
      // Arrange
      process.env.AWS_REGION = 'us-west-2';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-Cloud-Environment', 'true');
      expect(apiClient.getHeaders()).toHaveProperty('X-AWS', 'true');
    });

    it('should include Serverless header in serverless environment', () => {
      // Arrange
      process.env.AWS_LAMBDA_FUNCTION_NAME = 'my-lambda-function';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-Serverless', 'true');
      expect(apiClient.getHeaders()).toHaveProperty('X-Lambda', 'true');
    });

    it('should include Platform header for Windows', () => {
      // Arrange
      os.platform.mockReturnValue('win32');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-Platform', 'windows');
    });

    it('should include Platform header for macOS', () => {
      // Arrange
      os.platform.mockReturnValue('darwin');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-Platform', 'macos');
    });

    it('should include Mobile header for mobile platforms', () => {
      // Arrange
      os.platform.mockReturnValue('ios');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-Mobile', 'true');
      expect(apiClient.getHeaders()).toHaveProperty('X-Platform', 'ios');
    });

    it('should include Electron header in Electron environment', () => {
      // Arrange
      process.env.ELECTRON_RUN_AS_NODE = 'true';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-Electron', 'true');
    });

    it('should include WSL header in WSL environment', () => {
      // Arrange
      os.platform.mockReturnValue('linux');
      process.env.WSL_DISTRO_NAME = 'Ubuntu';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-WSL', 'true');
    });

    it('should not include special headers in regular environment', () => {
      // Arrange
      process.env.NODE_ENV = 'development';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).not.toHaveProperty('X-CI-Environment');
      expect(apiClient.getHeaders()).not.toHaveProperty('X-Docker-Environment');
      expect(apiClient.getHeaders()).not.toHaveProperty('X-Kubernetes');
      expect(apiClient.getHeaders()).not.toHaveProperty('X-Cloud-Environment');
      expect(apiClient.getHeaders()).not.toHaveProperty('X-Serverless');
    });
  });

  describe('File Paths', () => {
    it('should use Windows file paths on Windows', () => {
      // Arrange
      os.platform.mockReturnValue('win32');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getFilePath('test.txt')).toBe('C:\\temp\\test.txt');
    });

    it('should use Unix file paths on Linux', () => {
      // Arrange
      os.platform.mockReturnValue('linux');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getFilePath('test.txt')).toBe('/tmp/test.txt');
    });

    it('should use Unix file paths on macOS', () => {
      // Arrange
      os.platform.mockReturnValue('darwin');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getFilePath('test.txt')).toBe('/Users/user/tmp/test.txt');
    });

    it('should use iOS file paths on iOS', () => {
      // Arrange
      os.platform.mockReturnValue('ios');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getFilePath('test.txt')).toBe('/var/mobile/tmp/test.txt');
    });

    it('should use Android file paths on Android', () => {
      // Arrange
      os.platform.mockReturnValue('android');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getFilePath('test.txt')).toBe('/data/local/tmp/test.txt');
    });

    it('should use WSL file paths on WSL', () => {
      // Arrange
      os.platform.mockReturnValue('linux');
      process.env.WSL_DISTRO_NAME = 'Ubuntu';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getFilePath('test.txt')).toBe('/mnt/c/temp/test.txt');
    });
  });

  describe('Environment Detection', () => {
    it('should detect Windows environment', () => {
      // Arrange
      os.platform.mockReturnValue('win32');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isWindows).toBe(true);
      expect(apiClient.getEnvironment().isMacOS).toBe(false);
      expect(apiClient.getEnvironment().isLinux).toBe(false);
    });

    it('should detect macOS environment', () => {
      // Arrange
      os.platform.mockReturnValue('darwin');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isMacOS).toBe(true);
      expect(apiClient.getEnvironment().isWindows).toBe(false);
      expect(apiClient.getEnvironment().isLinux).toBe(false);
    });

    it('should detect Linux environment', () => {
      // Arrange
      os.platform.mockReturnValue('linux');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isLinux).toBe(true);
      expect(apiClient.getEnvironment().isWindows).toBe(false);
      expect(apiClient.getEnvironment().isMacOS).toBe(false);
    });

    it('should detect iOS environment', () => {
      // Arrange
      os.platform.mockReturnValue('ios');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isIOS).toBe(true);
      expect(apiClient.getEnvironment().isMobile).toBe(true);
    });

    it('should detect Android environment', () => {
      // Arrange
      os.platform.mockReturnValue('android');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isAndroid).toBe(true);
      expect(apiClient.getEnvironment().isMobile).toBe(true);
    });

    it('should detect CI environment', () => {
      // Arrange
      process.env.CI = 'true';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isCI).toBe(true);
    });

    it('should detect GitHub Actions environment', () => {
      // Arrange
      process.env.GITHUB_ACTIONS = 'true';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isGitHubActions).toBe(true);
      expect(apiClient.getEnvironment().isCI).toBe(true);
    });

    it('should detect Jenkins environment', () => {
      // Arrange
      process.env.JENKINS_URL = 'http://jenkins.example.com';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isJenkins).toBe(true);
      expect(apiClient.getEnvironment().isCI).toBe(true);
    });

    it('should detect Docker environment', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/.dockerenv');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isDocker).toBe(true);
      expect(apiClient.getEnvironment().isContainerized).toBe(true);
    });

    it('should detect Kubernetes environment', () => {
      // Arrange
      process.env.KUBERNETES_SERVICE_HOST = 'kubernetes.default.svc.cluster.local';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isKubernetes).toBe(true);
      expect(apiClient.getEnvironment().isContainerized).toBe(true);
    });

    it('should detect AWS environment', () => {
      // Arrange
      process.env.AWS_REGION = 'us-west-2';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isAWS).toBe(true);
      expect(apiClient.getEnvironment().isCloudEnvironment).toBe(true);
    });

    it('should detect Lambda environment', () => {
      // Arrange
      process.env.AWS_LAMBDA_FUNCTION_NAME = 'my-lambda-function';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isLambda).toBe(true);
      expect(apiClient.getEnvironment().isServerless).toBe(true);
      expect(apiClient.getEnvironment().isAWS).toBe(true);
    });

    it('should detect Electron environment', () => {
      // Arrange
      process.env.ELECTRON_RUN_AS_NODE = 'true';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isElectron).toBe(true);
    });

    it('should detect WSL environment', () => {
      // Arrange
      os.platform.mockReturnValue('linux');
      process.env.WSL_DISTRO_NAME = 'Ubuntu';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isWSL).toBe(true);
      expect(apiClient.getEnvironment().isLinux).toBe(true);
    });

    it('should detect development environment', () => {
      // Arrange
      process.env.NODE_ENV = 'development';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isDevelopment).toBe(true);
      expect(apiClient.getEnvironment().isProduction).toBe(false);
      expect(apiClient.getEnvironment().isTest).toBe(false);
      expect(apiClient.getEnvironment().isStaging).toBe(false);
    });

    it('should detect production environment', () => {
      // Arrange
      process.env.NODE_ENV = 'production';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isProduction).toBe(true);
      expect(apiClient.getEnvironment().isDevelopment).toBe(false);
      expect(apiClient.getEnvironment().isTest).toBe(false);
      expect(apiClient.getEnvironment().isStaging).toBe(false);
    });

    it('should detect test environment', () => {
      // Arrange
      process.env.NODE_ENV = 'test';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isTest).toBe(true);
      expect(apiClient.getEnvironment().isDevelopment).toBe(false);
      expect(apiClient.getEnvironment().isProduction).toBe(false);
      expect(apiClient.getEnvironment().isStaging).toBe(false);
    });

    it('should detect staging environment', () => {
      // Arrange
      process.env.NODE_ENV = 'staging';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isStaging).toBe(true);
      expect(apiClient.getEnvironment().isDevelopment).toBe(false);
      expect(apiClient.getEnvironment().isProduction).toBe(false);
      expect(apiClient.getEnvironment().isTest).toBe(false);
    });
  });

  describe('Browser Information', () => {
    it('should get browser information', () => {
      // Act
      const apiClient = createEnvironmentAwareApiClient();
      const browserInfo = apiClient.getBrowserInfo();

      // Assert
      expect(browserInfo).toBeDefined();
      expect(browserInfo.name).toBeDefined();
      expect(browserInfo.version).toBeDefined();
      expect(browserInfo.userAgent).toBeDefined();
      expect(typeof browserInfo.isMobile).toBe('boolean');
      expect(typeof browserInfo.isTablet).toBe('boolean');
      expect(typeof browserInfo.isDesktop).toBe('boolean');
    });
  });

  describe('Network Information', () => {
    it('should get network information', () => {
      // Act
      const apiClient = createEnvironmentAwareApiClient();
      const networkInfo = apiClient.getNetworkInfo();

      // Assert
      expect(networkInfo).toBeDefined();
      expect(typeof networkInfo.online).toBe('boolean');
      expect(networkInfo.effectiveType).toBeDefined();
      expect(typeof networkInfo.downlink).toBe('number');
      expect(typeof networkInfo.rtt).toBe('number');
      expect(typeof networkInfo.saveData).toBe('boolean');
    });
  });
});
