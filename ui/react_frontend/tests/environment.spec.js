/**
 * Environment Detection Tests
 * 
 * This file contains tests for the environment detection module.
 * It tests the detection of different environments:
 * - Operating Systems (Windows, macOS, Linux, WSL)
 * - CI environments (GitHub Actions, Jenkins, GitLab CI, etc.)
 * - Container environments (Docker, Kubernetes, Docker Compose, etc.)
 * - Cloud environments (AWS, Azure, GCP)
 * 
 * @version 1.0.0
 */

const { describe, it, expect, beforeEach, afterEach, vi } = require('vitest');
const path = require('path');
const fs = require('fs');
const os = require('os');

// Import the environment detection module
const { 
  detectEnvironment, 
  createEnvironmentReport,
  safeFileExists,
  safeReadFile,
  safelyCreateDirectory,
  safelyWriteFile
} = require('./helpers/environment-detection');

describe('Environment Detection Module', () => {
  // Save original environment variables
  const originalEnv = { ...process.env };
  
  // Mock fs, os, and process modules
  vi.mock('fs', () => ({
    existsSync: vi.fn(),
    readFileSync: vi.fn(),
    mkdirSync: vi.fn(),
    writeFileSync: vi.fn(),
    unlinkSync: vi.fn()
  }));
  
  vi.mock('os', () => ({
    platform: vi.fn(),
    type: vi.fn(),
    release: vi.fn(),
    tmpdir: vi.fn(),
    homedir: vi.fn(),
    hostname: vi.fn(),
    userInfo: vi.fn(),
    totalmem: vi.fn(),
    freemem: vi.fn(),
    cpus: vi.fn()
  }));
  
  // Reset mocks and environment variables before each test
  beforeEach(() => {
    vi.resetAllMocks();
    process.env = { ...originalEnv };
    
    // Default mock values
    os.platform.mockReturnValue('linux');
    os.type.mockReturnValue('Linux');
    os.release.mockReturnValue('5.10.0');
    os.tmpdir.mockReturnValue('/tmp');
    os.homedir.mockReturnValue('/home/user');
    os.hostname.mockReturnValue('test-host');
    os.userInfo.mockReturnValue({ username: 'testuser' });
    os.totalmem.mockReturnValue(8589934592); // 8 GB
    os.freemem.mockReturnValue(4294967296); // 4 GB
    os.cpus.mockReturnValue([
      { model: 'Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz', speed: 2600 },
      { model: 'Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz', speed: 2600 }
    ]);
    
    // Mock process.cwd()
    vi.spyOn(process, 'cwd').mockReturnValue('/home/user/project');
    
    // Mock fs functions
    fs.existsSync.mockReturnValue(false);
    fs.readFileSync.mockReturnValue('');
    fs.mkdirSync.mockReturnValue(undefined);
    fs.writeFileSync.mockReturnValue(undefined);
  });
  
  // Restore original environment variables after each test
  afterEach(() => {
    process.env = originalEnv;
    vi.restoreAllMocks();
  });
  
  describe('detectEnvironment', () => {
    it('should detect Linux environment', () => {
      os.platform.mockReturnValue('linux');
      
      const env = detectEnvironment();
      
      expect(env.isLinux).toBe(true);
      expect(env.isWindows).toBe(false);
      expect(env.isMacOS).toBe(false);
      expect(env.platform).toBe('linux');
    });
    
    it('should detect Windows environment', () => {
      os.platform.mockReturnValue('win32');
      
      const env = detectEnvironment();
      
      expect(env.isWindows).toBe(true);
      expect(env.isLinux).toBe(false);
      expect(env.isMacOS).toBe(false);
      expect(env.platform).toBe('win32');
    });
    
    it('should detect macOS environment', () => {
      os.platform.mockReturnValue('darwin');
      
      const env = detectEnvironment();
      
      expect(env.isMacOS).toBe(true);
      expect(env.isWindows).toBe(false);
      expect(env.isLinux).toBe(false);
      expect(env.platform).toBe('darwin');
    });
    
    it('should detect WSL environment', () => {
      os.platform.mockReturnValue('linux');
      process.env.WSL_DISTRO_NAME = 'Ubuntu';
      
      const env = detectEnvironment();
      
      expect(env.isWSL).toBe(true);
      expect(env.isLinux).toBe(true);
    });
    
    it('should detect GitHub Actions CI environment', () => {
      process.env.GITHUB_ACTIONS = 'true';
      
      const env = detectEnvironment();
      
      expect(env.isCI).toBe(true);
      expect(env.isGitHubActions).toBe(true);
    });
    
    it('should detect Docker environment', () => {
      fs.existsSync.mockImplementation((path) => {
        if (path === '/.dockerenv') return true;
        return false;
      });
      
      const env = detectEnvironment();
      
      expect(env.isDocker).toBe(true);
      expect(env.isContainerized).toBe(true);
    });
    
    it('should detect Kubernetes environment', () => {
      process.env.KUBERNETES_SERVICE_HOST = 'kubernetes.default.svc.cluster.local';
      
      const env = detectEnvironment();
      
      expect(env.isKubernetes).toBe(true);
      expect(env.isContainerized).toBe(true);
    });
    
    it('should detect Docker Compose environment', () => {
      process.env.COMPOSE_PROJECT_NAME = 'test-project';
      
      const env = detectEnvironment();
      
      expect(env.isDockerCompose).toBe(true);
      expect(env.isContainerized).toBe(true);
    });
    
    it('should detect AWS environment', () => {
      process.env.AWS_REGION = 'us-west-2';
      
      const env = detectEnvironment();
      
      expect(env.isAWS).toBe(true);
      expect(env.isCloudEnvironment).toBe(true);
    });
    
    it('should detect Azure environment', () => {
      process.env.AZURE_FUNCTIONS_ENVIRONMENT = 'Production';
      
      const env = detectEnvironment();
      
      expect(env.isAzure).toBe(true);
      expect(env.isCloudEnvironment).toBe(true);
    });
    
    it('should detect GCP environment', () => {
      process.env.GOOGLE_CLOUD_PROJECT = 'test-project';
      
      const env = detectEnvironment();
      
      expect(env.isGCP).toBe(true);
      expect(env.isCloudEnvironment).toBe(true);
    });
    
    it('should detect Node.js environment', () => {
      process.env.NODE_ENV = 'production';
      
      const env = detectEnvironment();
      
      expect(env.isProduction).toBe(true);
      expect(env.isDevelopment).toBe(false);
      expect(env.isTest).toBe(false);
    });
    
    it('should handle errors gracefully', () => {
      os.userInfo.mockImplementation(() => {
        throw new Error('User info error');
      });
      
      const env = detectEnvironment();
      
      expect(env.username).toBe('unknown');
      expect(env.platform).toBe('linux');
    });
  });
  
  describe('Utility Functions', () => {
    it('should safely check if a file exists', () => {
      fs.existsSync.mockImplementation((path) => {
        if (path === '/test/exists.txt') return true;
        return false;
      });
      
      expect(safeFileExists('/test/exists.txt')).toBe(true);
      expect(safeFileExists('/test/not-exists.txt')).toBe(false);
      
      fs.existsSync.mockImplementation(() => {
        throw new Error('File system error');
      });
      
      expect(safeFileExists('/test/error.txt')).toBe(false);
    });
    
    it('should safely read a file', () => {
      fs.readFileSync.mockImplementation((path) => {
        if (path === '/test/file.txt') return 'file content';
        throw new Error('File not found');
      });
      
      expect(safeReadFile('/test/file.txt')).toBe('file content');
      expect(safeReadFile('/test/not-found.txt')).toBe(null);
    });
    
    it('should safely create a directory', () => {
      fs.existsSync.mockReturnValue(false);
      
      expect(safelyCreateDirectory('/test/dir')).toBe(true);
      expect(fs.mkdirSync).toHaveBeenCalledWith('/test/dir', { recursive: true });
      
      fs.mkdirSync.mockImplementation(() => {
        throw new Error('Permission denied');
      });
      
      expect(safelyCreateDirectory('/test/error-dir')).toBe(false);
    });
    
    it('should safely write a file', () => {
      fs.existsSync.mockReturnValue(false);
      
      expect(safelyWriteFile('/test/file.txt', 'content')).toBe(true);
      expect(fs.writeFileSync).toHaveBeenCalledWith('/test/file.txt', 'content');
      
      fs.writeFileSync.mockImplementation(() => {
        throw new Error('Permission denied');
      });
      
      expect(safelyWriteFile('/test/error-file.txt', 'content')).toBe(false);
    });
  });
});
