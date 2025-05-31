# Test Coverage Workflow

## Overview

This document describes the test coverage requirements and workflow configuration for the pAIssive_income project. The project enforces a minimum test coverage threshold to ensure code quality and reliability.

## Coverage Threshold

The project requires a minimum of **15%** test coverage for all code. This threshold is enforced in the following workflow files:

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
pytest --cov=. --cov-report=xml --cov-report=term-missing --cov-fail-under=15

# Run specific tests with coverage
pytest path/to/test_file.py --cov=. --cov-report=term-missing --cov-fail-under=15
```

## CI/CD Integration

The coverage threshold is enforced in the CI/CD pipeline. If the coverage falls below 15%, the workflow will fail, preventing the code from being merged.

### Workflow Configuration

Each workflow file includes the `--cov-fail-under=15` parameter to enforce the coverage threshold:

```yaml
- name: Run tests with coverage
  run: |
    python -m pytest --cov=. --cov-report=xml --cov-report=term-missing --cov-fail-under=15
```

## Improving Coverage

If your PR fails due to insufficient coverage, consider:

1. Adding tests for untested code paths
2. Refactoring complex code to make it more testable
3. Excluding specific lines that cannot be tested (using `# pragma: no cover`)

### Strategies for Improving Coverage

#### 1. Identify Low-Coverage Modules

Use the coverage report to identify modules with low coverage:

```bash
# Generate an HTML coverage report
pytest --cov=. --cov-report=html

# Open the report in your browser
# On Windows
start htmlcov/index.html
# On macOS
open htmlcov/index.html
# On Linux
xdg-open htmlcov/index.html
```

#### 2. Focus on High-Impact Areas

Prioritize testing for:
- Core business logic
- Error-prone code
- Code that changes frequently
- Public APIs and interfaces

#### 3. Use Test-Driven Development (TDD)

Write tests before implementing new features to ensure high coverage from the start:
1. Write a failing test that defines the expected behavior
2. Implement the minimum code needed to pass the test
3. Refactor the code while keeping tests passing

#### 4. Test Edge Cases

Ensure your tests cover edge cases:
- Empty inputs
- Boundary values
- Invalid inputs
- Error conditions
- Concurrent operations (if applicable)

#### 5. Use Parameterized Tests

Use parameterized tests to test multiple scenarios with minimal code:

```python
import pytest

@pytest.mark.parametrize("input_value,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
    (4, 16),
    (5, 25),
])
def test_square(input_value, expected):
    assert square(input_value) == expected
```

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
