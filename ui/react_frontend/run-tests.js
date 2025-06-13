/**
 * Automated Test Runner
 * 
 * This script automatically:
 * 1. Starts the Flask backend server
 * 2. Starts the React frontend development server
 * 3. Runs the frontend tests
 * 4. Shuts down all servers when done
 * 
 * Usage:
 *   node run-tests.js [test-file-path]
 * 
 * Example:
 *   node run-tests.js tests/e2e/simple.spec.ts
 *   node run-tests.js tests/e2e/agent_ui.spec.ts
 *   node run-tests.js (runs all tests)
 */

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

// Configuration
const config = {
  flaskPort: 5000,
  reactPort: 3000,
  startupTimeout: 30000, // 30 seconds
  shutdownTimeout: 10000, // 10 seconds
  testTimeout: 120000, // 2 minutes
  projectRoot: path.resolve(__dirname, '../..'),
  frontendRoot: __dirname,
  logDir: path.join(__dirname, 'logs'),
  testArgs: process.argv.slice(2)
};

// Ensure log directory exists
if (!fs.existsSync(config.logDir)) {
  fs.mkdirSync(config.logDir, { recursive: true });
}

// Create log files
const logFile = path.join(config.logDir, `test-run-${Date.now()}.log`);
const logStream = fs.createWriteStream(logFile, { flags: 'a' });

// Store process references for cleanup
const processes = {
  flask: null,
  react: null
};

// Helper to log messages
function log(message, level = 'info') {
  const timestamp = new Date().toISOString();
  const formattedMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
  console.log(formattedMessage);
  logStream.write(formattedMessage + '\n');
}

// Helper to check if a port is in use
function isPortInUse(port) {
  try {
    // Different command based on OS
    if (os.platform() === 'win32') {
      const result = execSync(`netstat -ano | findstr :${port}`).toString();
      return result.length > 0;
    } else {
      const result = execSync(`lsof -i:${port}`).toString();
      return result.length > 0;
    }
  } catch (error) {
    // If the command fails, the port is likely not in use
    return false;
  }
}

// Helper to kill a process by port
function killProcessOnPort(port) {
  try {
    if (os.platform() === 'win32') {
      const result = execSync(`netstat -ano | findstr :${port}`).toString();
      const lines = result.split('\n');
      for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        if (parts.length > 4) {
          const pid = parts[4];
          if (pid && !isNaN(parseInt(pid))) {
            log(`Killing process with PID ${pid} on port ${port}`);
            execSync(`taskkill /F /PID ${pid}`);
          }
        }
      }
    } else {
      const pid = execSync(`lsof -t -i:${port}`).toString().trim();
      if (pid) {
        log(`Killing process with PID ${pid} on port ${port}`);
        execSync(`kill -9 ${pid}`);
      }
    }
  } catch (error) {
    log(`No process found on port ${port} or error killing process: ${error.message}`, 'warn');
  }
}

// Start Flask backend server
function startFlaskServer() {
  return new Promise((resolve, reject) => {
    log('Starting Flask backend server...');
    
    // Check if port is already in use
    if (isPortInUse(config.flaskPort)) {
      log(`Port ${config.flaskPort} is already in use. Attempting to kill the process...`, 'warn');
      killProcessOnPort(config.flaskPort);
    }
    
    // Determine Python executable (python or python3)
    const pythonCmd = os.platform() === 'win32' ? 'python' : 'python3';
    
    // Start Flask server
    const flaskProcess = spawn(pythonCmd, ['-m', 'flask', 'run'], {
      cwd: config.projectRoot,
      env: { ...process.env, FLASK_APP: 'app.py', FLASK_ENV: 'development' },
      shell: true
    });
    
    processes.flask = flaskProcess;
    
    // Set up timeout for server startup
    const timeout = setTimeout(() => {
      log('Flask server startup timed out', 'error');
      reject(new Error('Flask server startup timed out'));
    }, config.startupTimeout);
    
    // Handle server output
    flaskProcess.stdout.on('data', (data) => {
      const output = data.toString();
      log(`Flask: ${output.trim()}`);
      
      // Check if server is running
      if (output.includes('Running on') || output.includes('Debugger PIN')) {
        clearTimeout(timeout);
        log('Flask server started successfully');
        resolve(flaskProcess);
      }
    });
    
    flaskProcess.stderr.on('data', (data) => {
      log(`Flask error: ${data.toString().trim()}`, 'error');
    });
    
    flaskProcess.on('error', (error) => {
      clearTimeout(timeout);
      log(`Failed to start Flask server: ${error.message}`, 'error');
      reject(error);
    });
    
    flaskProcess.on('close', (code) => {
      if (code !== 0) {
        clearTimeout(timeout);
        log(`Flask server exited with code ${code}`, 'error');
        reject(new Error(`Flask server exited with code ${code}`));
      }
    });
  });
}

