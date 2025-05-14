# Test Setup Script Workflow

## Overview

This document describes the GitHub Actions workflow for testing the development environment setup scripts. These scripts are used to set up the development environment for the project, and this workflow ensures they work correctly across different platforms and configurations.

## Workflow File

The workflow is defined in `.github/workflows/test-setup-script.yml` and is designed to test the following setup scripts:

- `enhanced_setup_dev_environment.py`
- `enhanced_setup_dev_environment.bat`
- `enhanced_setup_dev_environment.sh`

## Key Features

### Trigger Conditions

The workflow runs under the following conditions:

- **Push**: To the main branch when setup scripts are modified
- **Pull Request**: To the main branch when setup scripts are modified
- **Manual**: Through workflow_dispatch with configurable parameters

### Configurable Options

When manually triggered, the workflow accepts the following input parameters:

- **platform**: The platform to test on (all, ubuntu, windows, macos)
- **setup_profile**: The setup profile to test (full, minimal, ui-only, backend-only)

### Cross-Platform Testing

The workflow tests the setup scripts on multiple platforms:

- **Ubuntu**: Tests the Python and shell scripts
- **Windows**: Tests the Python and batch scripts
- **macOS**: Tests the Python and shell scripts

### Setup Profile Testing

The workflow tests different setup profiles:

- **Full**: Complete development environment setup
- **Minimal**: Minimal setup with essential components only
- **UI-Only**: Setup for frontend development only
- **Backend-Only**: Setup for backend development only

## Workflow Structure

The workflow consists of the following jobs:

### 1. Test on Ubuntu

Tests the setup scripts on Ubuntu with the following steps:

1. Checkout the repository
2. Set up Python
3. Run the Python setup script
4. Run the shell setup script
5. Verify the setup by checking installed tools and dependencies

### 2. Test on Windows

Tests the setup scripts on Windows with the following steps:

1. Checkout the repository
2. Set up Python
3. Run the Python setup script
4. Run the batch setup script
5. Verify the setup by checking installed tools and dependencies

### 3. Test on macOS

Tests the setup scripts on macOS with the following steps:

1. Checkout the repository
2. Set up Python
3. Run the Python setup script
4. Run the shell setup script
5. Verify the setup by checking installed tools and dependencies

## Usage

### Running Manually

To run the workflow manually:

1. Go to the Actions tab in the GitHub repository
2. Select "Test Setup Script" workflow
3. Click "Run workflow"
4. Select the platform and setup profile
5. Click "Run workflow"

### Viewing Results

To view the results of the workflow:

1. Go to the Actions tab in the GitHub repository
2. Select the workflow run
3. Review the job outputs and logs

## Best Practices

When modifying the setup scripts:

1. **Test Locally**: Test the scripts locally before pushing changes
2. **Run the Workflow**: Run the workflow manually to verify changes
3. **Check All Platforms**: Ensure the scripts work on all supported platforms
4. **Verify All Profiles**: Test all setup profiles to ensure they work correctly

## Troubleshooting

### Common Issues

1. **Script Permissions**: Ensure shell scripts have execute permissions
2. **Path Issues**: Check for hardcoded paths that may not exist on all platforms
3. **Dependency Conflicts**: Verify that dependencies are compatible across platforms
4. **Environment Variables**: Ensure environment variables are set correctly

### Debugging

To debug issues with the setup scripts:

1. Review the workflow logs for error messages
2. Run the scripts locally with verbose output
3. Add debug print statements to the scripts
4. Test individual components of the setup process

## Related Documentation

- [Enhanced Setup](../enhanced_setup.md)
- [Getting Started](../getting-started.md)
- [Contributing](../contributing.md)
