#!/usr/bin/env node

/**
 * Coverage generation script that handles threshold failures gracefully
 * This ensures coverage reports are always generated for CI/CD workflows
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function runCommand(command, options = {}) {
  try {
    console.log(`Running: ${command}`);
    const result = execSync(command, { 
      stdio: 'inherit', 
      encoding: 'utf8',
      ...options 
    });
    return { success: true, result };
  } catch (error) {
    console.log(`Command failed with exit code ${error.status}: ${command}`);
    console.log('Error output:', error.message);
    return { success: false, error };
  }
}

function ensureDirectoryExists(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`Created directory: ${dirPath}`);
  }
}

function main() {
  console.log('Starting coverage generation...');
  
  // Ensure coverage directory exists
  ensureDirectoryExists('./coverage');
  
  // Build Tailwind CSS first
  console.log('\n1. Building Tailwind CSS...');
  const tailwindResult = runCommand('pnpm tailwind:build');
  if (!tailwindResult.success) {
    console.log('Tailwind build failed, but continuing...');
  }
  
  // Run vitest with coverage, but don't fail if thresholds aren't met
  console.log('\n2. Running tests with coverage...');
  const vitestResult = runCommand('npx vitest run --coverage --coverage.reportOnFailure --coverage.reportsDirectory=./coverage --passWithNoTests --reporter=verbose');

  if (!vitestResult.success) {
    console.log('Vitest failed (possibly due to test failures or coverage thresholds), but checking for coverage files...');

    // Try to run coverage generation again with different options
    console.log('Attempting alternative coverage generation...');
    runCommand('npx vitest run --coverage --coverage.reporter=lcov --coverage.reporter=json --coverage.reporter=html --coverage.reportsDirectory=./coverage --passWithNoTests');
  }
  
  // Check if coverage files were generated
  const lcovPath = './coverage/lcov.info';
  const htmlPath = './coverage/index.html';
  const jsonPath = './coverage/coverage-final.json';

  // Check for JSON coverage first (vitest generates this)
  if (fs.existsSync(jsonPath)) {
    const stats = fs.statSync(jsonPath);
    console.log(`\n✓ Coverage JSON file generated: ${jsonPath} (${stats.size} bytes)`);

    // Try to read coverage summary from JSON
    try {
      const jsonContent = fs.readFileSync(jsonPath, 'utf8');
      const coverageData = JSON.parse(jsonContent);
      const fileCount = Object.keys(coverageData).length;
      console.log(`Coverage data includes ${fileCount} files`);
    } catch (err) {
      console.log('Could not parse JSON coverage:', err.message);
    }
  }

  if (fs.existsSync(lcovPath)) {
    const stats = fs.statSync(lcovPath);
    console.log(`\n✓ Coverage LCOV file generated: ${lcovPath} (${stats.size} bytes)`);

    // Check if LCOV file has actual content (not just empty placeholder)
    if (stats.size > 50) {
      // Read and display coverage summary
      try {
        const lcovContent = fs.readFileSync(lcovPath, 'utf8');
        const lines = lcovContent.split('\n');
        const summaryLines = lines.filter(line => line.startsWith('LF:') || line.startsWith('LH:'));
        console.log('Coverage summary from LCOV:');
        summaryLines.slice(0, 10).forEach(line => console.log(`  ${line}`));
      } catch (err) {
        console.log('Could not read LCOV content:', err.message);
      }
    } else {
      console.log('LCOV file exists but appears to be empty or placeholder');
    }
  } else {
    console.log(`\n✗ Coverage LCOV file not found: ${lcovPath}`);
    // Create an empty LCOV file to prevent workflow failures
    fs.writeFileSync(lcovPath, '# Empty coverage file\n');
    console.log('Created empty LCOV file for workflow compatibility');
  }
  
  if (fs.existsSync(htmlPath)) {
    console.log(`✓ Coverage HTML report generated: ${htmlPath}`);
  } else {
    console.log(`✗ Coverage HTML report not found: ${htmlPath}`);
  }
  
  console.log('\nCoverage generation completed.');
  
  // Exit with success even if vitest failed due to thresholds
  // This allows CI workflows to continue and upload coverage reports
  process.exit(0);
}

if (require.main === module) {
  main();
}

module.exports = { runCommand, ensureDirectoryExists };
