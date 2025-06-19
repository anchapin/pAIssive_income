/**
 * Verify Environment Detection Script
 * 
 * This script verifies that all environment detection modules work correctly
 * and can be imported without errors.
 */

const fs = require('fs');
const path = require('path');

// Create report directory
const reportDir = path.join(process.cwd(), 'playwright-report');
if (!fs.existsSync(reportDir)) {
  fs.mkdirSync(reportDir, { recursive: true });
}

// Logging
function log(message, level = 'info') {
  const timestamp = new Date().toISOString();
  const prefix = `[${timestamp}] [verify-env-detection] [${level.toUpperCase()}]`;
  console.log(`${prefix} ${message}`);
}

// Test environment detection modules
async function verifyEnvironmentDetection() {
  log('Starting environment detection verification');
  
  const modules = [
    './helpers/unified-environment',
    './helpers/environment-detection', 
    './helpers/ci-environment'
  ];

  let allSuccess = true;
  let results = [];

  for (const modulePath of modules) {
    try {
      log(`Testing module: ${modulePath}`);
      
      // Try to require the module
      const module = require(modulePath);
      
      // Check if module exports expected functions
      const hasExports = module && typeof module === 'object';
      
      results.push({
        module: modulePath,
        success: true,
        exports: Object.keys(module || {}),
        error: null
      });
      
      log(`✓ Module ${modulePath}: imported successfully with ${Object.keys(module || {}).length} exports`);
      
    } catch (error) {
      allSuccess = false;
      results.push({
        module: modulePath,
        success: false,
        exports: [],
        error: error.message
      });
      
      log(`✗ Module ${modulePath}: ${error.message}`, 'error');
    }
  }

  // Test basic environment detection
  try {
    const unifiedEnv = require('./helpers/unified-environment');
    const isCI = unifiedEnv.isCI();
    const isGitHubActions = unifiedEnv.isGitHubActions();
    
    log(`Environment detection: CI=${isCI}, GitHub Actions=${isGitHubActions}`);
    
    results.push({
      module: 'environment-test',
      success: true,
      data: { isCI, isGitHubActions },
      error: null
    });
    
  } catch (error) {
    allSuccess = false;
    results.push({
      module: 'environment-test',
      success: false,
      data: null,
      error: error.message
    });
    
    log(`✗ Environment test failed: ${error.message}`, 'error');
  }

  // Generate report
  const report = {
    timestamp: new Date().toISOString(),
    success: allSuccess,
    results: results,
    summary: {
      total: results.length,
      passed: results.filter(r => r.success).length,
      failed: results.filter(r => !r.success).length
    }
  };

  // Write report
  const reportFile = path.join(reportDir, 'environment-detection-verification.json');
  fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
  
  // Write summary
  const summaryFile = path.join(reportDir, 'environment-detection-summary.txt');
  fs.writeFileSync(summaryFile, 
    `Environment Detection Verification Summary\n` +
    `=========================================\n` +
    `Timestamp: ${report.timestamp}\n` +
    `Overall Success: ${allSuccess ? 'Yes' : 'No'}\n` +
    `Total Tests: ${report.summary.total}\n` +
    `Passed: ${report.summary.passed}\n` +
    `Failed: ${report.summary.failed}\n` +
    `\n` +
    `Module Results:\n` +
    results.map(r => 
      `- ${r.module}: ${r.success ? '✓' : '✗'} ${r.success ? `(${r.exports?.length || 0} exports)` : r.error}`
    ).join('\n') + '\n'
  );

  log(`Verification complete: ${report.summary.passed}/${report.summary.total} tests passed`);
  log(`Reports written to ${reportFile} and ${summaryFile}`);

  return allSuccess;
}

// Run verification
verifyEnvironmentDetection()
  .then(success => {
    if (success) {
      log('Environment detection verification completed successfully');
      process.exit(0);
    } else {
      log('Environment detection verification failed', 'error');
      process.exit(1);
    }
  })
  .catch(error => {
    log(`Verification error: ${error.message}`, 'error');
    process.exit(1);
  });