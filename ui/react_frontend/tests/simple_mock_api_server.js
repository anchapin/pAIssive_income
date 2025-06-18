/**
 * Simple Mock API Server for testing
 * 
 * This is a simplified version that avoids path-to-regexp entirely
 */

const fs = require('fs');
const path = require('path');
const express = require('express');
const cors = require('cors');

// CI environment detection
const isCI = process.env.CI === 'true' || process.env.GITHUB_ACTIONS === 'true';
const PORT = process.env.MOCK_API_PORT || process.env.PORT || 8000;

// Create Express app with minimal setup
const app = express();

// Basic middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Create report directory
const reportDir = path.join(process.cwd(), 'playwright-report');
if (!fs.existsSync(reportDir)) {
  fs.mkdirSync(reportDir, { recursive: true });
}

// Simple logging
function log(message, level = 'info') {
  const timestamp = new Date().toISOString();
  const prefix = `[${timestamp}] [simple-mock-api] [${level.toUpperCase()}]`;
  console.log(`${prefix} ${message}`);
}

// Mock data
const mockAgent = {
  id: 1,
  name: 'Test Agent',
  description: 'This is a test agent for e2e testing'
};

// Simple routes without complex patterns
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
  log('Received action: ' + JSON.stringify(action).substring(0, 100));
  res.json({
    status: 'success',
    action_id: 123,
    timestamp: new Date().toISOString(),
    received: action
  });
});

app.get('/api/status', (req, res) => {
  log('GET /api/status request received');
  res.json({
    status: 'running',
    version: '1.0.0',
    environment: 'test',
    timestamp: new Date().toISOString()
  });
});

// Catch-all for API routes
app.all('/api/*', (req, res) => {
  // Sanitize method and path for logging to prevent log injection
  const sanitizedMethod = (req.method || '').replace(/[\r\n\t]/g, '').substring(0, 10);
  const sanitizedPath = (req.path || '').replace(/[\r\n\t]/g, '').substring(0, 100);
  log('Unhandled API request: ' + sanitizedMethod + ' ' + sanitizedPath);
  res.json({
    status: 'warning',
    message: 'Endpoint not implemented in mock server',
    path: sanitizedPath,
    method: sanitizedMethod,
    timestamp: new Date().toISOString()
  });
});

// Error handling
app.use((err, req, res, next) => {
  // Sanitize inputs for logging to prevent log injection
  const sanitizedMethod = (req.method || '').replace(/[\r\n\t]/g, '').substring(0, 10);
  const sanitizedPath = (req.path || '').replace(/[\r\n\t]/g, '').substring(0, 100);
  const sanitizedError = (err.message || '').replace(/[\r\n\t]/g, '').substring(0, 200);
  log('Error processing ' + sanitizedMethod + ' ' + sanitizedPath + ': ' + sanitizedError, 'error');
  res.status(500).json({
    status: 'error',
    message: 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

// Start server
const server = app.listen(PORT, () => {
  log(`Simple mock API server running on port ${PORT}`);
  
  // Create success marker files
  fs.writeFileSync(path.join(reportDir, 'simple-mock-api-success.txt'), 
    `Simple mock API server started successfully at ${new Date().toISOString()}\nPort: ${PORT}\n`);
  
  log('Server successfully started');
});

// Handle server shutdown
process.on('SIGTERM', () => {
  log('Received SIGTERM, shutting down gracefully');
  server.close(() => {
    log('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  log('Received SIGINT, shutting down gracefully');
  server.close(() => {
    log('Server closed');
    process.exit(0);
  });
});

module.exports = { app, server };