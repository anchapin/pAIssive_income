/**
 * Tailwind CSS Utility Functions
 *
 * This module provides utility functions for working with Tailwind CSS,
 * including custom configuration paths, input/output paths, and watch mode.
 * Enhanced with robust error handling, logging, and configuration management.
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Log levels
const LOG_LEVELS = {
  error: 0,
  warn: 1,
  info: 2,
  debug: 3
};

// Default configuration
const DEFAULT_CONFIG_PATHS = [
  './tailwind.config.json',
  './ui/tailwind.config.json',
  './config/tailwind.config.json'
];

// Global configuration
let globalConfig = null;

// Default log level and format
let currentLogLevel = 'info';
let currentLogFormat = 'simple';
let logToFile = false;
let logFilePath = './logs/tailwind-build.log';

/**
 * Enhanced logging function with levels and file logging
 *
 * @param {string} message - Message to log
 * @param {string} level - Log level (error, warn, info, debug)
 * @param {Object} meta - Additional metadata to log
 */
function log(message, level = 'info', meta = {}) {
  // Check if we should log this message based on level
  if (LOG_LEVELS[level] > LOG_LEVELS[currentLogLevel]) {
    return;
  }

  const timestamp = new Date().toISOString();

  // Format for console output
  let consoleMessage = `[${timestamp}] ${level.toUpperCase()}: ${message}`;

  // Add metadata if present and format is detailed
  if (currentLogFormat === 'detailed' && Object.keys(meta).length > 0) {
    consoleMessage += ` ${JSON.stringify(meta)}`;
  }

  // Log to console based on level
  switch (level) {
    case 'error':
      console.error(consoleMessage);
      break;
    case 'warn':
      console.warn(consoleMessage);
      break;
    case 'debug':
      console.debug(consoleMessage);
      break;
    default:
      console.log(consoleMessage);
  }

  // Log to file if enabled
  if (logToFile && logFilePath) {
    try {
      const logDir = path.dirname(logFilePath);
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }

      // Create a safe log entry without using spread operator
      const safeLogEntry = {
        timestamp: timestamp,
        level: level,
        message: message
      };

      // Add metadata properties individually
      if (meta && typeof meta === 'object') {
        Object.keys(meta).forEach(key => {
          // Skip error objects to prevent circular references
          if (key !== 'error' || typeof meta[key] !== 'object') {
            safeLogEntry[key] = meta[key];
          } else {
            // For error objects, just log the message
            safeLogEntry[key] = meta[key].message || 'Unknown error';
          }
        });
      }

      fs.appendFileSync(
        logFilePath,
        JSON.stringify(safeLogEntry) + '\n',
        'utf8'
      );
    } catch (err) {
      console.error(`Failed to write to log file: ${err.message}`);
    }
  }
}

/**
 * Update logging configuration
 *
 * @param {Object} config - Logging configuration
 */
function updateLoggingConfig(config) {
  if (config?.logging?.level) {
    currentLogLevel = config.logging.level;
  }

  if (config?.logging?.format) {
    currentLogFormat = config.logging.format;
  }

  if (config?.logging?.logToFile !== undefined) {
    logToFile = config.logging.logToFile;
  }

  if (config?.logging?.logFilePath) {
    logFilePath = config.logging.logFilePath;
  }
}

/**
 * Load configuration from file
 *
 * @param {string} configPath - Path to configuration file
 * @returns {Object} - Loaded configuration or null if failed
 */
function loadConfig(configPath) {
  try {
    if (!fs.existsSync(configPath)) {
      return null;
    }

    const configData = fs.readFileSync(configPath, 'utf8');
    return JSON.parse(configData);
  } catch (err) {
    log(`Failed to load configuration from ${configPath}: ${err.message}`, 'error', { error: err });
    return null;
  }
}

/**
 * Get configuration, loading from file if not already loaded
 *
 * @returns {Object} - Configuration object
 */
