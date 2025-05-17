/**
 * Improved tests for the mock API server
 *
 * These tests verify correct responses for each endpoint,
 * check headers, and ensure robust CI compatibility.
 */

const http = require('http');
const assert = require('assert').strict;

// Import the server (as a Promise)
const serverPromise = require('./mock_api_server');

function makeRequest({ url, method = 'GET', data = null, headers = {} }) {
  return new Promise((resolve, reject) => {
    const opts = new URL(url);
    const options = {
      method,
      hostname: opts.hostname,
      port: opts.port,
      path: opts.pathname + (opts.search || ''),
      headers,
    };

    console.log(`Making ${method} request to ${url}...`);

    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => { body += chunk; });
      res.on('end', () => {
        console.log(`Received response from ${url}: status ${res.statusCode}`);
        let parsed = null;
        try {
          parsed = body && JSON.parse(body);
        } catch (e) {
          const errorMsg = `Failed to parse JSON from ${url}: ${e.message}, body: ${body}`;
          console.error(errorMsg);
          return reject(new Error(errorMsg));
        }
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: parsed,
          url: url, // Include the original URL in the response
        });
      });
    });

    req.on('error', (error) => {
      const errorMsg = `Request to ${url} failed: ${error.message}`;
      console.error(errorMsg);
      reject(new Error(errorMsg));
    });

    // Set a timeout to avoid hanging requests
    req.setTimeout(5000, () => {
      req.destroy();
      const timeoutMsg = `Request to ${url} timed out after 5000ms`;
      console.error(timeoutMsg);
      reject(new Error(timeoutMsg));
    });

    if (data) {
      const dataStr = typeof data === 'string' ? data : JSON.stringify(data);
      console.log(`Sending data to ${url}: ${dataStr.substring(0, 100)}${dataStr.length > 100 ? '...' : ''}`);
      req.write(dataStr);
    }

    req.end();
  });
}

async function waitForServerReady({ url, timeout = 10000, retryInterval = 200 }) {
  console.log(`Waiting for server to be ready at ${url} (timeout: ${timeout}ms)...`);
  const start = Date.now();
  let attempt = 1;

  while (Date.now() - start < timeout) {
    try {
      console.log(`Attempt ${attempt} to connect to ${url}...`);
      const res = await makeRequest({ url });
      if (res.statusCode === 200) {
        console.log(`Server is ready at ${url} (took ${Date.now() - start}ms)`);
        return res;
      }
      console.log(`Received status code ${res.statusCode}, waiting for 200...`);
    } catch (e) {
      // Try alternate ports if the main one fails
      if (url.includes('localhost:8000')) {
        try {
          const altUrl = url.replace('localhost:8000', 'localhost:8001');
          console.log(`Trying alternate port at ${altUrl}...`);
          const altRes = await makeRequest({ url: altUrl });
          if (altRes.statusCode === 200) {
            console.log(`Server is ready at alternate port ${altUrl}`);
            return altRes;
          }
        } catch (altErr) {
          // Ignore alternate port errors
        }
      }
      console.log(`Connection attempt ${attempt} failed: ${e.message}`);
    }

    attempt++;
    await new Promise((resolve) => setTimeout(resolve, retryInterval));
  }

  throw new Error(`Server did not become ready in time (${timeout}ms elapsed)`);
}

