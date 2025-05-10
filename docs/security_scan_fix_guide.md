# Security Scan Fix Guide

This guide explains how to use the security scan fix scripts to address security issues identified in security scans.

## Overview

The project includes scripts to help fix security scan issues:

1. `fix_security_scan_issues.py`: A Python script that can:
   - Update the `.gitleaks.toml` file to allowlist known false positives
   - Add comments to indicate test data
   - Rename sensitive variable names
   - Process specific files or scan results

2. `fix_security_scan.bat`: A batch script that runs `fix_security_scan_issues.py` with common options

## Using the Scripts

### Fix Security Scan Issues

To fix security scan issues, you can use the `fix_security_scan.bat` script:

```bash
# Run with default options
fix_security_scan.bat

# Run with scan results file
fix_security_scan.bat security_scan_results.txt
```

Or you can run the Python script directly:

```bash
# Update Gitleaks configuration
python fix_security_scan_issues.py --update-config

# Add comments to indicate test data
python fix_security_scan_issues.py --add-comments

# Rename sensitive variable names
python fix_security_scan_issues.py --rename-variables

# Process specific files
python fix_security_scan_issues.py --specific-files users/password_reset.py users/services.py

# Process scan results
python fix_security_scan_issues.py --scan-results security_scan_results.txt

# Combine options
python fix_security_scan_issues.py --update-config --add-comments --verbose
```

### Command-Line Options

The `fix_security_scan_issues.py` script supports the following options:

- `--directory`, `-d`: Directory to process (default: current directory)
- `--add-comments`, `-c`: Add comments to indicate test data
- `--rename-variables`, `-r`: Rename sensitive variable names
- `--update-config`, `-u`: Update Gitleaks configuration
- `--verbose`, `-v`: Enable verbose output
- `--specific-files`, `-f`: Specific files to process
- `--scan-results`, `-s`: Path to a file containing security scan results

## Understanding False Positives

Many security scan issues are false positives. See [Security Scan False Positives](security_scan_false_positives.md) for more information.

## Best Practices

When fixing security scan issues, follow these best practices:

1. **Review Changes**: Always review the changes made by the scripts before committing them.

2. **Test**: Run the security scan again after making changes to verify that the issues are fixed.

3. **Document**: Document any false positives and how they are being handled.

4. **Use Dynamic Generation**: Where possible, use dynamic generation of test credentials instead of hardcoded values.

5. **Secure Coding Practices**: Use secure coding practices to handle sensitive information:
   - Don't log sensitive information
   - Use environment variables for secrets
   - Use secure storage for secrets
   - Use proper authentication and authorization

## Handling Real Security Issues

If you discover a real security issue in the codebase, please follow the guidelines in `SECURITY.md` to report it responsibly.
