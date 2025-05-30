# Environment Detection Module

The Environment Detection Module provides a comprehensive way to detect and handle different environments across the application. It consists of both Python and JavaScript implementations that share the same detection logic and provide similar interfaces.

## Overview

The module detects:

- **Operating Systems**: Windows, macOS, Linux, WSL
- **CI environments**: GitHub Actions, Jenkins, GitLab CI, CircleCI, Travis, Azure Pipelines, TeamCity, Bitbucket, AppVeyor, Drone, Buddy, Buildkite, AWS CodeBuild, Vercel, Netlify, Heroku, Semaphore, Codefresh, Woodpecker, Harness, Render, Railway, Fly.io, Codemagic, GitHub Codespaces, Google Cloud Build, Alibaba Cloud DevOps, Huawei Cloud DevCloud, Tencent Cloud CODING, Baidu Cloud CICD, Sourcegraph, Gitpod, Replit, Stackblitz, Glitch, etc.
- **Container environments**: Docker, Podman, LXC/LXD, Containerd, CRI-O, Docker Compose, Kubernetes, Docker Swarm, rkt, Singularity
- **Cloud environments**: AWS, Azure, GCP, Oracle Cloud (OCI), IBM Cloud, DigitalOcean, Linode, Vultr, Cloudflare, Alibaba Cloud, Tencent Cloud, Huawei Cloud
- **Serverless environments**: Lambda, Azure Functions, Cloud Functions
- **Node.js environments**: Development, Production, Test, Staging

## Key Features

- **Comprehensive Detection**: Detects a wide range of CI platforms, container environments, cloud providers, and operating systems.
- **Consistent Interface**: Both Python and JavaScript implementations provide similar interfaces for easy integration.
- **Fallback Mechanisms**: Uses multiple detection methods with fallbacks to ensure reliable detection.
- **Environment Reports**: Generates detailed reports about the detected environment for debugging and logging.
- **Simulation Support**: Includes tools to simulate different environments for testing.
- **Test Integration**: Integrates with testing frameworks to adjust test behavior based on the environment.

## Usage

### JavaScript

```javascript
const { detectEnvironment, createEnvironmentReport } = require('./helpers/environment-detection');

// Get environment information
const env = detectEnvironment();

// Check if running in a CI environment
if (env.isCI) {
  console.log(`Running in CI: ${env.ciPlatform}`);

  // Check for specific CI platforms
  if (env.isGitHubActions) {
    console.log('Running in GitHub Actions');
  } else if (env.isBuildkite) {
    console.log('Running in Buildkite');
  } else if (env.isCodefresh) {
    console.log('Running in Codefresh');
  } else if (env.isSemaphore) {
    console.log('Running in Semaphore');
  } else if (env.isHarness) {
    console.log('Running in Harness');
  }
}

// Check if running in a container
if (env.isContainerized) {
  if (env.isDocker) {
    console.log('Running in Docker');
  } else if (env.isKubernetes) {
    console.log('Running in Kubernetes');
  } else if (env.isRkt) {
    console.log('Running in rkt');
  } else if (env.isContainerd) {
    console.log('Running in containerd');
  } else if (env.isCRIO) {
    console.log('Running in CRI-O');
  } else if (env.isSingularity) {
    console.log('Running in Singularity');
  }
}

// Check if running in a cloud environment
if (env.isCloudEnvironment) {
  if (env.isAWS) {
    console.log('Running in AWS');
  } else if (env.isAzure) {
    console.log('Running in Azure');
  } else if (env.isGCP) {
    console.log('Running in GCP');
  } else if (env.isOracleCloud) {
    console.log('Running in Oracle Cloud');
  } else if (env.isIBMCloud) {
    console.log('Running in IBM Cloud');
  } else if (env.isAlibabaCloud) {
    console.log('Running in Alibaba Cloud');
  } else if (env.isTencentCloud) {
    console.log('Running in Tencent Cloud');
  } else if (env.isHuaweiCloud) {
    console.log('Running in Huawei Cloud');
  }
}

// Create a detailed environment report
createEnvironmentReport('environment-report.txt', { verbose: true });
```

### Python

