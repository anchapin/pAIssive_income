/**
 * Setup script for CI environment
 * This script sets up the CI environment for running tests
 * by creating necessary directories and mock implementations.
 */

const fs = require('fs');
const path = require('path');
const { installMockPathToRegexp } = require('./path-to-regexp-mock');

/**
 * Create necessary directories for tests
 * @returns {boolean} Whether the directories were created successfully
 */
function createDirectories() {
  try {
    const directories = [
      'logs',
      'playwright-report',
      'test-results'
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
    
    return true;
  } catch (error) {
    console.error(`Failed to create directories: ${error.message}`);
    return false;
  }
}

/**
 * Create marker files to indicate CI environment
 * @returns {boolean} Whether the marker files were created successfully
 */
function createMarkerFiles() {
  try {
    const logsDir = path.join(process.cwd(), 'logs');
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir, { recursive: true });
    }
    
    // Create a marker file to indicate CI environment
    fs.writeFileSync(
      path.join(logsDir, 'ci-environment-setup.txt'),
      `CI environment setup at ${new Date().toISOString()}\n` +
      `Node.js version: ${process.version}\n` +
      `Platform: ${process.platform}\n` +
      `Working directory: ${process.cwd()}\n` +
      `This file indicates that the CI environment was set up for running tests.`
    );
    
    // Create a marker file in the playwright-report directory
    const reportDir = path.join(process.cwd(), 'playwright-report');
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
    
    fs.writeFileSync(
      path.join(reportDir, 'ci-environment-setup.txt'),
      `CI environment setup at ${new Date().toISOString()}\n` +
      `Node.js version: ${process.version}\n` +
      `Platform: ${process.platform}\n` +
      `Working directory: ${process.cwd()}\n` +
      `This file indicates that the CI environment was set up for running tests.`
    );
    
    return true;
  } catch (error) {
    console.error(`Failed to create marker files: ${error.message}`);
    return false;
  }
}

/**
 * Setup the CI environment
 * @returns {boolean} Whether the setup was successful
 */
function setupCIEnvironment() {
  console.log('Setting up CI environment...');
  
  // Create necessary directories
  const directoriesCreated = createDirectories();
  if (!directoriesCreated) {
    console.error('Failed to create directories');
  }
  
  // Create marker files
  const markerFilesCreated = createMarkerFiles();
  if (!markerFilesCreated) {
    console.error('Failed to create marker files');
  }
  
  // Install mock path-to-regexp
  const mockInstalled = installMockPathToRegexp();
  if (!mockInstalled) {
    console.error('Failed to install mock path-to-regexp');
  }
  
  console.log('CI environment setup complete');
  return directoriesCreated && markerFilesCreated && mockInstalled;
}

// Export the functions
module.exports = {
  createDirectories,
  createMarkerFiles,
  installMockPathToRegexp: installMockPathToRegexp,
  setupCIEnvironment
};

// If this file is run directly, setup the CI environment
if (require.main === module) {
  setupCIEnvironment();
}
