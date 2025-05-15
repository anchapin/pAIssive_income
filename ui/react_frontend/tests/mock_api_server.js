/**
 * Mock API Server for testing
 *
 * This file provides a simple mock API server for testing purposes.
 * It can be used in the CI environment to avoid relying on the Python API server.
 */

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

// Create Express app
const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors());
app.use(express.json());

// Mock data
const mockAgent = {
  id: 1,
  name: 'Test Agent',
  description: 'This is a test agent for e2e testing'
};

// Routes
app.get('/health', (req, res) => {
  console.log('Health check request received');
  res.json({ status: 'ok' });
});

app.get('/api/agent', (req, res) => {
  console.log('GET /api/agent request received');
  res.json(mockAgent);
});

app.post('/api/agent/action', (req, res) => {
  const action = req.body;
  console.log('Received action:', action);
  res.json({ status: 'success', action_id: 123 });
});

// Additional routes for testing
app.get('/api/status', (req, res) => {
  console.log('GET /api/status request received');
  res.json({
    status: 'running',
    version: '1.0.0',
    environment: 'test'
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal Server Error' });
});

// Start server
const server = app.listen(PORT, () => {
  console.log(`Mock API server running on port ${PORT}`);
  console.log(`Available endpoints:`);
  console.log(`- GET /health`);
  console.log(`- GET /api/agent`);
  console.log(`- POST /api/agent/action`);
  console.log(`- GET /api/status`);
});

// Export server for testing
module.exports = server;
