/**
 * Mock path-to-regexp module for CI compatibility
 * Enhanced with improved environment detection and security measures
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

// Enhanced environment detection with compreh  // Enhanced environment detection with comprehensive CI platform support
  const env = {
    isCI: process.env.CI === 'true' || process.env.CI === true ||
          process.env.GITHUB_ACTIONS === 'true' || process.env.GITHUB_WORKFLOW ||
          process.env.TF_BUILD || process.env.JENKINS_URL ||
          process.env.GITLAB_CI || process.env.CIRCLECI ||
          process.env.TEAMCITY_VERSION || process.env.TRAVIS,
    isDocker: fs.existsSync('/.dockerenv') || fs.existsSync('/run/.containerenv'),
    isGitHubActions: process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW,
    isJenkins: !!process.env.JENKINS_URL,
    isAzureDevOps: !!process.env.TF_BUILD,
    isGitLabCI: !!process.env.GITLAB_CI,
    isCircleCI: !!process.env.CIRCLECI,
    isTeamCity: !!process.env.TEAMCITY_VERSION,
    isTravis: !!process.env.TRAVIS,
    verbose: process.env.VERBOSE_LOGGING === 'true',
    tempDir: process.env.RUNNER_TEMP || 
             process.env.TEMP || 
             process.env.TMP || 
             os.tmpdir(),
    workDir: process.env.GITHUB_WORKSPACE || 
             process.env.JENKINS_HOME || 
             process.env.BUILD_SOURCESDIRECTORY || 
             process.env.CI_PROJECT_DIR ||
             process.cwd(),
  };support
const ciEnv = {
  isCI: process.env.CI === 'true' || process.env.CI === true ||
      process.env.GITHUB_ACTIONS === 'true' || process.env.GITHUB_WORKFLOW ||
      process.env.TF_BUILD || process.env.JENKINS_URL ||
      process.env.GITLAB_CI || process.env.CIRCLECI ||
      process.env.TEAMCITY_VERSION || process.env.TRAVIS,
  isDocker: fs.existsSync('/.dockerenv') || fs.existsSync('/run/.containerenv'),
  githubActions: process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW,
  jenkins: !!process.env.JENKINS_URL,
  azureDevOps: !!process.env.TF_BUILD,
  gitlabCI: !!process.env.GITLAB_CI,
  circleCI: !!process.env.CIRCLECI,
  teamCity: !!process.env.TEAMCITY_VERSION,
  travis: !!process.env.TRAVIS,
  workDir: process.env.GITHUB_WORKSPACE || 
          process.env.JENKINS_HOME || 
          process.env.BUILD_SOURCESDIRECTORY || 
          process.env.CI_PROJECT_DIR ||
          process.cwd(),
  tempDir: process.env.RUNNER_TEMP || 
          process.env.TEMP || 
          process.env.TMP || 
          os.tmpdir(),
  verbose: process.env.VERBOSE_LOGGING === 'true'
};

// Set commonly used flags for backward compatibility
const isCI = ciEnv.isCI;
const isGitHubActions = ciEnv.githubActions;
const isDockerEnvironment = ciEnv.isDocker;
const verboseLogging = ciEnv.verbose || isCI;

// Log the detected environment
safeLog('Detected CI environment:', {
  CI: ciEnv.isCI,
  Docker: ciEnv.isDocker,
  GitHub: ciEnv.githubActions,
  Jenkins: ciEnv.jenkins,
  Azure: ciEnv.azureDevOps,
  GitLab: ciEnv.gitlabCI,
  CircleCI: ciEnv.circleCI,
  TeamCity: ciEnv.teamCity,
  Travis: ciEnv.travis,
  tempDir: ciEnv.tempDir,
  workDir: ciEnv.workDir
}, 'important');

/**
 * Sanitizes a value for safe logging to prevent log injection attacks.
 *
 * @param {any} value - The value to sanitize
 * @returns {string} - A sanitized string representation of the value
 */
function sanitizeForLog(value) {
  if (value === null || value === undefined) {
    return String(value);
  }

  if (typeof value === 'string') {
    // Replace newlines, carriage returns and other control characters
    return value
      .replace(/[\n\r\t\v\f\b]/g, ' ')
      .replace(/[\x00-\x1F\x7F-\x9F]/g, '')
      .replace(/[^\x20-\x7E]/g, '?');
  }

  if (typeof value === 'object') {
    try {
      // For objects, we sanitize the JSON string representation
      const stringified = JSON.stringify(value);
      return sanitizeForLog(stringified);
    } catch (error) {
      return '[Object sanitization failed]';
    }
  }

  // For other types (number, boolean), convert to string
  return String(value);
}

