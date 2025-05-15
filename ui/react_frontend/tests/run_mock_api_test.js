/**
 * Script to run the mock API server tests
 *
 * This script starts the mock API server and runs the tests against it.
 * It's used to verify that the server is working correctly before running the E2E tests.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Ensure the playwright-report directory exists
const reportDir = path.join(process.cwd(), 'playwright-report');
if (!fs.existsSync(reportDir)) {
  fs.mkdirSync(reportDir, { recursive: true });
  console.log(`Created playwright-report directory at ${reportDir}`);
}

// Start the mock API server
console.log('Starting mock API server...');
const server = spawn('node', [path.join(__dirname, 'mock_api_server.js')], {
  stdio: 'pipe',
  detached: true
});

// Log server output
server.stdout.on('data', (data) => {
  console.log(`Server: ${data}`);
});

server.stderr.on('data', (data) => {
  console.error(`Server error: ${data}`);
});

// Wait for the server to start
console.log('Waiting for server to start...');
setTimeout(() => {
  // Run the tests
  console.log('Running tests...');
  const test = spawn('node', [path.join(__dirname, 'mock_api_server.test.js')], {
    stdio: 'inherit'
  });

  test.on('close', (code) => {
    console.log(`Tests exited with code ${code}`);

    // Create a test report
    const reportPath = path.join(reportDir, 'mock-api-test-report.txt');
    fs.writeFileSync(reportPath, `Mock API server test completed at ${new Date().toISOString()}\nExit code: ${code}`);
    console.log(`Test report saved to ${reportPath}`);

    // Kill the server - use different approach for Windows vs Unix
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

    process.exit(code);
  });
}, 2000);

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