function getConfig() {
  if (globalConfig) {
    return globalConfig;
  }

  // Try to load from default paths
  for (const configPath of DEFAULT_CONFIG_PATHS) {
    const config = loadConfig(configPath);
    if (config) {
      console.log(`[${new Date().toISOString()}] Loaded configuration from ${configPath}`);
      globalConfig = config;

      // Update logging configuration
      updateLoggingConfig(config);

      return config;
    }
  }

  // No config found, use defaults
  console.log(`[${new Date().toISOString()}] No configuration file found, using defaults`);
  globalConfig = {
    defaults: {
      static: {
        configPath: './tailwind.config.js',
        inputPath: './ui/static/css/tailwind.css',
        outputPath: './ui/static/css/tailwind.output.css',
        minify: true
      },
      react: {
        configPath: './ui/react_frontend/tailwind.config.js',
        inputPath: './ui/react_frontend/src/index.css',
        outputPath: './ui/react_frontend/src/tailwind.output.css',
        minify: true
      }
    },
    logging: {
      level: 'info',
      format: 'simple'
    },
    errorHandling: {
      retryCount: 3,
      retryDelay: 1000,
      failFast: false
    }
  };

  // Update logging configuration with defaults
  updateLoggingConfig(globalConfig);

  return globalConfig;
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
 * @param {Array} options.files - Multiple input/output file pairs
 * @param {Object} options.postcss - PostCSS configuration
 * @returns {boolean} - Whether the build was successful
 */
function buildTailwind(options = {}) {
  const config = getConfig();
  const errorConfig = config?.errorHandling || {};

  try {
    // Handle single file or multiple files
    if (options.files && Array.isArray(options.files) && options.files.length > 0) {
      return buildMultipleFiles(options);
    }

    // Extract options with defaults from config
    const defaults = config?.defaults?.static || {};
    const {
      configPath = defaults.configPath || './tailwind.config.js',
      inputPath = defaults.inputPath || './ui/static/css/tailwind.css',
      outputPath = defaults.outputPath || './ui/static/css/tailwind.output.css',
      minify = defaults.minify !== undefined ? defaults.minify : true,
      watch = false,
      postcss = config?.postcss || {}
    } = options;

    log(`Building Tailwind CSS with options:`, 'info', {
      configPath,
      inputPath,
      outputPath,
      minify,
      watch,
      postcssEnabled: !!postcss.useConfigFile
    });

    // Ensure the output directory exists
    const outputDir = path.dirname(outputPath);
    if (!fs.existsSync(outputDir)) {
      log(`Creating output directory: ${outputDir}`, 'info');
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Build the command
    let baseCommand = `tailwindcss -c ${configPath} -i ${inputPath} -o ${outputPath}`;

    // Add PostCSS config if specified
    if (postcss.useConfigFile && postcss.configPath) {
      baseCommand += ` --postcss=${postcss.configPath}`;
    }

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

    // Track attempts for retry logic
    let attemptCount = 0;
    const maxAttempts = errorConfig.retryCount || 3;
    const retryDelay = errorConfig.retryDelay || 1000;

    // Try each build method with retries
    for (const method of buildMethods) {
      attemptCount = 0;

      while (attemptCount < maxAttempts) {
        try {
          log(`Trying to build tailwind with ${method.name} (attempt ${attemptCount + 1}/${maxAttempts})...`, 'info');

          if (watch) {
            // For watch mode, we need to spawn a child process
            const parts = method.command.split(' ');
            const proc = spawn(parts[0], parts.slice(1), {
              stdio: 'inherit',
              shell: process.platform === 'win32' // Use shell on Windows
            });

            // Set up error handling for the process
            proc.on('error', (err) => {
              log(`Error with ${method.name}: ${err.message}`, 'error', { error: err });
            });

            // Set up exit handling
            proc.on('exit', (code) => {
              if (code !== 0) {
                log(`Process exited with code ${code}`, 'warn');
              }
            });

            // Return true immediately since this is a long-running process
            return true;
          } else {
            // For one-time build, use execSync
            execSync(method.command, { stdio: 'inherit' });
            log(`Tailwind CSS built successfully with ${method.name}`, 'info', {
              method: method.name,
              configPath,
              inputPath,
              outputPath
            });
            return true;
          }
        } catch (error) {
          attemptCount++;
          log(`Failed to build tailwind with ${method.name} (attempt ${attemptCount}/${maxAttempts}): ${error.message}`, 'error', {
            error: error.message,
            method: method.name,
            attempt: attemptCount,
            command: method.command
          });

          // If we have more attempts, wait before retrying
          if (attemptCount < maxAttempts) {
            log(`Retrying in ${retryDelay}ms...`, 'info');
            // Sleep for retryDelay milliseconds
            const sleepUntil = Date.now() + retryDelay;
            while (Date.now() < sleepUntil) { /* empty */ }
          }
        }
      }
    }

    log('All tailwind build methods failed after retries', 'error');
    return false;
  } catch (error) {
    log(`Unexpected error in buildTailwind: ${error.message}`, 'error', { error });

    // If failFast is true, throw the error, otherwise return false
    if (errorConfig.failFast) {
      throw error;
    }

    return false;
  }
}

/**
 * Build multiple Tailwind CSS files
 *
 * @param {Object} options - Build options
 * @param {Array} options.files - Array of file configurations
 * @param {boolean} options.watch - Whether to watch for changes
 * @param {boolean} options.parallel - Whether to build in parallel
 * @returns {boolean} - Whether all builds were successful
 */
function buildMultipleFiles(options) {
  const { files, watch, parallel = false } = options;
  const config = getConfig();

  log(`Building multiple Tailwind CSS files`, 'info', {
    fileCount: files.length,
    watch,
    parallel
  });

  // If parallel is enabled and we're not in watch mode, build all files in parallel
  if (parallel && !watch) {
    const maxConcurrent = config?.performance?.concurrentBuilds || 2;
    log(`Building in parallel with max ${maxConcurrent} concurrent builds`, 'info');

    // Process files in batches
    const results = [];
    for (let i = 0; i < files.length; i += maxConcurrent) {
      const batch = files.slice(i, i + maxConcurrent);
      const batchPromises = batch.map(file => {
        return new Promise(resolve => {
          const success = buildTailwind({
            ...options,
            configPath: file.configPath,
            inputPath: file.inputPath,
            outputPath: file.outputPath,
            minify: file.minify !== undefined ? file.minify : options.minify,
            watch: false // Never watch in parallel mode
          });
          resolve(success);
        });
      });

      // Wait for all promises in this batch to resolve
      const batchResults = Promise.all(batchPromises);
      results.push(...batchResults);
    }

    // Check if all builds were successful
    return results.every(result => result === true);
  } else {
    // Build files sequentially
    let allSuccessful = true;

    for (const file of files) {
      const success = buildTailwind({
        ...options,
        configPath: file.configPath,
        inputPath: file.inputPath,
        outputPath: file.outputPath,
        minify: file.minify !== undefined ? file.minify : options.minify,
        watch // Pass through watch mode
      });

      if (!success && !watch) {
        allSuccessful = false;

        // If continueOnError is false, stop on first failure
        if (!config?.errorHandling?.continueOnError) {
          log(`Build failed for ${file.inputPath} -> ${file.outputPath}, stopping`, 'error');
          return false;
        }
      }
    }

    return allSuccessful;
  }
}

/**
 * Start watch mode for Tailwind CSS
 *
 * @param {Object} options - Watch options
 * @param {string} options.configPath - Path to tailwind config file
 * @param {string} options.inputPath - Path to input CSS file
 * @param {string} options.outputPath - Path to output CSS file
 * @returns {Object} - The spawned process
 */
function watchTailwind(options = {}) {
  return buildTailwind({
    ...options,
    watch: true,
    minify: false // Usually don't minify in watch mode for faster builds
  });
}

/**
 * Build Tailwind CSS for both static and React frontend
 *
 * @param {Object} options - Build options
 * @param {Object} options.static - Options for static build
 * @param {Object} options.react - Options for React build
 * @param {boolean} options.watch - Whether to watch for changes
 * @param {boolean} options.parallel - Whether to build in parallel
 * @param {Object} options.buildTools - Integration with other build tools
 * @returns {boolean} - Whether the build was successful
 */
function buildAllTailwind(options = {}) {
  const config = getConfig();
  const defaults = config.defaults || {};

  try {
    const {
      static = defaults.static || {},
      react = defaults.react || {},
      watch = false,
      parallel = config?.performance?.concurrentBuilds > 1,
      buildTools = config?.buildTools || {}
    } = options;

    log(`Building all Tailwind CSS files`, 'info', { watch, parallel });

    // Check for webpack or vite integration
    const useWebpack = buildTools.webpack?.enabled || config?.buildTools?.webpack?.enabled;
    const useVite = buildTools.vite?.enabled || config?.buildTools?.vite?.enabled;

    // If using webpack or vite, use the integrated build process
    if (useWebpack) {
      return buildWithWebpack(options);
    } else if (useVite) {
      return buildWithVite(options);
    }

    // Use multiple file build approach for better performance and flexibility
    const files = [
      {
        configPath: static.configPath || defaults.static?.configPath || './tailwind.config.js',
        inputPath: static.inputPath || defaults.static?.inputPath || './ui/static/css/tailwind.css',
        outputPath: static.outputPath || defaults.static?.outputPath || './ui/static/css/tailwind.output.css',
        minify: static.minify !== undefined ? static.minify : (defaults.static?.minify !== undefined ? defaults.static.minify : true),
        type: 'static'
      },
      {
        configPath: react.configPath || defaults.react?.configPath || './ui/react_frontend/tailwind.config.js',
        inputPath: react.inputPath || defaults.react?.inputPath || './ui/react_frontend/src/index.css',
        outputPath: react.outputPath || defaults.react?.outputPath || './ui/react_frontend/src/tailwind.output.css',
        minify: react.minify !== undefined ? react.minify : (defaults.react?.minify !== undefined ? defaults.react.minify : true),
        type: 'react'
      }
    ];

    // Add any additional files from the configuration
    if (options.additionalFiles && Array.isArray(options.additionalFiles)) {
      files.push(...options.additionalFiles);
    }

    return buildMultipleFiles({
      files,
      watch,
      parallel: watch ? false : parallel, // Don't use parallel in watch mode
      postcss: options.postcss || config?.postcss
    });
  } catch (error) {
    log(`Error in buildAllTailwind: ${error.message}`, 'error', { error });

    // If failFast is true, throw the error, otherwise return false
    if (config?.errorHandling?.failFast) {
      throw error;
    }

    return false;
  }
}

/**
 * Build Tailwind CSS with webpack integration
 *
 * @param {Object} options - Build options
 * @returns {boolean} - Whether the build was successful
 */
function buildWithWebpack(options = {}) {
  const config = getConfig();
  const webpackConfig = options.buildTools?.webpack || config?.buildTools?.webpack || {};

  try {
    log(`Building Tailwind CSS with webpack integration`, 'info', {
      configPath: webpackConfig.configPath
    });

    // Check if webpack is installed
    try {
      require.resolve('webpack');
    } catch (error) {
      log('Webpack is not installed. Please install webpack to use this feature.', 'error');
      return false;
    }

    // Load webpack config
    const webpackConfigPath = webpackConfig.configPath || './webpack.config.js';
    if (!fs.existsSync(webpackConfigPath)) {
      log(`Webpack config file not found: ${webpackConfigPath}`, 'error');
      return false;
    }

    // Run webpack build
    const webpack = require('webpack');
    const webpackConfigFile = require(path.resolve(webpackConfigPath));

    // Add PostCSS plugins for Tailwind if not already present
    if (!webpackConfigFile.module?.rules) {
      log('Invalid webpack config: missing module.rules', 'error');
      return false;
    }

    // Find CSS rule and add PostCSS loader if needed
    let cssRuleFound = false;
    for (const rule of webpackConfigFile.module.rules) {
      if (rule.test && rule.test.toString().includes('.css')) {
        cssRuleFound = true;

        // Check if PostCSS loader is already configured
        const hasPostCSSLoader = rule.use && rule.use.some(loader =>
          (typeof loader === 'string' && loader.includes('postcss-loader')) ||
          (typeof loader === 'object' && loader.loader && loader.loader.includes('postcss-loader'))
        );

        if (!hasPostCSSLoader) {
          log('Adding PostCSS loader to webpack CSS rule', 'info');

          // Add PostCSS loader
          if (!rule.use) {
            rule.use = [];
          }

          rule.use.push({
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: [
                  require('tailwindcss'),
                  require('autoprefixer')
                ]
              }
            }
          });
        }
      }
    }

    if (!cssRuleFound) {
      log('No CSS rule found in webpack config. Tailwind CSS may not be properly processed.', 'warn');
    }

    // Run webpack
    return new Promise((resolve) => {
      webpack(webpackConfigFile, (err, stats) => {
        if (err || stats.hasErrors()) {
          log('Webpack build failed', 'error', {
            error: err?.message || 'See webpack output for details'
          });
          resolve(false);
        } else {
          log('Webpack build completed successfully', 'info');
          resolve(true);
        }
      });
    });
  } catch (error) {
    log(`Error in buildWithWebpack: ${error.message}`, 'error', { error });
    return false;
  }
}