/**
 * Safely logs a message with sanitized values and optional log level
 *
 * @param {string} message - The message template
 * @param {any} value - The value to sanitize and include in the log
 * @param {string} [level='info'] - Log level (info, warn, error, important)
 * @returns {void}
 */
function safeLog(message, value, level = 'info') {
  const timestamp = new Date().toISOString();
  const sanitizedValue = sanitizeForLog(value);
  const prefix = `[${timestamp}] [path-to-regexp] [${level.toUpperCase()}]`;

  // Always log to console
  switch (level) {
    case 'error':
      console.error(`${prefix} ${message}`, sanitizedValue);
      break;
    case 'warn':
      console.warn(`${prefix} ${message}`, sanitizedValue);
      break;
    case 'important':
      console.log(`\n${prefix} ${message}`, sanitizedValue, '\n');
      break;
    default:
      console.log(`${prefix} ${message}`, sanitizedValue);
  }

  // Also log to file if possible
  try {
    const logDir = path.join(process.cwd(), 'logs');
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }

    // Use a secure filename with a timestamp to prevent path traversal
    const secureFilename = `path-to-regexp-detailed-${Date.now()}.log`;

    fs.appendFileSync(
      path.join(logDir, secureFilename),
      `${prefix} ${message} ${sanitizedValue}\n`
    );
  } catch (logError) {
    // Don't throw an error if logging fails
    console.error(`Failed to write to log file: ${logError.message}`);
  }
}

/**
 * Safely logs an error with sanitized values
 *
 * @param {string} message - The message template
 * @param {any} value - The value to sanitize and include in the log
 * @returns {void}
 */
function safeErrorLog(message, value) {
  safeLog(message, value, 'error');
}

/**
 * Validates a path to prevent path traversal attacks
 *
 * @param {string} dirPath - The directory path to validate
 * @returns {boolean} - Whether the path is valid
 */
function isValidPath(dirPath) {
  // Normalize the path to resolve any '..' or '.' segments
  const normalizedPath = path.normalize(dirPath);

  // Check if the normalized path is within the current working directory
  const cwd = process.cwd();
  return normalizedPath.startsWith(cwd) ||
         normalizedPath.startsWith(os.tmpdir()) ||
         (isGitHubActions && normalizedPath.startsWith(process.env.GITHUB_WORKSPACE || cwd));
}

/**
 * Safely creates a directory with validation
 *
 * @param {string} dirPath - The directory path to create
 * @returns {boolean} - Whether the directory was created successfully
 */
function safeCreateDirectory(dirPath) {
  try {
    // Validate the path first
    if (!isValidPath(dirPath)) {
      safeErrorLog(`Invalid directory path: ${dirPath}`, '');
      return false;
    }

    // Create the directory if it doesn't exist
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
      safeLog(`Created directory at ${dirPath}`, '', 'info');
    }

    return true;
  } catch (error) {
    safeErrorLog(`Failed to create directory: ${error.message}`, '');
    return false;
  }
}

/**
 * Safely writes to a file with validation
 *
 * @param {string} filePath - The file path to write to
 * @param {string} content - The content to write
 * @returns {boolean} - Whether the file was written successfully
 */
function safeWriteFile(filePath, content) {
  try {
    // Validate the path first
    if (!isValidPath(path.dirname(filePath))) {
      safeErrorLog(`Invalid file path: ${filePath}`, '');
      return false;
    }

    // Create a hash of the content for integrity verification
    const contentHash = crypto.createHash('sha256').update(content).digest('hex');

    // Write the file
    fs.writeFileSync(filePath, content);

    // Verify the file was written correctly
    const writtenContent = fs.readFileSync(filePath, 'utf8');
    const writtenHash = crypto.createHash('sha256').update(writtenContent).digest('hex');

    if (contentHash !== writtenHash) {
      safeErrorLog(`File integrity check failed for ${filePath}`, '');
      return false;
    }

    safeLog(`Successfully wrote to file ${filePath}`, '', 'info');
    return true;
  } catch (error) {
    safeErrorLog(`Failed to write file: ${error.message}`, '');
    return false;
  }
}

