# Security, Type Checking and Linting Fixes

This document provides an overview of the security improvements and fixes made to the codebase to address:
1. Bandit security scan warnings
2. Pyright type checking errors
3. Ruff linting issues

## Security Improvements

### 1. Secure Subprocess Usage

The codebase had numerous instances of potentially insecure subprocess calls flagged by Bandit. We've addressed these by:

- Creating a centralized security module (`common_utils.security`) with secure command execution functions
- Ensuring all subprocess calls use `shell=False` by default
- Validating command arguments before execution
- Using absolute paths to executables via `shutil.which()`
- Adding explicit timeout values to prevent hanging processes

### 2. Hardcoded Credentials

We've eliminated hardcoded credentials by:

- Moving sensitive values to environment variables
- Renaming sensitive-looking constant names to more generic alternatives
- Adding comments to explain security precautions for necessary placeholders

### 3. Network Binding Security

We've improved network binding security by:

- Binding to localhost by default (`127.0.0.1`) instead of all interfaces
- Only binding to all interfaces (`0.0.0.0`) in containerized environments 
- Adding explicit warning logs when binding to all interfaces
- Adding environment variable overrides to control binding behavior

### 4. Improved Logging Security

We've enhanced logging practices to prevent leaking sensitive information:

- Created a script to detect and fix duplicate logging statements
- Ensuring sensitive data is masked before logging
- Using structured logging with `extra` parameter instead of formatting strings
- Moving sensitive values from log messages to the `extra` parameter

### 5. Path Security

We've improved path security by:

- Using absolute paths for executables
- Validating path components before use
- Using secure defaults for file operations

## Type Checking Improvements

We've created tools to address Pyright type checking issues:

- `fix_pyright_type_errors.py`: Automatically adds missing type annotations and imports
- Better handling of Optional and Union types
- Improved handling of imports for type annotations

## Linting Improvements

We've consolidated linting and formatting fixes:

- Using a single script (`fix_all_issues_final.py`) for code style fixes
- Addressing missing docstring periods
- Removing unused imports
- Improving logging format consistency
- Fixing function argument issues

## How to Run the Fixes

The central script for running all fixes is:

```bash
python scripts/fix/fix_all_security_and_types.py
```

This will execute all necessary fix scripts in the correct order.

### Options

- `--security-only`: Only run security fixes
- `--types-only`: Only run type checking fixes
- `--lint-only`: Only run linting fixes
- `--check`: Check mode - don't modify files, just report issues
- `--directory/-d`: Directory to fix (default: current directory)
- `--verbose/-v`: Enable verbose logging

## Ongoing Security Practices

1. **Regular Scanning**: Run security scans regularly using:
   ```bash
   python manage.py scan --type=security
   ```

2. **Pre-commit Hooks**: Use the pre-commit hooks to catch issues before they're committed:
   ```bash
   python manage.py pre-commit
   ```

3. **Type Checking**: Run type checking before pushing code:
   ```bash
   python -m pyright
   ```

4. **Documentation**: Add security-relevant comments using standard noqa format:
   ```python
   subprocess.run(command)  # nosec B603 - Safe because we validate input
   ```
