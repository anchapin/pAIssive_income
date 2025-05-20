/**
 * Auto-installer for enhanced path-to-regexp mock
 */

const fs = require('fs');
const path = require('path');

// Environment detection
const env = {
  isCI: process.env.CI === 'true' || process.env.GITHUB_ACTIONS === 'true',
  isDocker: fs.existsSync('/.dockerenv') || fs.existsSync('/run/.containerenv'),
  workDir: process.env.GITHUB_WORKSPACE || process.cwd(),
  tempDir: process.env.RUNNER_TEMP || require('os').tmpdir()
};

function installMock() {
  console.log('Installing enhanced path-to-regexp mock...');

  const locations = [
    path.join(env.workDir, 'node_modules', 'path-to-regexp'),
    path.join(env.workDir, '.cache', 'path-to-regexp'),
    path.join(env.tempDir, 'path-to-regexp')
  ];

  for (const location of locations) {
    try {
      if (!fs.existsSync(location)) {
        fs.mkdirSync(location, { recursive: true });
      }

      // Copy mock files
      const sourceDir = __dirname;
      ['index.js', 'package.json', 'README.md'].forEach(file => {
        fs.copyFileSync(
          path.join(sourceDir, file),
          path.join(location, file)
        );
      });

      console.log(`Successfully installed mock at ${location}`);
      return true;
    } catch (error) {
      console.warn(`Failed to install at ${location}:`, error.message);
    }
  }

  throw new Error('Failed to install mock in any location');
}

// Auto-install in CI environments
if (env.isCI || env.isDocker) {
  try {
    installMock();
    console.log('Mock installation complete');
  } catch (error) {
    console.error('Mock installation failed:', error.message);
    process.exit(1);
  }
}

module.exports = { installMock };
