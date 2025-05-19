/**
 * Tailwind CSS Watch Script
 * 
 * This script starts watch processes for both static and React frontend Tailwind CSS.
 * It handles process management and graceful shutdown.
 */

const { spawn } = require('child_process');
const { log, buildAllTailwind } = require('./tailwind_utils');

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    staticConfig: './tailwind.config.js',
    staticInput: './ui/static/css/tailwind.css',
    staticOutput: './ui/static/css/tailwind.output.css',
    reactConfig: './ui/react_frontend/tailwind.config.js',
    reactInput: './ui/react_frontend/src/index.css',
    reactOutput: './ui/react_frontend/src/tailwind.output.css'
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--static-config' && i + 1 < args.length) {
      options.staticConfig = args[++i];
    } else if (arg === '--static-input' && i + 1 < args.length) {
      options.staticInput = args[++i];
    } else if (arg === '--static-output' && i + 1 < args.length) {
      options.staticOutput = args[++i];
    } else if (arg === '--react-config' && i + 1 < args.length) {
      options.reactConfig = args[++i];
    } else if (arg === '--react-input' && i + 1 < args.length) {
      options.reactInput = args[++i];
    } else if (arg === '--react-output' && i + 1 < args.length) {
      options.reactOutput = args[++i];
    }
  }

  return options;
}

// Start watch processes
function startWatchProcesses(options) {
  log('Starting Tailwind CSS watch processes...');

  // Start watch mode for both static and React frontend
  buildAllTailwind({
    static: {
      configPath: options.staticConfig,
      inputPath: options.staticInput,
      outputPath: options.staticOutput,
      minify: false
    },
    react: {
      configPath: options.reactConfig,
      inputPath: options.reactInput,
      outputPath: options.reactOutput,
      minify: false
    },
    watch: true
  });

  log('Watch processes started. Press Ctrl+C to stop.');
}

// Handle process exit
function setupExitHandlers() {
  // Handle Ctrl+C
  process.on('SIGINT', () => {
    log('Received SIGINT. Shutting down watch processes...');
    process.exit(0);
  });

  // Handle process termination
  process.on('SIGTERM', () => {
    log('Received SIGTERM. Shutting down watch processes...');
    process.exit(0);
  });

  // Handle uncaught exceptions
  process.on('uncaughtException', (error) => {
    log(`Uncaught exception: ${error.message}`);
    process.exit(1);
  });

  // Handle unhandled promise rejections
  process.on('unhandledRejection', (reason, promise) => {
    log(`Unhandled promise rejection: ${reason}`);
    process.exit(1);
  });
}

// Main function
function main() {
  try {
    log('Starting Tailwind CSS watch script...');
    
    // Parse command line arguments
    const options = parseArgs();
    log(`Options: ${JSON.stringify(options, null, 2)}`);
    
    // Setup exit handlers
    setupExitHandlers();
    
    // Start watch processes
    startWatchProcesses(options);
  } catch (error) {
    log(`Error: ${error.message}`);
    process.exit(1);
  }
}

// Run the main function
main();
