/**
 * Install script for the enhanced mock path-to-regexp
 * This script handles installing the mock in the correct location
 * and setting up the necessary files and permissions.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Enhanced environment detection
const env = {
  isCI: process.env.CI === 'true' || process.env.GITHUB_ACTIONS === 'true' ||
        process.env.TF_BUILD || process.env.JENKINS_URL ||
        process.env.GITLAB_CI || process.env.CIRCLECI,
  isDocker: fs.existsSync('/.dockerenv') || fs.existsSync('/run/.containerenv'),
  verbose: process.env.VERBOSE_LOGGING === 'true',
  tempDir: process.env.RUNNER_TEMP || os.tmpdir(),
  workDir: process.env.GITHUB_WORKSPACE || process.cwd()
};

function debug(msg) {
  if (env.verbose) {
    console.log(`[path-to-regexp-install] ${msg}`);
  }
}

function installMock() {
  debug('Starting mock installation');

  // Prioritized locations to try installing the mock
  const locations = [
    path.join(process.cwd(), 'node_modules', 'path-to-regexp'),
    path.join(process.cwd(), 'node_modules', '.cache', 'path-to-regexp'),
    path.join(env.workDir, 'node_modules', 'path-to-regexp'),
    path.join(env.tempDir, 'node_modules', 'path-to-regexp')
  ];

  for (const location of locations) {
    try {
      debug(`Trying to install at: ${location}`);

      // Create the directory structure
      fs.mkdirSync(location, { recursive: true });
      debug('Created directory structure');

      // Copy the mock implementation
      const sourceFile = path.join(__dirname, 'index.js');
      fs.copyFileSync(sourceFile, path.join(location, 'index.js'));
      debug('Copied mock implementation');

      // Create package.json
      const packageJson = {
        name: 'path-to-regexp',
        version: '0.0.0',
        main: 'index.js',
        description: 'Mock implementation for CI compatibility',
        license: 'MIT'
      };

      fs.writeFileSync(
        path.join(location, 'package.json'),
        JSON.stringify(packageJson, null, 2)
      );
      debug('Created package.json');

      // Set permissions in CI environment
      if (env.isCI || env.isDocker) {
        fs.chmodSync(location, 0o777);
        fs.chmodSync(path.join(location, 'index.js'), 0o666);
        fs.chmodSync(path.join(location, 'package.json'), 0o666);
        debug('Set CI permissions');
      }

      debug('Successfully installed mock');
      return true;
    } catch (error) {
      debug(`Failed to install at ${location}: ${error.message}`);
      // Continue to next location
      continue;
    }
  }

  debug('Failed to install mock in any location');
  return false;
}

if (require.main === module) {
  // Script was run directly
  const success = installMock();
  process.exit(success ? 0 : 1);
} else {
  // Script was required as a module
  module.exports = installMock;
}
