# Workflow Testing Guide

This guide provides comprehensive instructions for testing GitHub Actions workflows locally and troubleshooting common issues.

## Overview

The project uses a consolidated CI/CD workflow (`consolidated-ci-cd.yml`) that includes:
- **lint-test**: Code quality, type checking, and testing across multiple platforms
- **security**: Comprehensive security scanning with multiple tools
- **build-deploy**: Docker image building and publishing

## Local Testing Methods

### Method 1: Act Tool (Recommended for Quick Testing)

The `act` tool allows you to run GitHub Actions workflows locally using Docker.

#### Installation
```bash
# Download act binary (already included in bin/ directory)
# Or install via package manager:
# Windows (Chocolatey): choco install act-cli
# macOS (Homebrew): brew install act
# Linux: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

#### Basic Usage
```bash
# List available jobs
act --list

# Test the main lint-test job
act -j lint-test -W .github/workflows/consolidated-ci-cd.yml

# Test specific workflow with artifacts
act -j lint-test -W .github/workflows/consolidated-ci-cd.yml --artifact-server-path /tmp/artifacts

# Test security scanning
act -j security -W .github/workflows/consolidated-ci-cd.yml
```

#### Known Limitations
- **Docker Image Compatibility**: May encounter GLIBC version mismatches with older Docker images
- **Platform Differences**: Some platform-specific features may not work correctly
- **Resource Constraints**: Local Docker environment may have different resource limits
- **Secret Management**: Local secrets handling differs from GitHub Actions

### Method 2: Direct Command Testing (Most Reliable)

For comprehensive testing without Docker limitations, run commands directly:

#### Linting Tests
```bash
# Run ruff linting (matches CI configuration)
ruff check . --exclude "ai_models/adapters/mcp_adapter.py" --exclude "tests/ai_models/adapters/test_mcp_adapter.py" --exclude "tests/test_mcp_import.py" --exclude "tests/test_mcp_top_level_import.py" --exclude "mock_mcp" --exclude "mock_crewai"

# Run pyright type checking
pyright . --exclude "ai_models/adapters/mcp_adapter.py" --exclude "tests/ai_models/adapters/test_mcp_adapter.py" --exclude "tests/test_mcp_import.py" --exclude "tests/test_mcp_top_level_import.py" --exclude "mock_mcp" --exclude "mock_crewai"
```

#### Test Execution
```bash
# Run tests with coverage (matches CI configuration)
python -m pytest tests/ \
  --verbose \
  --cov=. \
  --cov-report=xml \
  --cov-report=term-missing \
  --cov-fail-under=15 \
  --junitxml=junit/test-results.xml \
  --maxfail=20 \
  --tb=short \
  --disable-warnings \
  --ignore-glob="**/mock_*" \
  --ignore-glob="**/mcp_*" \
  --ignore-glob="**/crewai*" \
  --ignore-glob="**/mem0*" \
  --ignore=tests/ai_models/adapters/test_mcp_adapter.py \
  --ignore=tests/test_mcp_import.py \
  --ignore=tests/test_mcp_top_level_import.py \
  --ignore=tests/test_crewai_agents.py \
  --ignore=tests/test_mem0_integration.py \
  --ignore=ai_models/artist_rl/test_artist_rl.py

# Quick test run (subset)
python -m pytest tests/ --maxfail=5 --tb=short -q --disable-warnings
```

#### Security Scanning
```bash
# Run bandit security scan
bandit -r . -f json -o security-reports/bandit-results.json || echo "Bandit scan completed"

# Run safety check
safety check --json --output security-reports/safety-results.json || echo "Safety check completed"

# Run pip-audit
pip-audit --format=json --output=security-reports/pip-audit-results.json || echo "pip-audit completed"
```

## Troubleshooting Common Issues

### Act Tool Issues

#### GLIBC Version Mismatches
```
Error: python: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.34' not found
```
**Solution**: This is a known limitation of act with older Docker images. Use direct command testing instead.

#### Docker Image Reference Errors
```
Error: invalid reference format
```
**Solution**: Check that the workflow file has proper Docker image references. Some workflows may need platform-specific image configurations.

#### Container Permission Issues
```
Error: permission denied
```
**Solution**: Ensure Docker is running with appropriate permissions, or use `sudo` if necessary.

### Direct Testing Issues

#### Import Errors
```
ModuleNotFoundError: No module named 'modelcontextprotocol'
```
**Solution**: The CI automatically creates mock modules. For local testing, either:
1. Install the problematic dependencies
2. Create mock modules manually
3. Use the test exclusions as shown in the examples above

#### Coverage Threshold Failures
```
FAIL Required test coverage of 15% not reached. Total coverage: X.XX%
```
**Solution**: This is expected when running individual test files. Run the full test suite or adjust the coverage threshold for local testing.

#### Path Issues on Windows
```
Error: No such file or directory
```
**Solution**: Use forward slashes in paths or use the `pathlib` module for cross-platform compatibility.

## Best Practices

### Before Pushing Changes
1. **Run linting locally**: `ruff check .` and `pyright .`
2. **Run core tests**: `python -m pytest tests/ --maxfail=10 -q`
3. **Check coverage**: Ensure your changes don't significantly reduce coverage
4. **Test security scans**: Run bandit and safety checks if modifying security-sensitive code

### Workflow Maintenance
1. **Regular Updates**: Keep workflow dependencies and actions up to date
2. **Monitor Performance**: Track workflow execution times and optimize as needed
3. **Review Exclusions**: Periodically review test exclusions and remove unnecessary ones
4. **Documentation**: Keep this guide updated with new troubleshooting information

### Local Development Environment
1. **Use uv for Python**: `uv pip install -r requirements.txt`
2. **Use pnpm for JavaScript**: `pnpm install`
3. **Set up pre-commit hooks**: `pre-commit install`
4. **Configure IDE**: Set up your IDE with the project's linting and formatting rules

## Workflow Configuration Details

### Test Exclusions
The following files and patterns are excluded from CI test runs:
- `tests/ai_models/adapters/test_mcp_adapter.py`
- `tests/test_mcp_import.py`
- `tests/test_mcp_top_level_import.py`
- `tests/test_crewai_agents.py`
- `tests/test_mem0_integration.py`
- `ai_models/artist_rl/test_artist_rl.py`
- All files in `mock_*` directories

### Mock Module Creation
The CI automatically creates mock modules for:
- `mock_mcp`: MCP (Model Context Protocol) functionality
- `mock_crewai`: CrewAI agent framework
- `mock_mem0`: mem0 memory integration

### Timeout Configuration
- **lint-test job**: 60-90 minutes (platform-dependent)
- **security job**: 60-90 minutes (platform-dependent)
- **build-deploy job**: 75 minutes
- **Individual steps**: 15-40 minutes (step-dependent)

## Additional Resources

- [GitHub Actions Documentation](02_github_actions.md)
- [Troubleshooting Guide](../07_troubleshooting_and_faq/troubleshooting.md)
- [Security Scanning Guide](../04_security_and_compliance/01_security_overview.md)
- [Act Tool Documentation](https://github.com/nektos/act)

For issues not covered in this guide, check the project's issue tracker or create a new issue with detailed information about the problem.
