/**
 * Test script for enhanced Tailwind CSS utilities
 *
 * This script tests the enhanced features of the Tailwind CSS build system.
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const {
  buildTailwind,
  buildAllTailwind,
  buildMultipleFiles,
  getConfig,
  loadConfig,
  createPostCSSConfig,
  loadPostCSSPlugins,
  updateLoggingConfig
} = require('./tailwind_utils');

// Suppress console output during tests
const originalConsoleLog = console.log;
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;
const originalConsoleDebug = console.debug;

function suppressConsole() {
  console.log = () => { };
  console.error = () => { };
  console.warn = () => { };
  console.debug = () => { };
}

function restoreConsole() {
  console.log = originalConsoleLog;
  console.error = originalConsoleError;
  console.warn = originalConsoleWarn;
  console.debug = originalConsoleDebug;
}

// Test configuration loading
function testConfigLoading() {
  console.log('Testing configuration loading...');

  // Create a temporary config file
  const tempConfigPath = path.join(__dirname, 'temp_config.json');
  const configData = {
    defaults: {
      static: {
        configPath: './test.config.js',
        inputPath: './test.input.css',
        outputPath: './test.output.css',
        minify: false
      }
    },
    logging: {
      level: 'error'
    }
  };

  fs.writeFileSync(tempConfigPath, JSON.stringify(configData, null, 2));

  try {
    const config = loadConfig(tempConfigPath);
    assert.deepStrictEqual(config, configData, 'Config loading failed');
    console.log('✅ Configuration loading test passed');
  } catch (error) {
    console.error('❌ Configuration loading test failed:', error.message);
  } finally {
    // Clean up
    if (fs.existsSync(tempConfigPath)) {
      fs.unlinkSync(tempConfigPath);
    }
  }
}

// Test PostCSS plugin loading
function testPostCSSPlugins() {
  console.log('Testing PostCSS plugin loading...');

  try {
    // Test with default plugins
    const defaultPlugins = loadPostCSSPlugins({});
    assert(Array.isArray(defaultPlugins), 'Default plugins should be an array');
    assert(defaultPlugins.length >= 2, 'Default plugins should include at least tailwind and autoprefixer');

    // Test with custom plugins
    const customPlugins = loadPostCSSPlugins({
      plugins: [
        { name: 'tailwindcss', options: {} },
        { name: 'autoprefixer', options: {} },
        { name: 'postcss-preset-env', options: { features: { 'nesting-rules': true } } }
      ]
    });

    assert(Array.isArray(customPlugins), 'Custom plugins should be an array');
    assert(customPlugins.length >= 3, 'Custom plugins should include all specified plugins');

    console.log('✅ PostCSS plugin loading test passed');
  } catch (error) {
    console.error('❌ PostCSS plugin loading test failed:', error.message);
  }
}

// Test PostCSS config creation
function testPostCSSConfig() {
  console.log('Testing PostCSS config creation...');

  try {
    const config = createPostCSSConfig({
      plugins: [
        { name: 'tailwindcss', options: {} },
        { name: 'autoprefixer', options: {} }
      ]
    });

    assert(config.plugins, 'Config should have plugins property');
    assert(Array.isArray(config.plugins), 'Plugins should be an array');
    assert(config.plugins.length >= 2, 'Config should have at least 2 plugins');

    console.log('✅ PostCSS config creation test passed');
  } catch (error) {
    console.error('❌ PostCSS config creation test failed:', error.message);
  }
}

// Run all tests
function runTests() {
  console.log('Running Tailwind CSS utility tests...');

  // Run tests
  testConfigLoading();
  testPostCSSPlugins();
  testPostCSSConfig();

  console.log('All tests completed');
}

// Run tests if this file is executed directly
if (require.main === module) {
  runTests();
}

module.exports = {
  runTests
};
