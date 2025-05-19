# CI Environment Detection

This document describes the CI environment detection functionality in the project. It explains how to use the detection scripts and how to simulate different CI environments for testing.

## Overview

The CI environment detection functionality is designed to detect and handle different environments:

- **Operating Systems**: Windows, macOS, Linux, WSL
- **CI environments**: GitHub Actions, Jenkins, GitLab CI, CircleCI, Travis, Azure Pipelines, TeamCity, Bitbucket, AppVeyor, Drone, Buddy, Buildkite, AWS CodeBuild, Vercel, Netlify, Heroku, Semaphore, Codefresh, Woodpecker, Harness, Render, Railway, Fly.io, etc.
- **Container environments**: Docker, Podman, LXC/LXD, Containerd, CRI-O, Docker Compose, Kubernetes, Docker Swarm
- **Cloud environments**: AWS, Azure, GCP, Oracle Cloud (OCI), IBM Cloud, DigitalOcean, Linode, Vultr, Cloudflare
- **Serverless environments**: Lambda, Azure Functions, Cloud Functions

It's designed to be used across the application to ensure consistent environment detection and handling with proper fallbacks.

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
