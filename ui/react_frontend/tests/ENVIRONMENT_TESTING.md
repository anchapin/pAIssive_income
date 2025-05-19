# Environment-Specific Testing

This document explains how to run and create tests for different environments in the React frontend.

## Overview

The React frontend is designed to run in various environments:

1. **Operating Systems**: Windows, macOS, Linux
2. **CI Environments**: GitHub Actions, Jenkins, GitLab CI, etc.
3. **Docker Containers**
4. **Node Environments**: Development, Production, Test

The environment-specific tests ensure that the application behaves correctly in all these environments.

## Test Structure

The environment-specific tests are organized into several files:

- `environment_detection.spec.js` - Tests for environment detection
- `platform_specific.spec.js` - Tests for platform-specific behavior (Windows, macOS, Linux)
- `ci_environment.spec.js` - Tests for CI environment-specific behavior
- `docker_environment.spec.js` - Tests for Docker environment-specific behavior
- `environment_ui.spec.jsx` - Tests for environment-specific UI behavior
- `environment_api.spec.js` - Tests for environment-specific API behavior

## Helper Modules

The tests use several helper modules that are mocked in the test files:

- `helpers/environment-detection.js` - Detects the current environment (OS, CI, Docker, Node)
- `helpers/platform-specific.js` - Handles platform-specific behavior (paths, commands)
- `helpers/ci-environment.js` - Handles CI environment-specific behavior (GitHub Actions, Jenkins, etc.)
- `helpers/docker-environment.js` - Handles Docker environment-specific behavior

These modules provide a consistent way to detect and handle different environments across the application.

## Running Tests

### Running All Environment Tests

To run all environment-specific tests:

```bash
npm run test:environments
# or
pnpm test:environments
```

This will run all the environment-specific tests, including:
- Environment detection tests
- Platform-specific tests
- CI environment tests
- Docker environment tests
- Environment-specific UI tests
- Environment-specific API tests

### Running Specific Environment Tests

To run tests for specific environments:

```bash
# Environment detection tests
pnpm test:environment:detection

# Platform-specific tests
pnpm test:platform

# CI environment tests
pnpm test:ci-env

# Docker environment tests
pnpm test:docker-env

# Environment-specific UI tests
pnpm test:environment:ui

# Environment-specific API tests
pnpm test:environment:api
```

### Testing Specific Platforms

To test specific platforms by mocking the platform detection:

```bash
# Windows tests
pnpm test:windows

# macOS tests
pnpm test:macos

# Linux tests
pnpm test:linux
```

These commands use the `MOCK_PLATFORM` environment variable to simulate different operating systems.

## Adding New Tests

When adding new tests for different environments:

1. **Use the helper modules**: The helper modules provide functions for detecting and handling different environments.
2. **Mock the environment**: Use the Vitest mocking capabilities to simulate different environments:
   ```javascript
   // Mock modules
   vi.mock('fs');
   vi.mock('path');
   vi.mock('os');

   // Set up mocks
   os.platform.mockReturnValue('win32'); // Mock Windows
   process.env.CI = 'true'; // Mock CI environment
   fs.existsSync.mockImplementation((path) => path === '/.dockerenv'); // Mock Docker
   ```
3. **Test all relevant environments**: Make sure to test all relevant environments (Windows, macOS, Linux, CI, Docker, etc.).
4. **Add test scripts**: Add new test scripts to `package.json` for running the new tests.
5. **Use proper file naming**: Name test files with `.spec.js` or `.spec.jsx` extension to ensure they're picked up by Vitest.
6. **Test UI components**: For UI components, use `@testing-library/react` to render and test components in different environments.

## Environment Detection

The `detectEnvironment` function in `helpers/environment-detection.js` detects the current environment and returns an object with environment information:

