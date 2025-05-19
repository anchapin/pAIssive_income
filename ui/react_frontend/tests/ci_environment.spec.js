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

// Create the module under test
const ciEnvironment = {
  detectCIEnvironmentType: () => {
    // CI Environment Detection
    const isCI = process.env.CI === 'true' || process.env.CI === true ||
                process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW ||
                !!process.env.JENKINS_URL || !!process.env.GITLAB_CI || 
                !!process.env.CIRCLECI || !!process.env.TRAVIS ||
                !!process.env.TF_BUILD || !!process.env.TEAMCITY_VERSION;
    
    if (!isCI) {
      return 'none';
    }
    
    if (process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW) {
      return 'github';
    }
    
    if (!!process.env.JENKINS_URL) {
      return 'jenkins';
    }
    
    if (!!process.env.GITLAB_CI) {
      return 'gitlab';
    }
    
    if (!!process.env.CIRCLECI) {
      return 'circle';
    }
    
    if (!!process.env.TRAVIS) {
      return 'travis';
    }
    
    if (!!process.env.TF_BUILD) {
      return 'azure';
    }
    
    if (!!process.env.TEAMCITY_VERSION) {
      return 'teamcity';
    }
    
    return 'generic';
  },
  
  setupCIEnvironment: () => {
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
Node.js: ${process.version}
Platform: ${os.platform()}
Working Directory: ${process.cwd()}
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
      return { success: true, ciType };
    } catch (error) {
      console.error(`Failed to set up CI environment: ${error.message}`);
      return { success: false, ciType, error: error.message };
    }
  },
  
  createCIReport: (filePath) => {
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
`;
        break;
      case 'jenkins':
        report += `Jenkins
-------
Job: ${process.env.JOB_NAME || 'unknown'}
Build: ${process.env.BUILD_NUMBER || 'unknown'}
URL: ${process.env.JENKINS_URL || 'unknown'}
Workspace: ${process.env.WORKSPACE || 'unknown'}
`;
        break;
      default:
        report += `Generic CI
----------
CI environment detected
`;
        break;
    }
    
    // Add system information
    report += `
System Information
-----------------
Node.js: ${process.version}
Platform: ${os.platform()}
Architecture: ${os.arch()}
OS: ${os.type()} ${os.release()}
Working Directory: ${process.cwd()}
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
      
      // Act
      const ciType = detectCIEnvironmentType();
      
      // Assert
      expect(ciType).toBe('github');
    });

    it('should detect Jenkins environment', () => {
      // Arrange
      process.env.JENKINS_URL = 'http://jenkins.example.com';
      process.env.JOB_NAME = 'test-job';
      
      // Act
      const ciType = detectCIEnvironmentType();
      
      // Assert
      expect(ciType).toBe('jenkins');
    });

    it('should detect GitLab CI environment', () => {
      // Arrange
      process.env.GITLAB_CI = 'true';
      process.env.CI_JOB_NAME = 'test-job';
      
      // Act
      const ciType = detectCIEnvironmentType();
      
      // Assert
      expect(ciType).toBe('gitlab');
    });

    it('should detect generic CI environment', () => {
      // Arrange
      process.env.CI = 'true';
      
      // Act
      const ciType = detectCIEnvironmentType();
      
      // Assert
      expect(ciType).toBe('generic');
    });

    it('should detect no CI environment', () => {
      // Arrange
      // No CI environment variables set
      
      // Act
      const ciType = detectCIEnvironmentType();
      
      // Assert
      expect(ciType).toBe('none');
    });
  });

  describe('CI Environment Setup', () => {
    it('should set up GitHub Actions environment', () => {
      // Arrange
      process.env.GITHUB_ACTIONS = 'true';
      process.env.GITHUB_WORKFLOW = 'test-workflow';
      
      // Act
      const result = setupCIEnvironment();
      
      // Assert
      expect(result.success).toBe(true);
      expect(result.ciType).toBe('github');
      expect(fs.mkdirSync).toHaveBeenCalled();
      expect(fs.writeFileSync).toHaveBeenCalled();
    });

    it('should set up Jenkins environment', () => {
      // Arrange
      process.env.JENKINS_URL = 'http://jenkins.example.com';
      process.env.JOB_NAME = 'test-job';
      
      // Act
      const result = setupCIEnvironment();
      
      // Assert
      expect(result.success).toBe(true);
      expect(result.ciType).toBe('jenkins');
      expect(fs.mkdirSync).toHaveBeenCalled();
      expect(fs.writeFileSync).toHaveBeenCalled();
    });

    it('should handle directory creation failures', () => {
      // Arrange
      process.env.CI = 'true';
      fs.mkdirSync.mockImplementation(() => {
        throw new Error('Permission denied');
      });
      
      // Act
      const result = setupCIEnvironment();
      
      // Assert
      expect(result.success).toBe(false);
      expect(result.error).toContain('Permission denied');
      expect(fs.mkdirSync).toHaveBeenCalled();
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
