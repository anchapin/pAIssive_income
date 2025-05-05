# GitHub Actions Local Testing Guide

This guide explains how to run GitHub Actions workflows locally using Act to verify that your changes will pass CI checks before pushing to the repository.

## Prerequisites

1. Install Act (already available in the `bin` directory):
   ```bash
   # If not already installed
   curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
   ```

2. Make sure Docker is installed and running (required by Act).

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
