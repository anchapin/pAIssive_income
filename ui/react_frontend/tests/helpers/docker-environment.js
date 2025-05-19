/**
 * Docker Environment Helper
 * 
 * This module provides functions to handle Docker environment-specific behavior.
 * It's designed to be used across the application to ensure consistent
 * Docker environment handling.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { detectEnvironment } = require('./environment-detection');

/**
 * Create necessary directories for Docker environment
 * @returns {Object} Result object with success status and error message
 */
function createDockerDirectories() {
  try {
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
    
    return { success: true };
  } catch (error) {
    console.error(`Failed to create directories: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Create marker files for Docker environment
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
      path.join(process.cwd(), 'test-results', 'docker-environment.txt')
    ];
    
    const markerContent = `Docker Environment
=================
Timestamp: ${timestamp}
Docker: ${env.isDocker ? 'Yes' : 'No'}
Node.js: ${env.nodeVersion}
Platform: ${env.platform}
Architecture: ${env.architecture}
OS: ${env.osType} ${env.osRelease}
Working Directory: ${env.workingDir}
`;
    
    for (const location of markerLocations) {
      try {
        const dir = path.dirname(location);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }
        
        fs.writeFileSync(location, markerContent);
        console.log(`Created marker file at ${location}`);
      } catch (error) {
        console.warn(`Failed to create marker file at ${location}: ${error.message}`);
        // Continue to the next location
      }
    }
    
    return { success: true };
  } catch (error) {
    console.error(`Failed to create marker files: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Set up Docker environment
 * @returns {Object} Result object with success status, isDocker flag, and error message
 */
function setupDockerEnvironment() {
  try {
    const env = detectEnvironment();
    
    if (!env.isDocker) {
      console.log('No Docker environment detected');
      return { success: true, isDocker: false };
    }
    
    console.log('Setting up Docker environment');
    
    // Create directories
    const dirResult = createDockerDirectories();
    if (!dirResult.success) {
      return { success: false, isDocker: true, error: `Failed to create directories: ${dirResult.error}` };
    }
    
    // Create marker files
    const markerResult = createDockerMarkerFiles();
    if (!markerResult.success) {
      return { success: false, isDocker: true, error: `Failed to create marker files: ${markerResult.error}` };
    }
    
    // Set environment variables
    process.env.DOCKER_ENVIRONMENT = 'true';
    
    console.log('Docker environment setup complete');
    return { success: true, isDocker: true };
  } catch (error) {
    console.error(`Failed to set up Docker environment: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Create a Docker environment report
 * @param {string} [filePath] - Optional file path to write the report to
 * @returns {string} Docker environment report
 */
function createDockerReport(filePath) {
  const env = detectEnvironment();
  
  const report = `Docker Environment Report
========================
Generated at: ${new Date().toISOString()}

Docker Environment:
- Docker: ${env.isDocker ? 'Yes' : 'No'}
- Detection Method: ${env.isDocker ? (fs.existsSync('/.dockerenv') ? '.dockerenv file' : 'Environment variable') : 'N/A'}

System Information:
- Node.js: ${env.nodeVersion}
- Platform: ${env.platform}
- Architecture: ${env.architecture}
- OS: ${env.osType} ${env.osRelease}
- Working Directory: ${env.workingDir}
- Temp Directory: ${env.tmpDir}

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

module.exports = {
  createDockerDirectories,
  createDockerMarkerFiles,
  setupDockerEnvironment,
  createDockerReport
};
