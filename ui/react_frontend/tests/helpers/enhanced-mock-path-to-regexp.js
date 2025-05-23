/**
 * Enhanced Mock Implementation for path-to-regexp
 * 
 * This module provides a robust mock implementation of path-to-regexp
 * that works in all CI environments, with comprehensive error handling
 * and fallback mechanisms.
 * 
 * It can be used to patch the require function or as a direct replacement
 * for the path-to-regexp module.
 */

/**
 * Create a mock implementation of path-to-regexp
 * @returns {Function} Mock path-to-regexp function with all required methods
 */
function createMockPathToRegexp() {
  // Main function
  const mockPathToRegexp = function(path, keys, options) {
    console.log(`Mock path-to-regexp called with path: ${path}`);

    try {
      // If keys is provided, populate it with parameter names
      if (Array.isArray(keys) && typeof path === 'string') {
        // Use a safer regex with a limited repetition to prevent ReDoS
        const paramNames = path.match(/:[a-zA-Z0-9_]{1,100}/g) || [];
        paramNames.forEach((param, index) => {
          keys.push({
            name: param.substring(1),
            prefix: '/',
            suffix: '',
            modifier: '',
            pattern: '[^/]+'
          });
        });
      }
    } catch (error) {
      console.error(`Error in mock path-to-regexp: ${error.message}`);
    }

    return /.*/;
  };

  // Add the main function as a property of itself (some libraries expect this)
  mockPathToRegexp.pathToRegexp = mockPathToRegexp;

  // Parse function
  mockPathToRegexp.parse = function(path) {
    console.log(`Mock path-to-regexp.parse called with path: ${path}`);

    try {
      // Return a more detailed parse result for better compatibility
      if (typeof path === 'string') {
        const tokens = [];
        const parts = path.split('/');
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
      }
    } catch (error) {
      console.error(`Error in mock path-to-regexp.parse: ${error.message}`);
    }

    return [];
  };

  // Compile function
  mockPathToRegexp.compile = function(path) {
    console.log(`Mock path-to-regexp.compile called with path: ${path}`);

    return function(params) {
      try {
        console.log(`Mock path-to-regexp.compile function called with params: ${JSON.stringify(params)}`);

        // Try to replace parameters in the path
        if (typeof path === 'string' && params) {
          let result = path;
          Object.keys(params).forEach(key => {
            result = result.replace(`:${key}`, params[key]);
          });
          return result;
        }
        return path || '';
      } catch (error) {
        console.error(`Error in mock path-to-regexp.compile: ${error.message}`);
        return path || '';
      }
    };
  };

  // Match function
  mockPathToRegexp.match = function(path) {
    console.log(`Mock path-to-regexp.match called with path: ${path}`);

    return function(pathname) {
      try {
        console.log(`Mock path-to-regexp.match function called with pathname: ${pathname}`);

        // Extract parameter values from the pathname if possible
        const params = {};
        if (typeof path === 'string' && typeof pathname === 'string') {
          const pathParts = path.split('/');
          const pathnameParts = pathname.split('/');

          if (pathParts.length === pathnameParts.length) {
            for (let i = 0; i < pathParts.length; i++) {
              if (pathParts[i].startsWith(':')) {
                const paramName = pathParts[i].substring(1);
                params[paramName] = pathnameParts[i];
              }
            }
          }
        }

        return { path: pathname, params: params, index: 0, isExact: true };
      } catch (error) {
        console.error(`Error in mock path-to-regexp.match: ${error.message}`);
        return { path: pathname, params: {}, index: 0, isExact: false };
      }
    };
  };

  // tokensToRegexp function
  mockPathToRegexp.tokensToRegexp = function(tokens, keys, options) {
    console.log('Mock path-to-regexp.tokensToRegexp called');

    try {
      // If keys is provided, populate it with parameter names from tokens
      if (Array.isArray(keys) && Array.isArray(tokens)) {
        tokens.forEach(token => {
          if (typeof token === 'object' && token.name) {
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
    } catch (error) {
      console.error(`Error in mock path-to-regexp.tokensToRegexp: ${error.message}`);
    }

    return /.*/;
  };

  // tokensToFunction function
  mockPathToRegexp.tokensToFunction = function(tokens, options) {
    console.log('Mock path-to-regexp.tokensToFunction called');

    return function(params) {
      try {
        console.log(`Mock path-to-regexp.tokensToFunction function called with params: ${JSON.stringify(params)}`);

        // Try to generate a path from tokens and params
        if (Array.isArray(tokens) && params) {
          let result = '';

          tokens.forEach(token => {
            if (typeof token === 'string') {
              result += token;
            } else if (typeof token === 'object' && token.name && params[token.name]) {
              result += params[token.name];
            }
          });

          return result;
        }
        return '';
      } catch (error) {
        console.error(`Error in mock path-to-regexp.tokensToFunction: ${error.message}`);
        return '';
      }
    };
  };

  // Add regexp property for compatibility with some libraries
  mockPathToRegexp.regexp = /.*/;

  // Add decode/encode functions for compatibility with some libraries
  mockPathToRegexp.decode = function(value) {
    try {
      return decodeURIComponent(value);
    } catch (error) {
      return value;
    }
  };

  mockPathToRegexp.encode = function(value) {
    try {
      return encodeURIComponent(value);
    } catch (error) {
      return value;
    }
  };

  return mockPathToRegexp;
}

/**
 * Patch the require function to handle path-to-regexp
 * @returns {boolean} True if patching was successful
 */
function patchRequireFunction() {
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

    console.log('Successfully patched require to handle path-to-regexp');
    return true;
  } catch (error) {
    console.error(`Failed to patch require: ${error.message}`);
    return false;
  }
}

// Export functions
module.exports = {
  createMockPathToRegexp,
  patchRequireFunction
};
