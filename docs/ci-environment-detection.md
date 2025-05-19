# CI Environment Detection

This document describes the CI environment detection functionality in the project. It explains how to use the detection scripts and how to simulate different CI environments for testing.

## Overview

The CI environment detection functionality is designed to detect and handle different environments:

- **Operating Systems**: Windows, macOS, Linux, WSL
- **CI environments**: GitHub Actions, Jenkins, GitLab CI, CircleCI, Travis, Azure Pipelines, TeamCity, Bitbucket, AppVeyor, Drone, Buddy, Buildkite, AWS CodeBuild, Vercel, Netlify, Heroku, Semaphore, Codefresh, Woodpecker, Harness, Render, Railway, Fly.io, Codemagic, GitHub Codespaces, Google Cloud Build, Alibaba Cloud DevOps, Huawei Cloud DevCloud, Tencent Cloud CODING, Baidu Cloud CICD, Sourcegraph, Gitpod, Replit, Stackblitz, Glitch, etc.
- **Container environments**: Docker, Podman, LXC/LXD, Containerd, CRI-O, Docker Compose, Kubernetes, Docker Swarm
- **Cloud environments**: AWS, Azure, GCP, Oracle Cloud (OCI), IBM Cloud, DigitalOcean, Linode, Vultr, Cloudflare
- **Serverless environments**: Lambda, Azure Functions, Cloud Functions

It's designed to be used across the application to ensure consistent environment detection and handling with proper fallbacks.

## Unified Environment Detection Module

The unified environment detection module provides a consistent way to detect and handle different environments across the application. It consists of both Python and JavaScript implementations that share the same detection logic and provide similar interfaces.

### Key Features

- **Comprehensive Detection**: Detects a wide range of CI platforms, container environments, cloud providers, and operating systems.
- **Consistent Interface**: Both Python and JavaScript implementations provide similar interfaces for easy integration.
- **Fallback Mechanisms**: Uses multiple detection methods with fallbacks to ensure reliable detection.
- **Environment Reports**: Generates detailed reports about the detected environment for debugging and logging.
- **Simulation Support**: Includes tools to simulate different environments for testing.
- **Test Integration**: Integrates with testing frameworks to adjust test behavior based on the environment.

### Use Cases

- **CI/CD Pipelines**: Adjust build and deployment processes based on the CI platform.
- **Testing**: Skip or modify tests based on the environment (e.g., skip browser tests in headless environments).
- **Configuration**: Load environment-specific configuration.
- **Logging**: Include environment information in logs for debugging.
- **Error Handling**: Provide environment context in error reports.
- **Feature Flags**: Enable or disable features based on the environment.
- **Performance Optimization**: Optimize performance based on the available resources in different environments.

## Python Implementation

### Using the Detection Script

The Python implementation is available in the `scripts/ci/detect_ci_environment.py` script. You can use it directly from the command line:

```bash
# Basic usage
python scripts/ci/detect_ci_environment.py

# Output in JSON format
python scripts/ci/detect_ci_environment.py --json

# Include verbose output
python scripts/ci/detect_ci_environment.py --verbose

# Create CI directories
python scripts/ci/detect_ci_environment.py --create-dirs
```

### Using the Python Module

You can also import the detection functionality in your Python scripts:

```python
from scripts.ci import detect_ci_environment

# Detect the current environment
env_info = detect_ci_environment()

# Check if running in a CI environment
if env_info["ci"]["is_ci"]:
    print(f"Running in {env_info['ci']['ci_platform']} CI environment")

# Check if running in a container
if env_info["container"]["is_containerized"]:
    if env_info["container"]["is_docker"]:
        print("Running in Docker container")
    elif env_info["container"]["is_kubernetes"]:
        print("Running in Kubernetes pod")

# Check if running in a cloud environment
if env_info["cloud"]["is_cloud"]:
    if env_info["cloud"]["is_aws"]:
        print("Running in AWS")
    elif env_info["cloud"]["is_azure"]:
        print("Running in Azure")
    elif env_info["cloud"]["is_gcp"]:
        print("Running in GCP")
```