// Start React frontend server
function startReactServer() {
  return new Promise((resolve, reject) => {
    log('Starting React frontend server...');
    
    // Check if port is already in use
    if (isPortInUse(config.reactPort)) {
      log(`Port ${config.reactPort} is already in use. Attempting to kill the process...`, 'warn');
      killProcessOnPort(config.reactPort);
    }
    
    // Start React server
    const reactProcess = spawn('npm', ['start'], {
      cwd: config.frontendRoot,
      env: { ...process.env, BROWSER: 'none' }, // Prevent browser from opening
      shell: true
    });
    
    processes.react = reactProcess;
    
    // Set up timeout for server startup
    const timeout = setTimeout(() => {
      log('React server startup timed out', 'error');
      reject(new Error('React server startup timed out'));
    }, config.startupTimeout);
    
    // Handle server output
    reactProcess.stdout.on('data', (data) => {
      const output = data.toString();
      log(`React: ${output.trim()}`);
      
      // Check if server is running
      if (output.includes('Compiled successfully') || 
          output.includes('You can now view') || 
          output.includes('Local:') ||
          output.includes('localhost:3000')) {
        clearTimeout(timeout);
        log('React server started successfully');
        resolve(reactProcess);
      }
    });
    
    reactProcess.stderr.on('data', (data) => {
      log(`React error: ${data.toString().trim()}`, 'error');
    });
    
    reactProcess.on('error', (error) => {
      clearTimeout(timeout);
      log(`Failed to start React server: ${error.message}`, 'error');
      reject(error);
    });
    
    reactProcess.on('close', (code) => {
      if (code !== 0) {
        clearTimeout(timeout);
        log(`React server exited with code ${code}`, 'error');
        reject(new Error(`React server exited with code ${code}`));
      }
    });
  });
}

// Run Playwright tests
function runTests() {
  return new Promise((resolve, reject) => {
    log('Running frontend tests...');
    
    // Determine test command
    const testArgs = ['npx', 'playwright', 'test'];
    
    // Add specific test file if provided
    if (config.testArgs.length > 0) {
      testArgs.push(...config.testArgs);
    }
    
    log(`Running command: ${testArgs.join(' ')}`);
    
    // Run tests
    const testProcess = spawn(testArgs.join(' '), {
      cwd: config.frontendRoot,
      shell: true,
      stdio: 'inherit' // Show test output directly in console
    });
    
    // Set up timeout for tests
    const timeout = setTimeout(() => {
      log('Tests timed out', 'error');
      testProcess.kill();
      reject(new Error('Tests timed out'));
    }, config.testTimeout);
    
    testProcess.on('error', (error) => {
      clearTimeout(timeout);
      log(`Failed to run tests: ${error.message}`, 'error');
      reject(error);
    });
    
    testProcess.on('close', (code) => {
      clearTimeout(timeout);
      if (code === 0) {
        log('Tests completed successfully');
        resolve();
      } else {
        log(`Tests failed with code ${code}`, 'error');
        reject(new Error(`Tests failed with code ${code}`));
      }
    });
  });
}

// Cleanup function to shut down all processes
function cleanup() {
  log('Cleaning up processes...');
  
  return new Promise((resolve) => {
    // Shutdown timeout to force kill if graceful shutdown fails
    const shutdownTimeout = setTimeout(() => {
      log('Graceful shutdown timed out, force killing processes', 'warn');
      
      if (processes.flask && !processes.flask.killed) {
        processes.flask.kill('SIGKILL');
      }
      
      if (processes.react && !processes.react.killed) {
        processes.react.kill('SIGKILL');
      }
      
      resolve();
    }, config.shutdownTimeout);
    
    // Try to kill Flask server
    if (processes.flask) {
      processes.flask.kill();
      log('Sent kill signal to Flask server');
    }
    
    // Try to kill React server
    if (processes.react) {
      processes.react.kill();
      log('Sent kill signal to React server');
    }
    
    // Also try to kill by port
    killProcessOnPort(config.flaskPort);
    killProcessOnPort(config.reactPort);
    
    // Clear timeout if both processes are confirmed dead
    const checkInterval = setInterval(() => {
      const flaskDead = !processes.flask || processes.flask.killed;
      const reactDead = !processes.react || processes.react.killed;
      
      if (flaskDead && reactDead) {
        clearInterval(checkInterval);
        clearTimeout(shutdownTimeout);
        log('All processes successfully terminated');
        resolve();
      }
    }, 500);
  });
}

// Main function
async function main() {
  log('=== Automated Test Runner Started ===');
  log(`Test arguments: ${config.testArgs.length ? config.testArgs.join(' ') : 'Running all tests'}`);
  
  try {
    // Start servers
    await startFlaskServer();
    await startReactServer();
    
    // Wait a bit for servers to stabilize
    log('Waiting for servers to stabilize...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Run tests
    await runTests();
    
    log('=== All tests completed successfully ===');
  } catch (error) {
    log(`Error: ${error.message}`, 'error');
    log('=== Tests failed or servers could not start ===', 'error');
  } finally {
    // Always clean up
    await cleanup();
    log('=== Automated Test Runner Finished ===');
    logStream.end();
  }
}

// Handle process termination
process.on('SIGINT', async () => {
  log('Received SIGINT signal, shutting down...', 'warn');
  await cleanup();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  log('Received SIGTERM signal, shutting down...', 'warn');
  await cleanup();
  process.exit(0);
});

// Start the main process
main();
