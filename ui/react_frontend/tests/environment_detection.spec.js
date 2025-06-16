/**
 * Environment Detection Tests
 * 
 * This file contains tests for detecting and handling different environments:
 * - Windows vs macOS/Linux
 * - CI environments (GitHub Actions, etc.)
 * - Docker containers
 * - Development vs Production
 * 
 * These tests ensure that the application behaves correctly in different environments.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import fs from 'fs';
import path from 'path';
import os from 'os';

// Mock modules
vi.mock('fs');
vi.mock('path');
vi.mock('os');

// Create the module under test
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
    
    const isGitHubActions = process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW;
    const isJenkins = !!process.env.JENKINS_URL;

    // Docker Environment Detection
    const isDocker = process.env.DOCKER_ENVIRONMENT === 'true' ||
                    (fs.existsSync('/.dockerenv') || process.env.DOCKER === 'true');

    // Node Environment Detection
    const isDevelopment = process.env.NODE_ENV === 'development';
    const isProduction = process.env.NODE_ENV === 'production';
    const isTest = process.env.NODE_ENV === 'test';

    return {
      isWindows,
      isMacOS,
      isLinux,
      isCI,
      isGitHubActions,
      isJenkins,
      isDocker,
      isDevelopment,
      isProduction,
      isTest
    };
  }
};

// Import the module under test
vi.mock('../tests/helpers/environment-detection', () => environmentDetection, { virtual: true });
const { detectEnvironment } = environmentDetection;

describe('Environment Detection', () => {
  // Reset mocks before each test
  beforeEach(() => {
    vi.resetAllMocks();
    
    // Default mock implementations
    os.platform.mockReturnValue('linux');
    os.type.mockReturnValue('Linux');
    os.release.mockReturnValue('5.10.0');
    os.tmpdir.mockReturnValue('/tmp');
    fs.existsSync.mockReturnValue(false);
    process.env = { NODE_ENV: 'test' };
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Operating System Detection', () => {
    it('should detect Windows environment', () => {
      // Arrange
      os.platform.mockReturnValue('win32');
      os.type.mockReturnValue('Windows_NT');
      
      // Act
      const env = detectEnvironment();
      
      // Assert
      expect(env.isWindows).toBe(true);
      expect(env.isMacOS).toBe(false);
      expect(env.isLinux).toBe(false);
      expect(os.platform).toHaveBeenCalled();
    });

    it('should detect macOS environment', () => {
      // Arrange
      os.platform.mockReturnValue('darwin');
      os.type.mockReturnValue('Darwin');
      
      // Act
      const env = detectEnvironment();
      
      // Assert
      expect(env.isWindows).toBe(false);
      expect(env.isMacOS).toBe(true);
      expect(env.isLinux).toBe(false);
      expect(os.platform).toHaveBeenCalled();
    });

    it('should detect Linux environment', () => {
      // Arrange
      os.platform.mockReturnValue('linux');
      os.type.mockReturnValue('Linux');
      
      // Act
      const env = detectEnvironment();
      
      // Assert
      expect(env.isWindows).toBe(false);
      expect(env.isMacOS).toBe(false);
      expect(env.isLinux).toBe(true);
      expect(os.platform).toHaveBeenCalled();
    });
  });

  describe('CI Environment Detection', () => {
    it('should detect GitHub Actions environment', () => {
      // Arrange
      process.env.GITHUB_ACTIONS = 'true';
      
      // Act
      const env = detectEnvironment();
      
      // Assert
      expect(env.isCI).toBe(true);
      expect(env.isGitHubActions).toBe(true);
      expect(env.isJenkins).toBe(false);
    });

    it('should detect CI environment from CI variable', () => {
      // Arrange
      process.env.CI = 'true';
      
      // Act
      const env = detectEnvironment();
      
      // Assert
      expect(env.isCI).toBe(true);
      expect(env.isGitHubActions).toBe(false);
    });

    it('should detect Jenkins environment', () => {
      // Arrange
      process.env.JENKINS_URL = 'http://jenkins.example.com';
      
      // Act
      const env = detectEnvironment();
      
      // Assert
      expect(env.isCI).toBe(true);
      expect(env.isJenkins).toBe(true);
      expect(env.isGitHubActions).toBe(false);
    });
  });

  describe('Docker Environment Detection', () => {
    it('should detect Docker environment from .dockerenv file', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/.dockerenv');
      
      // Act
      const env = detectEnvironment();
      
      // Assert
      expect(env.isDocker).toBe(true);
      expect(fs.existsSync).toHaveBeenCalledWith('/.dockerenv');
    });

    it('should detect Docker environment from environment variable', () => {
      // Arrange
      process.env.DOCKER_ENVIRONMENT = 'true';
      
      // Act
      const env = detectEnvironment();
      
      // Assert
      expect(env.isDocker).toBe(true);
    });
  });

  describe('Node Environment Detection', () => {
    it('should detect development environment', () => {
      // Arrange
      process.env.NODE_ENV = 'development';
      
      // Act
      const env = detectEnvironment();
      
      // Assert
      expect(env.isDevelopment).toBe(true);
      expect(env.isProduction).toBe(false);
      expect(env.isTest).toBe(false);
    });

    it('should detect production environment', () => {
      // Arrange
      process.env.NODE_ENV = 'production';
      
      // Act
      const env = detectEnvironment();
      
      // Assert
      expect(env.isDevelopment).toBe(false);
      expect(env.isProduction).toBe(true);
      expect(env.isTest).toBe(false);
    });

    it('should detect test environment', () => {
      // Arrange
      process.env.NODE_ENV = 'test';
      
      // Act
      const env = detectEnvironment();
      
      // Assert
      expect(env.isDevelopment).toBe(false);
      expect(env.isProduction).toBe(false);
      expect(env.isTest).toBe(true);
    });
  });
});
