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
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Mock data
const mockAgent = {
  id: 1,
  name: 'Test Agent',
  description: 'This is a test agent for e2e testing'
};

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.get('/api/agent', (req, res) => {
  res.json(mockAgent);
});

app.post('/api/agent/action', (req, res) => {
  const action = req.body;
  console.log('Received action:', action);
  res.json({ status: 'success', action_id: 123 });
});

// Start server
const server = app.listen(PORT, () => {
  console.log(`Mock API server running on port ${PORT}`);
});

// Export server for testing
module.exports = server;