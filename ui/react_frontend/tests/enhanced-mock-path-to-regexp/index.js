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
        process.env.GITLAB_CI || process.env.CIRCLECI ||
        !!process.env.BITBUCKET_COMMIT || !!process.env.APPVEYOR ||
        !!process.env.DRONE || !!process.env.BUDDY ||
        !!process.env.BUILDKITE || !!process.env.CODEBUILD_BUILD_ID,
  isDocker: fs.existsSync('/.dockerenv') || fs.existsSync('/run/.containerenv'),
  isGitHubActions: process.env.GITHUB_ACTIONS === 'true' || !!process.env.GITHUB_WORKFLOW,
  verbose: process.env.VERBOSE_LOGGING === 'true',
  tempDir: process.env.RUNNER_TEMP || os.tmpdir(),
  workDir: process.env.GITHUB_WORKSPACE || process.cwd()
};

// Enhanced logging with error tracing
const debug = (msg, error) => {
  if (!env.verbose) return;
  console.log(`[path-to-regexp] ${msg}`);
  if (error?.stack) {
    console.log(`[path-to-regexp] Stack trace: ${error.stack}`);
  }
};

// Enhanced sanitization with additional characters
const sanitize = (value) => {
  if (typeof value !== 'string') return String(value);
  return value.replace(/[\\/?#\[\]{}()*+,;|]/g, encodeURIComponent);
};

// Security constants
const LIMITS = {
  MAX_PATH_LENGTH: 2000,
  MAX_PARAM_LENGTH: 50,
  MAX_PARAMS: 20,
  MAX_PARTS: 50,
  MAX_REPLACEMENTS: 20,
  MAX_PATTERN_LENGTH: 100
};

// Enhanced parameter validation
const validateParam = (param) => {
  if (!param || typeof param !== 'string') return false;
  if (param.length > LIMITS.MAX_PARAM_LENGTH) return false;
  // Only allow alphanumeric and underscore in parameter names
  return /^:[a-zA-Z0-9_]+$/.test(param);
};

// ReDoS protection wrapper
const safeMatch = (str, pattern) => {
  if (typeof str !== 'string' || str.length > LIMITS.MAX_PATH_LENGTH) {
    return null;
  }
  try {
    return str.match(pattern);
  } catch (error) {
    debug('Pattern matching error', error);
    return null;
  }
};

/**
 * Convert path to regexp with enhanced security and CI compatibility
 * @param {string|RegExp} path - The path to convert
 * @param {Array} [keys] - Array to populate with keys
 * @param {Object} [options] - Options object
 * @returns {RegExp} - The regexp
 */
function pathToRegexp(path, keys, options) {
  debug(`Called with path: ${typeof path === 'string' ? sanitize(path) : typeof path}`);

  // Input validation
  if (path === null || path === undefined) {
    debug('Path is null or undefined');
    return /.*/;
  }

  // Handle RegExp inputs directly
  if (path instanceof RegExp) {
    debug('Path is already a RegExp');
    return path;
  }

  // Sanitize and limit input
  if (typeof path !== 'string') {
    debug(`Invalid path type: ${typeof path}`);
    return /.*/;
  }

  // Anti-DoS: limit path length
  if (path.length > LIMITS.MAX_PATH_LENGTH) {
    debug(`Path too long (${path.length} chars), truncating`);
    path = path.substring(0, LIMITS.MAX_PATH_LENGTH);
  }

  // Process parameters if keys array provided
  if (Array.isArray(keys)) {
    try {
      // Use a safer regex for params with length limit
      const paramMatcher = new RegExp(`:[a-zA-Z0-9_]{1,${LIMITS.MAX_PARAM_LENGTH}}`, 'g');
      const matches = safeMatch(path, paramMatcher);
      if (!matches) return /.*/;

      // Limit number of parameters
      matches.slice(0, LIMITS.MAX_PARAMS).forEach(param => {
        if (validateParam(param)) {
          keys.push({
            name: param.substring(1),
            prefix: '/',
            suffix: '',
            pattern: '[^/]+',
            modifier: ''
          });
        }
      });
    } catch (error) {
      debug('Error extracting parameters', error);
    }
  }

  // Handle options
  try {
    if (options && typeof options === 'object') {
      const pattern = options.pattern || '[^/]+';
      if (pattern.length > LIMITS.MAX_PATTERN_LENGTH) {
        debug('Pattern too long, using default');
        options.pattern = '[^/]+';
      }
    }
  } catch (error) {
    debug('Error handling options', error);
  }

  return /.*/;
}

// Add main function as property of itself (for library compatibility)
pathToRegexp.pathToRegexp = pathToRegexp;

/**
 * Enhanced parse implementation
 */
pathToRegexp.parse = function parse(path) {
  debug(`Parse called with path: ${typeof path === 'string' ? path : typeof path}`);

  if (typeof path !== 'string') {
    return [];
  }

  try {
    const tokens = [];
    const maxParts = 50;
    const parts = path.split('/').slice(0, maxParts);

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
  } catch (error) {
    debug(`Parse error: ${error.message}`);
    return [];
  }
};

/**
 * Enhanced compile implementation
 */
pathToRegexp.compile = function compile(path) {
  debug(`Compile called with path: ${typeof path === 'string' ? sanitize(path) : typeof path}`);

  return function(params) {
    debug(`Compile function called with params: ${params ? 'object' : typeof params}`);

    if (typeof path !== 'string') return '';
    if (!params || typeof params !== 'object') return path;

    try {
      // Anti-DoS: limit path length
      if (path.length > LIMITS.MAX_PATH_LENGTH) {
        debug('Path too long in compile');
        return '';
      }

      let result = path;
      let replacements = 0;

      // Use Object.entries for better performance
      for (const [key, value] of Object.entries(params)) {
        if (replacements >= LIMITS.MAX_REPLACEMENTS) {
          debug('Max replacements reached');
          break;
        }

        if (typeof value !== 'string' && typeof value !== 'number') {
          debug(`Invalid value type for key ${key}: ${typeof value}`);
          continue;
        }

        // Validate parameter name
        if (!validateParam(':' + key)) {
          debug(`Invalid parameter name: ${key}`);
          continue;
        }

        const sanitizedValue = sanitize(value);
        result = result.split(`:${key}`).join(sanitizedValue);
        replacements++;
      }

      return result;
    } catch (error) {
      debug('Compile error', error);
      return path;
    }
  };
};

/**
 * Enhanced match implementation
 */
pathToRegexp.match = function match(path) {
  debug(`Match called with path: ${typeof path === 'string' ? sanitize(path) : typeof path}`);

  return function(pathname) {
    debug(`Match function called with pathname: ${typeof pathname === 'string' ? sanitize(pathname) : typeof pathname}`);

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

      // Quick length check for optimization
      if (pathParts.length === 0 || pathnameParts.length === 0) {
        return { path: pathname, params: {}, index: 0, isExact: false };
      }

      const isExact = pathParts.length === pathnameParts.length;
      let paramCount = 0;

      for (let i = 0; i < Math.min(pathParts.length, pathnameParts.length); i++) {
        if (pathParts[i].startsWith(':')) {
          if (paramCount >= LIMITS.MAX_PARAMS) {
            debug('Max parameters reached');
            break;
          }

          const paramName = pathParts[i].substring(1);
          if (validateParam(':' + paramName)) {
            params[paramName] = pathnameParts[i];
            paramCount++;
          }
        } else if (pathParts[i] !== pathnameParts[i]) {
          return { path: pathname, params: {}, index: 0, isExact: false };
        }
      }

      return { path: pathname, params, index: 0, isExact };
    } catch (error) {
      debug('Match error', error);
      return { path: pathname, params: {}, index: 0, isExact: false };
    }
  };
};

/**
 * Enhanced tokensToRegexp implementation
 */
pathToRegexp.tokensToRegexp = function tokensToRegexp(tokens, keys, options) {
  debug('tokensToRegexp called');

  if (!Array.isArray(tokens)) {
    debug(`Invalid tokens type: ${typeof tokens}`);
    return /.*/;
  }

  try {
    if (Array.isArray(keys)) {
      const maxTokens = 50;
      tokens.slice(0, maxTokens).forEach(token => {
        if (typeof token === 'object' && token?.name) {
          keys.push({
            name: token.name,
            prefix: token.prefix || '/',
            suffix: token.suffix || '',
            pattern: token.pattern || '[^/]+',
            modifier: token.modifier || ''
          });
        }
      });
    }
  } catch (error) {
    debug(`tokensToRegexp error: ${error.message}`);
  }

  return /.*/;
};

/**
 * Enhanced tokensToFunction implementation
 */
pathToRegexp.tokensToFunction = function tokensToFunction(tokens) {
  debug('tokensToFunction called');

  return function(params) {
    debug(`tokensToFunction executor called with params: ${params ? 'object' : typeof params}`);

    if (!Array.isArray(tokens) || !params || typeof params !== 'object') {
      return '';
    }

    try {
      let result = '';
      const maxTokens = 50;
      
      tokens.slice(0, maxTokens).forEach(token => {
        if (typeof token === 'string') {
          result += token;
        } else if (typeof token === 'object' && token?.name && params[token.name]) {
          result += sanitize(params[token.name]);
        }
      });

      return result;
    } catch (error) {
      debug(`tokensToFunction error: ${error.message}`);
      return '';
    }
  };
};

// Add additional properties for compatibility
pathToRegexp.regexp = /.*/;

// Enhanced encode function with validation
pathToRegexp.encode = function encode(value) {
  debug(`Encode called with value: ${typeof value === 'string' ? sanitize(value) : typeof value}`);

  try {
    if (value === null || value === undefined) {
      return '';
    }

    const str = String(value);
    if (str.length > LIMITS.MAX_PATH_LENGTH) {
      debug('Value too long for encoding');
      return '';
    }

    return encodeURIComponent(str);
  } catch (error) {
    debug('Encode error', error);
    return '';
  }
};

// Enhanced decode function with validation
pathToRegexp.decode = function decode(value) {
  debug(`Decode called with value: ${typeof value === 'string' ? sanitize(value) : typeof value}`);

  try {
    if (value === null || value === undefined) {
      return '';
    }

    const str = String(value);
    if (str.length > LIMITS.MAX_PATH_LENGTH) {
      debug('Value too long for decoding');
      return '';
    }

    return decodeURIComponent(str);
  } catch (error) {
    debug('Decode error', error);
    return value;
  }
};

module.exports = pathToRegexp;