## JavaScript Implementation

### Using the Detection Module

The JavaScript implementation is available in the `ui/react_frontend/tests/helpers/environment-detection.js` module. You can import it in your JavaScript files:

```javascript
const { detectEnvironment, createEnvironmentReport } = require('./helpers/environment-detection');

// Detect the current environment
const env = detectEnvironment();

// Check if running in a CI environment
if (env.isCI) {
  console.log(`Running in ${env.isGitHubActions ? 'GitHub Actions' :
                            env.isJenkins ? 'Jenkins' :
                            env.isGitLabCI ? 'GitLab CI' :
                            'generic'} CI environment`);
}

// Check if running in a container
if (env.isContainerized) {
  if (env.isDocker) {
    console.log('Running in Docker container');
  } else if (env.isPodman) {
    console.log('Running in Podman container');
  } else if (env.isLXC) {
    console.log('Running in LXC/LXD container');
  } else if (env.isContainerd) {
    console.log('Running in Containerd container');
  } else if (env.isCRIO) {
    console.log('Running in CRI-O container');
  } else if (env.isKubernetes) {
    console.log('Running in Kubernetes pod');

    // Check Kubernetes distribution
    if (env.isOpenShift) {
      console.log('Running on OpenShift');
    } else if (env.isGKE) {
      console.log('Running on Google Kubernetes Engine');
    } else if (env.isEKS) {
      console.log('Running on Amazon EKS');
    } else if (env.isAKS) {
      console.log('Running on Azure Kubernetes Service');
    }
  } else if (env.isDockerCompose) {
    console.log('Running in Docker Compose environment');
  } else if (env.isDockerSwarm) {
    console.log('Running in Docker Swarm environment');
  }
}

// Check if running in a cloud environment
if (env.isCloudEnvironment) {
  if (env.isAWS) {
    console.log('Running in AWS');

    // Check AWS services
    if (env.isAWSLambda) {
      console.log('Running in AWS Lambda');
    } else if (env.isAWSECS) {
      console.log('Running in AWS ECS');
    } else if (env.isAWSFargate) {
      console.log('Running in AWS Fargate');
    }
  } else if (env.isAzure) {
    console.log('Running in Azure');

    // Check Azure services
    if (env.isAzureFunctions) {
      console.log('Running in Azure Functions');
    } else if (env.isAzureAppService) {
      console.log('Running in Azure App Service');
    }
  } else if (env.isGCP) {
    console.log('Running in GCP');

    // Check GCP services
    if (env.isGCPCloudFunctions) {
      console.log('Running in GCP Cloud Functions');
    } else if (env.isGCPCloudRun) {
      console.log('Running in GCP Cloud Run');
    }
  } else if (env.isOCI) {
    console.log('Running in Oracle Cloud Infrastructure');
  } else if (env.isIBMCloud) {
    console.log('Running in IBM Cloud');
  } else if (env.isDigitalOcean) {
    console.log('Running in DigitalOcean');
  } else if (env.isLinode) {
    console.log('Running in Linode');
  } else if (env.isVultr) {
    console.log('Running in Vultr');
  } else if (env.isCloudflare) {
    console.log('Running in Cloudflare');
  }
}

// Create an environment report
const report = createEnvironmentReport();
console.log(report);

// Create a JSON environment report
const jsonReport = createEnvironmentReport(null, { formatJson: true });
console.log(JSON.parse(jsonReport));

// Save the report to a file
createEnvironmentReport('environment-report.txt');
```

## Simulating CI Environments

You can simulate different CI environments for testing using the `scripts/ci/simulate_ci_environment.py` script:

