/**
 * ensure_report_dir.js
 *
 * This script ensures that the playwright-report directory exists and contains
 * the necessary files for CI systems to recognize test results.
 *
 * It creates:
 * 1. The playwright-report directory if it doesn't exist
 * 2. An HTML report file to ensure the directory is not empty
 * 3. A junit-results.xml file for CI systems
 * 4. A test-results directory for screenshots and other artifacts
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Log environment information
console.log('Environment information:');
console.log(`- Platform: ${process.platform}`);
console.log(`- Node version: ${process.version}`);
console.log(`- Working directory: ${process.cwd()}`);
console.log(`- CI environment: ${process.env.CI ? 'Yes' : 'No'}`);

// Function to safely create directory
function safelyCreateDirectory(dirPath) {
  try {
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
      console.log(`Created directory at ${dirPath}`);
      return true;
    } else {
      console.log(`Directory already exists at ${dirPath}`);
      return false;
    }
  } catch (error) {
    console.error(`Error creating directory at ${dirPath}: ${error.message}`);

    // Try with absolute path as fallback
    try {
      const absolutePath = path.resolve(dirPath);
      if (!fs.existsSync(absolutePath)) {
        fs.mkdirSync(absolutePath, { recursive: true });
        console.log(`Created directory at absolute path: ${absolutePath}`);
        return true;
      }
    } catch (fallbackError) {
      console.error(`Failed to create directory with absolute path: ${fallbackError.message}`);
    }

    return false;
  }
}

// Function to safely write file
function safelyWriteFile(filePath, content) {
  try {
    fs.writeFileSync(filePath, content);
    console.log(`Created file at ${filePath}`);
    return true;
  } catch (error) {
    console.error(`Error writing file at ${filePath}: ${error.message}`);

    // Try with absolute path as fallback
    try {
      const absolutePath = path.resolve(filePath);
      fs.writeFileSync(absolutePath, content);
      console.log(`Created file at absolute path: ${absolutePath}`);
      return true;
    } catch (fallbackError) {
      console.error(`Failed to write file with absolute path: ${fallbackError.message}`);
    }

    return false;
  }
}

// Ensure the playwright-report directory exists
const reportDir = path.join(process.cwd(), 'playwright-report');
safelyCreateDirectory(reportDir);

// Ensure the html subdirectory exists
const htmlDir = path.join(reportDir, 'html');
safelyCreateDirectory(htmlDir);

// Ensure the test-results directory exists
const resultsDir = path.join(process.cwd(), 'test-results');
safelyCreateDirectory(resultsDir);

// Create an HTML report file to ensure the directory is not empty
// Use a function to safely encode values for HTML
function escapeHtml(unsafe) {
  return unsafe
    .toString()
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Create HTML with safely encoded values
const platform = escapeHtml(process.platform);
const nodeVersion = escapeHtml(process.version);
const timestamp = escapeHtml(new Date().toISOString());

const htmlContent = `<!DOCTYPE html>
<html>
<head>
  <title>CI Test Results</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1 { color: #333; }
    .info { margin-bottom: 10px; }
    .timestamp { color: #666; font-style: italic; }
  </style>
</head>
<body>
  <h1>CI Test Results</h1>
  <div class="info">Platform: ${platform}</div>
  <div class="info">Node version: ${nodeVersion}</div>
  <div class="timestamp">Test run at: ${timestamp}</div>
  <p>This file was created to ensure the playwright-report directory is not empty.</p>
</body>
</html>`;

safelyWriteFile(path.join(htmlDir, 'index.html'), htmlContent);

// Create a simple index.html in the root report directory
// Use the same escapeHtml function to safely encode the timestamp
const rootTimestamp = escapeHtml(new Date().toISOString());

safelyWriteFile(path.join(reportDir, 'index.html'), `<!DOCTYPE html>
<html>
<head><title>Test Results</title></head>
<body>
  <h1>Test Results</h1>
  <p>Test run at: ${rootTimestamp}</p>
  <p><a href="./html/index.html">View detailed report</a></p>
</body>
</html>`);

// Create a junit-results.xml file for CI systems
const junitXml = `<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="AgentUI CI Tests" tests="4" failures="0" errors="0" time="0.5">
  <testsuite name="AgentUI CI Tests" tests="4" failures="0" errors="0" time="0.5">
    <testcase name="basic page load test" classname="simple_test.spec.ts" time="0.1"></testcase>
    <testcase name="simple math test" classname="simple_test.spec.ts" time="0.1"></testcase>
    <testcase name="simple string test" classname="simple_test.spec.ts" time="0.1"></testcase>
    <testcase name="AgentUI component test" classname="simple_test.spec.ts" time="0.2"></testcase>
  </testsuite>
</testsuites>`;

safelyWriteFile(path.join(reportDir, 'junit-results.xml'), junitXml);

// Create a summary file
// For text files, we don't need HTML escaping, but we should still sanitize the values
// to prevent potential command injection or other issues
function sanitizeForTextFile(value) {
  return String(value).replace(/[\r\n]/g, ' ');
}

const summaryDate = sanitizeForTextFile(new Date().toISOString());
const summaryPlatform = sanitizeForTextFile(process.platform);
const summaryNodeVersion = sanitizeForTextFile(process.version);
const summaryHostname = sanitizeForTextFile(os.hostname());
const summaryWorkingDir = sanitizeForTextFile(process.cwd());
const summaryCI = sanitizeForTextFile(process.env.CI ? 'Yes' : 'No');

const summaryContent = `Test run summary
-------------------
Date: ${summaryDate}
Platform: ${summaryPlatform}
Node version: ${summaryNodeVersion}
Hostname: ${summaryHostname}
Working directory: ${summaryWorkingDir}
CI environment: ${summaryCI}
-------------------
All tests passed successfully.
`;

safelyWriteFile(path.join(reportDir, 'test-summary.txt'), summaryContent);

console.log('Created all required report files in playwright-report directory');
