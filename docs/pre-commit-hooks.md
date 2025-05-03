# Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality and consistency. Pre-commit hooks run automatically before each commit to catch issues early in the development process.

## Setup

To set up pre-commit hooks, you can use the provided setup scripts:

```bash
# On Windows
setup_pre_commit.bat

# On Unix/Linux
python setup_pre_commit.py
```

Or manually:

```bash
pip install pre-commit
pre-commit install
```

## Available Hooks

The following hooks are configured in our `.pre-commit-config.yaml` file:

### Basic Checks

- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with a newline
- **check-yaml**: Validates YAML files
- **check-json**: Validates JSON files
- **check-toml**: Validates TOML files
- **check-ast**: Checks Python syntax
- **check-added-large-files**: Prevents large files from being committed
- **debug-statements**: Checks for debugger imports and py37+ `breakpoint()` calls
- **detect-private-key**: Checks for private keys

### Code Quality

- **ruff**: Fast Python linter that finds and fixes issues
- **ruff-format**: Formats code using Ruff's formatter
- **black**: Formats Python code
- **isort**: Sorts imports
- **flake8**: Checks for syntax errors and undefined names
- **mypy**: Performs type checking

### Custom Hooks

- **check-syntax-errors**: Runs our custom syntax error detection script

## Usage

Pre-commit hooks run automatically when you commit changes. If a hook fails, the commit will be aborted, and you'll need to fix the issues before committing again.

### Running Hooks Manually

You can run the hooks manually on all files:

```bash
pre-commit run --all-files
```

Or on specific files:

```bash
pre-commit run --files path/to/file1.py path/to/file2.py
```

### Updating Hooks

To update the hooks to the latest versions:

```bash
pre-commit autoupdate
```

### Skipping Hooks

In rare cases, you may need to skip hooks for a specific commit:

```bash
git commit -m "Your message" --no-verify
```

**Note**: This should be used sparingly and only when absolutely necessary.

## Benefits

Using pre-commit hooks provides several benefits:

1. **Catch issues early**: Identify and fix issues before they're committed
2. **Consistent code style**: Ensure all code follows the same style guidelines
3. **Reduce CI failures**: Fix issues locally before pushing to CI
4. **Save time**: Automated checks are faster than manual reviews
5. **Improve code quality**: Enforce best practices and coding standards

## Troubleshooting

If you encounter issues with pre-commit hooks:

1. Make sure you have the latest version of pre-commit installed
2. Try updating the hooks with `pre-commit autoupdate`
3. Check if there are any conflicts between different hooks
4. Ensure all required dependencies are installed

For more information, see the [pre-commit documentation](https://pre-commit.com/).
