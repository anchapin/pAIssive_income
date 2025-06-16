/**
 * Mock Server Helper
 * 
 * This module provides helper functions for the mock API server to ensure
 * it works correctly in CI environments, especially with GitHub Actions.
 * 
 * It includes functions to:
 * - Create a simple mock implementation of path-to-regexp
 * - Patch the require function to handle path-to-regexp imports
 * - Create directories with error handling
 * - Write files with error handling
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Import the unified environment detection module if available
let unifiedEnv;
try {
  unifiedEnv = require('./unified-environment');
  console.log('Successfully imported unified environment detection module');
} catch (importError) {
  console.warn(`Failed to import unified environment detection module: ${importError.message}`);
  
  // Try alternative paths for the unified environment module
  try {
    unifiedEnv = require('./environment-detection').detectEnvironment();
    console.log('Successfully imported environment-detection module as fallback');
  } catch (fallbackError) {
    console.warn(`Failed to import environment-detection module: ${fallbackError.message}`);
    // Continue with existing detection logic
    unifiedEnv = null;
  }
}

// Enhanced environment detection
const isCI = unifiedEnv ? 
  (typeof unifiedEnv.isCI === 'function' ? unifiedEnv.isCI() : unifiedEnv.isCI) : 
  process.env.CI === 'true' || process.env.CI === true ||
  process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW;

const isGitHubActions = unifiedEnv ?
  (typeof unifiedEnv.isGitHubActions === 'function' ? unifiedEnv.isGitHubActions() : unifiedEnv.isGitHubActions) :
  process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW || !!process.env.GITHUB_RUN_ID;

// Function to safely create directory with multiple fallbacks
function safelyCreateDirectory(dirPath) {
  try {
    if (unifiedEnv && typeof unifiedEnv.createDirectoryWithErrorHandling === 'function') {
      return unifiedEnv.createDirectoryWithErrorHandling(dirPath);
    }
    
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
      console.log(`Created directory at ${dirPath}`);
      return true;
    }
    return true;
  } catch (error) {
    console.error(`Failed to create directory at ${dirPath}: ${error.message}`);
    
    // Try with absolute path as fallback
    try {
      const absolutePath = path.resolve(dirPath);
      if (!fs.existsSync(absolutePath)) {
        fs.mkdirSync(absolutePath, { recursive: true });
        console.log(`Created directory at absolute path: ${absolutePath}`);
        return true;
      }
      return true;
    } catch (fallbackError) {
      console.error(`Failed to create directory with absolute path: ${fallbackError.message}`);
      return false;
    }
  }
}

// Function to safely write file with fallbacks
function safelyWriteFile(filePath, content, options = {}) {
  try {
    const { append = false } = options;
    
    if (append) {
      fs.appendFileSync(filePath, content);
    } else {
      fs.writeFileSync(filePath, content);
    }
    
    console.log(`${append ? 'Appended to' : 'Created'} file at ${filePath}`);
    return true;
  } catch (error) {
    console.error(`Error writing file at ${filePath}: ${error.message}`);
    
    // Try with absolute path as fallback
    try {
      const absolutePath = path.resolve(filePath);
      
      if (options.append) {
        fs.appendFileSync(absolutePath, content);
      } else {
        fs.writeFileSync(absolutePath, content);
      }
      
      console.log(`${options.append ? 'Appended to' : 'Created'} file at absolute path: ${absolutePath}`);
      return true;
    } catch (fallbackError) {
      console.error(`Failed to write file with absolute path: ${fallbackError.message}`);
      return false;
    }
  }
}

// Create a simple mock implementation of path-to-regexp
function createMockPathToRegexp() {
  function pathToRegexp(path, keys, options) {
    console.log(`Mock path-to-regexp called with path: ${path}`);
    
    // If keys is provided, populate it with parameter names
    if (Array.isArray(keys) && typeof path === 'string') {
      const paramNames = path.match(/:[a-zA-Z0-9_]+/g) || [];
      paramNames.forEach((param) => {
        keys.push({
          name: param.substring(1),
          prefix: '/',
          suffix: '',
          modifier: '',
          pattern: '[^/]+'
        });
      });
    }
    
    return /.*/;
  }
  
  // Add the main function as a property of itself
  pathToRegexp.pathToRegexp = pathToRegexp;
  
  // Add all necessary methods
  pathToRegexp.parse = function() { return []; };
  pathToRegexp.compile = function() { return function() { return ''; }; };
  pathToRegexp.match = function() { return function() { return { path: '', params: {}, index: 0, isExact: true }; }; };
  pathToRegexp.tokensToRegexp = function() { return /.*/; };
  pathToRegexp.tokensToFunction = function() { return function() { return ''; }; };
  pathToRegexp.regexp = /.*/;
  
  return pathToRegexp;
}

// Patch the require function to handle path-to-regexp imports
function patchRequireFunction() {
  console.log('Patching require function for path-to-regexp');
  
  try {
    const Module = require('module');
    const originalRequire = Module.prototype.require;
    
    Module.prototype.require = function(id) {
      if (id === 'path-to-regexp') {
        console.log('Intercepted require for path-to-regexp');
        return createMockPathToRegexp();
      }
      return originalRequire.call(this, id);
    };
    
    console.log('Successfully patched require function');
    return true;
  } catch (error) {
    console.error(`Failed to patch require function: ${error.message}`);
    return false;
  }
}

// Export all functions
module.exports = {
  isCI,
  isGitHubActions,
  safelyCreateDirectory,
  safelyWriteFile,
  createMockPathToRegexp,
  patchRequireFunction
};