/**
 * Build Tailwind CSS with Vite integration
 *
 * @param {Object} options - Build options
 * @returns {boolean} - Whether the build was successful
 */
function buildWithVite(options = {}) {
  const config = getConfig();
  const viteConfig = options.buildTools?.vite || config?.buildTools?.vite || {};

  try {
    log(`Building Tailwind CSS with Vite integration`, 'info', {
      configPath: viteConfig.configPath
    });

    // Check if vite is installed
    try {
      require.resolve('vite');
    } catch (error) {
      log('Vite is not installed. Please install vite to use this feature.', 'error');
      return false;
    }

    // Load vite config
    const viteConfigPath = viteConfig.configPath || './vite.config.js';
    if (!fs.existsSync(viteConfigPath)) {
      log(`Vite config file not found: ${viteConfigPath}`, 'error');
      return false;
    }

    // Run vite build
    const { build } = require('vite');

    return build({
      configFile: viteConfigPath,
      mode: 'production'
    }).then(() => {
      log('Vite build completed successfully', 'info');
      return true;
    }).catch(error => {
      log(`Vite build failed: ${error.message}`, 'error', { error });
      return false;
    });
  } catch (error) {
    log(`Error in buildWithVite: ${error.message}`, 'error', { error });
    return false;
  }
}

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const config = getConfig();
  const defaults = config?.defaults?.static || {};

  // Initialize with defaults from config
  const options = {
    configPath: defaults.configPath || './tailwind.config.js',
    inputPath: defaults.inputPath || './ui/static/css/tailwind.css',
    outputPath: defaults.outputPath || './ui/static/css/tailwind.output.css',
    minify: defaults.minify !== undefined ? defaults.minify : true,
    watch: false,
    help: false,
    files: [],
    parallel: config?.performance?.concurrentBuilds > 1,
    postcss: {
      useConfigFile: config?.postcss?.useConfigFile || false,
      configPath: config?.postcss?.configPath || './postcss.config.js',
      plugins: config?.postcss?.plugins || []
    },
    buildTools: {
      webpack: {
        enabled: config?.buildTools?.webpack?.enabled || false,
        configPath: config?.buildTools?.webpack?.configPath || './webpack.config.js'
      },
      vite: {
        enabled: config?.buildTools?.vite?.enabled || false,
        configPath: config?.buildTools?.vite?.configPath || './vite.config.js'
      }
    },
    configFilePath: null,
    logLevel: config?.logging?.level || 'info'
  };

  // Parse arguments
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--config' && i + 1 < args.length) {
      options.configPath = args[++i];
    } else if (arg === '--input' && i + 1 < args.length) {
      options.inputPath = args[++i];
    } else if (arg === '--output' && i + 1 < args.length) {
      options.outputPath = args[++i];
    } else if (arg === '--watch') {
      options.watch = true;
    } else if (arg === '--no-minify') {
      options.minify = false;
    } else if (arg === '--help' || arg === '-h') {
      options.help = true;
    } else if (arg === '--parallel') {
      options.parallel = true;
    } else if (arg === '--no-parallel') {
      options.parallel = false;
    } else if (arg === '--config-file' && i + 1 < args.length) {
      options.configFilePath = args[++i];
      // Load configuration from specified file
      const fileConfig = loadConfig(options.configFilePath);
      if (fileConfig) {
        // Override defaults with file configuration
        globalConfig = fileConfig;

        // Update options with new config
        const newDefaults = fileConfig?.defaults?.static || {};
        options.configPath = options.configPath || newDefaults.configPath;
        options.inputPath = options.inputPath || newDefaults.inputPath;
        options.outputPath = options.outputPath || newDefaults.outputPath;
        options.minify = options.minify !== undefined ? options.minify : newDefaults.minify;
        options.parallel = options.parallel !== undefined ? options.parallel : (fileConfig?.performance?.concurrentBuilds > 1);
        options.postcss = fileConfig?.postcss || options.postcss;
        options.buildTools = fileConfig?.buildTools || options.buildTools;
        options.logLevel = fileConfig?.logging?.level || options.logLevel;
      }
    } else if (arg === '--log-level' && i + 1 < args.length) {
      const level = args[++i].toLowerCase();
      if (['error', 'warn', 'info', 'debug'].includes(level)) {
        options.logLevel = level;
      } else {
        log(`Invalid log level: ${level}. Using default.`, 'warn');
      }
    } else if (arg === '--postcss-config' && i + 1 < args.length) {
      options.postcss.useConfigFile = true;
      options.postcss.configPath = args[++i];
    } else if (arg === '--webpack' && i + 1 < args.length) {
      options.buildTools.webpack.enabled = true;
      options.buildTools.webpack.configPath = args[++i];
    } else if (arg === '--vite' && i + 1 < args.length) {
      options.buildTools.vite.enabled = true;
      options.buildTools.vite.configPath = args[++i];
    } else if (arg === '--add-file' && i + 3 < args.length) {
      // Format: --add-file <config> <input> <output>
      options.files.push({
        configPath: args[++i],
        inputPath: args[++i],
        outputPath: args[++i],
        minify: options.minify
      });
    }
  }

  // If files were specified, use them instead of single file options
  if (options.files.length === 0 && options.inputPath && options.outputPath) {
    options.files.push({
      configPath: options.configPath,
      inputPath: options.inputPath,
      outputPath: options.outputPath,
      minify: options.minify
    });
  }

  return options;
}

