# GitHub Advanced Security Bandit Configuration

This document explains the Bandit configuration setup for GitHub Advanced Security in the pAIssive_income project.

## Overview

[Bandit](https://bandit.readthedocs.io/) is a tool designed to find common security issues in Python code. It is integrated into our CI/CD pipeline and GitHub Advanced Security to identify potential security vulnerabilities.

## Configuration Structure

The project uses a hierarchical configuration structure for Bandit:

1. **Platform-specific run ID configurations**: Located in `.github/bandit/bandit-config-{platform}-{run_id}.yaml`
2. **Generic platform configurations**: Located in `.github/bandit/bandit-config-{platform}.yaml`
3. **Fallback configuration**: Located in `.bandit` (root directory)

This structure allows for flexible configuration based on the platform (Linux, Windows, macOS) and specific run IDs.

## Run ID-specific Configurations

The following run ID-specific configurations are available:

### Linux
- `.github/bandit/bandit-config-linux-14974236301.yaml`
- `.github/bandit/bandit-config-linux-14976101411.yaml`
- `.github/bandit/bandit-config-linux-14977094424.yaml`
- `.github/bandit/bandit-config-linux-14977626158.yaml`
- `.github/bandit/bandit-config-linux-14978521232.yaml`
- `.github/bandit/bandit-config-linux-14987452007.yaml`

### Windows
- `.github/bandit/bandit-config-windows-14974236301.yaml`
- `.github/bandit/bandit-config-windows-14976101411.yaml`
- `.github/bandit/bandit-config-windows-14977094424.yaml`
- `.github/bandit/bandit-config-windows-14977626158.yaml`
- `.github/bandit/bandit-config-windows-14978521232.yaml`
- `.github/bandit/bandit-config-windows-14987452007.yaml`

### macOS
- `.github/bandit/bandit-config-macos-14974236301.yaml`
- `.github/bandit/bandit-config-macos-14976101411.yaml`
- `.github/bandit/bandit-config-macos-14977094424.yaml`
- `.github/bandit/bandit-config-macos-14977626158.yaml`
- `.github/bandit/bandit-config-macos-14978521232.yaml`
- `.github/bandit/bandit-config-macos-14987452007.yaml`

## Generic Platform Configurations

- `.github/bandit/bandit-config-linux.yaml`
- `.github/bandit/bandit-config-windows.yaml`
- `.github/bandit/bandit-config-macos.yaml`

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

1. Determines the appropriate configuration file based on the platform and run ID
2. Installs Bandit if not already available
3. Runs Bandit with the configuration file
4. Generates a SARIF report
5. Uploads the SARIF report to GitHub Advanced Security with the appropriate category

## Running Bandit Locally

To run Bandit locally with the same configuration as the CI/CD pipeline:

```bash
# Install Bandit
pip install bandit

# Run Bandit with the configuration file
bandit -r . -c .github/bandit/bandit-config-linux.yaml  # For Linux
bandit -r . -c .github/bandit/bandit-config-windows.yaml  # For Windows
bandit -r . -c .github/bandit/bandit-config-macos.yaml  # For macOS
```

## Troubleshooting

If you encounter issues with Bandit in the GitHub Advanced Security setup:

1. Check that the configuration files are properly formatted
2. Verify that the SARIF output is valid
3. Ensure that the GitHub Actions workflow is using the correct category name for the SARIF upload

## References

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [GitHub Advanced Security Documentation](https://docs.github.com/en/github/finding-security-vulnerabilities-and-errors-in-your-code)
- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
