# Security Overview

This document outlines the project's security strategy, policies, and key best practices.

## Security Policy

See [SECURITY.md](../../SECURITY.md) for the official security policy and reporting procedures.

## Security Strategy & Best Practices

- **No use of pickle/marshal for serialization**
- **All network operations must have timeouts**
- **Input validation required for all external data**
- **Secure defaults for all configurations**
- **Explicit imports only (no * imports)**
- **Never use `shell=True` with subprocess calls**
- **Validate all command arguments for subprocess calls**
- **Use absolute paths for executables when possible**

## Secure Development Workflow

- Security review required for all PRs
- No sensitive data in logs/comments
- Regular dependency updates
- Code scanning must pass before merge

## Recent Security Fixes

- Input validation for all subprocess calls (`shell=False` everywhere)
- Secure attribute access for agents
- DiskCache now uses JSON-only serialization (no pickle)
- API/server binding restricted to `127.0.0.1` by default
- Network timeouts on all operations
- Hash operations updated for cryptographic best practices
- Secure logging system implemented (see below)

## Secure Logging Implementation

See [security_fixes.md](../../security_fixes.md) and [security_fixes_summary.md](../../security_fixes_summary.md) for full details. In summary:
- All sensitive data is masked before logging or storing
- Custom `SecureLogger` masks secrets automatically
- No sensitive data is logged or stored in clear text

## Security Monitoring and Audits

- GitHub security/code scanning enabled
- Dependabot and pnpm audit for dependencies
- Weekly review of security alerts
- Monthly dependency audit
- Quarterly full codebase security review

## For a full history of applied fixes, see [Security Fixes Archive](../09_archive_and_notes/)