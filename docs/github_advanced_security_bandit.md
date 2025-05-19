# GitHub Advanced Security Bandit Configuration

This document explains the Bandit configuration setup for GitHub Advanced Security in the pAIssive_income project.

## Overview

[Bandit](https://bandit.readthedocs.io/) is a tool designed to find common security issues in Python code. It is integrated into our CI/CD pipeline and GitHub Advanced Security to identify potential security vulnerabilities.

## Configuration Structure

The project uses a template-based configuration structure for Bandit:

1. **Template configuration**: Located in `.github/bandit/bandit-config-template.yaml`
2. **Platform-specific configurations**: Located in `.github/bandit/bandit-config-{platform}.yaml`
3. **Platform-specific test run ID configurations**: Located in `.github/bandit/bandit-config-{platform}-test_run_id.yaml`
4. **Fallback configuration**: Located in `.bandit` (root directory)

This structure allows for flexible configuration based on the platform (Linux, Windows, macOS) while maintaining consistency across environments.

## Template-based Configuration

The project has moved from individual run-specific configuration files to a template-based approach. This change:

1. **Reduces duplication**: Instead of maintaining multiple similar configuration files, we use templates
2. **Improves maintainability**: Changes to configuration settings only need to be made in one place
3. **Ensures consistency**: All platforms use the same base configuration with platform-specific overrides only when necessary

### Template Files

- `.github/bandit/bandit-config-template.yaml` - Base template for all configurations
- `.github/bandit/bandit-config-linux-template.yaml` - Linux-specific template

## Platform Configurations

- `.github/bandit/bandit-config-linux.yaml`
- `.github/bandit/bandit-config-windows.yaml`
- `.github/bandit/bandit-config-macos.yaml`

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

### Shell Injection Configuration

The configuration now uses a simplified shell injection detection approach:

```yaml
# Simplified shell configuration
shell_injection:
  no_shell: []  # Commands that don't use shell=True
  shell: []     # Commands that are allowed to use shell=True
```

This replaces the previous more verbose configuration that explicitly listed all shell commands.

## GitHub Actions Integration

The Bandit scan is integrated into the GitHub Actions workflow in `.github/workflows/consolidated-ci-cd.yml`. The workflow:

1. Determines the appropriate configuration file based on the platform
2. Installs Bandit if not already available
3. Runs Bandit with the configuration file
4. Generates a SARIF report
5. Creates an empty SARIF file as a fallback if the scan fails
6. Uploads the SARIF report to GitHub Advanced Security with the appropriate category

### Configuration Generation

The workflow now uses a simplified approach:

1. Platform-specific configuration files are used directly
2. If a platform-specific file is not available, it falls back to the template
3. The template-based approach eliminates the need to generate run-specific configurations for each workflow run

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
