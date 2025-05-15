/**
 * Fallback Server for E2E Testing
 * 
 * This is a simple Express server that serves a minimal HTML page
 * for E2E testing when the React development server fails to start.
 * It includes a basic implementation of the AgentUI component to
 * ensure that tests can still run.
 */

const express = require('express');
const path = require('path');
const fs = require('fs');

// Create Express app
const app = express();
const PORT = process.env.PORT || 3000;

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
    fs.appendFileSync(path.join(logDir, 'fallback-server.log'), logMessage);
  } catch (error) {
    console.error(`Failed to write to log file: ${error}`);
  }
}

// Serve static files from the public directory
app.use(express.static('public'));

// Create a public directory if it doesn't exist
if (!fs.existsSync('public')) {
  fs.mkdirSync('public', { recursive: true });
  log('Created public directory');
}

// Create a simple index.html for the root route
const indexHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>pAIssive Income Framework</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background-color: #f8f9fc;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
      color: #4e73df;
    }
    .agent-ui-container {
      margin-top: 20px;
      padding: 15px;
      border: 1px solid #4e73df;
      border-radius: 8px;
    }
    .agent-ui-component {
      background-color: white;
      padding: 15px;
      border-radius: 4px;
      border: 1px solid #007bff;
    }
    .agent-actions {
      margin-top: 15px;
    }
    button {
      padding: 8px 16px;
      margin-right: 8px;
      border-radius: 4px;
      cursor: pointer;
    }
    .primary-button {
      background-color: #007bff;
      color: white;
      border: none;
    }
    .secondary-button {
      background-color: #f5f5f5;
      color: black;
      border: 1px solid #007bff;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>pAIssive Income Framework</h1>
    <p>This is a fallback page for E2E testing.</p>
    
    <div id="root">
      <!-- React app would normally mount here -->
      <div class="agent-ui-container">
        <h2>Agent UI Integration</h2>
        <div class="agent-ui-component">
          <h3 style="color: #007bff;">Test Agent</h3>
          <div class="agent-description">This is a test agent for e2e testing</div>
          <div class="agent-actions">
            <button class="primary-button" id="help-button">Help</button>
            <button class="secondary-button" id="start-button">Start</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Simple script to handle button clicks
    document.getElementById('help-button').addEventListener('click', function() {
      console.log('Help button clicked');
      alert('Help requested');
    });
    
    document.getElementById('start-button').addEventListener('click', function() {
      console.log('Start button clicked');
      alert('Agent started');
    });
  </script>
</body>
</html>
`;

// Create the index.html file
fs.writeFileSync('public/index.html', indexHtml);
log('Created index.html file');

// Create an about page HTML
const aboutHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>About - pAIssive Income Framework</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background-color: #f8f9fc;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h6 {
      color: #4e73df;
    }
    .agent-ui-container {
      margin-top: 20px;
      padding: 15px;
      border: 1px solid #4e73df;
      border-radius: 8px;
    }
    .agent-ui-component {
      background-color: white;
      padding: 15px;
      border-radius: 4px;
      border: 1px solid #007bff;
    }
    .agent-actions {
      margin-top: 15px;
    }
    button {
      padding: 8px 16px;
      margin-right: 8px;
      border-radius: 4px;
      cursor: pointer;
    }
    .primary-button {
      background-color: #007bff;
      color: white;
      border: none;
    }
    .secondary-button {
      background-color: #f5f5f5;
      color: black;
      border: 1px solid #007bff;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>About pAIssive Income Framework</h1>
    <p>This is a fallback About page for E2E testing.</p>
    
    <div id="root">
      <!-- React app would normally mount here -->
      <div class="agent-ui-container">
        <h6>Agent UI Integration</h6>
        <div class="agent-ui-component" data-testid="agent-ui-component">
          <h3 style="color: #007bff;">Test Agent</h3>
          <div class="agent-description" data-testid="agent-description">This is a test agent for e2e testing</div>
          <div class="agent-actions">
            <button class="primary-button" id="help-button" data-testid="help-button">Help</button>
            <button class="secondary-button" id="start-button" data-testid="start-button">Start</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Simple script to handle button clicks
    document.getElementById('help-button').addEventListener('click', function() {
      console.log('Help button clicked');
      alert('Help requested');
    });
    
    document.getElementById('start-button').addEventListener('click', function() {
      console.log('Start button clicked');
      alert('Agent started');
    });
  </script>
</body>
</html>
`;

// Create the about.html file
fs.writeFileSync('public/about.html', aboutHtml);
log('Created about.html file');

// Handle all routes for SPA
app.get('/', (req, res) => {
  log('GET / request received');
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

app.get('/about', (req, res) => {
  log('GET /about request received');
  res.sendFile(path.join(__dirname, '../public/about.html'));
});

// Catch-all route for other paths
app.get('*', (req, res) => {
  log(`GET ${req.path} request received - redirecting to index.html`);
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

// Start server
try {
  const server = app.listen(PORT, () => {
    log(`Fallback server running on port ${PORT}`);
    log(`Available routes:`);
    log(`- GET /`);
    log(`- GET /about`);
  });

  // Handle server errors
  server.on('error', (err) => {
    log(`Server error: ${err.message}`);
    console.error(err.stack);
  });

  // Export server for testing
  module.exports = server;
} catch (error) {
  log(`Failed to start server: ${error.message}`);
  console.error(error.stack);
  process.exit(1);
}