// Display help message
function displayHelp() {
  log(`
Tailwind CSS Utility Script

Usage:
  node tailwind_utils.js [options]

Basic Options:
  --config <path>       Path to tailwind config file (default: ./tailwind.config.js)
  --input <path>        Path to input CSS file (default: ./ui/static/css/tailwind.css)
  --output <path>       Path to output CSS file (default: ./ui/static/css/tailwind.output.css)
  --watch               Watch for changes and rebuild
  --no-minify           Don't minify the output
  --help, -h            Display this help message

Advanced Options:
  --config-file <path>  Path to JSON configuration file
  --log-level <level>   Set log level (error, warn, info, debug)
  --parallel            Build multiple files in parallel
  --no-parallel         Disable parallel builds

Multiple File Support:
  --add-file <config> <input> <output>  Add a file to build (can be used multiple times)

PostCSS Integration:
  --postcss-config <path>  Path to PostCSS config file

Build Tool Integration:
  --webpack <path>      Enable webpack integration with config path
  --vite <path>         Enable Vite integration with config path
  `, 'info');
}

/**
 * Add custom PostCSS plugins
 *
 * @param {Object} options - PostCSS options
 * @param {Array} options.plugins - Array of plugin configurations
 * @returns {Array} - Array of instantiated PostCSS plugins
 */
