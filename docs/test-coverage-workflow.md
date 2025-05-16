# Test Coverage Workflow

## Overview

This document describes the test coverage requirements and workflow configuration for the pAIssive_income project. The project enforces a minimum test coverage threshold to ensure code quality and reliability.

## Coverage Threshold

The project requires a minimum of **80%** test coverage for all code. This threshold is enforced in the following workflow files:

- `.github/workflows/python-tests.yml`
- `.github/workflows/mcp-adapter-tests.yml`
- `.github/workflows/consolidated-ci-cd.yml`
- `pytest.ini`

## Coverage Configuration

The coverage configuration is defined in `.coveragerc`, which specifies:

- Source directories to include in coverage analysis
- Files and directories to exclude from coverage analysis
- Lines to exclude from coverage analysis (e.g., debug code, abstract methods)

## Running Tests with Coverage

To run tests with coverage locally:

```bash
# Run tests with coverage report
pytest --cov=. --cov-report=xml --cov-report=term-missing --cov-fail-under=80

# Run specific tests with coverage
pytest path/to/test_file.py --cov=. --cov-report=term-missing --cov-fail-under=80
```

## CI/CD Integration

The coverage threshold is enforced in the CI/CD pipeline. If the coverage falls below 80%, the workflow will fail, preventing the code from being merged.

### Workflow Configuration

Each workflow file includes the `--cov-fail-under=80` parameter to enforce the coverage threshold:

```yaml
- name: Run tests with coverage
  run: |
    python -m pytest --cov=. --cov-report=xml --cov-report=term-missing --cov-fail-under=80
```

## Improving Coverage

If your PR fails due to insufficient coverage, consider:

1. Adding tests for untested code paths
2. Refactoring complex code to make it more testable
3. Excluding specific lines that cannot be tested (using `# pragma: no cover`)

## Coverage Reports

Coverage reports are generated in multiple formats:

- Terminal output (for quick feedback)
- XML report (for CI/CD integration)
- HTML report (for detailed analysis)

The reports show:
- Overall coverage percentage
- Coverage by file
- Missing lines (lines not covered by tests)

## Codecov Integration

Coverage reports are uploaded to Codecov for tracking coverage trends over time. The Codecov dashboard provides:

- Coverage history
- Coverage by file and directory
- Coverage changes in PRs

## Conclusion

Maintaining high test coverage is essential for ensuring code quality and reliability. The 80% threshold provides a balance between thorough testing and development velocity.
