# GitHub Actions Test Workflow

This document provides detailed information about the Python Tests workflow used in our GitHub Actions CI/CD pipeline.

## Overview

The Python Tests workflow (`.github/workflows/test.yml`) is a reusable workflow that runs Python tests with pytest. It is designed to be called from other workflows, providing a standardized way to run tests across different parts of the project.

## Recent Updates

The workflow has been updated with the following improvements:

1. **Enhanced Artifact Management**:
   - Added `if: always()` condition to the test results upload step to ensure results are always uploaded, even if tests fail
   - Improved artifact naming with unique identifiers using `${{ github.run_id }}` and `${{ github.job }}`
   - Added a separate step for uploading coverage reports

2. **Dependency Management Improvements**:
   - Updated to use `actions/cache@v4` for caching dependencies
   - Added `.pytest_cache` to the cached paths for faster test runs
   - Improved error handling in the dependency installation step with fallback mechanisms

3. **Test Execution Enhancements**:
   - Added support for customizable test paths via the `test-path` input parameter
   - Set a timeout of 15 minutes to prevent hanging test runs
   - Configured parallel test execution with `-n auto` for faster test runs

## Workflow Configuration

### Inputs

The workflow accepts the following inputs:

- **python-version** (required): The Python version to use for testing
- **test-path** (optional, default: "tests/"): The path to the tests to run

### Key Steps

1. **Checkout Code**: Uses `actions/checkout@v4` to fetch the repository code
2. **Set up Python**: Uses `actions/setup-python@v5` with the specified Python version
3. **Cache Dependencies**: Caches uv dependencies to speed up subsequent runs
4. **Install uv**: Installs the uv package manager for faster dependency installation
5. **Install Dependencies**: Installs test dependencies and project dependencies
6. **Run Tests**: Executes pytest with coverage reporting and parallel execution
7. **Upload Results**: Uploads test results and coverage reports as artifacts

## Usage Example

This workflow is designed to be called from other workflows. Here's an example of how to use it:

```yaml
name: Run Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    uses: ./.github/workflows/test.yml
    with:
      python-version: "3.12"
      test-path: "tests/unit/"
```

## Best Practices

When using this workflow, consider the following best practices:

1. **Specify Test Path**: Use the `test-path` parameter to run only the tests relevant to your changes
2. **Review Artifacts**: Always check the uploaded test results and coverage reports
3. **Maintain Coverage**: Ensure that code changes maintain or improve the coverage percentage

## Related Workflows

This workflow is part of our CI/CD pipeline and works in conjunction with:

- **ci.yml**: Comprehensive CI workflow that calls this workflow
- **consolidated-ci-cd.yml**: Main CI/CD pipeline that includes testing
- **check-documentation.yml**: Ensures documentation is updated when code changes

## Troubleshooting

If you encounter issues with this workflow:

1. **Test Failures**: Check the test results artifact for detailed error messages
2. **Dependency Issues**: Verify that all required dependencies are listed in requirements files
3. **Timeout Errors**: Consider splitting large test suites into smaller parts
