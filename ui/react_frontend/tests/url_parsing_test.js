/**
 * URL Parsing Test
 * 
 * This script tests the URL parsing functions in the mock API server.
 * It ensures that the parseUrl and generateUrl functions work correctly.
 * 
 * Usage:
 *   node tests/url_parsing_test.js
 */

const fs = require('fs');
const path = require('path');

// Configuration
const config = {
  logDir: path.join(process.cwd(), 'logs'),
  reportDir: path.join(process.cwd(), 'test-results'),
  isCI: process.env.CI === 'true' || process.env.CI === true,
  verboseLogging: process.env.VERBOSE_LOGGING === 'true' || process.env.CI === 'true'
};

// Create log directory if it doesn't exist
if (!fs.existsSync(config.logDir)) {
  fs.mkdirSync(config.logDir, { recursive: true });
}

// Create report directory if it doesn't exist
if (!fs.existsSync(config.reportDir)) {
  fs.mkdirSync(config.reportDir, { recursive: true });
}

// Logger function
function log(message, level = 'info') {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
  
  console.log(logMessage);
  
  try {
    fs.appendFileSync(
      path.join(config.logDir, 'url-parsing-test.log'),
      logMessage + '\n'
    );
  } catch (error) {
    console.error(`Failed to write to log file: ${error.message}`);
  }
}

// Create a report file
function createReport(filename, content) {
  try {
    fs.writeFileSync(
      path.join(config.reportDir, filename),
      content
    );
    log(`Created report file: ${filename}`);
  } catch (error) {
    log(`Failed to create report file ${filename}: ${error.message}`, 'error');
  }
}

// URL parsing function (copied from mock_api_server.js for testing)
function parseUrl(pattern, url) {
  try {
    // Sanitize inputs to prevent security issues
    if (typeof pattern !== 'string' || typeof url !== 'string') {
      console.warn(`Invalid inputs to parseUrl: pattern=${typeof pattern}, url=${typeof url}`);
      return { match: false, params: {} };
    }

    // Log the inputs for debugging
    if (config.verboseLogging) {
      console.log(`Parsing URL: pattern=${pattern}, url=${url}`);
    }

    // Split the pattern and URL into segments
    const patternSegments = pattern.split('/').filter(Boolean);
    const urlSegments = url.split('/').filter(Boolean);

    // If the number of segments doesn't match, it's not a match
    if (patternSegments.length !== urlSegments.length) {
      return { match: false, params: {} };
    }

    // Extract parameters from the URL
    const params = {};
    let match = true;

    for (let i = 0; i < patternSegments.length; i++) {
      const patternSegment = patternSegments[i];
      const urlSegment = urlSegments[i];

      // If the pattern segment starts with a colon, it's a parameter
      if (patternSegment.startsWith(':')) {
        const paramName = patternSegment.substring(1);
        
        // Validate the parameter name to prevent security issues
        if (/^[a-zA-Z0-9_]+$/.test(paramName)) {
          // Decode the URL segment to handle URL encoding
          try {
            params[paramName] = decodeURIComponent(urlSegment);
          } catch (decodeError) {
            // If decoding fails, use the raw segment
            params[paramName] = urlSegment;
          }
        } else {
          console.warn(`Invalid parameter name in URL pattern: ${paramName}`);
          match = false;
          break;
        }
      } else if (patternSegment !== urlSegment) {
        // If the segments don't match and it's not a parameter, it's not a match
        match = false;
        break;
      }
    }

    return { match, params };
  } catch (error) {
    console.error(`Error parsing URL: ${error.message}`);
    return { match: false, params: {} };
  }
}

// URL generation function (copied from mock_api_server.js for testing)
function generateUrl(pattern, params) {
  try {
    // Sanitize inputs to prevent security issues
    if (typeof pattern !== 'string') {
      console.warn(`Invalid pattern in generateUrl: ${typeof pattern}`);
      return '';
    }

    if (!params || typeof params !== 'object') {
      console.warn(`Invalid params in generateUrl: ${typeof params}`);
      return pattern;
    }

    // Log the inputs for debugging
    if (config.verboseLogging) {
      console.log(`Generating URL: pattern=${pattern}, params=${JSON.stringify(params)}`);
    }

    // Replace parameters in the pattern
    let result = pattern;
    Object.keys(params).forEach(key => {
      // Validate the parameter name to prevent security issues
      if (/^[a-zA-Z0-9_]+$/.test(key)) {
        // Encode the parameter value to handle special characters
        let value;
        try {
          value = encodeURIComponent(params[key]);
        } catch (encodeError) {
          // If encoding fails, use the raw value
          value = params[key];
        }

        // Replace the parameter in the pattern
        result = result.split(`:${key}`).join(value);
      } else {
        console.warn(`Invalid parameter name in generateUrl: ${key}`);
      }
    });

    return result;
  } catch (error) {
    console.error(`Error generating URL: ${error.message}`);
    return pattern;
  }
}

