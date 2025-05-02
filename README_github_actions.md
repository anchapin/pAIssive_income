# Running GitHub Actions Locally

This document explains how to run GitHub Actions locally and the changes made to fix failing tests.

## Setup

1. Install Act (GitHub Actions local runner):

   ```bash
   choco install act-cli  # Windows
   brew install act       # macOS
   curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   pip install -e .
   ```

## Running Linting Checks

You can run linting checks on a specific file or the entire codebase:

```bash
# Run linting on a specific file
python run_linting.py path/to/file.py

# Run linting on the entire codebase
python run_linting.py
```

## Using GitHub Actions Locally

We've created several scripts to help run GitHub Actions locally:

1. Using the batch file:

   ```bash
   # Run the simple-lint workflow on a specific file
   run_github_actions.bat --workflow .github/workflows/simple-lint.yml --file path/to/file.py

   # Run the lint-and-test workflow
   run_github_actions.bat --workflow .github/workflows/lint-and-test.yml --job lint

   # Run with a specific Docker platform
   run_github_actions.bat --workflow .github/workflows/simple-lint.yml --platform "ubuntu-latest=catthehacker/ubuntu:act-latest"
   ```

2. Using the Python script directly:

   ```bash
   # Run the simple-lint workflow on a specific file
   python run_github_actions_locally.py --workflow .github/workflows/simple-lint.yml --file path/to/file.py

   # Run the lint-and-test workflow
   python run_github_actions_locally.py --workflow .github/workflows/lint-and-test.yml --job lint

   # Run with a specific Docker platform
   python run_github_actions_locally.py --workflow .github/workflows/simple-lint.yml --platform "ubuntu-latest=catthehacker/ubuntu:act-latest"
   ```

3. Running tests with the local test runner:

   ```bash
   python run_local_tests.py --test-path tests/ai_models --verbose
   ```

## Issues Fixed

### 1. Hypothesis Module Conflict

**Issue**: The custom `hypothesis` module in the project conflicts with the installed `hypothesis` package.

**Fix**: Renamed the custom module to `custom_stubs/hypothesis_stub`.

### 2. Fallback Strategy Issues

**Issue**: The fallback strategy cascade is not working as expected. The `MODEL_TYPE` strategy is not being tried after `SIMILAR_MODEL`.

**Fix**: Updated the cascade order to include `SIZE_TIER` and fixed the `_apply_size_tier_strategy` method to handle None values.

### 3. Memory Cache Eviction

**Issue**: The LRU eviction policy is not working as expected in the memory cache.

**Fix**: Updated the `_evict_item` method to properly implement LRU eviction.

### 4. Pydantic Warnings

**Issue**: Pydantic warnings about protected namespace conflicts.

**Fix**: Added `model_config = {'protected_namespaces': ()}` to model classes.

### 5. Semver Warnings

**Issue**: Semver deprecation warnings.

**Fix**: Replaced `semver.parse` with `semver.Version.parse`.

## Available Workflows

The project has several GitHub Actions workflows:

1. `simple-lint.yml` - A simple workflow for linting a specific file
2. `lint-and-test.yml` - A comprehensive workflow for linting and testing the entire codebase
3. `lint_and_quality.yml` - Runs linting and code quality checks
4. `run_tests.yml` - Runs tests
5. `security_scan.yml` - Runs security scans
6. `deploy.yml` - Deploys the application

## Troubleshooting

If you encounter issues with Act, try the following:

1. Make sure Docker is running
2. Try using a different platform:

   ```bash
   run_github_actions.bat --platform ubuntu-latest=catthehacker/ubuntu:act-latest
   ```

3. Check the [Act documentation](https://github.com/nektos/act)

## Next Steps

1. Run the full test suite to ensure all tests pass
2. Update the GitHub Actions workflows to use the fixed code
3. Create a pull request with the fixes
