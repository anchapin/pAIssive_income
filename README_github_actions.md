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

## Running Tests Locally

We've created several scripts to help run tests locally:

1. `run_local_tests.py` - Run tests with the correct Python path:
   ```bash
   python run_local_tests.py --test-path tests/ai_models --verbose
   ```

2. `run_github_actions.bat` - Fix failing tests and run GitHub Actions locally:
   ```bash
   run_github_actions.bat
   ```

3. `run_github_actions_locally.py` - Run GitHub Actions with Act:
   ```bash
   python run_github_actions_locally.py --workflow .github/workflows/local-test.yml
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

## GitHub Actions Workflows

The project has several GitHub Actions workflows:

1. `lint_and_quality.yml` - Runs linting and code quality checks
2. `run_tests.yml` - Runs tests
3. `security_scan.yml` - Runs security scans
4. `deploy.yml` - Deploys the application
5. `local-test.yml` - A simplified workflow for local testing

## Next Steps

1. Run the full test suite to ensure all tests pass
2. Update the GitHub Actions workflows to use the fixed code
3. Create a pull request with the fixes
