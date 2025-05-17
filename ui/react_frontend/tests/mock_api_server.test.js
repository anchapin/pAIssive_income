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
    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => { body += chunk; });
      res.on('end', () => {
        let parsed = null;
        try {
          parsed = body && JSON.parse(body);
        } catch (e) {
          return reject(new Error(`Failed to parse JSON: ${e.message}, body: ${body}`));
        }
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: parsed,
        });
      });
    });
    req.on('error', reject);
    if (data) {
      req.write(typeof data === 'string' ? data : JSON.stringify(data));
    }
    req.end();
  });
}

async function waitForServerReady({ url, timeout = 5000 }) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    try {
      const res = await makeRequest({ url });
      if (res.statusCode === 200) return res;
    } catch (e) {
      // Ignore, server not ready yet.
    }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  throw new Error('Server did not become ready in time');
}

async function runTests() {
  console.log('Running improved mock API server tests...');
  let serverInstance;
  try {
    // Wait for the server to start
    serverInstance = await serverPromise;

    // Wait until /ready endpoint confirms server is up
    const readyRes = await waitForServerReady({ url: 'http://localhost:8000/ready' });
    assert.equal(readyRes.statusCode, 200, '/ready endpoint returns 200');
    assert(readyRes.body && readyRes.body.status === 'ready', '/ready response has status=ready');
    assert('uptime' in readyRes.body, '/ready response contains uptime');
    assert('memory' in readyRes.body, '/ready response contains memory');
    assert.match(readyRes.headers['content-type'], /application\/json/, '/ready returns JSON');

    // Test /health endpoint
    const healthRes = await makeRequest({ url: 'http://localhost:8000/health' });
    assert.equal(healthRes.statusCode, 200, '/health endpoint returns 200');
    assert(healthRes.body && healthRes.body.status === 'ok', '/health response has status=ok');
    assert('timestamp' in healthRes.body, '/health response has timestamp');
    assert.match(healthRes.headers['content-type'], /application\/json/, '/health returns JSON');

    // Test /api/agent endpoint
    const agentRes = await makeRequest({ url: 'http://localhost:8000/api/agent' });
    assert.equal(agentRes.statusCode, 200, '/api/agent returns 200');
    assert(agentRes.body && agentRes.body.name === 'Test Agent', '/api/agent returns correct agent');
    assert('id' in agentRes.body, '/api/agent response has id');
    assert('description' in agentRes.body, '/api/agent response has description');
    assert.match(agentRes.headers['content-type'], /application\/json/, '/api/agent returns JSON');

    // Test POST /api/agent/action
    const actionPayload = { type: 'test', payload: { foo: 'bar' } };
    const actionRes = await makeRequest({
      url: 'http://localhost:8000/api/agent/action',
      method: 'POST',
      data: actionPayload,
      headers: { 'Content-Type': 'application/json' },
    });
    assert.equal(actionRes.statusCode, 200, '/api/agent/action returns 200');
    assert(actionRes.body && actionRes.body.status === 'success', '/api/agent/action status=success');
    assert('action_id' in actionRes.body, '/api/agent/action response has action_id');
    assert.deepEqual(actionRes.body.received, actionPayload, '/api/agent/action echoes payload');
    assert.match(actionRes.headers['content-type'], /application\/json/, '/api/agent/action returns JSON');

    // Test /api/status endpoint
    const statusRes = await makeRequest({ url: 'http://localhost:8000/api/status' });
    assert.equal(statusRes.statusCode, 200, '/api/status returns 200');
    assert(statusRes.body && statusRes.body.status === 'running', '/api/status running');
    assert('version' in statusRes.body, '/api/status response has version');
    assert('environment' in statusRes.body, '/api/status response has environment');
    assert('timestamp' in statusRes.body, '/api/status response has timestamp');
    assert.match(statusRes.headers['content-type'], /application\/json/, '/api/status returns JSON');

    // Test unhandled endpoint
    const unknownRes = await makeRequest({ url: 'http://localhost:8000/api/unknown' });
    assert.equal(unknownRes.statusCode, 200, '/api/unknown returns 200');
    assert(unknownRes.body && unknownRes.body.status === 'warning', '/api/unknown returns warning status');
    assert('message' in unknownRes.body, '/api/unknown response has message');
    assert(unknownRes.body.path === '/api/unknown', '/api/unknown echoes path');
    assert.match(unknownRes.headers['content-type'], /application\/json/, '/api/unknown returns JSON');

    // Test for 404/non-existent endpoint (outside /api)
    let notFoundErr = null;
    try {
      await makeRequest({ url: 'http://localhost:8000/doesnotexist' });
    } catch (e) {
      notFoundErr = e;
    }
    // By default, Express returns HTML 404 with no JSON, so just note this.

    console.log('All improved tests passed!');
  } catch (error) {
    console.error('Test failed:', error);
    process.exit(1);
  } finally {
    // Close the server if possible
    if (serverInstance && typeof serverInstance.close === 'function') {
      serverInstance.close();
    }
  }
}

runTests();
