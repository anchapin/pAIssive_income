/**
 * Enhanced Docker Environment Helper
 *
 * This module provides comprehensive functions to handle Docker environment-specific behavior.
 * It supports Docker, Docker Compose, Kubernetes, and Docker Swarm environments.
 *
 * It's designed to be used across the application to ensure consistent
 * Docker environment handling with proper fallbacks and error handling.
 *
 * @version 2.0.0
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
 * Create necessary directories for Docker environment with enhanced error handling
 * @returns {Object} Result object with success status and error message
 */
function createDockerDirectories() {
  try {
    const directories = [
      'logs',
      'playwright-report',
      'test-results',
      'coverage',
      'docker-reports',
      path.join('playwright-report', 'docker'),
      path.join('test-results', 'docker'),
      path.join('logs', 'docker')
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
 * Create marker files for Docker environment with enhanced container detection
 * @returns {Object} Result object with success status and error message
 */
function createDockerMarkerFiles() {
  try {
    const env = detectEnvironment();
    const timestamp = new Date().toISOString();

    // Create marker files in multiple locations to ensure at least one succeeds
    const markerLocations = [
      path.join(process.cwd(), 'logs', 'docker-environment.txt'),
      path.join(process.cwd(), 'playwright-report', 'docker-environment.txt'),
      path.join(process.cwd(), 'test-results', 'docker-environment.txt'),
      path.join(process.cwd(), 'docker-reports', 'environment.txt'),
      path.join(process.cwd(), 'logs', 'docker', 'environment.txt'),
      path.join(process.cwd(), 'playwright-report', 'docker', 'environment.txt'),
      path.join(process.cwd(), 'test-results', 'docker', 'environment.txt')
    ];

    // Create enhanced marker content with more container information
    const markerContent = `Docker Environment
=================
Timestamp: ${timestamp}

Container Detection:
- Docker: ${env.isDocker ? 'Yes' : 'No'}
- Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}
- Docker Compose: ${env.isDockerCompose ? 'Yes' : 'No'}
- Docker Swarm: ${env.isDockerSwarm ? 'Yes' : 'No'}
- Containerized: ${env.isContainerized ? 'Yes' : 'No'}

System Information:
- Node.js: ${env.nodeVersion}
- Platform: ${env.platform}
- Architecture: ${env.architecture}
- OS: ${env.osType} ${env.osRelease}
- Working Directory: ${env.workingDir}
- Hostname: ${env.hostname || 'unknown'}

Environment Variables:
- NODE_ENV: ${process.env.NODE_ENV || 'not set'}
- DOCKER_ENVIRONMENT: ${process.env.DOCKER_ENVIRONMENT || 'not set'}
- KUBERNETES_SERVICE_HOST: ${process.env.KUBERNETES_SERVICE_HOST || 'not set'}
- COMPOSE_PROJECT_NAME: ${process.env.COMPOSE_PROJECT_NAME || 'not set'}
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
    const jsonMarkerPath = path.join(process.cwd(), 'docker-reports', 'environment.json');
    const jsonContent = JSON.stringify({
      timestamp,
      containerDetection: {
        isDocker: env.isDocker,
        isKubernetes: env.isKubernetes,
        isDockerCompose: env.isDockerCompose,
        isDockerSwarm: env.isDockerSwarm,
        isContainerized: env.isContainerized
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
        DOCKER_ENVIRONMENT: process.env.DOCKER_ENVIRONMENT || 'not set',
        KUBERNETES_SERVICE_HOST: process.env.KUBERNETES_SERVICE_HOST || 'not set',
        COMPOSE_PROJECT_NAME: process.env.COMPOSE_PROJECT_NAME || 'not set'
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
 * Set up Docker environment with enhanced container detection
 * @param {Object} [options] - Setup options
 * @param {boolean} [options.forceDocker=false] - Force Docker environment setup even if not detected
 * @param {boolean} [options.setupKubernetes=true] - Set up Kubernetes-specific environment if detected
 * @param {boolean} [options.setupDockerCompose=true] - Set up Docker Compose-specific environment if detected
 * @param {boolean} [options.setupDockerSwarm=true] - Set up Docker Swarm-specific environment if detected
 * @returns {Object} Result object with success status, container environment flags, and error message
 */
function setupDockerEnvironment(options = {}) {
  try {
    const {
      forceDocker = false,
      setupKubernetes = true,
      setupDockerCompose = true,
      setupDockerSwarm = true
    } = options;

    const env = detectEnvironment();

    // Check if any container environment is detected
    const isContainerized = env.isContainerized || forceDocker;

    if (!isContainerized) {
      console.log('No container environment detected');
      return {
        success: true,
        isDocker: false,
        isKubernetes: false,
        isDockerCompose: false,
        isDockerSwarm: false,
        isContainerized: false
      };
    }

    console.log('Setting up container environment');
    console.log(`- Docker: ${env.isDocker ? 'Yes' : 'No'}`);
    console.log(`- Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}`);
    console.log(`- Docker Compose: ${env.isDockerCompose ? 'Yes' : 'No'}`);
    console.log(`- Docker Swarm: ${env.isDockerSwarm ? 'Yes' : 'No'}`);

    // Create directories
    const dirResult = createDockerDirectories();
    if (!dirResult.success) {
      return {
        success: false,
        isDocker: env.isDocker,
        isKubernetes: env.isKubernetes,
        isDockerCompose: env.isDockerCompose,
        isDockerSwarm: env.isDockerSwarm,
        isContainerized: true,
        error: `Failed to create directories: ${dirResult.error}`
      };
    }

    // Create marker files
    const markerResult = createDockerMarkerFiles();
    if (!markerResult.success) {
      return {
        success: false,
        isDocker: env.isDocker,
        isKubernetes: env.isKubernetes,
        isDockerCompose: env.isDockerCompose,
        isDockerSwarm: env.isDockerSwarm,
        isContainerized: true,
        error: `Failed to create marker files: ${markerResult.error}`
      };
    }

    // Set environment variables
    if (env.isDocker || forceDocker) {
      process.env.DOCKER_ENVIRONMENT = 'true';
    }

    // Set up Kubernetes-specific environment if detected
    if (setupKubernetes && env.isKubernetes) {
      process.env.KUBERNETES_ENVIRONMENT = 'true';

      // Create Kubernetes-specific directories
      safelyCreateDirectory(path.join(process.cwd(), 'kubernetes-reports'));

      // Create Kubernetes marker file
      const k8sMarkerPath = path.join(process.cwd(), 'kubernetes-reports', 'environment.json');
      const k8sContent = JSON.stringify({
        timestamp: new Date().toISOString(),
        kubernetes: {
          serviceHost: process.env.KUBERNETES_SERVICE_HOST || 'unknown',
          port: process.env.KUBERNETES_PORT || 'unknown',
          namespace: process.env.KUBERNETES_NAMESPACE || 'unknown',
          podName: process.env.POD_NAME || 'unknown',
          podIp: process.env.POD_IP || 'unknown'
        }
      }, null, 2);

      safelyWriteFile(k8sMarkerPath, k8sContent);
    }

    // Set up Docker Compose-specific environment if detected
    if (setupDockerCompose && env.isDockerCompose) {
      process.env.DOCKER_COMPOSE_ENVIRONMENT = 'true';

      // Create Docker Compose-specific directories
      safelyCreateDirectory(path.join(process.cwd(), 'docker-compose-reports'));

      // Create Docker Compose marker file
      const composeMarkerPath = path.join(process.cwd(), 'docker-compose-reports', 'environment.json');
      const composeContent = JSON.stringify({
        timestamp: new Date().toISOString(),
        dockerCompose: {
          projectName: process.env.COMPOSE_PROJECT_NAME || 'unknown',
          file: process.env.COMPOSE_FILE || 'unknown',
          separator: process.env.COMPOSE_PATH_SEPARATOR || 'unknown'
        }
      }, null, 2);

      safelyWriteFile(composeMarkerPath, composeContent);
    }

    // Set up Docker Swarm-specific environment if detected
    if (setupDockerSwarm && env.isDockerSwarm) {
      process.env.DOCKER_SWARM_ENVIRONMENT = 'true';

      // Create Docker Swarm-specific directories
      safelyCreateDirectory(path.join(process.cwd(), 'docker-swarm-reports'));

      // Create Docker Swarm marker file
      const swarmMarkerPath = path.join(process.cwd(), 'docker-swarm-reports', 'environment.json');
      const swarmContent = JSON.stringify({
        timestamp: new Date().toISOString(),
        dockerSwarm: {
          nodeId: process.env.SWARM_NODE_ID || 'unknown',
          manager: process.env.SWARM_MANAGER || 'unknown'
        }
      }, null, 2);

      safelyWriteFile(swarmMarkerPath, swarmContent);
    }

    console.log('Container environment setup complete');
    return {
      success: true,
      isDocker: env.isDocker || forceDocker,
      isKubernetes: env.isKubernetes && setupKubernetes,
      isDockerCompose: env.isDockerCompose && setupDockerCompose,
      isDockerSwarm: env.isDockerSwarm && setupDockerSwarm,
      isContainerized: true
    };
  } catch (error) {
    console.error(`Failed to set up container environment: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Create a comprehensive Docker environment report
 * @param {string} [filePath] - Optional file path to write the report to
 * @param {Object} [options] - Report options
 * @param {boolean} [options.includeEnvVars=false] - Whether to include all environment variables
 * @param {boolean} [options.includeSystemInfo=true] - Whether to include detailed system info
 * @param {boolean} [options.formatJson=false] - Whether to format as JSON instead of text
 * @returns {string} Docker environment report
 */
function createDockerReport(filePath, options = {}) {
  const env = detectEnvironment();
  const {
    includeEnvVars = false,
    includeSystemInfo = true,
    formatJson = false
  } = options;

  // Determine Docker detection method
  let detectionMethod = 'N/A';
  if (env.isDocker) {
    if (safeFileExists('/.dockerenv')) {
      detectionMethod = '.dockerenv file';
    } else if (safeFileExists('/run/.containerenv')) {
      detectionMethod = '.containerenv file';
    } else if (safeFileExists('/proc/1/cgroup') && safeReadFile('/proc/1/cgroup')?.includes('docker')) {
      detectionMethod = 'cgroup file';
    } else if (process.env.DOCKER_ENVIRONMENT === 'true' || process.env.DOCKER === 'true') {
      detectionMethod = 'Environment variable';
    }
  }

  // If JSON format is requested, return JSON
  if (formatJson) {
    const reportObj = {
      timestamp: new Date().toISOString(),
      containerEnvironment: {
        isDocker: env.isDocker,
        isKubernetes: env.isKubernetes,
        isDockerCompose: env.isDockerCompose,
        isDockerSwarm: env.isDockerSwarm,
        isContainerized: env.isContainerized,
        detectionMethod
      },
      systemInfo: {
        nodeVersion: env.nodeVersion,
        platform: env.platform,
        architecture: env.architecture,
        osType: env.osType,
        osRelease: env.osRelease,
        workingDirectory: env.workingDir,
        tempDirectory: env.tmpDir,
        homeDirectory: env.homeDir
      }
    };

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

    // Include environment variables
    if (includeEnvVars) {
      reportObj.environmentVariables = process.env;
    } else {
      // Include only relevant environment variables
      reportObj.environmentVariables = {
        NODE_ENV: process.env.NODE_ENV || 'not set',
        DOCKER_ENVIRONMENT: process.env.DOCKER_ENVIRONMENT || 'not set',
        KUBERNETES_ENVIRONMENT: process.env.KUBERNETES_ENVIRONMENT || 'not set',
        DOCKER_COMPOSE_ENVIRONMENT: process.env.DOCKER_COMPOSE_ENVIRONMENT || 'not set',
        DOCKER_SWARM_ENVIRONMENT: process.env.DOCKER_SWARM_ENVIRONMENT || 'not set',
        KUBERNETES_SERVICE_HOST: process.env.KUBERNETES_SERVICE_HOST || 'not set',
        KUBERNETES_PORT: process.env.KUBERNETES_PORT || 'not set',
        COMPOSE_PROJECT_NAME: process.env.COMPOSE_PROJECT_NAME || 'not set',
        COMPOSE_FILE: process.env.COMPOSE_FILE || 'not set',
        SWARM_NODE_ID: process.env.SWARM_NODE_ID || 'not set'
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
  const report = `Container Environment Report
===========================
Generated at: ${new Date().toISOString()}

Container Environment:
- Docker: ${env.isDocker ? 'Yes' : 'No'}
- Kubernetes: ${env.isKubernetes ? 'Yes' : 'No'}
- Docker Compose: ${env.isDockerCompose ? 'Yes' : 'No'}
- Docker Swarm: ${env.isDockerSwarm ? 'Yes' : 'No'}
- Containerized: ${env.isContainerized ? 'Yes' : 'No'}
- Detection Method: ${detectionMethod}

System Information:
- Node.js: ${env.nodeVersion}
- Platform: ${env.platform}
- Architecture: ${env.architecture}
- OS: ${env.osType} ${env.osRelease}
- Working Directory: ${env.workingDir}
- Temp Directory: ${env.tmpDir}
- Home Directory: ${env.homeDir}
${includeSystemInfo ? `
Detailed System Information:
- Hostname: ${env.hostname}
- Username: ${env.username}
- Memory Total: ${formatBytes(env.memory.total)}
- Memory Free: ${formatBytes(env.memory.free)}
- CPUs: ${env.cpus.length}
` : ''}

Environment Variables:
- NODE_ENV: ${process.env.NODE_ENV || 'not set'}
- DOCKER_ENVIRONMENT: ${process.env.DOCKER_ENVIRONMENT || 'not set'}
- KUBERNETES_ENVIRONMENT: ${process.env.KUBERNETES_ENVIRONMENT || 'not set'}
- DOCKER_COMPOSE_ENVIRONMENT: ${process.env.DOCKER_COMPOSE_ENVIRONMENT || 'not set'}
- DOCKER_SWARM_ENVIRONMENT: ${process.env.DOCKER_SWARM_ENVIRONMENT || 'not set'}
- KUBERNETES_SERVICE_HOST: ${process.env.KUBERNETES_SERVICE_HOST || 'not set'}
- KUBERNETES_PORT: ${process.env.KUBERNETES_PORT || 'not set'}
- COMPOSE_PROJECT_NAME: ${process.env.COMPOSE_PROJECT_NAME || 'not set'}
- COMPOSE_FILE: ${process.env.COMPOSE_FILE || 'not set'}
- SWARM_NODE_ID: ${process.env.SWARM_NODE_ID || 'not set'}
${includeEnvVars ? formatEnvironmentVariables() : ''}
`;

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
  createDockerDirectories,
  createDockerMarkerFiles,
  setupDockerEnvironment,
  createDockerReport,
  formatBytes,
  formatEnvironmentVariables
};