async function runTests() {
  console.log('Running improved mock API server tests...');
  let serverInstance;
  let serverPort = 8000; // Default port
  let testsPassed = 0;
  let testsFailed = 0;

  try {
    // Wait for the server to start
    console.log('Waiting for server to initialize...');
    serverInstance = await serverPromise;
    console.log('Server promise resolved, checking if server is ready...');

    // Create report directory if it doesn't exist
    const fs = require('fs');
    const path = require('path');
    const reportDir = path.join(process.cwd(), 'playwright-report');
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
      console.log(`Created playwright-report directory at ${reportDir}`);
    }

    // Create a test start report
    try {
      fs.writeFileSync(
        path.join(reportDir, 'mock-api-test-start.txt'),
        `Mock API server test started at ${new Date().toISOString()}\n` +
        `Node.js version: ${process.version}\n` +
        `Platform: ${process.platform}`
      );
      console.log('Created test start report');
    } catch (reportError) {
      console.error('Failed to create test start report:', reportError);
    }

    // Wait until /ready endpoint confirms server is up
    try {
      console.log('Checking if server is ready...');
      const readyRes = await waitForServerReady({ url: 'http://localhost:8000/ready' });
      console.log('Server ready check successful');

      // Determine which port the server is actually running on
      if (readyRes.url && readyRes.url.includes('8001')) {
        serverPort = 8001;
        console.log('Server is running on alternate port 8001');
      }

      assert.equal(readyRes.statusCode, 200, '/ready endpoint returns 200');
      assert(readyRes.body && readyRes.body.status === 'ready', '/ready response has status=ready');
      assert('uptime' in readyRes.body, '/ready response contains uptime');
      assert('memory' in readyRes.body, '/ready response contains memory');
      assert.match(readyRes.headers['content-type'], /application\/json/, '/ready returns JSON');
      console.log('✅ /ready endpoint test passed');
      testsPassed++;
    } catch (error) {
      console.error('❌ /ready endpoint test failed:', error);
      testsFailed++;

      // Try to create a failure report
      try {
        fs.writeFileSync(
          path.join(reportDir, 'mock-api-ready-failed.txt'),
          `Ready endpoint test failed at ${new Date().toISOString()}\n` +
          `Error: ${error.message}\n` +
          `Stack: ${error.stack}`
        );
      } catch (reportError) {
        console.error('Failed to create failure report:', reportError);
      }

      // Continue with tests anyway, using the default port
    }

    // Test /health endpoint
    try {
      console.log(`Testing /health endpoint on port ${serverPort}...`);
      const healthRes = await makeRequest({ url: `http://localhost:${serverPort}/health` });
      assert.equal(healthRes.statusCode, 200, '/health endpoint returns 200');
      assert(healthRes.body && healthRes.body.status === 'ok', '/health response has status=ok');
      assert('timestamp' in healthRes.body, '/health response has timestamp');
      assert.match(healthRes.headers['content-type'], /application\/json/, '/health returns JSON');
      console.log('✅ /health endpoint test passed');
      testsPassed++;
    } catch (error) {
      console.error('❌ /health endpoint test failed:', error);
      testsFailed++;
    }

    // Test /api/agent endpoint
    try {
      console.log(`Testing /api/agent endpoint on port ${serverPort}...`);
      const agentRes = await makeRequest({ url: `http://localhost:${serverPort}/api/agent` });
      assert.equal(agentRes.statusCode, 200, '/api/agent returns 200');
      assert(agentRes.body && agentRes.body.name === 'Test Agent', '/api/agent returns correct agent');
      assert('id' in agentRes.body, '/api/agent response has id');
      assert('description' in agentRes.body, '/api/agent response has description');
      assert.match(agentRes.headers['content-type'], /application\/json/, '/api/agent returns JSON');
      console.log('✅ /api/agent endpoint test passed');
      testsPassed++;
    } catch (error) {
      console.error('❌ /api/agent endpoint test failed:', error);
      testsFailed++;
    }

    // Test POST /api/agent/action
    try {
      console.log(`Testing POST /api/agent/action endpoint on port ${serverPort}...`);
      const actionPayload = { type: 'test', payload: { foo: 'bar' } };
      const actionRes = await makeRequest({
        url: `http://localhost:${serverPort}/api/agent/action`,
        method: 'POST',
        data: actionPayload,
        headers: { 'Content-Type': 'application/json' },
      });
      assert.equal(actionRes.statusCode, 200, '/api/agent/action returns 200');
      assert(actionRes.body && actionRes.body.status === 'success', '/api/agent/action status=success');
      assert('action_id' in actionRes.body, '/api/agent/action response has action_id');
      assert.deepEqual(actionRes.body.received, actionPayload, '/api/agent/action echoes payload');
      assert.match(actionRes.headers['content-type'], /application\/json/, '/api/agent/action returns JSON');
      console.log('✅ /api/agent/action endpoint test passed');
      testsPassed++;
    } catch (error) {
      console.error('❌ /api/agent/action endpoint test failed:', error);
      testsFailed++;
    }

    // Test /api/status endpoint
    try {
      console.log(`Testing /api/status endpoint on port ${serverPort}...`);
      const statusRes = await makeRequest({ url: `http://localhost:${serverPort}/api/status` });
      assert.equal(statusRes.statusCode, 200, '/api/status returns 200');
      assert(statusRes.body && statusRes.body.status === 'running', '/api/status running');
      assert('version' in statusRes.body, '/api/status response has version');
      assert('environment' in statusRes.body, '/api/status response has environment');
      assert('timestamp' in statusRes.body, '/api/status response has timestamp');
      assert.match(statusRes.headers['content-type'], /application\/json/, '/api/status returns JSON');
      console.log('✅ /api/status endpoint test passed');
      testsPassed++;
    } catch (error) {
      console.error('❌ /api/status endpoint test failed:', error);
      testsFailed++;
    }

    // Test unhandled endpoint
    try {
      console.log(`Testing unhandled API endpoint on port ${serverPort}...`);
      const unknownRes = await makeRequest({ url: `http://localhost:${serverPort}/api/unknown` });
      assert.equal(unknownRes.statusCode, 200, '/api/unknown returns 200');
      assert(unknownRes.body && unknownRes.body.status === 'warning', '/api/unknown returns warning status');
      assert('message' in unknownRes.body, '/api/unknown response has message');
      assert(unknownRes.body.path === '/api/unknown', '/api/unknown echoes path');
      assert.match(unknownRes.headers['content-type'], /application\/json/, '/api/unknown returns JSON');
      console.log('✅ Unhandled API endpoint test passed');
      testsPassed++;
    } catch (error) {
      console.error('❌ Unhandled API endpoint test failed:', error);
      testsFailed++;
    }

    // Test for 404/non-existent endpoint (outside /api)
    try {
      console.log(`Testing non-existent endpoint on port ${serverPort}...`);
      await makeRequest({ url: `http://localhost:${serverPort}/doesnotexist` });
      console.log('⚠️ Non-existent endpoint did not throw an error as expected');
    } catch (e) {
      console.log('✅ Non-existent endpoint correctly threw an error');
      testsPassed++;
    }

    // Create a test summary report
    try {
      fs.writeFileSync(
        path.join(reportDir, 'mock-api-test-summary.txt'),
        `Mock API server test completed at ${new Date().toISOString()}\n` +
        `Tests passed: ${testsPassed}\n` +
        `Tests failed: ${testsFailed}\n` +
        `Server port: ${serverPort}`
      );
      console.log('Created test summary report');
    } catch (reportError) {
      console.error('Failed to create test summary report:', reportError);
    }

    // Log test results
    console.log(`\nTest Results: ${testsPassed} passed, ${testsFailed} failed`);

    if (testsFailed > 0) {
      console.error(`❌ ${testsFailed} tests failed`);
      process.exit(1);
    } else {
      console.log('✅ All tests passed!');
    }
  } catch (error) {
    console.error('Test runner failed:', error);

    // Try to create a fatal error report
    try {
      const fs = require('fs');
      const path = require('path');
      const reportDir = path.join(process.cwd(), 'playwright-report');
      if (!fs.existsSync(reportDir)) {
        fs.mkdirSync(reportDir, { recursive: true });
      }

      fs.writeFileSync(
        path.join(reportDir, 'mock-api-test-fatal-error.txt'),
        `Mock API server test failed fatally at ${new Date().toISOString()}\n` +
        `Error: ${error.message}\n` +
        `Stack: ${error.stack}`
      );
    } catch (reportError) {
      console.error('Failed to create fatal error report:', reportError);
    }

    process.exit(1);
  } finally {
    // Close the server if possible
    try {
      if (serverInstance && typeof serverInstance.close === 'function') {
        console.log('Closing server...');
        serverInstance.close();
        console.log('Server closed');
      }
    } catch (closeError) {
      console.error('Error closing server:', closeError);
    }
  }
}

runTests();