function loadPostCSSPlugins(options = {}) {
  const plugins = [];

  if (!options.plugins || !Array.isArray(options.plugins)) {
    return [
      require('tailwindcss'),
      require('autoprefixer')
    ];
  }

  for (const plugin of options.plugins) {
    try {
      if (!plugin.name) {
        log(`Invalid plugin configuration: missing name`, 'warn');
        continue;
      }

      // Try to require the plugin
      const pluginModule = require(plugin.name);

      // Initialize the plugin with options
      if (plugin.options) {
        plugins.push(pluginModule(plugin.options));
      } else {
        plugins.push(pluginModule);
      }

      log(`Loaded PostCSS plugin: ${plugin.name}`, 'debug');
    } catch (error) {
      log(`Failed to load PostCSS plugin ${plugin.name}: ${error.message}`, 'error', { error });
    }
  }

  // Ensure tailwindcss and autoprefixer are included
  const hasTailwind = options.plugins.some(p => p.name === 'tailwindcss');
  const hasAutoprefixer = options.plugins.some(p => p.name === 'autoprefixer');

  if (!hasTailwind) {
    plugins.unshift(require('tailwindcss'));
  }

  if (!hasAutoprefixer) {
    plugins.push(require('autoprefixer'));
  }

  return plugins;
}

