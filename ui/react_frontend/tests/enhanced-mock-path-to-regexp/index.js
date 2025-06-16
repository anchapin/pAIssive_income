/**
 * Enhanced mock implementation of path-to-regexp for CI compatibility
 * Created for GitHub Actions and Docker environments
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

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
  MAX_REPLACEMENTS: 20,
  MAX_PATTERN_LENGTH: 100
};

// Logging helper
function debug(msg, error) {
  if (!env.verbose) return;
  console.log(`[path-to-regexp] ${msg}`);
  if (error?.stack) {
    console.log(`[path-to-regexp] Stack trace: ${error.stack}`);
  }
}

// Sanitize values for logging
function sanitize(value) {
  if (value === null || value === undefined) return String(value);
  const str = String(value);
  return str.length > 100 ? str.substring(0, 97) + '...' : str;
}

/**
 * Convert path to regexp
 */
function pathToRegexp(path, keys, options) {
  debug(`Called with path: ${sanitize(path)}`);

  // Handle different input types
  if (path instanceof RegExp) return path;
  if (Array.isArray(path)) return new RegExp('.*');
  
  // If keys is provided, populate it with parameter names
  if (Array.isArray(keys) && typeof path === 'string') {
    try {
      const paramNames = path.match(/:[a-zA-Z0-9_]{1,100}/g) || [];
      paramNames.forEach((param, index) => {
        if (index >= LIMITS.MAX_PARAMS) return;
        keys.push({
          name: param.substring(1),
          prefix: '/',
          suffix: '',
          modifier: '',
          pattern: '[^/]+'
        });
      });
    } catch (error) {
      debug('Error processing keys', error);
    }
  }

  return new RegExp('.*');
}

// Add all required methods
pathToRegexp.parse = function parse(path) {
  debug(`Parse called with path: ${sanitize(path)}`);
  
  if (typeof path !== 'string') return [];
  if (path.length > LIMITS.MAX_PATH_LENGTH) return [];
  
  const tokens = [];
  const parts = path.split('/').slice(0, LIMITS.MAX_PARTS);
  
  parts.forEach(part => {
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
};

pathToRegexp.compile = function compile(str) {
  debug(`Compile called with str: ${sanitize(str)}`);

  return function(params) {
    try {
      if (params && typeof str === 'string') {
        let result = str;
        const replacements = [];
        Object.keys(params).forEach(key => {
          if (replacements.length >= LIMITS.MAX_REPLACEMENTS) return;
          if (key.length > LIMITS.MAX_PARAM_LENGTH) return;
          const value = String(params[key]);
          if (value.length > LIMITS.MAX_PATTERN_LENGTH) return;
          const regex = new RegExp(':' + key + '(?![a-zA-Z0-9_])', 'g');
          result = result.replace(regex, value);
          replacements.push(key);
        });
        return result;
      }
      return str || '';
    } catch (error) {
      debug('Error in compile function', error);
      return str || '';
    }
  };
};

pathToRegexp.match = function match(path) {
  debug(`Match called with path: ${sanitize(path)}`);

  return function(pathname) {
    debug(`Match function called with pathname: ${sanitize(pathname)}`);

    if (typeof path !== 'string' || typeof pathname !== 'string') {
      return { path: pathname, params: {}, index: 0, isExact: false };
    }

    try {
      // Anti-DoS checks
      if (path.length > LIMITS.MAX_PATH_LENGTH || pathname.length > LIMITS.MAX_PATH_LENGTH) {
        debug('Path or pathname too long');
        return { path: pathname, params: {}, index: 0, isExact: false };
      }

      const params = {};
      const pathParts = path.split('/').slice(0, LIMITS.MAX_PARTS);
      const pathnameParts = pathname.split('/').slice(0, LIMITS.MAX_PARTS);

      let isExact = pathParts.length === pathnameParts.length;
      let paramCount = 0;

      // Extract parameters even if the path doesn't match exactly
      const minLength = Math.min(pathParts.length, pathnameParts.length);

      for (let i = 0; i < minLength; i++) {
        if (pathParts[i] && pathParts[i].startsWith(':')) {
          if (paramCount >= LIMITS.MAX_PARAMS) break;
          const paramName = pathParts[i].substring(1);
          if (paramName.length > LIMITS.MAX_PARAM_LENGTH) continue;
          params[paramName] = pathnameParts[i];
          paramCount++;
        }
      }

      return {
        path: pathname,
        params,
        index: 0,
        isExact
      };
    } catch (error) {
      debug('Error in match function', error);
      return { path: pathname, params: {}, index: 0, isExact: false };
    }
  };
};

// Add regexp property for compatibility
pathToRegexp.regexp = /.*/;

// Add encode/decode functions
pathToRegexp.encode = function encode(value) {
  try {
    return encodeURIComponent(value);
  } catch (error) {
    debug('Error encoding value', error);
    return value;
  }
};

pathToRegexp.decode = function decode(value) {
  try {
    return decodeURIComponent(value);
  } catch (error) {
    debug('Error decoding value', error);
    return value;
  }
};

module.exports = pathToRegexp;
