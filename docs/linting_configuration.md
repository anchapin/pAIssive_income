# Linting and Formatting Configuration

This document provides an overview of the linting and formatting configuration for the pAIssive Income project.

## Overview

The project uses [Ruff](https://github.com/astral-sh/ruff) as the primary tool for both linting and formatting. Ruff is a fast, comprehensive Python linter and formatter that combines the functionality of multiple tools like Flake8, Black, isort, and more.

## Configuration Files

- **ruff.toml**: Contains the configuration for Ruff, including linting rules and formatting settings.
- **.pre-commit-config.yaml**: Configures pre-commit hooks, including Ruff for linting and formatting.
- **pyproject.toml**: Can contain configuration for Pyrefly type checking (if needed).

## Linting Rules

The project uses a comprehensive set of linting rules, as defined in `ruff.toml`:

```toml
# Comprehensive rule selection
[lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "W",   # pycodestyle warnings
    "B",   # flake8-bugbear
    "C",   # flake8-comprehensions
    "T",   # flake8-print
    "UP",  # pyupgrade
    "RUF", # Ruff-specific rules
    "N",   # pep8-naming
    "PT",  # flake8-pytest-style
    "SIM", # flake8-simplify
    "ARG", # flake8-unused-arguments
    "ERA", # eradicate
    "PL",  # pylint
    "TRY", # tryceratops
    "FIX", # autofix
]
```

## Formatting Settings

The project uses Ruff for code formatting with the following settings:

```toml
[format]
quote-style = "double"
indent-style = "space"
docstring-code-format = true
docstring-code-line-length = 88
line-ending = "auto"
```

## Running Linting and Formatting

### Command Line

You can run linting and formatting checks from the command line:

```bash
# Run linting checks
ruff check .

# Run formatting checks
ruff format --check .

# Fix linting issues
ruff check --fix .

# Format code
ruff format .
```

### Using fix_linting_issues.py

The project includes a custom script for fixing linting issues:

```bash
# Fix all Python files
python fix_linting_issues.py

# Fix specific files
python fix_linting_issues.py path/to/file1.py path/to/file2.py

# Check only (don't fix)
python fix_linting_issues.py --check

# Skip Ruff
python fix_linting_issues.py --no-ruff

# Verbose output
python fix_linting_issues.py --verbose
```

### Pre-commit Hooks

The project uses pre-commit hooks to automatically check and fix linting and formatting issues before committing:

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit hooks on all files
pre-commit run --all-files

# Run pre-commit hooks on staged files
pre-commit run
```

## CI/CD Integration

The project's CI/CD pipeline includes steps for linting and formatting checks:

1. **GitHub Actions**: The `.github/workflows/consolidated-ci-cd.yml` workflow includes steps for running Ruff linting and formatting checks.
2. **Automated Fixes**: The `.github/workflows/fix-linting-issues.yml` workflow automatically fixes linting issues in pull requests.

## IDE Integration

### VS Code

For VS Code, add the following to your `.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.pyreflyEnabled": true,

    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": true,
            "source.organizeImports.ruff": true
        }
    }
}
```

### PyCharm

For PyCharm, install the [Ruff plugin](https://plugins.jetbrains.com/plugin/20574-ruff) and configure it to run on save.

## Troubleshooting

If you encounter issues with linting or formatting:

1. Make sure you have Ruff installed:
   ```bash
   pip install ruff
   ```

2. Check that your IDE is configured to use Ruff.

3. Try running Ruff manually to see if there are any errors:
   ```bash
   ruff check path/to/file.py
   ruff format path/to/file.py
   ```

4. If you're still having issues, try running the `fix_linting_issues.py` script with the `--verbose` flag:
   ```bash
   python fix_linting_issues.py --verbose
   ```

## Migration from Flake8 and MyPy

The project has migrated from using Flake8 to using Ruff as the primary linting tool. Ruff provides all the functionality of Flake8 and more, with significantly better performance.

Additionally, the project has migrated from using MyPy to using Pyright for type checking. Pyright offers improved performance and better error messages compared to MyPy. See the [Type Checking](type-checking.md) documentation for more details.

If you encounter any references to Flake8 or MyPy in documentation or scripts, please update them to reference Ruff and Pyright respectively.
