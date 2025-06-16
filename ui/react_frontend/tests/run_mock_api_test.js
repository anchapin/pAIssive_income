/**
 * Script to run the mock API server tests
 *
 * This script starts the mock API server and runs the tests against it.
 * It's used to verify that the server is working correctly before running the E2E tests.
 *
 * Enhanced with improved error handling and logging for CI environments.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');

// Ensure the playwright-report directory exists
const reportDir = path.join(process.cwd(), 'playwright-report');
if (!fs.existsSync(reportDir)) {
  fs.mkdirSync(reportDir, { recursive: true });
  console.log(`Created playwright-report directory at ${reportDir}`);
}

// Ensure the logs directory exists
const logDir = path.join(process.cwd(), 'logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
  console.log(`Created logs directory at ${logDir}`);
}

// Create a test run report
const testRunReport = path.join(reportDir, 'mock-api-test-run.txt');
fs.writeFileSync(testRunReport,
  `Mock API test run started at ${new Date().toISOString()}\n` +
  `Node.js version: ${process.version}\n` +
  `Platform: ${process.platform}\n` +
  `Working directory: ${process.cwd()}\n`
);
console.log(`Created test run report at ${testRunReport}`);

// Function to check if server is ready
function checkServerReady(port, maxRetries = 15) {
  return new Promise((resolve) => {
    let retries = 0;

    function tryConnect() {
      retries++;
      console.log(`Checking if server is ready (attempt ${retries}/${maxRetries})...`);

      const req = http.request({
        hostname: 'localhost',
        port: port,
        path: '/health',
        method: 'GET',
        timeout: 2000 // Increase timeout
      }, (res) => {
        console.log(`Server responded with status code: ${res.statusCode}`);
        if (res.statusCode === 200) {
          let data = '';
          res.on('data', (chunk) => { data += chunk; });
          res.on('end', () => {
            console.log(`Server is ready on port ${port}`);
            fs.appendFileSync(testRunReport, `Server ready on port ${port} at ${new Date().toISOString()}\n`);
            resolve(true);
          });
        } else {
          if (retries < maxRetries) {
            setTimeout(tryConnect, 500);
          } else {
            console.log(`Server responded with non-200 status code after ${maxRetries} attempts`);
            fs.appendFileSync(testRunReport, `Server responded with non-200 status code after ${maxRetries} attempts\n`);
            resolve(false);
          }
        }
      });

      req.on('error', (err) => {
        console.log(`Connection attempt failed: ${err.message}`);
        if (retries < maxRetries) {
          setTimeout(tryConnect, 500);
        } else {
          console.log(`Server not ready after ${maxRetries} attempts`);
          fs.appendFileSync(testRunReport, `Server not ready after ${maxRetries} attempts: ${err.message}\n`);
          resolve(false);
        }
      });

      // Set a timeout to avoid hanging requests
      req.setTimeout(2000, () => {
        req.destroy();
        console.log(`Request timed out after 2000ms`);
        if (retries < maxRetries) {
          setTimeout(tryConnect, 500);
        } else {
          console.log(`Server not ready after ${maxRetries} attempts (timeout)`);
          fs.appendFileSync(testRunReport, `Server not ready after ${maxRetries} attempts (timeout)\n`);
          resolve(false);
        }
      });

      req.end();
    }

    tryConnect();
  });
}

// Start the mock API server
console.log('Starting mock API server...');
fs.appendFileSync(testRunReport, `Starting mock API server at ${new Date().toISOString()}\n`);

const server = spawn('node', [path.join(__dirname, 'mock_api_server.js')], {
  stdio: 'pipe',
  detached: true
});

// Create a server log file
const serverLogFile = path.join(logDir, 'mock-api-server-run.log');
const serverLogStream = fs.createWriteStream(serverLogFile, { flags: 'a' });

// Log server output
server.stdout.on('data', (data) => {
  const output = data.toString().trim();
  console.log(`Server: ${output}`);
  serverLogStream.write(`[${new Date().toISOString()}] [OUT] ${output}\n`);
});

server.stderr.on('data', (data) => {
  const output = data.toString().trim();
  console.error(`Server error: ${output}`);
  serverLogStream.write(`[${new Date().toISOString()}] [ERR] ${output}\n`);
  fs.appendFileSync(testRunReport, `Server error: ${output}\n`);
});

server.on('error', (err) => {
  console.error(`Failed to start server: ${err.message}`);
  serverLogStream.write(`[${new Date().toISOString()}] [FATAL] Failed to start server: ${err.message}\n`);
  fs.appendFileSync(testRunReport, `Failed to start server: ${err.message}\n`);
  process.exit(1);
});

// Wait for the server to start and check if it's ready
console.log('Waiting for server to start...');
fs.appendFileSync(testRunReport, `Waiting for server to start at ${new Date().toISOString()}\n`);

// Try multiple ports
async function checkServerPorts() {
  const ports = [8000, 8001, 8002, 8003, 8004];

  for (const port of ports) {
    console.log(`Checking if server is ready on port ${port}...`);
    const isReady = await checkServerReady(port);
    if (isReady) {
      console.log(`Server is ready on port ${port}, running tests...`);
      fs.appendFileSync(testRunReport, `Server is ready on port ${port} at ${new Date().toISOString()}\n`);
      runTests();
      return;
    }
  }

  // If no port is ready, try running the tests directly
  console.log('Server not ready on any port, running tests directly...');
  fs.appendFileSync(testRunReport, `Server not ready on any port, running tests directly at ${new Date().toISOString()}\n`);

  // Create a report file to indicate server check failure
  try {
    fs.writeFileSync(
      path.join(reportDir, 'server-check-failed.txt'),
      `Server not ready on any port at ${new Date().toISOString()}\n` +
      `Checked ports: ${ports.join(', ')}\n` +
      `Continuing with direct tests...`
    );
  } catch (error) {
    console.error(`Failed to create server check failure report: ${error.message}`);
  }

  runTests();
}

function runTests() {
  // Run the tests
  console.log('Running tests...');
  fs.appendFileSync(testRunReport, `Running tests at ${new Date().toISOString()}\n`);

  const test = spawn('node', [path.join(__dirname, 'mock_api_server.test.js')], {
    stdio: 'inherit'
  });

  test.on('close', (code) => {
    console.log(`Tests exited with code ${code}`);
    fs.appendFileSync(testRunReport, `Tests exited with code ${code} at ${new Date().toISOString()}\n`);

    // Create a test report
    const reportPath = path.join(reportDir, 'mock-api-test-report.txt');
    fs.writeFileSync(reportPath,
      `Mock API server test completed at ${new Date().toISOString()}\n` +
      `Exit code: ${code}\n` +
      `Server PID: ${server.pid || 'unknown'}\n`
    );
    console.log(`Test report saved to ${reportPath}`);

    // Kill the server - use different approach for Windows vs Unix
    if (server.pid) {
      try {
        console.log(`Terminating server process (PID: ${server.pid})...`);
        fs.appendFileSync(testRunReport, `Terminating server process (PID: ${server.pid}) at ${new Date().toISOString()}\n`);

        if (process.platform === 'win32') {
          // Windows-specific process termination
          require('child_process').exec(`taskkill /pid ${server.pid} /T /F`);
        } else {
          // Unix-specific process termination
          process.kill(-server.pid);
        }

        console.log('Server process terminated');
        fs.appendFileSync(testRunReport, `Server process terminated at ${new Date().toISOString()}\n`);
      } catch (error) {
        console.error(`Error killing server process: ${error}`);
        fs.appendFileSync(testRunReport, `Error killing server process: ${error.message} at ${new Date().toISOString()}\n`);
      }
    } else {
      console.log('No server PID available, cannot terminate server');
      fs.appendFileSync(testRunReport, `No server PID available, cannot terminate server at ${new Date().toISOString()}\n`);
    }

    // Close the log stream
    serverLogStream.end();

    // Exit with the same code as the test
    process.exit(code);
  });
}

// Start checking server ports after a short delay
setTimeout(checkServerPorts, 2000);

// Handle script termination
process.on('SIGINT', () => {
  if (server.pid) {
    try {
      if (process.platform === 'win32') {
        // Windows-specific process termination
        require('child_process').exec(`taskkill /pid ${server.pid} /T /F`);
      } else {
        // Unix-specific process termination
        process.kill(-server.pid);
      }
    } catch (error) {
      console.error(`Error killing server process: ${error}`);
    }
  }
  process.exit();
});
