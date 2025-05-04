# DevOps Scripts

This directory contains various scripts for DevOps tasks such as running GitHub Actions workflows locally, linting code, running tests, and fixing syntax errors.

## Scripts Overview

### GitHub Actions

- **run_github_actions_locally.py**: Script to run GitHub Actions workflows locally using Act.
  ```bash
  # List available workflows
  python run_github_actions_locally.py --list
  
  # Run a specific workflow
  python run_github_actions_locally.py --workflow .github/workflows/local-testing.yml
  
  # Run only linting
  python run_github_actions_locally.py --workflow .github/workflows/local-testing.yml --lint-only
  
  # Run only tests
  python run_github_actions_locally.py --workflow .github/workflows/local-testing.yml --test-only
  
  # Run with a specific file
  python run_github_actions_locally.py --workflow .github/workflows/local-testing.yml --file path/to/file.py
  ```

### Linting

- **run_linting.py**: Script to run linting checks on Python files.
  ```bash
  # Run linting on all Python files
  python run_linting.py
  
  # Run linting on a specific directory
  python run_linting.py path/to/directory
  
  # Run linting on specific files
  python run_linting.py --files path/to/file1.py path/to/file2.py
  
  # Fix linting issues automatically
  python run_linting.py --fix
  ```

### Testing

- **run_tests.py**: Script to run tests with various options.
  ```bash
  # Run all tests
  python run_tests.py
  
  # Run tests with verbose output
  python run_tests.py --verbose
  
  # Run tests with coverage reporting
  python run_tests.py --coverage
  
  # Run tests with HTML coverage report
  python run_tests.py --coverage --html
  
  # Run tests in parallel
  python run_tests.py --parallel
  
  # Run only unit tests
  python run_tests.py --unit
  
  # Run only integration tests
  python run_tests.py --integration
  
  # Run tests for a specific file
  python run_tests.py --file path/to/file.py
  ```

### Syntax Error Fixing

- **fix_syntax_errors_batch.py**: Script to fix syntax errors in Python files.
  ```bash
  # Fix syntax errors in all Python files
  python fix_syntax_errors_batch.py
  
  # Fix syntax errors in a specific file
  python fix_syntax_errors_batch.py path/to/file.py
  
  # Check for syntax errors without fixing
  python fix_syntax_errors_batch.py --check
  ```

- **fix_test_collection_warnings.py**: Script to fix common issues that prevent test collection.
  ```bash
  # Fix test collection warnings in all Python files
  python fix_test_collection_warnings.py
  
  # Fix test collection warnings in a specific file
  python fix_test_collection_warnings.py path/to/file.py
  
  # Check for test collection warnings without fixing
  python fix_test_collection_warnings.py --check
  ```

## Installation

To use these scripts, you need to install the required dependencies:

```bash
# Install linting tools
pip install flake8 black isort ruff

# Install testing tools
pip install pytest pytest-cov pytest-xdist

# Install Act for running GitHub Actions locally
# On Windows:
choco install act-cli

# On macOS:
brew install act

# On Linux:
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

## Workflow Integration

These scripts are integrated with the GitHub Actions workflows in the `.github/workflows` directory. The workflows use these scripts to check for syntax errors, run linting checks, and run tests.

## Future Improvements

- Add pre-commit hooks to prevent committing files with syntax errors
- Implement more comprehensive tests
- Add support for additional linting tools
- Improve error handling and reporting
