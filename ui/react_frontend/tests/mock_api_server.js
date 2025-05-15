/**
 * Mock API Server for testing
 *
 * This file provides a simple mock API server for testing purposes.
 * It can be used in the CI environment to avoid relying on the Python API server.
 *
 * Enhanced with better error handling and logging for CI environments.
 */

const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

// Create Express app
const app = express();
const PORT = process.env.PORT || 8000;

// Setup logging
const logDir = path.join(process.cwd(), 'logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
  console.log(`Created logs directory at ${logDir}`);
}

// Logger function
function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  console.log(logMessage.trim());

  // Also write to log file
  try {
    fs.appendFileSync(path.join(logDir, 'mock-api-server.log'), logMessage);
  } catch (error) {
    console.error(`Failed to write to log file: ${error}`);
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
  log(`Received action: ${JSON.stringify(action)}`);
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
  log(`Unhandled API request: ${req.method} ${req.url}`);
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
  log(`Error processing ${req.method} ${req.url}: ${err.message}`);
  console.error(err.stack);
  res.status(500).json({
    error: 'Internal Server Error',
    message: err.message,
    timestamp: new Date().toISOString()
  });
});

// Process error handling
process.on('uncaughtException', (err) => {
  log(`Uncaught Exception: ${err.message}`);
  console.error(err.stack);
});

process.on('unhandledRejection', (reason, promise) => {
  log(`Unhandled Rejection at: ${promise}, reason: ${reason}`);
});

// Start server
let server;
try {
  server = app.listen(PORT, () => {
    log(`Mock API server running on port ${PORT}`);
    log(`Available endpoints:`);
    log(`- GET /health`);
    log(`- GET /api/agent`);
    log(`- POST /api/agent/action`);
    log(`- GET /api/status`);
  });

  // Handle server errors
  server.on('error', (err) => {
    log(`Server error: ${err.message}`);
    console.error(err.stack);
  });
} catch (error) {
  log(`Failed to start server: ${error.message}`);
  console.error(error.stack);
  process.exit(1);
}

// Export server for testing
module.exports = server;
