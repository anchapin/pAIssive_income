/**
 * Simple Fallback HTTP Server for Mock API in CI Environments
 * 
 * This is an ultra-simple HTTP server that can be used as a last resort
 * when the mock API server fails to start in CI environments.
 * It responds to all requests with a 200 OK and a simple JSON response.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// Create logs directory if it doesn't exist
const logDir = path.join(process.cwd(), 'logs');
try {
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
    console.log(`Created logs directory at ${logDir}`);
  }
} catch (error) {
  console.error(`Failed to create logs directory: ${error.message}`);
}

// Create a log file
const logFile = path.join(logDir, 'simple-fallback-server.log');
try {
  fs.writeFileSync(logFile, `Simple fallback server started at ${new Date().toISOString()}\n`);
  console.log(`Created log file at ${logFile}`);
} catch (error) {
  console.error(`Failed to create log file: ${error.message}`);
}

// Log function
function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  console.log(logMessage.trim());
  
  try {
    fs.appendFileSync(logFile, logMessage);
  } catch (error) {
    console.error(`Failed to write to log file: ${error.message}`);
  }
}

// Create the server
const server = http.createServer((req, res) => {
  const url = req.url;
  const method = req.method;
  
  log(`${method} ${url}`);
  
  // Set CORS headers for all responses
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  // Handle OPTIONS requests (CORS preflight)
  if (method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }
  
  // Set content type to JSON for all responses
  res.setHeader('Content-Type', 'application/json');
  
  // Handle different endpoints
  if (url === '/health' || url === '/ready') {
    // Health check endpoint
    res.writeHead(200);
    res.end(JSON.stringify({
      status: 'ok',
      timestamp: new Date().toISOString(),
      server: 'simple-fallback',
      uptime: process.uptime()
    }));
  } else if (url.startsWith('/api/v1/status') || url === '/api/status') {
    // Status endpoint
    res.writeHead(200);
    res.end(JSON.stringify({
      status: 'running',
      version: '1.0.0',
      environment: 'ci-fallback',
      timestamp: new Date().toISOString(),
      server: 'simple-fallback'
    }));
  } else if (url.startsWith('/api/v1/niches') || url === '/api/niches') {
    // Niches endpoint
    if (url.includes('/1') || url.endsWith('/1')) {
      // Single niche
      res.writeHead(200);
      res.end(JSON.stringify({
        id: 1,
        name: 'Test Niche',
        description: 'This is a test niche for CI compatibility',
        server: 'simple-fallback'
      }));
    } else {
      // All niches
      res.writeHead(200);
      res.end(JSON.stringify([
        {
          id: 1,
          name: 'Test Niche',
          description: 'This is a test niche for CI compatibility',
          server: 'simple-fallback'
        }
      ]));
    }
  } else if (url.startsWith('/api/agent')) {
    // Agent endpoint
    res.writeHead(200);
    res.end(JSON.stringify({
      id: 1,
      name: 'Test Agent',
      description: 'This is a test agent for CI compatibility',
      server: 'simple-fallback'
    }));
  } else {
    // Default response for any other endpoint
    res.writeHead(200);
    res.end(JSON.stringify({
      status: 'ok',
      message: 'Simple fallback server response',
      path: url,
      method: method,
      timestamp: new Date().toISOString(),
      server: 'simple-fallback'
    }));
  }
});

// Start the server
const PORT = process.env.PORT || 8000;
server.listen(PORT, () => {
  log(`Simple fallback server running on port ${PORT}`);
  
  // Create a marker file to indicate the server is running
  try {
    const reportDir = path.join(process.cwd(), '..', 'playwright-report');
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
    const markerFile = path.join(reportDir, 'simple-fallback-server-running.txt');
    fs.writeFileSync(markerFile, `Simple fallback server running on port ${PORT} at ${new Date().toISOString()}\n`);
    log(`Created marker file at ${markerFile}`);
  } catch (error) {
    log(`Failed to create marker file: ${error.message}`);
  }
});

// Handle server errors
server.on('error', (error) => {
  log(`Server error: ${error.message}`);
  
  // Try to start on a different port if the default port is in use
  if (error.code === 'EADDRINUSE') {
    const newPort = PORT + 1;
    log(`Port ${PORT} is in use, trying port ${newPort}`);
    
    server.listen(newPort, () => {
      log(`Simple fallback server running on port ${newPort}`);
      
      // Create a marker file to indicate the server is running on a different port
      try {
        const reportDir = path.join(process.cwd(), '..', 'playwright-report');
        if (!fs.existsSync(reportDir)) {
          fs.mkdirSync(reportDir, { recursive: true });
        }
        const markerFile = path.join(reportDir, 'simple-fallback-server-running.txt');
        fs.writeFileSync(markerFile, `Simple fallback server running on port ${newPort} at ${new Date().toISOString()}\n`);
        log(`Created marker file at ${markerFile}`);
      } catch (error) {
        log(`Failed to create marker file: ${error.message}`);
      }
    });
  }
});

// Handle process termination
process.on('SIGINT', () => {
  log('Received SIGINT signal, shutting down server');
  server.close(() => {
    log('Server closed gracefully');
    process.exit(0);
  });
});

process.on('SIGTERM', () => {
  log('Received SIGTERM signal, shutting down server');
  server.close(() => {
    log('Server closed gracefully');
    process.exit(0);
  });
});
