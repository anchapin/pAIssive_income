# GitHub Actions Local Testing

This document summarizes the process of running GitHub Actions locally and the issues found.

## Setup

1. Install Act (GitHub Actions local runner):
   ```bash
   choco install act-cli  # Windows
   brew install act       # macOS
   curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux
   ```

2. Fix the hypothesis module conflict:
   - The custom `hypothesis` module in the project conflicts with the installed `hypothesis` package
   - Renamed the custom module to `custom_stubs/hypothesis_stub`

3. Create a local test runner script:
   - Created `run_local_tests.py` to run tests with the correct Python path
   - Added command-line arguments for test path, verbosity, and coverage

## Running Tests Locally

Run tests using the local test runner script:

```bash
python run_local_tests.py --test-path tests/ai_models --verbose
```

Run tests with coverage:

```bash
python run_local_tests.py --test-path tests --coverage
```

Run GitHub Actions locally using Act:

```bash
python run_github_actions_locally.py --workflow .github/workflows/local-test.yml
```

## Issues Found

### 1. Hypothesis Module Conflict

**Issue**: The custom `hypothesis` module in the project conflicts with the installed `hypothesis` package.

**Fix**: Renamed the custom module to `custom_stubs/hypothesis_stub`.

### 2. Failing Tests

The following tests are failing:

1. `tests/ai_models/fallbacks/test_fallback_strategy.py::TestFallbackManager::test_cascading_fallback_chain`
   - **Error**: `AssertionError: 'model_type' not found in ['default', 'similar_model']`
   - **Fix**: The fallback strategy cascade is not working as expected. The `MODEL_TYPE` strategy is not being tried after `SIMILAR_MODEL`.

2. `tests/ai_models/fallbacks/test_fallback_strategy.py::TestFallbackManager::test_size_tier_strategy`
   - **Error**: `AssertionError: <FallbackStrategy.SIMILAR_MODEL: 'similar_model'> != <FallbackStrategy.SIZE_TIER: 'size_tier'>`
   - **Fix**: The `SIZE_TIER` strategy is failing with an error: `'<' not supported between instances of 'NoneType' and 'int'`, causing it to fall back to `SIMILAR_MODEL`.

3. `tests/ai_models/test_caching.py::test_cache_size_and_eviction`
   - **Error**: `AssertionError` - The LRU eviction policy is not working as expected.
   - **Fix**: The cache implementation needs to be fixed to properly evict the least recently used items.

### 3. Warnings

1. Pydantic warnings about protected namespace conflicts:
   ```
   UserWarning: Field "model_sources" has conflict with protected namespace "model_".
   You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
   ```

2. Semver deprecation warnings:
   ```
   DeprecationWarning: Function 'semver.parse' is deprecated. Deprecated since version 2.10.0.
   This function will be removed in semver 3. Use the respective 'semver.Version.parse' instead.
   ```

## Next Steps

1. Fix the failing tests:
   - Update the fallback strategy implementation to properly cascade through all strategies
   - Fix the SIZE_TIER strategy to handle None values for model size
   - Fix the cache eviction policy implementation

2. Address the warnings:
   - Update Pydantic models to set `model_config['protected_namespaces'] = ()`
   - Update semver usage to use `semver.Version.parse` instead of `semver.parse`

3. Run the full test suite with the fixes applied

4. Update the GitHub Actions workflows to use the fixed code
