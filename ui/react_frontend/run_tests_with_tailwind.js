/**
 * Enhanced Script to run tests with tailwind CSS build
 *
 * This script ensures that tailwind CSS is built before running tests
 * It includes robust fallback mechanisms for different environments
 *
 * Features:
 * - Support for custom Tailwind CSS configuration paths
 * - Support for custom input and output paths
 * - Support for custom test commands
 * - Support for parallel test execution
 */

const path = require('path');
const fs = require('fs');
const { spawnSync } = require('child_process');
const tailwindUtils = require('./tailwind_utils');

// Import utility functions
const {
  buildTailwind,
  checkTailwindOutput,
  runTestsWithTailwind,
  log
} = tailwindUtils;

// Check if a command exists
function commandExists(command) {
  try {
    const result = spawnSync(process.platform === 'win32' ? 'where' : 'which', [command], {
      stdio: 'pipe',
      encoding: 'utf-8'
    });
    return result.status === 0;
  } catch (error) {
    return false;
  }
}

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    configPath: './tailwind.config.js',
    inputPath: './src/index.css',
    outputPath: './src/tailwind.output.css',
    testCommand: '',
    parallel: false,
    watch: false,
    skipBuild: false,
    skipTests: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--config' && i + 1 < args.length) {
      options.configPath = args[++i];
    } else if (arg === '--input' && i + 1 < args.length) {
      options.inputPath = args[++i];
    } else if (arg === '--output' && i + 1 < args.length) {
      options.outputPath = args[++i];
    } else if (arg === '--test-command' && i + 1 < args.length) {
      options.testCommand = args[++i];
    } else if (arg === '--parallel') {
      options.parallel = true;
    } else if (arg === '--watch') {
      options.watch = true;
    } else if (arg === '--skip-build') {
      options.skipBuild = true;
    } else if (arg === '--skip-tests') {
      options.skipTests = true;
    }
  }

  return options;
}

// Main function
async function main() {
  try {
    log('Starting test process with tailwind build...');
    log(`Running in environment: ${process.env.NODE_ENV || 'development'}`);
    log(`Platform: ${process.platform}`);

    // Parse command line arguments
    const options = parseArgs();
    log(`Options: ${JSON.stringify(options, null, 2)}`);

    // Check if we're in a Docker container
    const inDocker = fs.existsSync('/.dockerenv') || (process.env.DOCKER_CONTAINER === 'true');
    log(`Running in Docker: ${inDocker ? 'yes' : 'no'}`);

    // Check if we're in a CI environment
    const inCI = process.env.CI === 'true';
    log(`Running in CI: ${inCI ? 'yes' : 'no'}`);

    // If watch mode is enabled, just start watching and exit
    if (options.watch) {
      log('Watch mode enabled, starting Tailwind CSS watch...');
      buildTailwind({
        configPath: options.configPath,
        inputPath: options.inputPath,
        outputPath: options.outputPath,
        minify: false,
        watch: true
      });
      return; // Exit the function, the watch process will keep running
    }

    // Check if tailwind.output.css exists and we're not skipping the build
    if (!options.skipBuild && !checkTailwindOutput(options.outputPath)) {
      log(`${options.outputPath} not found, building it...`);
      const buildSuccess = await buildTailwind({
        configPath: options.configPath,
        inputPath: options.inputPath,
        outputPath: options.outputPath,
        minify: true,
        watch: false
      });

      if (!buildSuccess) {
        log('Failed to build tailwind CSS after trying all methods');
        process.exit(1);
      }
    } else if (options.skipBuild) {
      log('Skipping Tailwind CSS build as requested');
    } else {
      log(`${options.outputPath} already exists, skipping build`);
    }

    // Run the tests if not skipping
    if (!options.skipTests) {
      const testSuccess = await runTestsWithTailwind({
        configPath: options.configPath,
        inputPath: options.inputPath,
        outputPath: options.outputPath,
        testCommand: options.testCommand,
        parallel: options.parallel
      });

      if (!testSuccess) {
        log('Failed to run tests after trying all methods');
        process.exit(1);
      }
    } else {
      log('Skipping tests as requested');
    }

    log('Test process completed successfully');
  } catch (error) {
    log(`Error: ${error.message}`);
    process.exit(1);
  }
}

// Run the main function
main().catch(error => {
  log(`Unhandled error: ${error.message}`);
  process.exit(1);
});
