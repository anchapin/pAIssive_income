# GitHub Actions Local Testing Guide

This guide explains how to run GitHub Actions workflows locally using Act to verify that your changes will pass CI checks before pushing to the repository.

## Prerequisites

1. Install Act (already available in the `bin` directory):
   ```bash
   # If not already installed
   curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
   ```

2. Make sure Docker is installed and running (required by Act).

3. Install Python dependencies:
   ```bash
   pip install pytest pytest-cov pytest-xdist mypy pyright ruff bandit safety pip-audit sarif-tools
   ```

## Running GitHub Actions Locally

### Using the Helper Script

We've created a helper script to simplify running GitHub Actions workflows locally:

```bash
# List available workflows
python run_github_actions_locally.py --list

# Run a specific workflow
python run_github_actions_locally.py --workflow act-simple-lint.yml

# Run a specific job in a workflow
python run_github_actions_locally.py --workflow lint-and-test.yml --job lint

# Run on a specific platform
python run_github_actions_locally.py --workflow act-simple-lint.yml --platform ubuntu-latest
```

### Using Act Directly

You can also use Act directly:

```bash
# Run a specific workflow
./bin/act -j test -W .github/workflows/local-test.yml

# Run with specific platform
./bin/act -P ubuntu-latest -j test -W .github/workflows/local-test.yml
```

## Available Workflows

1. **local-test.yml**: Simple workflow to run tests on a subset of modules
2. **act-local-test.yml**: More comprehensive workflow with both testing and linting
3. **act-simple-lint.yml**: Simple linting workflow optimized for Act
4. **lint-and-test.yml**: Full CI workflow that runs on PRs and pushes to main branches
5. **simple-lint.yml**: Quick linting check for specific files

## Fixing Common Issues

### Pydantic Deprecation Warnings

Use the `fix_pydantic_models.py` script to update Pydantic models to use ConfigDict instead of class-based config:

```bash
# Run in dry-run mode to see what would be changed
python fix_pydantic_models.py --dry-run

# Fix all Pydantic models in the project
python fix_pydantic_models.py

# Fix Pydantic models in a specific directory
python fix_pydantic_models.py api/schemas
```

### Test Collection Warnings

Use the `fix_test_collection_warnings.py` script to fix test collection warnings for classes with `__init__` constructors:

```bash
# Run in dry-run mode to see what would be changed
python fix_test_collection_warnings.py --dry-run

# Fix all test files in the project
python fix_test_collection_warnings.py

# Fix test files in a specific directory
python fix_test_collection_warnings.py tests/api
```

### Linting Issues

Use the `run_linting.py` script to check and fix linting issues:

```bash
# Check linting for a specific file
python run_linting.py path/to/file.py

# Check linting for all Python files in a directory
python run_linting.py path/to/directory

# Check linting for specific file patterns
python run_linting.py --files "api/*.py" "tests/*.py"
```

## Troubleshooting

### Common Issues

1. **Docker not running**: Act requires Docker to be running. Make sure Docker is installed and running.

2. **Missing dependencies**: Make sure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Permission issues**: If you encounter permission issues with Act's cache:
   ```bash
   sudo chmod -R 777 ~/.cache/act
   ```

   Or clear the Act cache:
   ```bash
   rm -rf ~/.cache/act
   ```

4. **GLIBC version issues**: If you see errors about GLIBC versions, use container-based workflows:
   - Use workflows with the `container` section like `act-simple-lint.yml`
   - These workflows specify a container image that's compatible with Act

### Getting Help

If you encounter issues that you can't resolve, please:

1. Check the Act documentation: https://github.com/nektos/act
2. Open an issue in the repository with details about the problem
3. Include the output of the failing command and any error messages

# Running GitHub Actions Locally

This document explains how to use the `run_github_actions_locally.py` script to run GitHub Actions workflows locally for the pAIssive Income project.

## Prerequisites

Before running the script, make sure you have the following dependencies installed:

```bash
pip install pytest pytest-cov pytest-xdist mypy pyright ruff bandit safety pip-audit sarif-tools
```

## Usage

### Windows

You can use the provided batch file:

```
run_github_actions.bat <command> [options]
```

### All Platforms

Alternatively, you can run the Python script directly:

```
python run_github_actions_locally.py <command> [options]
```

## Available Commands

### Security Scan

Run security scans similar to the GitHub Actions workflow:

```
run_github_actions.bat security [--output-dir OUTPUT_DIR]
```

This will:
1. Install and verify sarif-tools
2. Run Bandit security scanner
3. Convert Bandit results to SARIF format
4. Run safety check
5. Run pip-audit

Results will be stored in the specified output directory (default: `./security-reports`).

### Linting

Run linting checks:

```
run_github_actions.bat lint [--file FILE_PATH]
```

This will run:
- ruff check
- ruff format
- mypy
- pyright

You can specify a particular file to lint with the `--file` option.

### Tests

Run tests:

```
run_github_actions.bat test [--path TEST_PATH]
```

This will run pytest with the same configurations as the GitHub Actions workflow.
You can specify a particular test path with the `--path` option.

## Troubleshooting sarif-tools Issues

If you encounter issues with sarif-tools:

1. The script will attempt to reinstall sarif-tools using `pip install --user sarif-tools --force-reinstall`
2. It will try multiple methods to run sarif-tools:
   - Direct command: `sarif-tools`
   - Python module: `python -m sarif_tools`
   - Full path: `~/.local/bin/sarif-tools`
3. As a last resort, it will create an empty SARIF file to prevent workflow failure

For persistent issues, you can manually install sarif-tools:

```
pip install --user sarif-tools
```

And verify it's in your PATH:

```
echo %PATH%  # On Windows
echo $PATH   # On Linux/macOS
```

## Example Workflow

To run a complete workflow that mimics the GitHub Actions CI:

1. Run linting: `run_github_actions.bat lint`
2. Run tests: `run_github_actions.bat test`
3. Run security scan: `run_github_actions.bat security`
