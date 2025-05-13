# Bandit Configuration for GitHub Advanced Security

This document explains the Bandit configuration used for security scanning in the GitHub Advanced Security setup.

## Overview

[Bandit](https://bandit.readthedocs.io/) is a tool designed to find common security issues in Python code. It is integrated into our CI/CD pipeline and GitHub Advanced Security to identify potential security vulnerabilities.

## Configuration Files

The project uses two configuration files for Bandit:

1. `.bandit` - A simple configuration file in INI format
2. `bandit.yaml` - A more detailed configuration file in YAML format

Both files contain similar settings, but the YAML file provides more flexibility and detailed configuration options.

## Key Configuration Settings

### Excluded Directories

The following directories are excluded from security scans:

- `tests` - Test files
- `venv`, `.venv`, `env`, `.env` - Virtual environments
- `__pycache__` - Python cache files
- `custom_stubs` - Custom type stubs
- `node_modules` - Node.js dependencies
- `build`, `dist` - Build artifacts

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

1. Installs Bandit if not already available
2. Runs Bandit with the configuration file
3. Generates a SARIF report
4. Uploads the SARIF report to GitHub Advanced Security

## Running Bandit Locally

To run Bandit locally with the same configuration as the CI/CD pipeline:

```bash
# Install Bandit
pip install bandit

# Run Bandit with the configuration file
bandit -r . -c .bandit

# Or with the YAML configuration
bandit -r . -c bandit.yaml
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
