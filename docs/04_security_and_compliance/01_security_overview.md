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

For more details, see the following sections.
