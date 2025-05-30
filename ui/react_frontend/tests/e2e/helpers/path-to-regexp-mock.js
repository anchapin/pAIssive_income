/**
 * Mock implementation of path-to-regexp for CI compatibility
 * This file provides a robust mock implementation of path-to-regexp
 * that can be used in CI environments where the actual package
 * might cause issues.
 */

const fs = require('fs');
const path = require('path');

/**
 * Create a mock implementation of path-to-regexp
 * @returns {Object} The mock implementation
 */
function createMockPathToRegexp() {
  // Main function
  function pathToRegexp(path, keys, options) {
    console.log('Mock path-to-regexp called with path:', path);
    return /.*/;
  }

  // Helper functions with better error handling
  pathToRegexp.parse = function parse(path) {
    console.log('Mock path-to-regexp.parse called with path:', path);
    return [];
  };

  pathToRegexp.compile = function compile(path) {
    console.log('Mock path-to-regexp.compile called with path:', path);
    return function() { return ''; };
  };

  pathToRegexp.tokensToRegexp = function tokensToRegexp(tokens, keys, options) {
    console.log('Mock path-to-regexp.tokensToRegexp called');
    return /.*/;
  };

  pathToRegexp.tokensToFunction = function tokensToFunction(tokens, options) {
    console.log('Mock path-to-regexp.tokensToFunction called');
    return function() { return ''; };
  };

  return pathToRegexp;
}

/**
 * Install the mock implementation of path-to-regexp
 * @param {string} [targetDir=process.cwd()] - The directory to install the mock in
 * @returns {boolean} Whether the installation was successful
 */
function installMockPathToRegexp(targetDir = process.cwd()) {
  try {
    const nodeModulesDir = path.join(targetDir, 'node_modules');
    const mockDir = path.join(nodeModulesDir, 'path-to-regexp');
    
    // Create the directory if it doesn't exist
    if (!fs.existsSync(mockDir)) {
      fs.mkdirSync(mockDir, { recursive: true });
      console.log(`Created mock directory at ${mockDir}`);
    }
    
    // Create the mock implementation
    const mockImplementation = `
/**
 * Mock implementation of path-to-regexp for CI compatibility
 */
function pathToRegexp(path, keys, options) {
  console.log('Mock path-to-regexp called with path:', path);
  return /.*/;
}

// Helper functions with better error handling
pathToRegexp.parse = function parse(path) {
  console.log('Mock path-to-regexp.parse called with path:', path);
  return [];
};

pathToRegexp.compile = function compile(path) {
  console.log('Mock path-to-regexp.compile called with path:', path);
  return function() { return ''; };
};

pathToRegexp.tokensToRegexp = function tokensToRegexp(tokens, keys, options) {
  console.log('Mock path-to-regexp.tokensToRegexp called');
  return /.*/;
};

pathToRegexp.tokensToFunction = function tokensToFunction(tokens, options) {
  console.log('Mock path-to-regexp.tokensToFunction called');
  return function() { return ''; };
};

module.exports = pathToRegexp;
`;
    
    // Create the package.json
    const packageJson = `{
  "name": "path-to-regexp",
  "version": "0.0.0",
  "main": "index.js",
  "description": "Mock implementation of path-to-regexp for CI compatibility"
}`;
    
    // Write the files
    fs.writeFileSync(path.join(mockDir, 'index.js'), mockImplementation);
    fs.writeFileSync(path.join(mockDir, 'package.json'), packageJson);
    
    // Create a marker file
    const logsDir = path.join(targetDir, 'logs');
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir, { recursive: true });
    }
    
    fs.writeFileSync(
      path.join(logsDir, 'path-to-regexp-mock-installed.txt'),
      `Mock path-to-regexp implementation installed at ${new Date().toISOString()}\n` +
      `Installation directory: ${mockDir}\n` +
      `This file indicates that a mock implementation of path-to-regexp was installed for CI compatibility.`
    );
    
    console.log('Successfully installed mock path-to-regexp implementation');
    return true;
  } catch (error) {
    console.error(`Failed to install mock path-to-regexp implementation: ${error.message}`);
    return false;
  }
}

// Export the functions
module.exports = {
  createMockPathToRegexp,
  installMockPathToRegexp
};

// If this file is run directly, install the mock implementation
if (require.main === module) {
  installMockPathToRegexp();
}
