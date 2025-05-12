# Code Formatting Guide

This guide explains the code formatting setup for the pAIssive Income project and how to fix formatting issues.

## Formatting Setup

The project uses [Ruff](https://github.com/astral-sh/ruff) as the primary code formatter and linter. Ruff is configured in `ruff.toml` and integrated into the pre-commit hooks in `.pre-commit-config.yaml`.

### Key Configuration Files

- **ruff.toml**: Contains Ruff configuration for both linting and formatting
- **.pre-commit-config.yaml**: Configures pre-commit hooks, including Ruff formatting and linting

## Fixing Formatting Issues

If you encounter formatting issues, you can use the provided `fix_formatting.py` script:

```bash
# Fix formatting issues in the default files
python fix_formatting.py

# Fix formatting issues in specific files
python fix_formatting.py --files path/to/file1.py path/to/file2.py
```

### Important Note on Black vs. Ruff

This project uses Ruff as the primary formatter, not Black. Running Black directly may cause formatting conflicts with Ruff. Always use Ruff for formatting to ensure consistency with the pre-commit hooks.

If you're using an IDE with Black integration, consider configuring it to use Ruff instead, or disable automatic formatting and use the pre-commit hooks or `fix_formatting.py` script.

## Running Pre-commit Hooks

To run all pre-commit hooks:

```bash
pre-commit run --all-files
```

To run only the formatting hook:

```bash
pre-commit run ruff-format --all-files
```

## Formatting Rules

The project follows these formatting rules:

- **Line Length**: 88 characters (configured in `ruff.toml`)
- **Quote Style**: Double quotes (configured in `ruff.toml`)
- **Indent Style**: Spaces (configured in `ruff.toml`)
- **Docstring Style**: Google style with code formatting (configured in `ruff.toml`)

## Troubleshooting

If you encounter formatting issues that can't be fixed automatically, check:

1. **Conflicting Formatters**: Make sure you're not running multiple formatters (e.g., Black and Ruff)
2. **IDE Integration**: Check if your IDE is configured to use a different formatter
3. **Configuration Files**: Verify that `ruff.toml` and `.pre-commit-config.yaml` are properly configured

For persistent issues, run:

```bash
ruff format --verbose path/to/file.py
```

This will provide more detailed information about the formatting issues.