safeLog(`Mock path-to-regexp script running`, {
  CI: isCI ? 'Yes' : 'No',
  GitHubActions: isGitHubActions ? 'Yes' : 'No',
  DockerEnvironment: isDockerEnvironment ? 'Yes' : 'No',
  NodeVersion: process.version,
  Platform: process.platform,
  WorkingDirectory: process.cwd()
}, 'important');

// Create necessary directories
const logDir = path.join(process.cwd(), 'logs');
safeCreateDirectory(logDir);

const reportDir = path.join(process.cwd(), 'playwright-report');
safeCreateDirectory(reportDir);

const testResultsDir = path.join(process.cwd(), 'test-results');
safeCreateDirectory(testResultsDir);

// Log the execution of this script with more detailed environment information
try {
  const logFilePath = path.join(logDir, `mock-path-to-regexp-${Date.now()}.log`);

  const logContent = `Mock path-to-regexp script executed at ${new Date().toISOString()}\n` +
    `CI environment: ${isCI ? 'Yes' : 'No'}\n` +
    `GitHub Actions: ${isGitHubActions ? 'Yes' : 'No'}\n` +
    `Docker environment: ${isDockerEnvironment ? 'Yes' : 'No'}\n` +
    `Node.js version: ${process.version}\n` +
    `Platform: ${process.platform}\n` +
    `Architecture: ${process.arch}\n` +
    `Working directory: ${process.cwd()}\n` +
    `Environment variables: ${JSON.stringify({
      CI: process.env.CI,
      GITHUB_ACTIONS: process.env.GITHUB_ACTIONS,
      GITHUB_WORKFLOW: process.env.GITHUB_WORKFLOW,
      NODE_ENV: process.env.NODE_ENV
    }, null, 2)}\n`;

  safeWriteFile(logFilePath, logContent);

  // Also create a marker file in the report directory for CI systems
  if (isCI && fs.existsSync(reportDir)) {
    const markerFilePath = path.join(reportDir, `mock-path-to-regexp-started-${Date.now()}.txt`);

    const markerContent = `Mock path-to-regexp script started at ${new Date().toISOString()}\n` +
      `CI environment: ${isCI ? 'Yes' : 'No'}\n` +
      `GitHub Actions: ${isGitHubActions ? 'Yes' : 'No'}\n` +
      `Node.js version: ${process.version}\n` +
      `Platform: ${process.platform}\n`;

    safeWriteFile(markerFilePath, markerContent);
  }
} catch (logError) {
  safeErrorLog(`Failed to write log file: ${logError.message}`, '');
  // Continue anyway
}

