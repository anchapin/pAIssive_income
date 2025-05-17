/**
 * Mock API Server for testing
 *
 * This file provides a simple mock API server for testing purposes.
 * It can be used in the CI environment to avoid relying on the Python API server.
 *
 * Enhanced with better error handling and logging for CI environments.
 * Improved for GitHub Actions compatibility.
 */

const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const http = require('http');

// Create Express app
const app = express();
const PORT = process.env.MOCK_API_PORT || process.env.PORT || 8000;

// Create a report directory for test artifacts
const reportDir = path.join(process.cwd(), 'playwright-report');
if (!fs.existsSync(reportDir)) {
  fs.mkdirSync(reportDir, { recursive: true });
  console.log(`Created playwright-report directory at ${reportDir}`);
}

// Setup logging
const logDir = path.join(process.cwd(), 'logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
  console.log(`Created logs directory at ${logDir}`);
}

// Helper function to create a report file
function createReport(filename, content) {
  try {
    fs.writeFileSync(path.join(reportDir, filename), content);
    console.log(`Created report file: ${filename}`);
  } catch (error) {
    console.error(`Failed to create report file ${filename}: ${error}`);
  }
}

// Logger function with enhanced reporting and sanitization
function log(message, level = 'info') {
  const timestamp = new Date().toISOString();

  // Sanitize the message to prevent log injection
  const sanitizedMessage = typeof message === 'string'
    ? message.replace(/[\r\n]/g, ' ')
    : String(message).replace(/[\r\n]/g, ' ');

  const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${sanitizedMessage}\n`;

  // Log to console with appropriate method
  if (level === 'error') {
    console.error(logMessage.trim());
  } else if (level === 'warn') {
    console.warn(logMessage.trim());
  } else {
    console.log(logMessage.trim());
  }

  // Also write to log file
  try {
    fs.appendFileSync(path.join(logDir, 'mock-api-server.log'), logMessage);
  } catch (error) {
    console.error(`Failed to write to log file: ${error}`);
  }

  // For important messages, also create a report file
  if (level === 'error' || level === 'warn') {
    try {
      const reportFilename = `mock-api-${level}-${Date.now()}.txt`;
      createReport(reportFilename, `${timestamp}: ${sanitizedMessage}`);
    } catch (reportError) {
      console.error(`Failed to create report for ${level} message: ${reportError}`);
    }
  }
}

// Middleware
app.use(cors({
  origin: '*', // Allow all origins for testing
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());

// Request logging middleware
app.use((req, res, next) => {
  log(`${req.method} ${req.url}`);
  next();
});

// Mock data
const mockAgent = {
  id: 1,
  name: 'Test Agent',
  description: 'This is a test agent for e2e testing'
};

// Routes
app.get('/health', (req, res) => {
  log('Health check request received');
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.get('/api/agent', (req, res) => {
  log('GET /api/agent request received');
  res.json(mockAgent);
});

app.post('/api/agent/action', (req, res) => {
  const action = req.body;
  // Safely log the action by using a separate parameter instead of string interpolation
  log('Received action: ' + JSON.stringify(action).replace(/[\r\n]/g, ' '));
  res.json({
    status: 'success',
    action_id: 123,
    timestamp: new Date().toISOString(),
    received: action
  });
});

// Additional routes for testing
app.get('/api/status', (req, res) => {
  log('GET /api/status request received');
  res.json({
    status: 'running',
    version: '1.0.0',
    environment: 'test',
    timestamp: new Date().toISOString()
  });
});

// Catch-all route for any other API endpoints
app.all('/api/*', (req, res) => {
  // Safely log the unhandled request with sanitized URL
  const sanitizedUrl = req.url.replace(/[\r\n]/g, '');
  log(`Unhandled API request: ${req.method} ${sanitizedUrl}`);
  res.json({
    status: 'warning',
    message: 'Endpoint not implemented in mock server',
    path: req.path,
    method: req.method,
    timestamp: new Date().toISOString()
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  // Sanitize error message and URL
  const sanitizedUrl = req.url.replace(/[\r\n]/g, '');
  const sanitizedErrorMsg = err.message.replace(/[\r\n]/g, ' ');
  log(`Error processing ${req.method} ${sanitizedUrl}: ${sanitizedErrorMsg}`);
  console.error(err.stack);
  res.status(500).json({
    error: 'Internal Server Error',
    message: sanitizedErrorMsg,
    timestamp: new Date().toISOString()
  });
});

// Process error handling
process.on('uncaughtException', (err) => {
  // Sanitize error message
  const sanitizedErrorMsg = err.message.replace(/[\r\n]/g, ' ');
  log(`Uncaught Exception: ${sanitizedErrorMsg}`);
  console.error(err.stack);
});

process.on('unhandledRejection', (reason, promise) => {
  // Sanitize reason
  const sanitizedReason = String(reason).replace(/[\r\n]/g, ' ');
  const sanitizedPromise = String(promise).replace(/[\r\n]/g, ' ');
  log(`Unhandled Rejection at: ${sanitizedPromise}, reason: ${sanitizedReason}`);
});

// Add a route to check if the server is running
app.get('/ready', (req, res) => {
  log('Ready check request received');
  res.json({
    status: 'ready',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage()
  });
});

// Create a startup report
createReport('mock-api-startup.txt',
  `Mock API server starting at ${new Date().toISOString()}\n` +
  `PORT: ${PORT}\n` +
  `NODE_ENV: ${process.env.NODE_ENV || 'not set'}\n` +
  `Platform: ${process.platform}\n` +
  `Node.js version: ${process.version}`
);

// Function to check if a port is in use
function isPortInUse(port) {
  return new Promise((resolve) => {
    const server = http.createServer();
    server.once('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        resolve(true);
      } else {
        resolve(false);
      }
      server.close();
    });

    server.once('listening', () => {
      server.close();
      resolve(false);
    });

    server.listen(port);
  });
}

// Start server with port retry logic
async function startServer() {
  let currentPort = PORT;
  let maxRetries = 3;
  let server;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      // Check if port is in use
      const portInUse = await isPortInUse(currentPort);
      if (portInUse) {
        log(`Port ${currentPort} is already in use, trying another port`, 'warn');
        currentPort++;
        continue;
      }

      // Try to start the server
      server = app.listen(currentPort, () => {
        log(`Mock API server running on port ${currentPort}`);
        log(`Available endpoints:`);
        log(`- GET /health`);
        log(`- GET /ready`);
        log(`- GET /api/agent`);
        log(`- POST /api/agent/action`);
        log(`- GET /api/status`);

        // Create a server started report
        createReport('mock-api-started.txt',
          `Mock API server started successfully at ${new Date().toISOString()}\n` +
          `Running on port: ${currentPort}\n` +
          `Process ID: ${process.pid}`
        );
      });

      // Handle server errors
      server.on('error', (err) => {
        log(`Server error: ${err.message}`, 'error');
        console.error(err.stack);

        // Create an error report
        createReport('mock-api-server-error.txt',
          `Server error at ${new Date().toISOString()}\n` +
          `Error: ${err.message}\n` +
          `Stack: ${err.stack}`
        );
      });

      // Server started successfully
      return server;
    } catch (error) {
      log(`Failed to start server on port ${currentPort} (attempt ${attempt}/${maxRetries}): ${error.message}`, 'error');
      console.error(error.stack);

      // Create an error report
      createReport('mock-api-startup-error.txt',
        `Failed to start server at ${new Date().toISOString()}\n` +
        `Attempt: ${attempt}/${maxRetries}\n` +
        `Port: ${currentPort}\n` +
        `Error: ${error.message}\n` +
        `Stack: ${error.stack}`
      );

      if (attempt === maxRetries) {
        log(`All ${maxRetries} attempts to start server failed`, 'error');
        process.exit(1);
      }

      // Try next port
      currentPort++;
    }
  }
}

// Start the server and export it
const serverPromise = startServer();

// Export server for testing
module.exports = serverPromise;
