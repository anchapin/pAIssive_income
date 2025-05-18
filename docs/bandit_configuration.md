# Bandit Configuration for GitHub Advanced Security

This document explains the Bandit configuration used for security scanning in the GitHub Advanced Security setup.

## Overview

[Bandit](https://bandit.readthedocs.io/) is a tool designed to find common security issues in Python code. It is integrated into our CI/CD pipeline and GitHub Advanced Security to identify potential security vulnerabilities.

## Configuration Files

The project uses a template-based configuration approach for Bandit:

1. `.github/bandit/bandit-config-template.yaml` - Base template for all configurations
2. `.github/bandit/bandit-config-{platform}.yaml` - Platform-specific configurations
3. `.bandit` - A simple fallback configuration file in INI format

For detailed information about the configuration structure and recent changes, see:
- [GitHub Advanced Security Bandit Configuration](github_advanced_security_bandit.md)
- [Bandit Configuration Changes](bandit_configuration_changes.md)

## Key Configuration Settings

### Excluded Directories

The following directories are excluded from security scans:

- `tests` - Test files
- `venv`, `.venv`, `env`, `.env` - Virtual environments
- `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache` - Cache directories
- `custom_stubs` - Custom type stubs
- `node_modules` - Node.js dependencies
- `build`, `dist` - Build artifacts
- `docs`, `docs_source` - Documentation
- `junit`, `bin`, `dev_tools`, `scripts`, `tool_templates` - Tools and utilities

### Skipped Tests

The following tests are skipped:

- `B101` - Use of assert detected (acceptable in test files)
- `B311` - Standard pseudo-random generators are not suitable for security/cryptographic purposes

### Output Format

The output format is set to SARIF (Static Analysis Results Interchange Format) for integration with GitHub Advanced Security.

### Severity and Confidence Levels

- Severity: MEDIUM
- Confidence: MEDIUM

## GitHub Actions Integration

The Bandit scan is integrated into the GitHub Actions workflow in `.github/workflows/consolidated-ci-cd.yml`. The workflow:

1. Determines the appropriate configuration file based on the platform
2. Installs Bandit if not already available
3. Runs Bandit with the configuration file
4. Generates a SARIF report
5. Creates an empty SARIF file as a fallback if the scan fails
6. Uploads the SARIF report to GitHub Advanced Security

The workflow now uses a simplified approach that eliminates the need to generate run-specific configurations for each workflow run. Instead, it uses platform-specific configuration files directly and falls back to templates if needed.

## Running Bandit Locally

To run Bandit locally with the same configuration as the CI/CD pipeline:

```bash
# Install Bandit
pip install bandit

# Run Bandit with the platform-specific configuration file
bandit -r . -c .github/bandit/bandit-config-linux.yaml  # For Linux
bandit -r . -c .github/bandit/bandit-config-windows.yaml  # For Windows
bandit -r . -c .github/bandit/bandit-config-macos.yaml  # For macOS

# Or with the fallback configuration
bandit -r . -c .bandit
```

## Troubleshooting

If you encounter issues with Bandit in the GitHub Advanced Security setup:

1. Check that the configuration files (`.bandit` and `bandit.yaml`) are properly formatted
2. Verify that the SARIF output is valid
3. Ensure that the GitHub Actions workflow is using the correct category name for the SARIF upload

## References

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [GitHub Advanced Security Documentation](https://docs.github.com/en/github/finding-security-vulnerabilities-and-errors-in-your-code)
- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
