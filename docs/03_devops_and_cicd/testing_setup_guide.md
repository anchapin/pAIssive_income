# Testing Setup Guide

## Overview

This guide provides developers with essential information about the project's testing configuration and CI/CD setup.

## Test Coverage Requirements

- **Minimum Coverage**: 15% for Python code
- **Current Coverage**: 17.28% (exceeds requirement)
- **Enforcement**: Automated via pytest with `--cov-fail-under=15`

## Test Configuration

### Pytest Configuration

The project uses consistent pytest configuration across `pytest.ini` and `pyproject.toml`:

```ini
[tool:pytest]
testpaths = tests
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=.
    --cov-report=term-missing
    --cov-fail-under=15
    --ignore-glob=**/mock_*
    --ignore-glob=**/mcp_*
    --ignore-glob=**/crewai*
```

### Asyncio Configuration

For tests using async/await:
```ini
asyncio_default_fixture_loop_scope = function
asyncio_mode = auto
asyncio_default_test_loop_scope = function
```

## Test Exclusions

### Excluded Files
The following test files are excluded from CI runs:
- `tests/ai_models/adapters/test_mcp_adapter.py`
- `tests/test_mcp_import.py`
- `tests/test_mcp_top_level_import.py`
- `tests/test_crewai_agents.py`
- `tests/test_mem0_integration.py`
- `ai_models/artist_rl/test_artist_rl.py`

### Excluded Directories
- `mock_mcp/` - Mock MCP modules
- `mock_crewai/` - Mock CrewAI modules  
- `mock_mem0/` - Mock mem0 modules

### Exclusion Rationale
Tests are excluded for these reasons:
1. **Optional Dependencies**: Require packages not installed in CI
2. **Integration Tests**: Need external services unavailable in CI
3. **Mock Module Issues**: Complex mock setups that cause collection errors
4. **Experimental Code**: Work-in-progress features not ready for CI

## Running Tests Locally

### Basic Test Run
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_simple.py -v
```

### Using CI Wrapper Scripts
```bash
# Enhanced CI wrapper (recommended)
python run_tests_ci_wrapper_enhanced.py

# Standard CI wrapper
python run_tests_ci_wrapper.py

# Basic test runner
python run_tests.py
```

### Coverage-Only Run
```bash
# Run tests that contribute to coverage
python -m pytest tests/test_simple.py tests/test_math_utils.py tests/common_utils/ tests/utils/ tests/test_config.py tests/test_authentication.py tests/test_error_handling.py --cov=. --cov-report=term-missing --cov-fail-under=15
```

## Package Management

### Python Dependencies
- **Tool**: `uv` (not pip)
- **Installation**: `uv pip install -r requirements.txt`
- **Virtual Environment**: `uv venv`

### JavaScript Dependencies
- **Tool**: `pnpm` (not npm)
- **Installation**: `pnpm install`
- **Testing**: `pnpm test`

## CI/CD Workflow Structure

### Test Execution Strategies
The CI workflows use multiple fallback strategies:

1. **Enhanced CI Wrapper**: Primary strategy with comprehensive error handling
2. **Standard CI Wrapper**: Fallback with basic error handling
3. **Direct Script**: Fallback using run_tests.py
4. **Minimal Pytest**: Final fallback with basic options

### Workflow Files
- `.github/workflows/consolidated-ci-cd.yml` - Main CI/CD pipeline
- `.github/workflows/python-tests.yml` - Python-specific tests
- `.github/workflows/test.yml` - Reusable test workflow

## Security Scanning

### Bandit Configuration
- **Config File**: `.bandit`
- **Exclusions**: Tests, virtual environments, node_modules
- **Skipped Rules**: B101 (assert), B311 (pseudo-random)

### Security Tools
- **Bandit**: Static analysis for Python security issues
- **Safety**: Python dependency vulnerability scanning
- **CodeQL**: GitHub's semantic code analysis
- **Trivy**: Container image vulnerability scanning

## Troubleshooting

### Common Issues

#### Pytest Collection Errors
**Problem**: `OSError: [Errno 2] No such file or directory`
**Solution**: Check for broken symlinks, ensure mock directories exist

#### Coverage Below Threshold
**Problem**: Coverage drops below 15%
**Solution**: Run more comprehensive tests or add unit tests for core modules

#### Import Errors in Tests
**Problem**: `ModuleNotFoundError` for optional dependencies
**Solution**: Add test to exclusion list or install missing dependencies

### Debug Commands
```bash
# Check for broken symlinks (Windows)
Get-ChildItem -Recurse -Force | Where-Object {$_.Attributes -match "ReparsePoint"}

# Test collection only
python -m pytest --collect-only -q

# Verbose test run with full output
python -m pytest -v --tb=long --no-header
```

## Best Practices

### Writing Tests
1. **Focus on Core Modules**: Prioritize testing utilities, configuration, and validation
2. **Mock External Dependencies**: Use mocks for APIs, databases, and external services
3. **Test Edge Cases**: Include error conditions and boundary cases
4. **Keep Tests Fast**: Avoid slow integration tests in unit test suites

### Maintaining Coverage
1. **Monitor Coverage Reports**: Check coverage after adding new code
2. **Add Tests for New Features**: Ensure new code includes corresponding tests
3. **Review Exclusions**: Periodically review excluded tests for inclusion
4. **Use Coverage Reports**: Identify untested code paths

### CI/CD Considerations
1. **Test Locally First**: Run tests locally before pushing
2. **Check Exclusions**: Ensure new tests don't require excluded dependencies
3. **Monitor Workflow Runs**: Watch for new failure patterns
4. **Update Documentation**: Keep testing docs current with changes

## Quick Reference

### Key Commands
```bash
# Run tests with coverage
pytest --cov=. --cov-report=term-missing --cov-fail-under=15

# Install dependencies
uv pip install -r requirements.txt

# JavaScript tests
pnpm test

# Local workflow testing
act -j test
```

### Key Files
- `pytest.ini` - Main pytest configuration
- `pyproject.toml` - Python project configuration
- `.bandit` - Security scan configuration
- `run_tests_ci_wrapper_enhanced.py` - Enhanced test runner

### Coverage Targets
- **Minimum**: 15% (enforced)
- **Current**: 17.28%
- **Goal**: Gradual improvement over time

For more detailed information, see:
- [GitHub Actions Documentation](02_github_actions.md)
- [PR #139 Workflow Fixes Summary](pr_139_workflow_fixes_summary.md)
- [Main README Testing Section](../../README.md#running-tests)
