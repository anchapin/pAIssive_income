/**
 * Ultra-simple HTTP server without any external dependencies
 * Avoids path-to-regexp and Express entirely
 */

const http = require('http');
const url = require('url');

const PORT = process.env.MOCK_API_PORT || process.env.PORT || 3001;

const server = http.createServer((req, res) => {
  const urlParts = url.parse(req.url, true);
  const pathname = urlParts.pathname;
  
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Content-Type', 'application/json');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  console.log(`${req.method} ${pathname}`);
  
  if (pathname === '/health') {
    res.writeHead(200);
    res.end(JSON.stringify({ status: 'healthy', timestamp: new Date().toISOString() }));
  } else if (pathname === '/api/status') {
    res.writeHead(200);
    res.end(JSON.stringify({ 
      server: 'simple-mock', 
      uptime: process.uptime(),
      timestamp: new Date().toISOString() 
    }));
  } else {
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not found' }));
  }
});

server.listen(PORT, () => {
  console.log(`Simple mock server running on port ${PORT}`);
});

process.on('SIGTERM', () => {
  console.log('Shutting down simple mock server');
  server.close();
});