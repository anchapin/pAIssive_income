# DevOps Scripts

This directory contains various scripts for DevOps tasks such as running GitHub Actions workflows locally,
linting code,
running tests,
and fixing syntax errors.

> **Note:** Additional documentation for DevOps scripts and workflows can be found in [docs/ci_cd_pipeline.md](docs/ci_cd_pipeline.md) in the centralized documentation.

## Unified Workflow (Recommended)

We now provide a **unified entrypoint** for all code quality,
linting,
formatting,
syntax,
docstring,
and security tasks.

**Use the Makefile for common developer tasks:**

```bash
make all           # Run all checks and fixes
make lint          # Lint codebase
make format        # Format codebase
make fix           # Run all automated code fixers
make docstring-fix # Fix docstring issues
make syntax-fix    # Fix syntax issues
make security      # Run security scans
make test          # Run all tests
make pre-commit    # Run all pre-commit checks
```

Or, run tasks directly with the unified CLI:

```bash
python scripts/manage_quality.py lint
python scripts/manage_quality.py fix
python scripts/manage_quality.py security-scan
# ...and more
```

The `.pre-commit-config.yaml` is configured to use this unified entrypoint for code quality hooks.

## Legacy Scripts (for reference)

**Note: The unified workflow described above is the recommended approach for routine development tasks.**

The following scripts are maintained for backward compatibility and advanced use cases only. New development should use the unified workflow instead of these individual scripts:

### GitHub Actions

- **run_github_actions_locally.py**: Script to run GitHub Actions workflows locally using Act.
  (See script for usage examples.)

### Linting

- **run_linting.py**: Script to run linting checks on Python files.
  (See script for usage examples.)

### Testing

- **run_tests.py**: Script to run tests with various options.
  (See script for usage examples.)

### Syntax Error Fixing

- **fix_syntax_errors_batch.py**: Script to fix syntax errors in Python files.
- **fix_test_collection_warnings.py**: Script to fix common issues that prevent test collection.

## Installation

To use the unified workflow and scripts, install the required dependencies:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or if curl is unavailable:
# pip install uv

# Install linting tools with uv
uv pip install ruff

# Install testing tools with uv
uv pip install pytest pytest-cov pytest-xdist

# Install Act for running GitHub Actions locally
# On Windows:
choco install act-cli

# On macOS:
brew install act

# On Linux:
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

## Workflow Integration

All code quality,
linting,
formatting,
syntax,
docstring,
and security tasks are now integrated via the Makefile,
unified Python entrypoint (`scripts/manage_quality.py`),
pre-commit hooks,
and CI workflows.