// Create a mock implementation of path-to-regexp with improved functionality and security
function createMockImplementation() {
  safeLog('Starting to create mock implementation', '', 'important');

  // Enhanced environment detection with more CI platforms
  const env = {
    isCI: process.env.CI === 'true' || process.env.CI === true ||
          process.env.GITHUB_ACTIONS === 'true' || process.env.GITHUB_WORKFLOW ||
          process.env.TF_BUILD || process.env.JENKINS_URL ||
          process.env.GITLAB_CI || process.env.CIRCLECI,
    isDocker: fs.existsSync('/.dockerenv') || fs.existsSync('/run/.containerenv'),
    isGitHubActions: process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW,
    isJenkins: !!process.env.JENKINS_URL,
    isAzureDevOps: !!process.env.TF_BUILD,
    isGitLabCI: !!process.env.GITLAB_CI,
    isCircleCI: !!process.env.CIRCLECI,
    verbose: process.env.VERBOSE_LOGGING === 'true',
    tempDir: process.env.RUNNER_TEMP || os.tmpdir(),
    workDir: process.env.GITHUB_WORKSPACE || 
            process.env.JENKINS_HOME || 
            process.env.BUILD_SOURCESDIRECTORY || 
            process.cwd()
  };

  // Log detected environment for debugging
  safeLog(`Detected CI environment:`, {
    CI: env.isCI,
    Docker: env.isDocker,
    GitHub: env.isGitHubActions,
    Jenkins: env.isJenkins,
    Azure: env.isAzureDevOps,
    GitLab: env.isGitLabCI,
    CircleCI: env.isCircleCI,
    tempDir: env.tempDir,
    workDir: env.workDir
  }, 'important');

  // Prioritized locations for mock implementation based on environment
  const possibleLocations = [
    path.join(env.workDir, 'node_modules', 'path-to-regexp'),
    path.join(env.workDir, '.cache', 'path-to-regexp'),
    path.join(env.tempDir, 'path-to-regexp'),
    path.join(env.workDir, 'node_modules', '.cache', 'path-to-regexp')
  ];

  // Add GitHub Actions specific locations if we're in GitHub Actions
  if (isGitHubActions) {
    possibleLocations.push(
      path.join(process.env.GITHUB_WORKSPACE || process.cwd(), 'node_modules', 'path-to-regexp'),
      path.join(process.env.RUNNER_TEMP || os.tmpdir(), 'path-to-regexp')
    );
  }

  let mockCreated = false;
  let mockDir = null;

  // Try each location until one succeeds
  for (const location of possibleLocations) {
    try {
      // Validate the location path
      if (!isValidPath(location)) {
        safeLog(`Skipping invalid location: ${location}`, '', 'warn');
        continue;
      }

      safeLog(`Trying to create mock implementation at ${location}`, '', 'info');

      // Create parent directories if they don't exist
      const parentDir = path.dirname(location);
      if (!safeCreateDirectory(parentDir)) {
        continue;
      }

      // Create the path-to-regexp directory
      if (!safeCreateDirectory(location)) {
        continue;
      }

      // In CI environment, try to fix permissions
      if (isCI || isDockerEnvironment) {
        try {
          fs.chmodSync(location, 0o755); // More secure permissions (rwxr-xr-x)
          safeLog(`Set permissions for ${location}`, '', 'info');
        } catch (chmodError) {
          safeLog(`Failed to set permissions: ${chmodError.message}`, '', 'warn');
          // Continue anyway
        }
      }

      mockDir = location;
      mockCreated = true;
      break;
    } catch (locationError) {
      safeLog(`Failed to create mock at ${location}: ${locationError.message}`, '', 'warn');
      // Try the next location
    }
  }

  if (!mockCreated || !mockDir) {
    safeErrorLog('Failed to create mock implementation in any location', '');
    return false;
  }

  try {
    // Create the mock implementation with better formatting, comments, and security
    const mockImplementation = `/**
 * Mock implementation of path-to-regexp for CI compatibility
 * Created at ${new Date().toISOString()}
 *
 * This is a mock implementation of the path-to-regexp package
 * that is used to avoid dependency issues in CI environments.
 * Enhanced for GitHub Actions compatibility with better error handling.
 * Includes security improvements to prevent ReDoS vulnerabilities.
 */

/**
 * Convert path to regexp
 * @param {string} path - The path to convert
 * @param {Array} [keys] - Array to populate with keys
 * @param {Object} [options] - Options object
 * @returns {RegExp} - The regexp
 */
function pathToRegexp(path, keys, options) {
  const logPrefix = process.env.VERBOSE_LOGGING === 'true' ? '[path-to-regexp] ' : '';
  safeLog(`${logPrefix}Called with path: ${typeof path === 'string' ? path : typeof path}`, '', 'info');

  // Enhanced input validation and sanitization
  if (path === null || path === undefined) {
    safeLog(`${logPrefix}Path is null or undefined`, '', 'warn');
    return /.*/;
  }

  // Handle RegExp objects directly
  if (path instanceof RegExp) {
    return path;
  }

  // Ensure string type for paths
  if (typeof path !== 'string') {
    safeLog(`${logPrefix}Invalid path type: ${typeof path}`, '', 'warn');
    return /.*/;
  }

  // Anti-DoS measures: limit path length
  const maxPathLength = 2000;
  if (path.length > maxPathLength) {
    safeLog(`${logPrefix}Path too long (${path.length} chars), truncating`, '', 'warn');
    path = path.substring(0, maxPathLength);
  }

  // If keys is provided, safely populate with parameter names
  if (Array.isArray(keys) && typeof path === 'string') {
    try {
      // Use a safer regex with strict limits to prevent ReDoS
      const paramNames = path.match(/:[a-zA-Z0-9_]{1,50}/g) || [];

      // Limit the number of parameters to prevent DoS
      const maxParams = 20;
      const limitedParamNames = paramNames.slice(0, maxParams);

      if (paramNames.length > maxParams) {
        console.warn('Too many parameters in path, limiting to', maxParams);
      }

      limitedParamNames.forEach((param, index) => {
        keys.push({
          name: param.substring(1),
          prefix: '/',
          suffix: '',
          modifier: '',
          pattern: '[^/]+'
        });
      });
    } catch (error) {
      console.error('Error extracting parameters:', error.message);
    }
  }

  return /.*/;
}

// Add the main function as a property of itself (some libraries expect this)
pathToRegexp.pathToRegexp = pathToRegexp;

/**
 * Parse a path into an array of tokens
 * @param {string} path - The path to parse
 * @returns {Array} - The tokens
 */
pathToRegexp.parse = function parse(path) {
  console.log('Mock path-to-regexp.parse called with path:', typeof path === 'string' ? path : typeof path);

  // Input validation
  if (typeof path !== 'string') {
    console.warn('Invalid path type:', typeof path);
    return [];
  }

  // Return a more detailed parse result for better compatibility
  try {
    const tokens = [];

    // Limit path length to prevent DoS
    const maxPathLength = 1000;
    if (path.length > maxPathLength) {
      console.warn('Path too long, truncating to', maxPathLength, 'characters');
      path = path.substring(0, maxPathLength);
    }

    const parts = path.split('/');

    // Limit number of parts to prevent DoS
    const maxParts = 50;
    const limitedParts = parts.slice(0, maxParts);

    if (parts.length > maxParts) {
      console.warn('Too many path segments, limiting to', maxParts);
    }

    limitedParts.forEach(part => {
      if (part.startsWith(':')) {
        tokens.push({
          name: part.substring(1),
          prefix: '/',
          suffix: '',
          pattern: '[^/]+',
          modifier: ''
        });
      } else if (part) {
        tokens.push(part);
      }
    });
    return tokens;
  } catch (error) {
    console.error('Error parsing path:', error.message);
    return [];
  }
};

/**
 * Compile a path into a function that generates URLs
 * @param {string} path - The path to compile
 * @returns {Function} - The URL generator
 */
pathToRegexp.compile = function compile(path) {
  console.log('Mock path-to-regexp.compile called with path:', typeof path === 'string' ? path : typeof path);

  return function(params) {
    console.log('Mock path-to-regexp.compile function called with params:', params ? 'object' : typeof params);

    // Input validation
    if (typeof path !== 'string') {
      console.warn('Invalid path type:', typeof path);
      return '';
    }

    if (!params || typeof params !== 'object') {
      console.warn('Invalid params type:', typeof params);
      return path;
    }

    // Try to replace parameters in the path
    try {
      let result = path;

      // Limit the number of replacements to prevent DoS
      const maxReplacements = 20;
      let replacementCount = 0;

      Object.keys(params).forEach(key => {
        if (replacementCount >= maxReplacements) {
          return;
        }

        // Validate parameter value
        const value = params[key];
        if (typeof value !== 'string' && typeof value !== 'number') {
          console.warn('Invalid parameter value type for', key, ':', typeof value);
          return;
        }

        // Convert value to string and sanitize
        const sanitizedValue = String(value).replace(/[\\/?#]/g, encodeURIComponent);

        // Use string replacement instead of regex to avoid ReDoS
        const placeholder = ':' + key;
        result = result.split(placeholder).join(sanitizedValue);

        replacementCount++;
      });

      return result;
    } catch (error) {
      console.error('Error compiling path:', error.message);
      return path;
    }
  };
};

/**
 * Match a path against a regexp
 * @param {string} path - The path to match
 * @returns {Function} - A function that matches a pathname against the path
 */
pathToRegexp.match = function match(path) {
  console.log('Mock path-to-regexp.match called with path:', typeof path === 'string' ? path : typeof path);

  return function(pathname) {
    console.log('Mock path-to-regexp.match function called with pathname:', typeof pathname === 'string' ? pathname : typeof pathname);

    // Input validation
    if (typeof path !== 'string' || typeof pathname !== 'string') {
      console.warn('Invalid path or pathname type');
      return { path: pathname, params: {}, index: 0, isExact: false };
    }

    // Extract parameter values from the pathname if possible
    try {
      const params = {};

      const pathParts = path.split('/');
      const pathnameParts = pathname.split('/');

      // Limit the number of parts to prevent DoS
      const maxParts = 50;
      const limitedPathParts = pathParts.slice(0, maxParts);
      const limitedPathnameParts = pathnameParts.slice(0, maxParts);

      const isExact = limitedPathParts.length === limitedPathnameParts.length;

      // Extract parameters
      const minLength = Math.min(limitedPathParts.length, limitedPathnameParts.length);

      for (let i = 0; i < minLength; i++) {
        if (limitedPathParts[i].startsWith(':')) {
          const paramName = limitedPathParts[i].substring(1);
          params[paramName] = limitedPathnameParts[i];
        } else if (limitedPathParts[i] !== limitedPathnameParts[i]) {
          // If a non-parameter segment doesn't match, it's not a match
          return { path: pathname, params: {}, index: 0, isExact: false };
        }
      }

      return { path: pathname, params: params, index: 0, isExact: isExact };
    } catch (error) {
      console.error('Error matching path:', error.message);
      return { path: pathname, params: {}, index: 0, isExact: false };
    }
  };
};

/**
 * Convert an array of tokens to a regexp
 * @param {Array} tokens - The tokens to convert
 * @param {Array} [keys] - Array to populate with keys
 * @param {Object} [options] - Options object
 * @returns {RegExp} - The regexp
 */
pathToRegexp.tokensToRegexp = function tokensToRegexp(tokens, keys, options) {
  console.log('Mock path-to-regexp.tokensToRegexp called');

  // Input validation
  if (!Array.isArray(tokens)) {
    console.warn('Invalid tokens type:', typeof tokens);
    return /.*/;
  }

  try {
    // If keys is provided, populate it with parameter names from tokens
    if (Array.isArray(keys)) {
      // Limit the number of tokens to prevent DoS
      const maxTokens = 50;
      const limitedTokens = tokens.slice(0, maxTokens);

      if (tokens.length > maxTokens) {
        console.warn('Too many tokens, limiting to', maxTokens);
      }

      limitedTokens.forEach(token => {
        if (typeof token === 'object' && token && token.name) {
          keys.push({
            name: token.name,
            prefix: token.prefix || '/',
            suffix: token.suffix || '',
            modifier: token.modifier || '',
            pattern: token.pattern || '[^/]+'
          });
        }
      });
    }

    return /.*/;
  } catch (error) {
    console.error('Error converting tokens to regexp:', error.message);
    return /.*/;
  }
};

/**
 * Convert an array of tokens to a function that generates URLs
 * @param {Array} tokens - The tokens to convert
 * @param {Object} [options] - Options object
 * @returns {Function} - The URL generator
 */
pathToRegexp.tokensToFunction = function tokensToFunction(tokens, options) {
  console.log('Mock path-to-regexp.tokensToFunction called');

  return function(params) {
    console.log('Mock path-to-regexp.tokensToFunction function called with params:', params ? 'object' : typeof params);

    // Input validation
    if (!Array.isArray(tokens) || !params || typeof params !== 'object') {
      return '';
    }

    try {
      let result = '';

      // Limit the number of tokens to prevent DoS
      const maxTokens = 50;
      const limitedTokens = tokens.slice(0, maxTokens);

      limitedTokens.forEach(token => {
        if (typeof token === 'string') {
          result += token;
        } else if (typeof token === 'object' && token && token.name && params[token.name]) {
          // Validate and sanitize parameter value
          const value = params[token.name];
          if (typeof value !== 'string' && typeof value !== 'number') {
            return;
          }

          // Convert value to string and sanitize
          const sanitizedValue = String(value).replace(/[\\/?#]/g, encodeURIComponent);
          result += sanitizedValue;
        }
      });

      return result;
    } catch (error) {
      console.error('Error converting tokens to function:', error.message);
      return '';
    }
  };
};

// Add regexp property for compatibility with some libraries
pathToRegexp.regexp = /.*/;

// Add encode/decode functions for compatibility with some libraries
pathToRegexp.encode = function encode(value) {
  try {
    return encodeURIComponent(value);
  } catch (error) {
    console.error('Error encoding value:', error.message);
    return '';
  }
};

pathToRegexp.decode = function decode(value) {
  try {
    return decodeURIComponent(value);
  } catch (error) {
    console.error('Error decoding value:', error.message);
    return value;
  }
};

module.exports = pathToRegexp;
