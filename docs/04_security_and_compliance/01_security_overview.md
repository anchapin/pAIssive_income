# Security Overview

This document summarizes the security posture, policies, and best practices for the project.

## Security Policy & Reporting

See [SECURITY.md](../../SECURITY.md) for the official security policy and reporting procedures.

## Overview

Security is a first-class concern across all areas of the codebase. Key areas include:
- Safe handling of secrets and credentials
- Secure logging (no sensitive data in logs)
- Secure serialization and deserialization
- Input validation everywhere (network, user, API)
- Secure configuration and defaults
- Regular dependency and code scanning

## Quick Links

- [Security Scanning & Tooling](02_scanning_and_tooling.md)
- [Secrets Management](03_secrets_management.md)
- [Input Validation Standards](04_input_validation_standards.md)
- [Security Fixes & Case Studies](../09_archive_and_notes/security_fixes_summaries.md)

## Best Practices

- No use of `pickle` or unsafe serialization
- All network operations must have explicit timeouts
- Input validation is required for all external data
- No `shell=True` in subprocess calls
- Secure logger (see implementation in common_utils/logging)
- Mask secrets in logs and outputs
- Secure defaults in configs
- Security review required for all PRs

## Enhanced Security Infrastructure (PR #139)

### Automated Security Scanning
- **Comprehensive Tool Coverage**: Bandit, Safety, Semgrep, Trivy, pip-audit, Gitleaks
- **Cross-Platform Support**: Platform-specific security tool installation and execution
- **SARIF Integration**: Proper SARIF format reports for GitHub Security tab integration
- **Automated Fallback Creation**: `scripts/security/create_security_fallbacks.py` prevents workflow failures

### Security Scan Configuration
- **Bandit**: Configured with `.bandit` file to exclude test directories and skip common false positives
- **Safety**: Scans Python dependencies for known vulnerabilities
- **CodeQL**: Performs static analysis for security issues
- **Trivy**: Scans container images for vulnerabilities
- **Semgrep**: Additional static analysis (Unix platforms only)
- **pip-audit**: Python package vulnerability scanning
- **Gitleaks**: Secret scanning for exposed credentials

### Security Workflow Improvements
- **Enhanced Error Handling**: Prevents security scan failures from blocking CI
- **Platform-Aware Execution**: Different security tools for different platforms
- **Automated Report Generation**: Consistent security report structure
- **Threshold Management**: Configurable security scan thresholds

For more details, see the following sections.