// Test cases for parseUrl
const parseUrlTestCases = [
  {
    name: 'Simple route',
    pattern: '/api/users',
    url: '/api/users',
    expected: { match: true, params: {} }
  },
  {
    name: 'Route with parameter',
    pattern: '/api/users/:id',
    url: '/api/users/123',
    expected: { match: true, params: { id: '123' } }
  },
  {
    name: 'Route with multiple parameters',
    pattern: '/api/users/:id/posts/:postId',
    url: '/api/users/123/posts/456',
    expected: { match: true, params: { id: '123', postId: '456' } }
  },
  {
    name: 'Route with encoded parameter',
    pattern: '/api/users/:name',
    url: '/api/users/John%20Doe',
    expected: { match: true, params: { name: 'John Doe' } }
  },
  {
    name: 'Non-matching route (different segments)',
    pattern: '/api/users/:id',
    url: '/api/posts/123',
    expected: { match: false, params: {} }
  },
  {
    name: 'Non-matching route (different length)',
    pattern: '/api/users/:id',
    url: '/api/users/123/posts',
    expected: { match: false, params: {} }
  },
  {
    name: 'Empty pattern',
    pattern: '',
    url: '/api/users',
    expected: { match: false, params: {} }
  },
  {
    name: 'Empty URL',
    pattern: '/api/users',
    url: '',
    expected: { match: false, params: {} }
  }
];

// Test cases for generateUrl
const generateUrlTestCases = [
  {
    name: 'Simple route',
    pattern: '/api/users',
    params: {},
    expected: '/api/users'
  },
  {
    name: 'Route with parameter',
    pattern: '/api/users/:id',
    params: { id: '123' },
    expected: '/api/users/123'
  },
  {
    name: 'Route with multiple parameters',
    pattern: '/api/users/:id/posts/:postId',
    params: { id: '123', postId: '456' },
    expected: '/api/users/123/posts/456'
  },
  {
    name: 'Route with parameter that needs encoding',
    pattern: '/api/users/:name',
    params: { name: 'John Doe' },
    expected: '/api/users/John%20Doe'
  },
  {
    name: 'Route with missing parameter',
    pattern: '/api/users/:id/posts/:postId',
    params: { id: '123' },
    expected: '/api/users/123/posts/:postId'
  },
  {
    name: 'Empty pattern',
    pattern: '',
    params: { id: '123' },
    expected: ''
  },
  {
    name: 'Null params',
    pattern: '/api/users/:id',
    params: null,
    expected: '/api/users/:id'
  }
];

// Run the tests
function runTests() {
  log('Starting URL parsing tests...');
  
  let parseUrlPassed = 0;
  let parseUrlFailed = 0;
  let generateUrlPassed = 0;
  let generateUrlFailed = 0;
  
  // Test parseUrl
  log('Testing parseUrl function...');
  parseUrlTestCases.forEach(testCase => {
    try {
      const result = parseUrl(testCase.pattern, testCase.url);
      
      // Check if the result matches the expected result
      const matchMatches = result.match === testCase.expected.match;
      const paramsMatch = JSON.stringify(result.params) === JSON.stringify(testCase.expected.params);
      
      if (matchMatches && paramsMatch) {
        log(`✅ [parseUrl] ${testCase.name}: PASSED`);
        parseUrlPassed++;
      } else {
        log(`❌ [parseUrl] ${testCase.name}: FAILED`, 'error');
        log(`  Expected: ${JSON.stringify(testCase.expected)}`, 'error');
        log(`  Actual: ${JSON.stringify(result)}`, 'error');
        parseUrlFailed++;
      }
    } catch (error) {
      log(`❌ [parseUrl] ${testCase.name}: ERROR - ${error.message}`, 'error');
      parseUrlFailed++;
    }
  });
  
  // Test generateUrl
  log('Testing generateUrl function...');
  generateUrlTestCases.forEach(testCase => {
    try {
      const result = generateUrl(testCase.pattern, testCase.params);
      
      if (result === testCase.expected) {
        log(`✅ [generateUrl] ${testCase.name}: PASSED`);
        generateUrlPassed++;
      } else {
        log(`❌ [generateUrl] ${testCase.name}: FAILED`, 'error');
        log(`  Expected: ${testCase.expected}`, 'error');
        log(`  Actual: ${result}`, 'error');
        generateUrlFailed++;
      }
    } catch (error) {
      log(`❌ [generateUrl] ${testCase.name}: ERROR - ${error.message}`, 'error');
      generateUrlFailed++;
    }
  });
  
  // Create a summary report
  const totalTests = parseUrlTestCases.length + generateUrlTestCases.length;
  const totalPassed = parseUrlPassed + generateUrlPassed;
  const totalFailed = parseUrlFailed + generateUrlFailed;
  
  log(`\nTest Summary:`);
  log(`parseUrl: ${parseUrlPassed} passed, ${parseUrlFailed} failed`);
  log(`generateUrl: ${generateUrlPassed} passed, ${generateUrlFailed} failed`);
  log(`Total: ${totalPassed} passed, ${totalFailed} failed (${totalTests} total)`);
  
  // Create a report file
  createReport('url-parsing-test-results.txt',
    `URL Parsing Test Results at ${new Date().toISOString()}\n\n` +
    `parseUrl: ${parseUrlPassed} passed, ${parseUrlFailed} failed\n` +
    `generateUrl: ${generateUrlPassed} passed, ${generateUrlFailed} failed\n` +
    `Total: ${totalPassed} passed, ${totalFailed} failed (${totalTests} total)\n\n` +
    `Environment:\n` +
    `CI: ${config.isCI ? 'Yes' : 'No'}\n` +
    `Node.js version: ${process.version}\n` +
    `Platform: ${process.platform}\n` +
    `Working directory: ${process.cwd()}\n`
  );
  
  // Return success if all tests passed
  return totalFailed === 0;
}

// Run the tests
const success = runTests();

// Exit with appropriate code
process.exit(success ? 0 : 1);