```bash
# Simulate GitHub Actions environment
python scripts/ci/simulate_ci_environment.py --ci-type github

# Simulate Jenkins environment
python scripts/ci/simulate_ci_environment.py --ci-type jenkins

# Simulate Docker environment
python scripts/ci/simulate_ci_environment.py --container-type docker

# Simulate Kubernetes environment
python scripts/ci/simulate_ci_environment.py --container-type kubernetes

# Simulate AWS environment
python scripts/ci/simulate_ci_environment.py --cloud-type aws

# Simulate AWS Lambda environment
python scripts/ci/simulate_ci_environment.py --cloud-type aws-lambda

# Simulate multiple environments
python scripts/ci/simulate_ci_environment.py --ci-type github --container-type docker --cloud-type aws

# Clean up simulated environment
python scripts/ci/simulate_ci_environment.py --cleanup
```

## Testing the Environment Detection

You can test the environment detection functionality using the provided test scripts:

```bash
# Test the Python implementation
python -m unittest scripts/ci/test_detect_ci_environment.py

# Test the JavaScript implementation
cd ui/react_frontend
npm test tests/environment-detection.test.js
```

## CI Environment Variables

The following environment variables are set in the GitHub workflow file for Linux/macOS runners:

```yaml
CI: true
CI_ENVIRONMENT: true
CI_PLATFORM: github
CI_OS: $(uname -s)
CI_ARCH: $(uname -m)
CI_PYTHON_VERSION: $(python --version | cut -d' ' -f2)
CI_NODE_VERSION: $(node --version)
CI_RUNNER_OS: ${{ runner.os }}
CI_WORKSPACE: ${{ github.workspace }}
```

These variables can be used in your scripts to detect the CI environment and adjust behavior accordingly.

## CI Directories

The following directories are created in the CI environment:

- `ci-reports`: For test reports, coverage reports, etc.
- `ci-artifacts`: For build artifacts, binaries, etc.
- `ci-logs`: For log files
- `ci-temp`: For temporary files
- `ci-cache`: For cached files

These directories can be used to store files that need to be shared between different steps in the CI workflow.

## Playwright Integration

The environment detection functionality is integrated with Playwright for end-to-end testing. This allows tests to adjust their behavior based on the detected environment.

### Using the Playwright Environment Module

The Playwright environment module is available in the `ui/react_frontend/tests/helpers/playwright-environment.js` file. It provides functions for configuring Playwright based on the detected environment:

```javascript
const { configurePlaywright, createPlaywrightEnvironmentReport } = require('./helpers/playwright-environment');

// Configure Playwright based on the detected environment
const playwrightConfig = configurePlaywright({ verbose: true });

// Create a Playwright environment report
const report = createPlaywrightEnvironmentReport({ filePath: 'playwright-report/environment-report.txt' });
```

### Using Environment-Specific Test Fixtures

The environment-specific test fixtures are available in the `ui/react_frontend/tests/fixtures/environment-fixtures.ts` file. They provide fixtures that can be used in Playwright tests:

```typescript
import { test, expect, skipInCI, runInCI } from '../fixtures/environment-fixtures';

// Test that runs in all environments
test('basic test', async ({ page, environmentInfo }) => {
  // Log the detected environment
  console.log(`Running in ${environmentInfo.platform} environment`);

  // Navigate to the home page
  await page.goto('/');

  // Take a screenshot with environment info in the filename
  await page.screenshotWithEnvironmentInfo({
    path: `test-results/home-page.png`,
    fullPage: true
  });
});

// Test that runs only in CI environments
runInCI('CI-only test', async ({ page, environmentInfo }) => {
  // This test only runs in CI environments
  expect(environmentInfo.isCI).toBeTruthy();
});

// Test that skips in CI environments
skipInCI('test that skips in CI environments', async ({ page, environmentInfo }) => {
  // This test will not run in CI environments
  expect(environmentInfo.isCI).toBeFalsy();
});
```

### Environment-Specific Test Artifacts

The environment-specific test fixtures provide a `testArtifacts` fixture that can be used to create and manage test artifacts:

