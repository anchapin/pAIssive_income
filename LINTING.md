# Linting Guide

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting Python code.

> **Note:** All code quality utility scripts (including fix_linting_issues.py) have been moved to the `scripts/fix/` directory. Please update all usage examples and CI/CD references to use `scripts/fix/fix_linting_issues.py` instead of the old root path.

## Using the Linting Script

The `fix_linting_issues.py` script can be run locally or through GitHub Actions.

### Running Locally

```bash
# Fix all Python files
python scripts/fix/fix_linting_issues.py

# Check for issues without fixing them
python scripts/fix/fix_linting_issues.py --check

# Fix specific files
python scripts/fix/fix_linting_issues.py path/to/file1.py path/to/file2.py

# Enable verbose output
python scripts/fix/fix_linting_issues.py --verbose

# Skip Ruff linter
python scripts/fix/fix_linting_issues.py --no-ruff

# Exclude specific patterns
python scripts/fix/fix_linting_issues.py --exclude "tests/" --exclude "legacy/"

# Use a file containing exclude patterns
python scripts/fix/fix_linting_issues.py --exclude-file .lintignore

# Enable parallel processing
python scripts/fix/fix_linting_issues.py --jobs 4  # Use 4 workers
python scripts/fix/fix_linting_issues.py -j 0      # Use all available CPU cores
```

### Command-Line Arguments

| Argument | Description |
|----------|-------------|
| `file_paths` | Paths to specific Python files to fix. If not provided, all Python files will be fixed. |
| `--check` | Check for issues without fixing them. |
| `--no-ruff` | Skip Ruff linter. |
| `--verbose` | Enable verbose output. |
| `--exclude PATTERN` | Patterns to exclude (can be used multiple times). |
| `--exclude-file FILE` | Path to a file containing patterns to exclude (one per line). |
| `--jobs N`, `-j N` | Number of parallel jobs to run. Default is 1 (sequential). Use -j 0 to use all available CPU cores. |

*All script references above assume the new path under `scripts/fix/`.*

### Exclude File Format

The exclude file (e.g., `.lintignore`) should contain one pattern per line. Empty lines and lines starting with `#` are ignored.

Example `.lintignore` file:
```
# Directories to exclude
tests/
legacy/
experimental/

# Files to exclude
setup.py
conftest.py
```

## GitHub Actions Workflow

The project includes a GitHub Actions workflow for automatically fixing linting issues. The workflow can be triggered manually from the Actions tab or automatically on pull requests and pushes to the main branch.

### Workflow Inputs

When triggering the workflow manually, you can provide the following inputs:

| Input | Description |
|-------|-------------|
| Specific file to fix | Path to a specific file to fix. Leave empty to process all files. |
| Check only, do not fix | Check for issues without fixing them. |
| Skip Ruff linter | Skip the Ruff linter. |
| Enable verbose output | Enable verbose output for detailed logs. |
| Patterns to exclude | Comma-separated list of patterns to exclude. |
| Path to file containing exclude patterns | Path to a file containing patterns to exclude. |
| Enable parallel processing | Enable parallel processing for faster execution. |

## Ruff Configuration

The project uses a `ruff.toml` file to configure Ruff. See the [Ruff documentation](https://docs.astral.sh/ruff/configuration/) for more information on configuring Ruff.

## Best Practices

1. **Run the linting script before committing**: This ensures your code follows the project's style guidelines.
2. **Use the `--check` flag to preview changes**: This allows you to see what would be changed without actually modifying files.
3. **Create a `.lintignore` file for your project**: This allows you to exclude specific files or directories from linting.
4. **Enable parallel processing for large codebases**: This can significantly speed up the linting process.
5. **Configure your IDE to use Ruff**: Many IDEs support Ruff integration, which can help you catch linting issues as you write code.