/**
 * Create a custom PostCSS configuration
 *
 * @param {Object} options - PostCSS options
 * @returns {Object} - PostCSS configuration object
 */
function createPostCSSConfig(options = {}) {
  const plugins = loadPostCSSPlugins(options);

  return {
    plugins
  };
}

// Main function
function main() {
  try {
    const options = parseArgs();

    if (options.help) {
      displayHelp();
      return;
    }

    // Set log level from options
    if (options.logLevel) {
      currentLogLevel = options.logLevel;
    }

    // Get configuration after parsing arguments
    const config = getConfig();

    log(`Building Tailwind CSS with options:`, 'info', {
      files: options.files.length,
      watch: options.watch,
      parallel: options.parallel,
      postcss: !!options.postcss?.useConfigFile,
      webpack: options.buildTools?.webpack?.enabled,
      vite: options.buildTools?.vite?.enabled
    });

    // Handle multiple files if specified
    if (options.files.length > 0) {
      buildMultipleFiles(options);
    } else if (options.buildTools?.webpack?.enabled) {
      buildWithWebpack(options);
    } else if (options.buildTools?.vite?.enabled) {
      buildWithVite(options);
    } else if (options.watch) {
      watchTailwind(options);
    } else {
      buildTailwind(options);
    }
  } catch (error) {
    console.error(`Unexpected error in main function: ${error.message}`);
    process.exit(1);
  }
}

// Run the main function if this file is executed directly
if (require.main === module) {
  main();
}

module.exports = {
  buildTailwind,
  watchTailwind,
  buildAllTailwind,
  buildMultipleFiles,
  buildWithWebpack,
  buildWithVite,
  loadPostCSSPlugins,
  createPostCSSConfig,
  getConfig,
  loadConfig,
  log,
  updateLoggingConfig
};
