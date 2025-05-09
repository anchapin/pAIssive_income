# Code Quality, Linting, Formatting, and Security

We use a unified workflow for all code quality, linting, formatting, syntax, docstring, and security tasks.

## Quickstart

- Run all checks and fixes:

  ```sh
  make all
  ```

- Run specific tasks:

  ```sh
  make lint         # Lint codebase
  make format       # Format codebase
  make fix          # Run all automated code fixers
  make docstring-fix # Fix docstring issues
  make syntax-fix   # Fix syntax issues
  make security     # Run security scans
  make test         # Run all tests
  make pre-commit   # Run all pre-commit checks
  ```

## Pre-commit hooks

Our `.pre-commit-config.yaml` is configured to use the unified entrypoint (`scripts/manage_quality.py`). Install and update pre-commit hooks:

```sh
pre-commit install
pre-commit run --all-files
```

## Manual invocation

You can also run tasks directly:

```sh
python scripts/manage_quality.py lint
python scripts/manage_quality.py fix
python scripts/manage_quality.py security-scan
# ...and more
```

See the Makefile for all available tasks.

