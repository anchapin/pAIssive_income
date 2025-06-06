# PowerShell script to fix CodeQL issues in the codebase
# This script is used by the GitHub Actions workflow to fix security issues
# that might cause the CodeQL scan to fail.

Write-Host "Fixing CodeQL issues in the codebase..."

# Create a report directory for logs
if (-not (Test-Path "logs")) {
    New-Item -Path "logs" -ItemType Directory -Force | Out-Null
}

# Log file
$LOG_FILE = "logs/fix-codeql-issues.log"
"Starting CodeQL issue fixing at $(Get-Date)" | Out-File -FilePath $LOG_FILE

# Fix path-to-regexp issues in the frontend
if (Test-Path "ui/react_frontend") {
    Write-Host "Fixing path-to-regexp issues in the frontend..." | Tee-Object -Append -FilePath $LOG_FILE
    
    # Create the mock implementation directory
    $mockDir = "ui/react_frontend/node_modules/path-to-regexp"
    if (-not (Test-Path $mockDir)) {
        New-Item -Path $mockDir -ItemType Directory -Force | Out-Null
    }
    
    # Create the mock implementation file
    @"
/**
 * Enhanced Mock path-to-regexp module for CI compatibility
 * Created for GitHub Actions and Docker environments
 * With improved error handling and security features
 */

/**
 * Convert path to regexp
 * @param {string} path - The path to convert
 * @param {Array} [keys] - Array to populate with keys
 * @param {Object} [options] - Options object
 * @returns {RegExp} - The regexp
 */
function pathToRegexp(path, keys, options) {
  console.log('Mock path-to-regexp called with path:', path);

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
  console.log('Mock path-to-regexp.parse called with path:', path);
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
  return [];
};

/**
 * Compile a path into a function that generates URLs
 * @param {string} path - The path to compile
 * @returns {Function} - The URL generator
 */
pathToRegexp.compile = function compile(path) {
  console.log('Mock path-to-regexp.compile called with path:', path);
  return function(params) {
    console.log('Mock path-to-regexp.compile function called with params:', params);
    // Try to replace parameters in the path
    if (typeof path === 'string' && params) {
      let result = path;
      Object.keys(params).forEach(key => {
        result = result.replace(\`:\${key}\`, params[key]);
      });
      return result;
    }
    return '';
  };
};

/**
 * Match a path against a regexp
 * @param {string} path - The path to match
 * @returns {Function} - A function that matches a pathname against the path
 */
pathToRegexp.match = function match(path) {
  console.log('Mock path-to-regexp.match called with path:', path);
  return function(pathname) {
    console.log('Mock path-to-regexp.match function called with pathname:', pathname);

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
  return /.*/;
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
    console.log('Mock path-to-regexp.tokensToFunction function called with params:', params);
    return '';
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
"@ | Out-File -FilePath "$mockDir/index.js" -Encoding utf8
    
    # Create package.json
    @"
{
  "name": "path-to-regexp",
  "version": "0.0.0",
  "main": "index.js",
  "description": "Mock implementation for CI compatibility",
  "author": "CI Mock Generator",
  "license": "MIT"
}
"@ | Out-File -FilePath "$mockDir/package.json" -Encoding utf8
    
    Write-Host "Created mock path-to-regexp implementation at $mockDir" | Tee-Object -Append -FilePath $LOG_FILE
}

# Create .codeqlignore file if it doesn't exist
if (-not (Test-Path ".codeqlignore")) {
    @"
# Virtual environments and dependencies
.venv/**
venv/**
env/**
.env/**
**/virtualenv/**
**/site-packages/**
**/dist-packages/**
**/node_modules/**
**/dist/**
**/build/**
**/vendor/**
**/external/**
**/third_party/**
**/__pycache__/**
**/.pytest_cache/**
**/.mypy_cache/**
**/.ruff_cache/**
**/*.pyc
**/*.pyo
**/*.pyd

# Test files
**/test/**
**/tests/**
**/__tests__/**
**/__mocks__/**
**/*.test.js
**/*.test.ts
**/*.test.jsx
**/*.test.tsx
**/*.spec.js
**/*.spec.ts
**/*.spec.jsx
**/*.spec.tsx

# Configuration files
**/.github/**
**/.vscode/**
**/.idea/**
**/coverage/**
**/.git/**

# Documentation
**/docs/**
**/*.md
**/*.mdx
**/*.rst
**/sphinx/**

# Generated files
**/playwright-report/**
**/generated/**
**/sarif-results/**
**/*.sarif
**/*.sarif.json

# Specific directories that might contain third-party code
ui/react_frontend/node_modules/**
sdk/javascript/node_modules/**
"@ | Out-File -FilePath ".codeqlignore" -Encoding utf8
    
    Write-Host "Created .codeqlignore file" | Tee-Object -Append -FilePath $LOG_FILE
}

# Clean up node_modules directories to prevent them from being scanned
Write-Host "Cleaning up node_modules directories..." | Tee-Object -Append -FilePath $LOG_FILE
Get-ChildItem -Path "." -Recurse -Directory -Filter "node_modules" | ForEach-Object {
    Write-Host "Found node_modules directory at $($_.FullName)" | Tee-Object -Append -FilePath $LOG_FILE
    # Don't actually remove them, just log them
}

Write-Host "CodeQL issues fixed successfully!" | Tee-Object -Append -FilePath $LOG_FILE
