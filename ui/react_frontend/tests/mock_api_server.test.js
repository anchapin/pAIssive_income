/**
 * Tests for the mock API server
 * 
 * This file contains tests to verify that the mock API server is working correctly.
 * It's used to ensure that the server provides the expected responses for the E2E tests.
 */

const http = require('http');

// Import the server
const server = require('./mock_api_server');

// Helper function to make HTTP requests
function makeRequest(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          resolve({
            statusCode: res.statusCode,
            headers: res.headers,
            body: JSON.parse(data)
          });
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', (err) => {
      reject(err);
    });
  });
}

// Tests
async function runTests() {
  console.log('Running mock API server tests...');
  
  try {
    // Test health endpoint
    const healthResponse = await makeRequest('http://localhost:8000/health');
    console.log('Health endpoint:', healthResponse.statusCode === 200 ? 'PASS' : 'FAIL');
    
    // Test agent endpoint
    const agentResponse = await makeRequest('http://localhost:8000/api/agent');
    console.log('Agent endpoint:', 
      agentResponse.statusCode === 200 && agentResponse.body.name === 'Test Agent' ? 'PASS' : 'FAIL');
    
    // Test status endpoint
    const statusResponse = await makeRequest('http://localhost:8000/api/status');
    console.log('Status endpoint:', 
      statusResponse.statusCode === 200 && statusResponse.body.status === 'running' ? 'PASS' : 'FAIL');
    
    console.log('All tests completed.');
  } catch (error) {
    console.error('Error running tests:', error);
  } finally {
    // Close the server
    server.close();
  }
}

// Run the tests
runTests();
