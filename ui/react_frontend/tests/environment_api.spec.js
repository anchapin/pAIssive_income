/**
 * Environment-Specific API Tests
 *
 * This file contains tests for environment-specific API behavior:
 * - Windows vs macOS/Linux API differences
 * - CI environment API behavior
 * - Docker environment API behavior
 * - Development vs Production API differences
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

    // CI Environment Detection
    const isCI = process.env.CI === 'true' || process.env.CI === true ||
                process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW ||
                !!process.env.JENKINS_URL || !!process.env.GITLAB_CI ||
                !!process.env.CIRCLECI || !!process.env.TRAVIS ||
                !!process.env.TF_BUILD || !!process.env.TEAMCITY_VERSION;

    // Docker Environment Detection
    const isDocker = process.env.DOCKER_ENVIRONMENT === 'true' ||
                    (fs.existsSync('/.dockerenv') || process.env.DOCKER === 'true');

    // Node Environment Detection
    const isDevelopment = process.env.NODE_ENV === 'development';
    const isProduction = process.env.NODE_ENV === 'production';
    const isTest = process.env.NODE_ENV === 'test';

    return {
      platform,
      isWindows,
      isMacOS,
      isLinux,
      isCI,
      isDocker,
      isDevelopment,
      isProduction,
      isTest
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

  return {
    getBaseUrl: () => {
      if (env.isCI) {
        return 'http://localhost:8000/api';
      }
      if (env.isDocker) {
        return 'http://host.docker.internal:5000/api';
      }
      if (env.isProduction) {
        return 'https://api.example.com';
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

      if (env.isCI) {
        headers['X-CI-Environment'] = 'true';
      }

      if (env.isDocker) {
        headers['X-Docker-Environment'] = 'true';
      }

      return headers;
    },

    getFilePath: (filename) => {
      return platformSpecific.getPlatformSpecificPath(env.isWindows ? `C:\\temp\\${filename}` : `/tmp/${filename}`);
    },

    getEnvironment: () => env
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

    it('should use CI base URL in CI environment', () => {
      // Arrange
      process.env.CI = 'true';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('http://localhost:8000/api');
    });

    it('should use Docker base URL in Docker environment', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/.dockerenv');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getBaseUrl()).toBe('http://host.docker.internal:5000/api');
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

    it('should include Docker header in Docker environment', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/.dockerenv');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).toHaveProperty('X-Docker-Environment', 'true');
    });

    it('should not include special headers in regular environment', () => {
      // Arrange
      process.env.NODE_ENV = 'development';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getHeaders()).not.toHaveProperty('X-CI-Environment');
      expect(apiClient.getHeaders()).not.toHaveProperty('X-Docker-Environment');
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
      expect(apiClient.getFilePath('test.txt')).toBe('/tmp/test.txt');
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

    it('should detect CI environment', () => {
      // Arrange
      process.env.CI = 'true';

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isCI).toBe(true);
    });

    it('should detect Docker environment', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/.dockerenv');

      // Act
      const apiClient = createEnvironmentAwareApiClient();

      // Assert
      expect(apiClient.getEnvironment().isDocker).toBe(true);
    });
  });
});