```python
from scripts.ci.detect_ci_environment import detect_ci_environment

# Get environment information
env_info = detect_ci_environment()

# Check if running in a CI environment
if env_info["ci"]["is_ci"]:
    print(f"Running in CI: {env_info['ci']['ci_platform']}")

# Check if running in a container
if env_info["container"]["is_containerized"]:
    if env_info["container"]["is_docker"]:
        print("Running in Docker")
    elif env_info["container"]["is_kubernetes"]:
        print("Running in Kubernetes")
    elif env_info["container"]["is_podman"]:
        print("Running in Podman")
    elif env_info["container"]["is_rkt"]:
        print("Running in rkt")
    elif env_info["container"]["is_singularity"]:
        print("Running in Singularity")
    elif env_info["container"]["is_crio"]:
        print("Running in CRI-O")
    elif env_info["container"]["is_containerd"]:
        print("Running in containerd")

# Check if running in a cloud environment
if env_info["cloud"]["is_cloud"]:
    if env_info["cloud"]["is_aws"]:
        print("Running in AWS")
    elif env_info["cloud"]["is_azure"]:
        print("Running in Azure")
    elif env_info["cloud"]["is_gcp"]:
        print("Running in GCP")
    elif env_info["cloud"]["is_oci"]:
        print("Running in Oracle Cloud")
    elif env_info["cloud"]["is_ibm_cloud"]:
        print("Running in IBM Cloud")
    elif env_info["cloud"]["is_alibaba_cloud"]:
        print("Running in Alibaba Cloud")
    elif env_info["cloud"]["is_tencent_cloud"]:
        print("Running in Tencent Cloud")
    elif env_info["cloud"]["is_huawei_cloud"]:
        print("Running in Huawei Cloud")
```

## Simulation

You can simulate different environments for testing using the simulation script:

```bash
# Simulate GitHub Actions
python scripts/ci/simulate_ci_environment.py --ci-type github

# Simulate Docker
python scripts/ci/simulate_ci_environment.py --container-type docker

# Simulate AWS
python scripts/ci/simulate_ci_environment.py --cloud-type aws

# Simulate multiple environments
python scripts/ci/simulate_ci_environment.py --ci-type github --container-type docker --cloud-type aws

# Clean up
python scripts/ci/simulate_ci_environment.py --cleanup
```

## Testing

The module includes comprehensive tests to ensure reliable detection:

```bash
# Run Python tests
python -m unittest scripts/ci/test_detect_ci_environment.py

# Run JavaScript tests
cd ui/react_frontend
npm test tests/environment-detection.test.js
```

## Adding Support for New Environments

See the [Adding Support for New CI Platforms](ci-environment-detection.md#adding-support-for-new-ci-platforms) section in the CI Environment Detection documentation for detailed instructions on how to add support for new environments.

## Troubleshooting

See the [Troubleshooting](ci-environment-detection.md#troubleshooting) section in the CI Environment Detection documentation for detailed troubleshooting information.

## Enhanced Features

The Environment Detection Module has been enhanced with the following features:

### Comprehensive Environment Report Generation ✅
- **Detailed Reports**: Generate comprehensive environment reports in both text and JSON formats ✅
- **Customizable Reports**: Configure what information to include in the reports ✅
- **CI-Specific Reports**: Create specialized reports for different CI platforms ✅
- **Container-Aware Reports**: Include detailed container runtime information ✅
- **Cloud-Aware Reports**: Include detailed cloud provider information ✅

### Improved Container Runtime Detection ✅
- **Docker**: Enhanced detection with multiple fallback methods ✅
- **rkt**: Comprehensive detection for rkt containers with detailed logging ✅
- **Containerd**: Improved detection with better error handling ✅

### Enhanced Windows Support (PR 166) ✅
- **Platform-Aware File Access**: Avoid attempting to read Linux-specific files (e.g., `/proc/1/cgroup`) on Windows platforms ✅
- **Improved Error Handling**: Enhanced error handling for system information that may not be available in all environments ✅
- **Memory and CPU Detection**: Added comprehensive system information detection with proper fallbacks for Windows ✅
- **Container Detection**: Platform-aware container detection that only checks Linux-specific files on Linux platforms ✅

### Enhanced CI Environment Helper (PR 166) ✅
- **Syntax Error Fixes**: Resolved template literal syntax errors that were preventing CI test execution ✅
- **Null Safety**: Added proper null checks for memory and CPU information to prevent runtime errors ✅
- **Enhanced Reporting**: Improved CI environment reporting with better error handling and fallbacks ✅
- **System Information**: Enhanced system information collection with proper error handling ✅

### Unified Environment Module Integration (PR 166) ✅
- **Consistent Interface**: Unified environment detection across all test files and modules ✅
- **Enhanced Logging**: Improved logging and debugging capabilities for environment detection ✅
- **Cross-Platform Compatibility**: Ensured consistent behavior across Windows, macOS, and Linux platforms ✅
- **Test Integration**: Enhanced integration with testing frameworks and CI environments ✅

## License

This module is part of the pAIssive_income project and is licensed under the same terms.