```javascript
const env = detectEnvironment();

// Operating System
console.log(`Platform: ${env.platform}`);
console.log(`Windows: ${env.isWindows}`);
console.log(`macOS: ${env.isMacOS}`);
console.log(`Linux: ${env.isLinux}`);

// CI Environment
console.log(`CI: ${env.isCI}`);
console.log(`GitHub Actions: ${env.isGitHubActions}`);
console.log(`Jenkins: ${env.isJenkins}`);
console.log(`GitLab CI: ${env.isGitLabCI}`);
console.log(`Circle CI: ${env.isCircleCI}`);
console.log(`Travis CI: ${env.isTravis}`);
console.log(`Azure Pipelines: ${env.isAzurePipelines}`);
console.log(`TeamCity: ${env.isTeamCity}`);

// Docker Environment
console.log(`Docker: ${env.isDocker}`);

// Node Environment
console.log(`Development: ${env.isDevelopment}`);
console.log(`Production: ${env.isProduction}`);
console.log(`Test: ${env.isTest}`);

// System Info
console.log(`Node Version: ${env.nodeVersion}`);
console.log(`Architecture: ${env.architecture}`);
console.log(`OS Type: ${env.osType}`);
console.log(`OS Release: ${env.osRelease}`);
console.log(`Temp Directory: ${env.tmpDir}`);
console.log(`Home Directory: ${env.homeDir}`);
console.log(`Working Directory: ${env.workingDir}`);
```

## Platform-Specific Behavior

The `platform-specific.js` helper module provides functions for handling platform-specific behavior:

```javascript
const { getPlatformSpecificPath, executeCommand } = require('./helpers/platform-specific');

// Get platform-specific path
const path = getPlatformSpecificPath('dir', 'file.txt');
// On Windows: 'dir\\file.txt'
// On Unix: 'dir/file.txt'

// Execute platform-specific command
const output = executeCommand('list-files');
// On Windows: Executes 'dir'
// On Unix: Executes 'ls -la'
```

## CI Environment Behavior

The `ci-environment.js` helper module provides functions for handling CI environment-specific behavior:

```javascript
const { setupCIEnvironment, createCIReport } = require('./helpers/ci-environment');

// Set up CI environment
const result = setupCIEnvironment();
console.log(`CI setup success: ${result.success}`);
console.log(`CI type: ${result.ciType}`);

// Create CI report
const report = createCIReport();
console.log(report);
```

## Docker Environment Behavior

The `docker-environment.js` helper module provides functions for handling Docker environment-specific behavior:

```javascript
const { setupDockerEnvironment, createDockerReport } = require('./helpers/docker-environment');

// Set up Docker environment
const result = setupDockerEnvironment();
console.log(`Docker setup success: ${result.success}`);
console.log(`Is Docker: ${result.isDocker}`);

// Create Docker report
const report = createDockerReport();
console.log(report);
```

## Troubleshooting

If tests fail in specific environments:

1. **Check the environment detection**: Make sure the environment is correctly detected.
2. **Check the mocks**: Make sure the mocks are correctly set up.
3. **Check the test environment**: Make sure the test environment is correctly set up.
4. **Check the test output**: Look for error messages in the test output.
5. **Try running in a real environment**: If possible, try running the tests in a real environment.

## CI Integration

The environment-specific tests are integrated with CI pipelines:

1. **GitHub Actions**: The tests run on Windows, macOS, and Linux.
2. **Docker**: The tests run in Docker containers.
3. **Jenkins**: The tests run on Jenkins.

The CI environment tests automatically detect the CI environment and adjust their behavior accordingly. For example, in GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [16.x, 18.x]

    steps:
    - uses: actions/checkout@v3
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'pnpm'
    - run: pnpm install
    - run: pnpm test:environments
```

This workflow runs the environment tests on multiple operating systems and Node.js versions.

## Adding New Environments

To add support for a new environment:

1. **Update the environment detection**: Add detection for the new environment in `helpers/environment-detection.js`.
2. **Add environment-specific behavior**: Add functions for handling the new environment in a new helper module.
3. **Add tests**: Add tests for the new environment.
4. **Add test scripts**: Add new test scripts to `package.json` for running the new tests.
5. **Update documentation**: Update this document with information about the new environment.
