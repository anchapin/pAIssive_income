/**
 * React Frontend Tailwind CSS Utility Functions
 *
 * This module provides utility functions for working with Tailwind CSS in the React frontend,
 * including custom configuration paths, input/output paths, and watch mode.
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Log function with timestamp
function log(message) {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${message}`);
}

/**
 * Build Tailwind CSS with custom configuration
 *
 * @param {Object} options - Build options
 * @param {string} options.configPath - Path to tailwind config file
 * @param {string} options.inputPath - Path to input CSS file
 * @param {string} options.outputPath - Path to output CSS file
 * @param {boolean} options.minify - Whether to minify the output
 * @param {boolean} options.watch - Whether to watch for changes
 * @returns {boolean} - Whether the build was successful
 */
function buildTailwind(options = {}) {
  const {
    configPath = './tailwind.config.js',
    inputPath = './src/index.css',
    outputPath = './src/tailwind.output.css',
    minify = true,
    watch = false,
  } = options;

  log(`Building Tailwind CSS with options: ${JSON.stringify(options, null, 2)}`);

  // Ensure the output directory exists
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    log(`Creating output directory: ${outputDir}`);
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Build the command
  const baseCommand = `tailwindcss -c ${configPath} -i ${inputPath} -o ${outputPath}`;
  const command = `${baseCommand}${minify ? ' --minify' : ''}${watch ? ' --watch' : ''}`;

  // Try different methods to build tailwind
  const isWindows = process.platform === 'win32';
  const directPath = isWindows ?
    path.join(process.cwd(), 'node_modules', '.bin', 'tailwindcss.cmd') :
    './node_modules/.bin/tailwindcss';

  const buildMethods = [
    { name: 'npx', command: `npx ${command}` },
    { name: 'pnpm', command: `pnpm exec ${command}` },
    { name: 'npm', command: `npm exec -- ${command}` },
    { name: 'direct', command: `"${directPath}" -c ${configPath} -i ${inputPath} -o ${outputPath}${minify ? ' --minify' : ''}${watch ? ' --watch' : ''}` }
  ];

  for (const method of buildMethods) {
    try {
      log(`Trying to build tailwind with ${method.name}...`);

      if (watch) {
        // For watch mode, we need to spawn a child process
        const parts = method.command.split(' ');
        const proc = spawn(parts[0], parts.slice(1), {
          stdio: 'inherit',
          shell: process.platform === 'win32' // Use shell on Windows
        });

        proc.on('error', (err) => {
          log(`Error with ${method.name}: ${err.message}`);
        });

        // Return true immediately since this is a long-running process
        return true;
      } else {
        // For one-time build, use execSync
        execSync(method.command, { stdio: 'inherit' });
        log(`Tailwind CSS built successfully with ${method.name}`);
        return true;
      }
    } catch (error) {
      log(`Failed to build tailwind with ${method.name}: ${error.message}`);
    }
  }

  log('All tailwind build methods failed');
  return false;
}

/**
 * Check if tailwind.output.css exists
 *
 * @param {string} outputPath - Path to check
 * @returns {boolean} - Whether the file exists
 */
function checkTailwindOutput(outputPath = './src/tailwind.output.css') {
  return fs.existsSync(outputPath);
}

/**
 * Run tests with Tailwind CSS
 *
 * @param {Object} options - Test options
 * @param {string} options.configPath - Path to tailwind config file
 * @param {string} options.inputPath - Path to input CSS file
 * @param {string} options.outputPath - Path to output CSS file
 * @param {string} options.testCommand - Custom test command to run
 * @param {boolean} options.parallel - Whether to run tests in parallel
 * @returns {boolean} - Whether the tests were successful
 */
async function runTestsWithTailwind(options = {}) {
  const {
    configPath = './tailwind.config.js',
    inputPath = './src/index.css',
    outputPath = './src/tailwind.output.css',
    testCommand = '',
    parallel = false
  } = options;

  log('Running tests with Tailwind CSS...');

  // Build Tailwind CSS first
  const tailwindBuilt = buildTailwind({
    configPath,
    inputPath,
    outputPath,
    minify: true,
    watch: false
  });

  if (!tailwindBuilt) {
    log('Failed to build Tailwind CSS, cannot run tests');
    return false;
  }

  // If a custom test command is provided, use it
  if (testCommand) {
    try {
      log(`Running custom test command: ${testCommand}`);
      execSync(testCommand, { stdio: 'inherit' });
      log('Tests completed successfully');
      return true;
    } catch (error) {
      log(`Tests failed: ${error.message}`);
      return false;
    }
  }

  // Otherwise, try different methods to run tests
  const testMethods = [
    { name: 'npx react-app-rewired', command: 'npx react-app-rewired test --passWithNoTests' },
    { name: 'pnpm test:legacy', command: 'pnpm test:legacy' },
    { name: 'npm test:legacy', command: 'npm run test:legacy' },
    { name: 'vitest', command: `npx vitest run --passWithNoTests${parallel ? ' --threads' : ''}` },
    { name: 'pnpm vitest', command: `pnpm test:unit${parallel ? ' -- --threads' : ''}` }
  ];

  for (const method of testMethods) {
    try {
      log(`Trying to run tests with ${method.name}...`);
      execSync(method.command, { stdio: 'inherit' });
      log(`Tests completed successfully with ${method.name}`);
      return true;
    } catch (error) {
      log(`Failed to run tests with ${method.name}: ${error.message}`);
    }
  }

  log('All test methods failed');
  return false;
}

module.exports = {
  buildTailwind,
  checkTailwindOutput,
  runTestsWithTailwind,
  log
};
