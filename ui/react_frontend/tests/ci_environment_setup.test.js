/**
 * CI Environment Setup Tests
 *
 * This file contains tests for the CI environment setup functionality.
 * It tests the setup process for different CI platforms and environments.
 */

import fs from 'fs';
import path from 'path';
import os from 'os';

// Mock the fs module
jest.mock('fs', () => ({
  existsSync: jest.fn(),
  readFileSync: jest.fn(),
  writeFileSync: jest.fn(),
  mkdirSync: jest.fn()
}));

// Mock the os module
jest.mock('os', () => ({
  platform: jest.fn(),
  release: jest.fn(),
  tmpdir: jest.fn(),
  homedir: jest.fn(),
  hostname: jest.fn(),
  userInfo: jest.fn(),
  totalmem: jest.fn(),
  freemem: jest.fn(),
  cpus: jest.fn()
}));

// Import the modules to test
import { detectEnvironment } from '../src/utils/environmentDetection';
import {
  setupCIEnvironment,
  getCIEnvironmentInfo,
  createCIReport,
  detectCIEnvironmentType
} from './helpers/ci-environment';

describe('CI Environment Setup Module', () => {
  // Store original environment variables
  const originalEnv = { ...process.env };

  // Setup before each test
  beforeEach(() => {
    // Reset all mocks
    jest.resetAllMocks();

    // Reset environment variables
    process.env = { ...originalEnv };

    // Default mock implementations
    fs.existsSync.mockImplementation(() => false);
    fs.readFileSync.mockImplementation(() => '');
    fs.mkdirSync.mockImplementation(() => undefined);
    fs.writeFileSync.mockImplementation(() => undefined);

    // Mock os functions
    os.platform.mockImplementation(() => 'linux');
    os.release.mockImplementation(() => '5.10.0');
    os.tmpdir.mockImplementation(() => '/tmp');
    os.homedir.mockImplementation(() => '/home/user');
    os.hostname.mockImplementation(() => 'test-host');
    os.userInfo.mockImplementation(() => ({ username: 'test-user' }));
    os.totalmem.mockImplementation(() => 16000000000);
    os.freemem.mockImplementation(() => 8000000000);
    os.cpus.mockImplementation(() => [{ model: 'Test CPU', speed: 2500 }]);
  });

  // Cleanup after each test
  afterEach(() => {
    // Restore original environment variables
    process.env = { ...originalEnv };
  });

  describe('setupCIEnvironment Function', () => {
    it('should set up GitHub Actions environment', () => {
      // Arrange
      process.env.GITHUB_ACTIONS = 'true';
      process.env.GITHUB_WORKFLOW = 'test-workflow';
      process.env.CI = 'true';

      // Act
      const result = setupCIEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.ciType).toBe('github');
    });

    it('should create CI directories when specified', () => {
      // Arrange
      process.env.CI = 'true';
      fs.existsSync.mockImplementation(() => false);

      // Act
      const result = setupCIEnvironment({ createDirectories: true });

      // Assert
      expect(result.success).toBe(true);
      expect(fs.mkdirSync).toHaveBeenCalled();
    });

    it('should handle errors during setup', () => {
      // Arrange
      process.env.CI = 'true';
      fs.mkdirSync.mockImplementation(() => { throw new Error('Test error'); });

      // Act
      const result = setupCIEnvironment({ createDirectories: true });

      // Assert
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('should set up Docker environment', () => {
      // Arrange
      process.env.CI = 'true';
      process.env.DOCKER_ENVIRONMENT = 'true';

      // Act
      const result = setupCIEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.ciType).toBe('generic');
    });

    it('should set up Kubernetes environment', () => {
      // Arrange
      process.env.CI = 'true';
      process.env.KUBERNETES_SERVICE_HOST = '10.0.0.1';

      // Act
      const result = setupCIEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.ciType).toBe('generic');
    });

    it('should force CI environment when forceCI is true', () => {
      // Arrange
      process.env.CI = 'false';
      delete process.env.GITHUB_ACTIONS;

      // Act
      const result = setupCIEnvironment({ forceCI: true });

      // Assert
      expect(result.success).toBe(true);
      expect(result.ciType).toBe('generic');
      expect(result.isCI).toBe(true);
    });

    it('should force specific CI type when forceCIType is provided', () => {
      // Arrange
      process.env.CI = 'true';

      // Act
      const result = setupCIEnvironment({ forceCIType: 'github' });

      // Assert
      expect(result.success).toBe(true);
      expect(result.ciType).toBe('github');
    });
  });

  describe('getCIEnvironmentInfo Function', () => {
    it('should return GitHub Actions environment info', () => {
      // Arrange
      process.env.GITHUB_ACTIONS = 'true';
      process.env.GITHUB_WORKFLOW = 'test-workflow';
      process.env.GITHUB_REPOSITORY = 'owner/repo';
      process.env.GITHUB_RUN_ID = '12345';
      process.env.CI = 'true';

      // Act
      const result = getCIEnvironmentInfo();

      // Assert
      expect(result.ciType).toBe('github');
      expect(result.github).toBeDefined();
      expect(result.github.workflow).toBe('test-workflow');
      expect(result.github.repository).toBe('owner/repo');
      expect(result.github.runId).toBe('12345');
    });

    it('should return Jenkins environment info', () => {
      // Arrange
      process.env.JENKINS_URL = 'http://jenkins.example.com';
      process.env.JOB_NAME = 'test-job';
      process.env.BUILD_NUMBER = '123';
      process.env.CI = 'true';

      // Act
      const result = getCIEnvironmentInfo();

      // Assert
      expect(result.ciType).toBe('jenkins');
      expect(result.jenkins).toBeDefined();
      expect(result.jenkins.jobName).toBe('test-job');
      expect(result.jenkins.buildNumber).toBe('123');
    });
  });

  describe('createCIReport Function', () => {
    it('should create a CI report file', () => {
      // Arrange
      process.env.CI = 'true';
      const filename = 'test-report.txt';

      // Act
      const result = createCIReport(filename, {
        includeEnvVars: false,
        includeSystemInfo: true,
        formatJson: false
      });

      // Assert
      expect(typeof result).toBe('string');
      expect(fs.writeFileSync).toHaveBeenCalled();
    });

    it('should create a JSON report when formatJson is true', () => {
      // Arrange
      process.env.CI = 'true';
      const filename = 'test-report.json';

      // Act
      const result = createCIReport(filename, {
        includeEnvVars: false,
        includeSystemInfo: true,
        formatJson: true
      });

      // Assert
      expect(typeof result).toBe('string');
      expect(() => JSON.parse(result)).not.toThrow();
      expect(fs.writeFileSync).toHaveBeenCalled();
    });

    it('should handle errors when creating a report', () => {
      // Arrange
      process.env.CI = 'true';
      fs.writeFileSync.mockImplementation(() => { throw new Error('Test error'); });

      // Act & Assert
      expect(() => {
        createCIReport('test.txt', {
          includeEnvVars: false,
          includeSystemInfo: true,
          formatJson: false
        });
      }).not.toThrow();
    });
  });
});
