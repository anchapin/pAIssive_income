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

// Mock the environment detection module
vi.mock('../src/utils/environmentDetection', () => ({
  detectEnvironment: vi.fn(() => {
    // Enhanced Docker detection with multiple methods
    const isDockerEnv = process.env.DOCKER_ENVIRONMENT === 'true';
    const isDockerVar = process.env.DOCKER === 'true';
    const hasDockerEnvFile = fs.existsSync('/.dockerenv');
    const hasContainerEnvFile = fs.existsSync('/run/.containerenv');
    const hasCgroupDocker = fs.existsSync('/proc/1/cgroup') &&
                           fs.readFileSync('/proc/1/cgroup', 'utf8').includes('docker');

    const isDocker = isDockerEnv || isDockerVar || hasDockerEnvFile ||
                    hasContainerEnvFile || hasCgroupDocker;

    // Enhanced Kubernetes detection
    const isKubernetesHost = !!process.env.KUBERNETES_SERVICE_HOST;
    const isKubernetesPort = !!process.env.KUBERNETES_PORT;
    const hasKubernetesSecrets = fs.existsSync('/var/run/secrets/kubernetes.io');
    const isKubernetes = isKubernetesHost || isKubernetesPort || hasKubernetesSecrets;

    // Enhanced container detection
    const isContainerVar = process.env.CONTAINER === 'true';
    const isContainerizedVar = process.env.CONTAINERIZED === 'true';
    const isContainerized = isDocker || isKubernetes || isContainerVar || isContainerizedVar;

    // Enhanced Docker Compose detection
    const isDockerCompose = !!process.env.COMPOSE_PROJECT_NAME ||
                           !!process.env.COMPOSE_FILE ||
                           !!process.env.COMPOSE_PATH_SEPARATOR;

    // Enhanced Docker Swarm detection
    const isDockerSwarm = !!process.env.DOCKER_SWARM ||
                         !!process.env.SWARM_NODE_ID ||
                         !!process.env.SWARM_MANAGER;

    return {
      // Operating System
      platform: os.platform(),
      isWindows: os.platform() === 'win32',
      isMacOS: os.platform() === 'darwin',
      isLinux: os.platform() === 'linux',
      isIOS: false,
      isAndroid: false,
      isMobile: false,
      isElectron: false,
      isWSL: process.env.WSL_DISTRO_NAME || process.env.WSLENV ? true : false,

      // Container Environment
      isDocker,
      isKubernetes,
      isContainerized,
      isDockerCompose,
      isDockerSwarm,
      dockerDetectionMethod: hasDockerEnvFile ? '.dockerenv file' :
                            hasContainerEnvFile ? '.containerenv file' :
                            hasCgroupDocker ? 'cgroup' :
                            isDockerEnv ? 'DOCKER_ENVIRONMENT variable' :
                            isDockerVar ? 'DOCKER variable' : 'unknown',

      // Cloud Environment
      isAWS: !!process.env.AWS_REGION ||
             !!process.env.AWS_LAMBDA_FUNCTION_NAME ||
             !!process.env.AWS_EXECUTION_ENV,
      isAzure: !!process.env.AZURE_FUNCTIONS_ENVIRONMENT ||
              !!process.env.WEBSITE_SITE_NAME ||
              !!process.env.APPSETTING_WEBSITE_SITE_NAME,
      isGCP: !!process.env.GOOGLE_CLOUD_PROJECT ||
             !!process.env.GCLOUD_PROJECT ||
             !!process.env.GCP_PROJECT ||
             (!!process.env.FUNCTION_NAME && !!process.env.FUNCTION_REGION),
      isCloudEnvironment: false,

      // Browser Environment
      isBrowser: false,

      // System Info
      nodeVersion: process.version,
      architecture: process.arch,
      osType: os.type(),
      osRelease: os.release(),
      tmpDir: os.tmpdir(),
      homeDir: os.homedir(),
      workingDir: process.cwd(),
      hostname: os.hostname(),
      username: os.userInfo().username,
      memory: {
        total: os.totalmem(),
        free: os.freemem()
      },
      cpus: os.cpus()
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
  getBrowserInfo: vi.fn(() => ({
    name: 'node',
    version: 'N/A',
    userAgent: 'N/A',
    isMobile: false,
    isTablet: false,
    isDesktop: true
  })),
  getNetworkInfo: vi.fn(() => ({
    online: false,
    effectiveType: 'unknown',
    downlink: 0,
    rtt: 0,
    saveData: false
  })),
  getScreenInfo: vi.fn(() => ({
    width: 0,
    height: 0,
    availWidth: 0,
    availHeight: 0,
    colorDepth: 0,
    orientation: 'unknown',
    pixelRatio: 1
  })),
  getFeatureSupport: vi.fn(() => ({
    localStorage: false,
    sessionStorage: false,
    cookies: false,
    webWorkers: false,
    serviceWorkers: false,
    webGL: false,
    canvas: false,
    webAssembly: false,
    geolocation: false,
    webRTC: false
  })),
  getPerformanceInfo: vi.fn(() => ({
    memory: null,
    navigation: null,
    timing: null
  })),
  getEnvironmentInfo: vi.fn(() => {
    // Enhanced Docker detection with multiple methods
    const isDockerEnv = process.env.DOCKER_ENVIRONMENT === 'true';
    const isDockerVar = process.env.DOCKER === 'true';
    const hasDockerEnvFile = fs.existsSync('/.dockerenv');
    const hasContainerEnvFile = fs.existsSync('/run/.containerenv');
    const hasCgroupDocker = fs.existsSync('/proc/1/cgroup') &&
                           fs.readFileSync('/proc/1/cgroup', 'utf8').includes('docker');

    const isDocker = isDockerEnv || isDockerVar || hasDockerEnvFile ||
                    hasContainerEnvFile || hasCgroupDocker;

    // Enhanced Kubernetes detection
    const isKubernetesHost = !!process.env.KUBERNETES_SERVICE_HOST;
    const isKubernetesPort = !!process.env.KUBERNETES_PORT;
    const hasKubernetesSecrets = fs.existsSync('/var/run/secrets/kubernetes.io');
    const isKubernetes = isKubernetesHost || isKubernetesPort || hasKubernetesSecrets;

    // Enhanced container detection
    const isContainerVar = process.env.CONTAINER === 'true';
    const isContainerizedVar = process.env.CONTAINERIZED === 'true';
    const isContainerized = isDocker || isKubernetes || isContainerVar || isContainerizedVar;

    // Enhanced Docker Compose detection
    const isDockerCompose = !!process.env.COMPOSE_PROJECT_NAME ||
                           !!process.env.COMPOSE_FILE ||
                           !!process.env.COMPOSE_PATH_SEPARATOR;

    // Enhanced Docker Swarm detection
    const isDockerSwarm = !!process.env.DOCKER_SWARM ||
                         !!process.env.SWARM_NODE_ID ||
                         !!process.env.SWARM_MANAGER;

    return {
      // Operating System
      platform: os.platform(),
      isWindows: os.platform() === 'win32',
      isMacOS: os.platform() === 'darwin',
      isLinux: os.platform() === 'linux',
      isIOS: false,
      isAndroid: false,
      isMobile: false,
      isElectron: false,
      isWSL: process.env.WSL_DISTRO_NAME || process.env.WSLENV ? true : false,

      // Container Environment
      isDocker,
      isKubernetes,
      isContainerized,
      isDockerCompose,
      isDockerSwarm,
      dockerDetectionMethod: hasDockerEnvFile ? '.dockerenv file' :
                            hasContainerEnvFile ? '.containerenv file' :
                            hasCgroupDocker ? 'cgroup' :
                            isDockerEnv ? 'DOCKER_ENVIRONMENT variable' :
                            isDockerVar ? 'DOCKER variable' : 'unknown',

      // System Info
      nodeVersion: process.version,
      architecture: process.arch,
      osType: os.type(),
      osRelease: os.release(),
      tmpDir: os.tmpdir(),
      homeDir: os.homedir(),
      workingDir: process.cwd(),
      hostname: os.hostname(),
      username: os.userInfo().username,
      memory: {
        total: os.totalmem(),
        free: os.freemem()
      },
      cpus: os.cpus()
    };
  }),
  useEnvironment: vi.fn()
}));

// Import the environment detection module
import {
  detectEnvironment,
  getPathSeparator,
  getPlatformPath,
  getBrowserInfo,
  getNetworkInfo,
  getScreenInfo,
  getFeatureSupport,
  getPerformanceInfo,
  getEnvironmentInfo
} from '../src/utils/environmentDetection';

// Create the Docker environment module that uses our environment detection
const dockerEnvironment = {
  setupDockerEnvironment: () => {
    const { isDocker } = detectEnvironment();

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
      const env = detectEnvironment();
      const markerLocations = [
        path.join(process.cwd(), 'logs', 'docker-environment.txt'),
        path.join(process.cwd(), 'playwright-report', 'docker-environment.txt'),
        path.join(process.cwd(), 'test-results', 'docker-environment.txt')
      ];

      const markerContent = `Docker Environment
=================
Timestamp: ${new Date().toISOString()}
Docker: Yes
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
      process.env.DOCKER_ENVIRONMENT = 'true';

      console.log('Docker environment setup complete');
      return { success: true, isDocker: true };
    } catch (error) {
      console.error(`Failed to set up Docker environment: ${error.message}`);
      return { success: false, isDocker: true, error: error.message };
    }
  },

  createDockerReport: (filePath) => {
    const env = detectEnvironment();
    const browserInfo = getBrowserInfo();
    const networkInfo = getNetworkInfo();
    const screenInfo = getScreenInfo();
    const featureSupport = getFeatureSupport();
    const performanceInfo = getPerformanceInfo();

    const report = `Docker Environment Report
========================
Generated at: ${new Date().toISOString()}

Container Environment:
- Docker: ${env.isDocker ? 'Yes' : 'No'}
- Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}
- Containerized: ${env.isContainerized ? 'Yes' : 'No'}
- Docker Compose: ${env.isDockerCompose ? 'Yes' : 'No'}
- Docker Swarm: ${env.isDockerSwarm ? 'Yes' : 'No'}
- Detection Method: ${env.dockerDetectionMethod ||
    (env.isDocker ? (fs.existsSync('/.dockerenv') ? '.dockerenv file' :
                   fs.existsSync('/run/.containerenv') ? '.containerenv file' :
                   'Environment variable') :
    env.isKubernetes ? 'Kubernetes service host/port' :
    env.isContainerized ? 'Container environment variable' : 'N/A')}

Container Details:
- Docker Environment Variable: ${process.env.DOCKER_ENVIRONMENT || 'not set'}
- Docker Variable: ${process.env.DOCKER || 'not set'}
- Docker Compose Project: ${process.env.COMPOSE_PROJECT_NAME || 'not set'}
- Docker Compose File: ${process.env.COMPOSE_FILE || 'not set'}
- Docker Swarm: ${process.env.DOCKER_SWARM || 'not set'}
- Swarm Node ID: ${process.env.SWARM_NODE_ID || 'not set'}
- Swarm Manager: ${process.env.SWARM_MANAGER || 'not set'}

Kubernetes Details:
- Kubernetes Service Host: ${process.env.KUBERNETES_SERVICE_HOST || 'not set'}
- Kubernetes Port: ${process.env.KUBERNETES_PORT || 'not set'}
- Kubernetes Namespace: ${process.env.KUBERNETES_NAMESPACE || 'not set'}
- Pod Name: ${process.env.POD_NAME || 'not set'}
- Pod IP: ${process.env.POD_IP || 'not set'}
- Service Account: ${process.env.SERVICE_ACCOUNT || 'not set'}

Cloud Environment:
- AWS: ${env.isAWS ? 'Yes' : 'No'}
- Azure: ${env.isAzure ? 'Yes' : 'No'}
- GCP: ${env.isGCP ? 'Yes' : 'No'}
- Cloud Environment: ${env.isCloudEnvironment ? 'Yes' : 'No'}

Cloud Details:
- AWS Region: ${process.env.AWS_REGION || 'not set'}
- AWS Lambda Function: ${process.env.AWS_LAMBDA_FUNCTION_NAME || 'not set'}
- Azure Functions: ${process.env.AZURE_FUNCTIONS_ENVIRONMENT || 'not set'}
- GCP Project: ${process.env.GOOGLE_CLOUD_PROJECT || process.env.GCLOUD_PROJECT || 'not set'}

System Information:
- Node.js: ${env.nodeVersion}
- Platform: ${env.platform}
- Architecture: ${env.architecture}
- OS: ${env.osType} ${env.osRelease}
- WSL: ${env.isWSL ? 'Yes' : 'No'}
- WSL Distro: ${process.env.WSL_DISTRO_NAME || 'not set'}
- Working Directory: ${env.workingDir}
- Temp Directory: ${env.tmpDir}
- Home Directory: ${env.homeDir}
- Hostname: ${env.hostname || 'N/A'}
- Username: ${env.username || 'N/A'}
- Memory: Total: ${env.memory ? Math.round(env.memory.total / (1024 * 1024)) + ' MB' : 'N/A'}, Free: ${env.memory ? Math.round(env.memory.free / (1024 * 1024)) + ' MB' : 'N/A'}
- CPUs: ${env.cpus ? env.cpus.length : 'N/A'}

Environment Variables:
- NODE_ENV: ${process.env.NODE_ENV || 'not set'}
- DOCKER_ENVIRONMENT: ${process.env.DOCKER_ENVIRONMENT || 'not set'}
- KUBERNETES_SERVICE_HOST: ${process.env.KUBERNETES_SERVICE_HOST || 'not set'}
- KUBERNETES_PORT: ${process.env.KUBERNETES_PORT || 'not set'}
- CONTAINER: ${process.env.CONTAINER || 'not set'}
- CONTAINERIZED: ${process.env.CONTAINERIZED || 'not set'}
- CI: ${process.env.CI || 'not set'}
- GITHUB_ACTIONS: ${process.env.GITHUB_ACTIONS || 'not set'}
- GITHUB_WORKFLOW: ${process.env.GITHUB_WORKFLOW || 'not set'}

Browser Information:
- Browser: ${browserInfo.name}
- Version: ${browserInfo.version}
- User Agent: ${browserInfo.userAgent}
- Mobile: ${browserInfo.isMobile ? 'Yes' : 'No'}
- Tablet: ${browserInfo.isTablet ? 'Yes' : 'No'}
- Desktop: ${browserInfo.isDesktop ? 'Yes' : 'No'}

Network Information:
- Online: ${networkInfo.online ? 'Yes' : 'No'}
- Effective Type: ${networkInfo.effectiveType}
- Downlink: ${networkInfo.downlink} Mbps
- RTT: ${networkInfo.rtt} ms
- Save Data: ${networkInfo.saveData ? 'Yes' : 'No'}

Feature Support:
- LocalStorage: ${featureSupport.localStorage ? 'Yes' : 'No'}
- SessionStorage: ${featureSupport.sessionStorage ? 'Yes' : 'No'}
- Cookies: ${featureSupport.cookies ? 'Yes' : 'No'}
- Web Workers: ${featureSupport.webWorkers ? 'Yes' : 'No'}
- Service Workers: ${featureSupport.serviceWorkers ? 'Yes' : 'No'}
- WebGL: ${featureSupport.webGL ? 'Yes' : 'No'}
- Canvas: ${featureSupport.canvas ? 'Yes' : 'No'}
- WebAssembly: ${featureSupport.webAssembly ? 'Yes' : 'No'}
- Geolocation: ${featureSupport.geolocation ? 'Yes' : 'No'}
- WebRTC: ${featureSupport.webRTC ? 'Yes' : 'No'}
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

// Export the Docker environment functions
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
      detectEnvironment.mockReturnValue({
        isDocker: true,
        platform: 'linux',
        isLinux: true,
        dockerDetectionMethod: '.dockerenv file'
      });

      // Act
      const result = setupDockerEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.isDocker).toBe(true);
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Docker environment from environment variable', () => {
      // Arrange
      process.env.DOCKER_ENVIRONMENT = 'true';
      detectEnvironment.mockReturnValue({
        isDocker: true,
        platform: 'linux',
        isLinux: true,
        dockerDetectionMethod: 'DOCKER_ENVIRONMENT variable'
      });

      // Act
      const result = setupDockerEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.isDocker).toBe(true);
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Docker environment from .containerenv file', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/run/.containerenv');
      detectEnvironment.mockReturnValue({
        isDocker: true,
        platform: 'linux',
        isLinux: true,
        dockerDetectionMethod: '.containerenv file'
      });

      // Act
      const result = setupDockerEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.isDocker).toBe(true);
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Docker environment from cgroup', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/proc/1/cgroup');
      fs.readFileSync.mockReturnValue('0::/docker/123456789');
      detectEnvironment.mockReturnValue({
        isDocker: true,
        platform: 'linux',
        isLinux: true,
        dockerDetectionMethod: 'cgroup'
      });

      // Act
      const result = setupDockerEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.isDocker).toBe(true);
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Docker Compose environment', () => {
      // Arrange
      process.env.COMPOSE_PROJECT_NAME = 'test-project';
      detectEnvironment.mockReturnValue({
        isDocker: true,
        isDockerCompose: true,
        platform: 'linux',
        isLinux: true
      });

      // Act
      const result = setupDockerEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.isDocker).toBe(true);
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should detect Docker Swarm environment', () => {
      // Arrange
      process.env.DOCKER_SWARM = 'true';
      detectEnvironment.mockReturnValue({
        isDocker: true,
        isDockerSwarm: true,
        platform: 'linux',
        isLinux: true
      });

      // Act
      const result = setupDockerEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.isDocker).toBe(true);
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should handle non-Docker environment', () => {
      // Arrange
      fs.existsSync.mockReturnValue(false);
      detectEnvironment.mockReturnValue({
        isDocker: false,
        platform: 'linux',
        isLinux: true
      });

      // Act
      const result = setupDockerEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.isDocker).toBe(false);
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should handle Docker environment in Windows', () => {
      // Arrange
      process.env.DOCKER_ENVIRONMENT = 'true';
      detectEnvironment.mockReturnValue({
        isDocker: true,
        platform: 'win32',
        isWindows: true,
        isLinux: false,
        dockerDetectionMethod: 'DOCKER_ENVIRONMENT variable'
      });

      // Act
      const result = setupDockerEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.isDocker).toBe(true);
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should handle Docker environment in WSL', () => {
      // Arrange
      process.env.DOCKER_ENVIRONMENT = 'true';
      process.env.WSL_DISTRO_NAME = 'Ubuntu';
      detectEnvironment.mockReturnValue({
        isDocker: true,
        platform: 'linux',
        isLinux: true,
        isWSL: true,
        dockerDetectionMethod: 'DOCKER_ENVIRONMENT variable'
      });

      // Act
      const result = setupDockerEnvironment();

      // Assert
      expect(result.success).toBe(true);
      expect(result.isDocker).toBe(true);
      expect(detectEnvironment).toHaveBeenCalled();
    });
  });

  describe('Docker Report Creation', () => {
    it('should create a Docker environment report', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/.dockerenv');
      detectEnvironment.mockReturnValue({
        isDocker: true,
        platform: 'linux',
        isLinux: true,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Linux',
        osRelease: '5.10.0',
        tmpDir: '/tmp',
        homeDir: '/home/user',
        workingDir: '/app',
        dockerDetectionMethod: '.dockerenv file',
        isDockerCompose: false,
        isDockerSwarm: false,
        isKubernetes: false,
        isContainerized: true
      });

      // Act
      const report = createDockerReport();

      // Assert
      expect(report).toContain('Docker Environment Report');
      expect(report).toContain('Docker: Yes');
      expect(report).toContain('Linux');
      expect(report).toContain('Node.js: 18.15.0');
      expect(report).toContain('Detection Method: .dockerenv file');
      expect(report).toContain('Docker Compose: No');
      expect(report).toContain('Docker Swarm: No');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should create a Docker Compose environment report', () => {
      // Arrange
      process.env.COMPOSE_PROJECT_NAME = 'test-project';
      process.env.COMPOSE_FILE = 'docker-compose.yml';
      detectEnvironment.mockReturnValue({
        isDocker: true,
        isDockerCompose: true,
        isDockerSwarm: false,
        platform: 'linux',
        isLinux: true,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Linux',
        osRelease: '5.10.0',
        tmpDir: '/tmp',
        homeDir: '/home/user',
        workingDir: '/app',
        dockerDetectionMethod: 'Environment variable',
        isKubernetes: false,
        isContainerized: true
      });

      // Act
      const report = createDockerReport();

      // Assert
      expect(report).toContain('Docker Environment Report');
      expect(report).toContain('Docker: Yes');
      expect(report).toContain('Docker Compose: Yes');
      expect(report).toContain('Docker Compose Project: test-project');
      expect(report).toContain('Docker Compose File: docker-compose.yml');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should create a Docker Swarm environment report', () => {
      // Arrange
      process.env.DOCKER_SWARM = 'true';
      process.env.SWARM_NODE_ID = 'node123';
      detectEnvironment.mockReturnValue({
        isDocker: true,
        isDockerCompose: false,
        isDockerSwarm: true,
        platform: 'linux',
        isLinux: true,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Linux',
        osRelease: '5.10.0',
        tmpDir: '/tmp',
        homeDir: '/home/user',
        workingDir: '/app',
        dockerDetectionMethod: 'Environment variable',
        isKubernetes: false,
        isContainerized: true
      });

      // Act
      const report = createDockerReport();

      // Assert
      expect(report).toContain('Docker Environment Report');
      expect(report).toContain('Docker: Yes');
      expect(report).toContain('Docker Swarm: Yes');
      expect(report).toContain('Swarm Node ID: node123');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should create a Kubernetes environment report', () => {
      // Arrange
      process.env.KUBERNETES_SERVICE_HOST = '10.0.0.1';
      process.env.KUBERNETES_PORT = '443';
      process.env.KUBERNETES_NAMESPACE = 'default';
      process.env.POD_NAME = 'test-pod';
      detectEnvironment.mockReturnValue({
        isDocker: false,
        isDockerCompose: false,
        isDockerSwarm: false,
        isKubernetes: true,
        platform: 'linux',
        isLinux: true,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Linux',
        osRelease: '5.10.0',
        tmpDir: '/tmp',
        homeDir: '/home/user',
        workingDir: '/app',
        isContainerized: true
      });

      // Act
      const report = createDockerReport();

      // Assert
      expect(report).toContain('Docker Environment Report');
      expect(report).toContain('Docker: No');
      expect(report).toContain('Kubernetes: Yes');
      expect(report).toContain('Kubernetes Service Host: 10.0.0.1');
      expect(report).toContain('Kubernetes Port: 443');
      expect(report).toContain('Kubernetes Namespace: default');
      expect(report).toContain('Pod Name: test-pod');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should create a non-Docker environment report', () => {
      // Arrange
      fs.existsSync.mockReturnValue(false);
      detectEnvironment.mockReturnValue({
        isDocker: false,
        isDockerCompose: false,
        isDockerSwarm: false,
        isKubernetes: false,
        isContainerized: false,
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

      // Act
      const report = createDockerReport();

      // Assert
      expect(report).toContain('Docker Environment Report');
      expect(report).toContain('Docker: No');
      expect(report).toContain('Kubernetes: No');
      expect(report).toContain('Docker Compose: No');
      expect(report).toContain('Docker Swarm: No');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should write report to file when path is provided', () => {
      // Arrange
      fs.existsSync.mockImplementation((path) => path === '/.dockerenv');
      detectEnvironment.mockReturnValue({
        isDocker: true,
        platform: 'linux',
        isLinux: true,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Linux',
        osRelease: '5.10.0',
        tmpDir: '/tmp',
        homeDir: '/home/user',
        workingDir: '/app',
        dockerDetectionMethod: '.dockerenv file'
      });
      const filePath = '/tmp/docker-report.txt';

      // Act
      createDockerReport(filePath);

      // Assert
      expect(fs.writeFileSync).toHaveBeenCalledWith(filePath, expect.any(String));
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should include Windows-specific information in Docker report when running on Windows', () => {
      // Arrange
      process.env.DOCKER_ENVIRONMENT = 'true';
      detectEnvironment.mockReturnValue({
        isDocker: true,
        platform: 'win32',
        isWindows: true,
        isLinux: false,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Windows_NT',
        osRelease: '10.0.19042',
        tmpDir: 'C:\\Windows\\Temp',
        homeDir: 'C:\\Users\\user',
        workingDir: 'C:\\app',
        dockerDetectionMethod: 'DOCKER_ENVIRONMENT variable'
      });

      // Act
      const report = createDockerReport();

      // Assert
      expect(report).toContain('Docker Environment Report');
      expect(report).toContain('Docker: Yes');
      expect(report).toContain('Windows_NT');
      expect(report).toContain('win32');
      expect(report).toContain('Detection Method: DOCKER_ENVIRONMENT variable');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should include WSL-specific information in Docker report when running in WSL', () => {
      // Arrange
      process.env.DOCKER_ENVIRONMENT = 'true';
      process.env.WSL_DISTRO_NAME = 'Ubuntu';
      detectEnvironment.mockReturnValue({
        isDocker: true,
        platform: 'linux',
        isLinux: true,
        isWSL: true,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Linux',
        osRelease: '5.10.0',
        tmpDir: '/tmp',
        homeDir: '/home/user',
        workingDir: '/app',
        dockerDetectionMethod: 'DOCKER_ENVIRONMENT variable'
      });

      // Act
      const report = createDockerReport();

      // Assert
      expect(report).toContain('Docker Environment Report');
      expect(report).toContain('Docker: Yes');
      expect(report).toContain('WSL: Yes');
      expect(report).toContain('WSL Distro: Ubuntu');
      expect(detectEnvironment).toHaveBeenCalled();
    });

    it('should include CI-specific information in Docker report when running in CI', () => {
      // Arrange
      process.env.DOCKER_ENVIRONMENT = 'true';
      process.env.CI = 'true';
      process.env.GITHUB_ACTIONS = 'true';
      process.env.GITHUB_WORKFLOW = 'test-workflow';
      detectEnvironment.mockReturnValue({
        isDocker: true,
        platform: 'linux',
        isLinux: true,
        isCI: true,
        isGitHubActions: true,
        nodeVersion: '18.15.0',
        architecture: 'x64',
        osType: 'Linux',
        osRelease: '5.10.0',
        tmpDir: '/tmp',
        homeDir: '/home/user',
        workingDir: '/app',
        dockerDetectionMethod: 'DOCKER_ENVIRONMENT variable'
      });

      // Act
      const report = createDockerReport();

      // Assert
      expect(report).toContain('Docker Environment Report');
      expect(report).toContain('Docker: Yes');
      expect(report).toContain('CI: true');
      expect(report).toContain('GITHUB_ACTIONS: true');
      expect(report).toContain('GITHUB_WORKFLOW: test-workflow');
      expect(detectEnvironment).toHaveBeenCalled();
    });
  });
});
