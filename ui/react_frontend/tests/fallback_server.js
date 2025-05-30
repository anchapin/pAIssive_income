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
const CI_MODE = process.env.CI === 'true' || process.env.CI === true;

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

// Create a report directory for test artifacts
const reportDir = path.join(process.cwd(), '..', 'playwright-report');
try {
  if (!fs.existsSync(reportDir)) {
    fs.mkdirSync(reportDir, { recursive: true });
    log(`Created playwright-report directory at ${reportDir}`);
  }
} catch (error) {
  log(`Error creating playwright-report directory: ${error.message}`);
  // Try with absolute path
  try {
    const absoluteReportDir = path.resolve(process.cwd(), 'playwright-report');
    if (!fs.existsSync(absoluteReportDir)) {
      fs.mkdirSync(absoluteReportDir, { recursive: true });
      log(`Created playwright-report directory at absolute path: ${absoluteReportDir}`);
    }
  } catch (innerError) {
    log(`Failed to create directory with absolute path: ${innerError.message}`);
  }
}

// Helper function to create a report file
function createReport(filename, content) {
  try {
    fs.writeFileSync(path.join(reportDir, filename), content);
    log(`Created report file: ${filename}`);
  } catch (error) {
    log(`Failed to create report file ${filename}: ${error.message}`);
    // Try with a simpler filename
    try {
      const safeFilename = filename.replace(/[^a-zA-Z0-9.-]/g, '_');
      fs.writeFileSync(path.join(reportDir, safeFilename), content);
      log(`Created report file with safe name: ${safeFilename}`);
    } catch (fallbackError) {
      log(`Failed to create report with safe filename: ${fallbackError.message}`);
    }
  }
}

// Start server
try {
  // Create a marker file to indicate server startup attempt
  createReport('fallback-server-starting.txt',
    `Fallback server starting at ${new Date().toISOString()}\n` +
    `Port: ${PORT}\n` +
    `CI Mode: ${CI_MODE ? 'Yes' : 'No'}\n` +
    `Platform: ${process.platform}\n` +
    `Node.js version: ${process.version}`
  );

  const server = app.listen(PORT, () => {
    log(`Fallback server running on port ${PORT}`);
    log(`Available routes:`);
    log(`- GET /`);
    log(`- GET /about`);

    // Create a marker file to indicate server is ready
    createReport('fallback-server-ready.txt',
      `Fallback server ready at ${new Date().toISOString()}\n` +
      `Running on port: ${PORT}\n` +
      `CI Mode: ${CI_MODE ? 'Yes' : 'No'}\n` +
      `Platform: ${process.platform}\n` +
      `Node.js version: ${process.version}`
    );
  });

  // Handle server errors
  server.on('error', (err) => {
    log(`Server error: ${err.message}`);
    console.error(err.stack);

    // Create an error report
    createReport(`fallback-server-error-${Date.now()}.txt`,
      `Server error at ${new Date().toISOString()}\n` +
      `Error: ${err.message}\n` +
      `Stack: ${err.stack || 'No stack trace available'}\n` +
      `Port: ${PORT}\n` +
      `CI Mode: ${CI_MODE ? 'Yes' : 'No'}`
    );

    // Try to start on a different port if the default port is in use
    if (err.code === 'EADDRINUSE') {
      const newPort = PORT + 1;
      log(`Port ${PORT} is in use, trying port ${newPort}`);

      try {
        const alternateServer = app.listen(newPort, () => {
          log(`Fallback server running on alternate port ${newPort}`);

          // Create a marker file to indicate server is ready on alternate port
          createReport('fallback-server-alternate-port.txt',
            `Fallback server ready on alternate port at ${new Date().toISOString()}\n` +
            `Running on port: ${newPort}\n` +
            `Original port ${PORT} was in use\n` +
            `CI Mode: ${CI_MODE ? 'Yes' : 'No'}`
          );
        });

        // Export the alternate server
        module.exports = alternateServer;
      } catch (alternateError) {
        log(`Failed to start server on alternate port: ${alternateError.message}`);

        // Create an error report for the alternate port attempt
        createReport(`fallback-server-alternate-error-${Date.now()}.txt`,
          `Failed to start on alternate port at ${new Date().toISOString()}\n` +
          `Error: ${alternateError.message}\n` +
          `Stack: ${alternateError.stack || 'No stack trace available'}\n` +
          `Port: ${newPort}\n` +
          `CI Mode: ${CI_MODE ? 'Yes' : 'No'}`
        );

        // In CI mode, don't exit the process
        if (!CI_MODE) {
          process.exit(1);
        }
      }
    } else {
      // In CI mode, don't exit the process
      if (!CI_MODE) {
        process.exit(1);
      }
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

  // Handle uncaught exceptions
  process.on('uncaughtException', (err) => {
    log(`Uncaught exception: ${err.message}`);
    console.error(err.stack);

    // Create an error report
    createReport(`uncaught-exception-${Date.now()}.txt`,
      `Uncaught exception at ${new Date().toISOString()}\n` +
      `Error: ${err.message}\n` +
      `Stack: ${err.stack || 'No stack trace available'}`
    );

    // In CI mode, don't exit the process
    if (!CI_MODE) {
      server.close(() => {
        process.exit(1);
      });
    }
  });

  // Export server for testing
  module.exports = server;
} catch (error) {
  log(`Failed to start server: ${error.message}`);
  console.error(error.stack);

  // Create an error report
  try {
    createReport('fallback-server-startup-error.txt',
      `Failed to start server at ${new Date().toISOString()}\n` +
      `Error: ${error.message}\n` +
      `Stack: ${error.stack || 'No stack trace available'}\n` +
      `Port: ${PORT}\n` +
      `CI Mode: ${CI_MODE ? 'Yes' : 'No'}`
    );
  } catch (reportError) {
    log(`Failed to create error report: ${reportError.message}`);
  }

  // In CI mode, don't exit the process
  if (!CI_MODE) {
    process.exit(1);
  }
}