```typescript
test('test artifacts', async ({ testArtifacts, environmentInfo }) => {
  // Save a test artifact
  const filePath = await testArtifacts.saveFile(
    'test-info.txt',
    `Test run at ${new Date().toISOString()}\n` +
    `Platform: ${environmentInfo.platform}\n` +
    `CI: ${environmentInfo.isCI ? 'Yes' : 'No'}\n`
  );

  // Save environment report
  const reportPath = await testArtifacts.saveEnvironmentReport();

  console.log(`Saved test artifact to ${filePath}`);
  console.log(`Saved environment report to ${reportPath}`);
});
```

## Troubleshooting

If you encounter issues with the environment detection, try the following:

1. Run the detection script with the `--verbose` flag to get more information:
   ```bash
   python scripts/ci/detect_ci_environment.py --verbose
   ```

2. Check the environment variables in your CI environment:
   ```bash
   env | grep -i ci
   ```

3. Check if the detection script can access the necessary files:
   ```bash
   ls -la /.dockerenv
   ls -la /proc/1/cgroup
   ls -la /var/run/secrets/kubernetes.io
   ```

4. Try simulating the environment locally:
   ```bash
   python scripts/ci/simulate_ci_environment.py --ci-type github
   ```

5. Run the test script to verify the detection functionality:
   ```bash
   python -m unittest scripts/ci/test_detect_ci_environment.py
   ```

6. For JavaScript/Playwright issues, run the environment detection tests:
   ```bash
   cd ui/react_frontend
   npm test tests/environment-detection.test.js
   ```

7. Create an environment report to see what's being detected:
   ```javascript
   const { createEnvironmentReport } = require('./helpers/environment-detection');
   createEnvironmentReport('environment-report.txt', { verbose: true });
   ```

### Common Issues and Solutions

#### Environment Not Detected Correctly

If the environment is not detected correctly, check the following:

1. **Missing Environment Variables**: Some CI platforms require specific environment variables to be set. Check the documentation for your CI platform to ensure all required variables are set.

2. **File Access Issues**: Some detection methods rely on accessing specific files (e.g., `/.dockerenv`, `/proc/1/cgroup`). Ensure the script has permission to access these files.

3. **Multiple Environments**: If you're running in multiple environments (e.g., Docker container in a CI environment), the detection might prioritize one environment over another. Use the environment report to see all detected environments.

#### New CI Platforms

For newly added CI platforms (Codemagic, GitHub Codespaces, Google Cloud Build, etc.), ensure that:

1. **Environment Variables**: The platform-specific environment variables are set correctly. Check the platform's documentation for the list of available variables.

2. **Detection Order**: The detection order might affect which platform is detected first. If you're running in multiple environments, the first detected platform will be reported as the primary CI platform.

3. **Custom Variables**: You can set custom environment variables to force detection of a specific platform:
   ```bash
   export CI_PLATFORM=github-codespaces
   export CI_TYPE=github-codespaces
   ```

#### Container and Cloud Environments

For container and cloud environments, check:

1. **Container Runtime**: Different container runtimes (Docker, Podman, LXC, etc.) have different detection methods. Ensure the correct runtime is detected.

2. **Cloud Provider**: Cloud providers have specific environment variables and metadata services. Ensure the script can access these services.

3. **Serverless Environments**: Serverless environments have limited file system access. Ensure the detection methods work in these environments.

### Getting Help

If you're still having issues, try the following:

1. **Check the Documentation**: The documentation for your CI platform might have information about environment variables and detection methods.

2. **Create an Issue**: Create an issue in the project repository with the environment report and a description of the problem.

3. **Contact Support**: Contact the support team for your CI platform for help with platform-specific issues.

## Adding Support for New CI Platforms

If you need to add support for a new CI platform, follow these steps:

### 1. Research the CI Platform

1. **Identify Environment Variables**: Find out what environment variables are set by the CI platform. Check the platform's documentation or run a test job that prints all environment variables.

2. **Identify Detection Methods**: Determine how to detect the CI platform. This usually involves checking for specific environment variables or files.

3. **Gather Sample Data**: If possible, gather sample data from the CI platform, such as environment variables, file paths, and other relevant information.

