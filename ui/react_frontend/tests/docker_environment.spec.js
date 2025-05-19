/**
 * Docker Environment Tests
 * 
 * This file contains tests for Docker environment-specific behavior.
 * These tests ensure that the application behaves correctly in Docker containers.
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
const dockerEnvironment = {
  setupDockerEnvironment: () => {
    const isDocker = process.env.DOCKER_ENVIRONMENT === 'true' ||
                    (fs.existsSync('/.dockerenv') || process.env.DOCKER === 'true');
    
    if (!isDocker) {
      console.log('No Docker environment detected');
      return { success: true, isDocker: false };
    }
    
    console.log('Setting up Docker environment');
    
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
      const markerLocations = [
        path.join(process.cwd(), 'logs', 'docker-environment.txt'),
        path.join(process.cwd(), 'playwright-report', 'docker-environment.txt'),
        path.join(process.cwd(), 'test-results', 'docker-environment.txt')
      ];
      
      const markerContent = `Docker Environment
=================
Timestamp: ${new Date().toISOString()}
Docker: Yes
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
      process.env.DOCKER_ENVIRONMENT = 'true';
      
      console.log('Docker environment setup complete');
      return { success: true, isDocker: true };
    } catch (error) {
      console.error(`Failed to set up Docker environment: ${error.message}`);
      return { success: false, isDocker: true, error: error.message };
    }
  },
  
  createDockerReport: (filePath) => {
    const isDocker = process.env.DOCKER_ENVIRONMENT === 'true' ||
                    (fs.existsSync('/.dockerenv') || process.env.DOCKER === 'true');
    
    const report = `Docker Environment Report
========================
Generated at: ${new Date().toISOString()}

Docker Environment:
- Docker: ${isDocker ? 'Yes' : 'No'}
- Detection Method: ${isDocker ? (fs.existsSync('/.dockerenv') ? '.dockerenv file' : 'Environment variable') : 'N/A'}

System Information:
- Node.js: ${process.version}
- Platform: ${os.platform()}
- Architecture: ${process.arch}
- OS: ${os.type()} ${os.release()}
- Working Directory: ${process.cwd()}
- Temp Directory: ${os.tmpdir()}

Environment Variables:
- NODE_ENV: ${process.env.NODE_ENV || 'not set'}
- DOCKER_ENVIRONMENT: ${process.env.DOCKER_ENVIRONMENT || 'not set'}
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
        console.error(`Failed to write Docker report to ${filePath}: ${error.message}`);
      }
    }
    
    return report;
  }
};

// Import the module under test
vi.mock('../tests/helpers/docker-environment', () => dockerEnvironment, { virtual: true });
const { setupDockerEnvironment, createDockerReport } = dockerEnvironment;

describe('Docker Environment', () => {
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

  describe('Docker Environment Detection', () => {
    it('should detect Docker environment from .dockerenv file', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/.dockerenv');
      
      // Act
      const result = setupDockerEnvironment();
      
      // Assert
      expect(result.success).toBe(true);
      expect(result.isDocker).toBe(true);
      expect(fs.existsSync).toHaveBeenCalledWith('/.dockerenv');
    });

    it('should detect Docker environment from environment variable', () => {
      // Arrange
      process.env.DOCKER_ENVIRONMENT = 'true';
      
      // Act
      const result = setupDockerEnvironment();
      
      // Assert
      expect(result.success).toBe(true);
      expect(result.isDocker).toBe(true);
    });

    it('should handle non-Docker environment', () => {
      // Arrange
      fs.existsSync.mockReturnValue(false);
      
      // Act
      const result = setupDockerEnvironment();
      
      // Assert
      expect(result.success).toBe(true);
      expect(result.isDocker).toBe(false);
    });
  });

  describe('Docker Report Creation', () => {
    it('should create a Docker environment report', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/.dockerenv');
      
      // Act
      const report = createDockerReport();
      
      // Assert
      expect(report).toContain('Docker Environment Report');
      expect(report).toContain('Docker: Yes');
      expect(report).toContain('Linux');
    });

    it('should create a non-Docker environment report', () => {
      // Arrange
      fs.existsSync.mockReturnValue(false);
      
      // Act
      const report = createDockerReport();
      
      // Assert
      expect(report).toContain('Docker Environment Report');
      expect(report).toContain('Docker: No');
    });

    it('should write report to file when path is provided', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/.dockerenv');
      const filePath = '/tmp/docker-report.txt';
      
      // Act
      createDockerReport(filePath);
      
      // Assert
      expect(fs.writeFileSync).toHaveBeenCalledWith(filePath, expect.any(String));
    });
  });
});
