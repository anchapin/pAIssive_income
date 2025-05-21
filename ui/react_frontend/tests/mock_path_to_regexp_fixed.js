/**
 * Enhanced Mock path-to-regexp module for CI compatibility
 * Created for GitHub Actions and Docker environments
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

// Enhanced environment detection
const env = {
  isCI: process.env.CI === 'true' || process.env.GITHUB_ACTIONS === 'true' ||
        process.env.TF_BUILD || process.env.JENKINS_URL ||
        process.env.GITLAB_CI || process.env.CIRCLECI,
  isDocker: fs.existsSync('/.dockerenv') || fs.existsSync('/run/.containerenv'),
  verbose: process.env.VERBOSE_LOGGING === 'true',
  tempDir: process.env.RUNNER_TEMP || os.tmpdir(),
  workDir: process.env.GITHUB_WORKSPACE || process.cwd()
};

// Security limits to prevent DoS
const LIMITS = {
  MAX_PATH_LENGTH: 2000,
  MAX_PARAM_LENGTH: 50,
  MAX_PARAMS: 20,
  MAX_PARTS: 50,
  MAX_REPLACEMENTS: 20
};

/**
 * Main path-to-regexp function
 */
function pathToRegexp(path, keys, options) {
  try {
    if (path === null || path === undefined) {
      console.warn('Path is null or undefined');
      return /.*/;
    }

    // Handle RegExp objects directly
    if (path instanceof RegExp) {
      return path;
    }

    // Ensure string type for paths
    if (typeof path !== 'string') {
      console.warn('Invalid path type:', typeof path);
      return /.*/;
    }

    // Anti-DoS measures: limit path length
    if (path.length > LIMITS.MAX_PATH_LENGTH) {
      console.warn(`Path too long (${path.length} chars), truncating`);
      path = path.substring(0, LIMITS.MAX_PATH_LENGTH);
    }

    // If keys is provided, safely populate with parameter names
    if (Array.isArray(keys) && typeof path === 'string') {
      try {
        // Use a safer regex with strict limits to prevent ReDoS
        const paramNames = path.match(/:[a-zA-Z0-9_]{1,50}/g) || [];
        
        // Limit number of parameters
        const limitedParamNames = paramNames.slice(0, LIMITS.MAX_PARAMS);

        if (paramNames.length > LIMITS.MAX_PARAMS) {
          console.warn(`Too many parameters (${paramNames.length}), limiting to ${LIMITS.MAX_PARAMS}`);
        }

        limitedParamNames.forEach(param => {
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
  } catch (error) {
    console.error('Error in pathToRegexp:', error.message);
    return /.*/;
  }
}

// Add the main function as a property of itself (some libraries expect this)
pathToRegexp.pathToRegexp = pathToRegexp;

/**
 * Parse function with enhanced validation
 */
pathToRegexp.parse = function parse(path) {
  try {
    if (typeof path !== 'string') {
      console.warn('Invalid path type:', typeof path);
      return [];
    }

    // Limit path length
    if (path.length > LIMITS.MAX_PATH_LENGTH) {
      path = path.substring(0, LIMITS.MAX_PATH_LENGTH);
      console.warn(`Path truncated to ${LIMITS.MAX_PATH_LENGTH} characters`);
    }

    const parts = path.split('/');
    const limitedParts = parts.slice(0, LIMITS.MAX_PARTS);
    
    if (parts.length > LIMITS.MAX_PARTS) {
      console.warn(`Too many path segments (${parts.length}), limiting to ${LIMITS.MAX_PARTS}`);
    }

    return limitedParts.map(part => {
      if (part.startsWith(':')) {
        return {
          name: part.substring(1),
          prefix: '/',
          suffix: '',
          modifier: '',
          pattern: '[^/]+'
        };
      }
      return part;
    }).filter(Boolean);
  } catch (error) {
    console.error('Error in parse:', error.message);
    return [];
  }
};

/**
 * Compile function with security improvements
 */
pathToRegexp.compile = function compile(path) {
  return function(params) {
    try {
      if (!params || typeof params !== 'object') {
        return path || '';
      }

      let result = path;
      let replacements = 0;

      for (const key of Object.keys(params)) {
        if (replacements >= LIMITS.MAX_REPLACEMENTS) {
          console.warn(`Max replacements (${LIMITS.MAX_REPLACEMENTS}) reached`);
          break;
        }

        const value = params[key];
        if (value === undefined || value === null) continue;

        // Sanitize the value
        const sanitized = String(value).replace(/[\\/?#]/g, encodeURIComponent);
        result = result.split(`:${key}`).join(sanitized);
        replacements++;
      }

      return result;
    } catch (error) {
      console.error('Error in compile:', error.message);
      return path || '';
    }
  };
};

/**
 * Match function for path matching
 */
pathToRegexp.match = function match(path) {
  return function(pathname) {
    try {
      if (typeof path !== 'string' || typeof pathname !== 'string') {
        return { path: pathname, params: {}, index: 0, isExact: false };
      }

      const params = {};
      const pathParts = path.split('/').slice(0, LIMITS.MAX_PARTS);
      const pathnameParts = pathname.split('/').slice(0, LIMITS.MAX_PARTS);
      const isExact = pathParts.length === pathnameParts.length;

      for (let i = 0; i < Math.min(pathParts.length, pathnameParts.length); i++) {
        if (pathParts[i].startsWith(':')) {
          params[pathParts[i].substring(1)] = pathnameParts[i];
        } else if (pathParts[i] !== pathnameParts[i]) {
          return { path: pathname, params: {}, index: 0, isExact: false };
        }
      }

      return { path: pathname, params, index: 0, isExact };
    } catch (error) {
      console.error('Error in match:', error.message);
      return { path: pathname, params: {}, index: 0, isExact: false };
    }
  };
};

/**
 * Utility function for secure value encoding
 */
pathToRegexp.encode = function encode(value) {
  try {
    return encodeURIComponent(value);
  } catch (error) {
    console.error('Error encoding value:', error.message);
    return '';
  }
};

/**
 * Utility function for secure value decoding
 */
pathToRegexp.decode = function decode(value) {
  try {
    return decodeURIComponent(value);
  } catch (error) {
    console.error('Error decoding value:', error.message);
    return value;
  }
};

// Add cross-platform path handling
const normalizePathForPlatform = (inputPath) => {
  try {
    // Convert to platform-specific path
    const normalized = path.normalize(inputPath);
    
    // Handle Windows paths in CI
    if (process.platform === 'win32') {
      return normalized.replace(/\\/g, '/');
    }
    return normalized;
  } catch (error) {
    console.error('Error normalizing path:', error.message);
    return inputPath;
  }
};

/**
 * Safely create test directories
 */
const setupTestDirectories = () => {
  const dirs = [
    path.join(process.cwd(), 'logs'),
    path.join(process.cwd(), 'test-results'),
    path.join(process.cwd(), 'playwright-report')
  ];

  for (const dir of dirs) {
    try {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        
        // Set permissions in CI environment
        if (env.isCI || env.isDocker) {
          fs.chmodSync(dir, 0o755);
        }
      }
    } catch (error) {
      console.warn(`Failed to create directory ${dir}:`, error.message);
      // Continue with other directories
    }
  }
};

// Call setup on module load
setupTestDirectories();

module.exports = pathToRegexp;