### 2. Update the JavaScript Implementation

1. **Add Detection Logic**: Add detection logic to the `detectEnvironment` function in `ui/react_frontend/tests/helpers/environment-detection.js`:

   ```javascript
   // New CI platform detection
   const isNewPlatform = !!process.env.NEW_PLATFORM_VAR ||
                        !!process.env.ANOTHER_NEW_PLATFORM_VAR ||
                        (process.env.CI_PLATFORM === 'new-platform') ||
                        (process.env.CI_TYPE === 'new-platform');
   ```

2. **Add to Return Object**: Add the new platform to the return object:

   ```javascript
   return {
     // ...
     isNewPlatform,
     // ...
   };
   ```

3. **Update JSON Report**: Add the new platform to the JSON report:

   ```javascript
   ciEnvironment: {
     // ...
     isNewPlatform: env.isNewPlatform,
     // ...
   }
   ```

4. **Update Text Report**: Add the new platform to the text report:

   ```javascript
   CI Environment:
   // ...
   - New Platform: ${env.isNewPlatform ? 'Yes' : 'No'}
   // ...
   ```

### 3. Update the Python Implementation

1. **Add Detection Logic**: Add detection logic to the `detect_ci_environment` function in `scripts/ci/detect_ci_environment.py`:

   ```python
   # New CI platform detection
   elif os.environ.get("NEW_PLATFORM_VAR") or os.environ.get("ANOTHER_NEW_PLATFORM_VAR"):
       ci_info["ci_type"] = "new-platform"
       ci_info["ci_platform"] = "New Platform"
       ci_info["ci_environment_variables"] = {
           key: value
           for key, value in os.environ.items()
           if key.startswith("NEW_PLATFORM_")
       }
   ```

2. **Update CI Detection**: Add the new platform to the CI detection logic:

   ```python
   "is_ci": (
       # ...
       or os.environ.get("NEW_PLATFORM_VAR") is not None
       or os.environ.get("ANOTHER_NEW_PLATFORM_VAR") is not None
       # ...
   ),
   ```

### 4. Update the Simulation Script

1. **Add Simulation Logic**: Add simulation logic to the `simulate_ci_environment.py` script:

   ```python
   def setup_new_platform():
       """Set up environment variables for the new platform."""
       return {
           "CI": "true",
           "NEW_PLATFORM_VAR": "true",
           "NEW_PLATFORM_BUILD_ID": "12345",
           "NEW_PLATFORM_JOB_ID": "67890",
           # Add other relevant environment variables
       }
   ```

2. **Update the `get_ci_env_vars` Function**: Add the new platform to the `get_ci_env_vars` function:

   ```python
   def get_ci_env_vars(ci_type: str) -> Dict[str, str]:
       # ...
       elif ci_type == "new-platform":
           return setup_new_platform()
       # ...
   ```

### 5. Update the Documentation

1. **Update the Overview**: Add the new platform to the list of supported CI platforms.

2. **Add Platform-Specific Information**: Add platform-specific information to the documentation, such as environment variables, detection methods, and any special considerations.

3. **Update the Troubleshooting Section**: Add platform-specific troubleshooting information if needed.

### 6. Test the Implementation

1. **Simulate the Environment**: Test the implementation by simulating the environment:

   ```bash
   python scripts/ci/simulate_ci_environment.py --ci-type new-platform
   ```

2. **Run the Detection Script**: Run the detection script to verify that the new platform is detected correctly:

   ```bash
   python scripts/ci/detect_ci_environment.py --verbose
   ```

3. **Run the Tests**: Run the tests to verify that the implementation works correctly:

   ```bash
   python -m unittest scripts/ci/test_detect_ci_environment.py
   ```

### 7. Submit a Pull Request

1. **Create a Branch**: Create a branch for your changes.

2. **Commit Your Changes**: Commit your changes with a descriptive commit message.

3. **Create a Pull Request**: Create a pull request with a description of the changes and any relevant information about the new platform.
