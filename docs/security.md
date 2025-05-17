# Security Documentation

## Overview
This document outlines security measures, fixes, and procedures implemented in the project.

## Recent Security Fixes

### Subprocess Security (May 2025)
- Added input validation for all subprocess calls
- Implemented absolute path resolution using `shutil.which()`
- Added checks for shell metacharacters to prevent command injection
- Fixed security issues in `install_mcp_sdk.py`, `setup_dev_environment.py`, and `enhanced_setup_dev_environment.py`
- All subprocess calls use `shell=False` to prevent shell injection attacks

### ResearchAgent Attribute Access
- Implemented secure attribute access using `self._name`
- Added input validation for all attributes
- Prevents unauthorized attribute access and injection attacks

### DiskCache Security
- Removed unsafe pickle serialization
- Implemented JSON-only serialization
- Prevents deserialization attacks and code execution

### Server Security
- Changed binding from 0.0.0.0 to 127.0.0.1
- Restricted access to localhost only
- Prevents unauthorized external access

### Network Security
- Added 30-second timeout on all network operations
- Implemented in InvoiceDelivery and related components
- Prevents hanging connections and DoS attacks

### Import Security
- Fixed import order in calculator.py and niche_analyzer.py
- Prevents module resolution attacks
- Ensures consistent and secure module loading

### Hash Operations
- Added `usedforsecurity=False` to SHA-256 operations
- Updated hash implementations in disk_cache.py and niche_analyzer.py
- Follows cryptographic best practices

## Monitoring Procedures

### Automated Monitoring
- GitHub security alerts enabled
- Dependabot alerts for dependency vulnerabilities
- Code scanning enabled for all pull requests

### Manual Monitoring
- Weekly security review of new changes
- Monthly dependency audit
- Quarterly full codebase security review

## Security Best Practices

### Code Guidelines
1. No use of pickle/marshal for serialization
2. All network operations must have timeouts
3. Input validation required for all external data
4. Use secure defaults for all configurations
5. Explicit imports only (no * imports)
6. Never use `shell=True` with subprocess calls
7. Always validate command arguments for subprocess calls
8. Use absolute paths for executables when possible

### Development Workflow
1. Security review required for all PRs
2. No sensitive data in logs/comments
3. Regular dependency updates
4. Code scanning must pass before merge

## Audit Schedule

### Weekly
- Review security alerts
- Check dependency vulnerabilities
- Monitor system logs

### Monthly
- Full dependency audit
- Review access controls
- Check configuration settings

### Quarterly
- Complete codebase security review
- Update security documentation
- Review security procedures

---

## Bandit Security Scan Optimization

Bandit security scans are configured for both accuracy and speed:

- **Parallel Processing**: Scans are run with 4 parallel workers (`-n 4`), significantly reducing scan time on multicore machines.
- **Targeted Scanning**: Only source code directories are scanned (`api/`, `app_flask/`, `services/`, `common_utils/`, `users/`, and `main.py`), avoiding unnecessary files.
- **Expanded Exclusions**: Large or irrelevant directories are excluded from scans, including:
  - `tests`, `venv`, `.venv`, `env`, `.env`, `__pycache__`, `custom_stubs`, `node_modules`, `build`, `dist`, `docs`, `docs_source`, `junit`, `bin`, `dev_tools`, `scripts`, `tool_templates`
- **Configuration Sync**: Both the Bandit configuration and scan scripts use these optimized settings for consistency.

For details or changes, see `run_bandit_scan.ps1` and `bandit.yaml`.
