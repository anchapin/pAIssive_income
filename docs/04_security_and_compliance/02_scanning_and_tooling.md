# Security Scanning and Tooling

This section documents the use of Bandit, CodeQL, Trivy, and pnpm audit for comprehensive security scanning.

## Tools Used

- **Bandit**: Static analysis for Python code
- **CodeQL**: Deep code scanning for vulnerabilities, secrets, and insecure patterns
- **Trivy**: Vulnerability scanning for containers and filesystems
- **pnpm audit**: Node.js dependency vulnerability scanning

## Bandit Scan Workflow Improvements

- Template-based configuration approach for improved maintainability
- Simplified shell injection configuration
- Enhanced directory exclusions for more comprehensive scanning
- Pre-create empty SARIF files to prevent workflow errors
- Explicit directory creation with error handling for SARIF results
- Robust error handling and verification steps before uploading scan results

See [bandit_configuration.md](../bandit_configuration.md) and [bandit_configuration_changes.md](../bandit_configuration_changes.md) for implementation details and recent changes.

## CodeQL Configuration and Security Fixes

### Configuration Status ✅ COMPLETE
- **Configuration Files**: All CodeQL workflow and configuration files are properly structured and validated
- **Category Naming**: Standardized category naming across all CodeQL workflows (fixed inconsistencies)
- **Path Exclusions**: `.codeqlignore` properly excludes venv/third-party code from scans
- **Query Suites**: Using `security-and-quality` queries for comprehensive coverage

### Security Issues Resolved ✅ COMPLETE
- **Clear-text Logging**: Fixed all instances of sensitive information being logged in clear text
- **Backend Information**: Removed sensitive backend identifiers from error messages
- **Generic Messages**: Replaced specific error details with generic security-safe messages
- **Comments Added**: Added security-focused comments explaining the rationale for changes

### Key Files Fixed
- `common_utils/secrets/secrets_manager.py`: All logging statements now use generic messages
- Error messages like "Invalid backend specified" instead of logging actual backend values
- Comments clearly indicate security considerations for each change

### Validation Complete
- All YAML configuration files pass syntax validation
- CodeQL workflows properly configured for JavaScript/TypeScript and Python
- Security fixes verified to not expose sensitive information
- Configuration tested and ready for production use

### Sustainability Measures
- Clear documentation of security patterns to follow
- Comments in code explaining security rationale
- Standardized approach for handling sensitive information in logs
- Configuration files designed to prevent future security issues

See [codeql_fix_summary.md](../../codeql_fix_summary.md) for historical details.

## Trivy & Node.js Dependency Scanning

- `pnpm audit` for JavaScript/TypeScript dependencies (see [pnpm docs](https://pnpm.io/cli/audit))
- Trivy scans all container builds and published images

See [security_scan_readme.md](../../security_scan_readme.md) for details.

## Handling False Positives

- Use `.bandit`, `.codeqlignore`, and `.trivyignore` to suppress known-safe findings
- Document reasoning for each ignore in version control

## Troubleshooting

- For persistent scan workflow issues, see `docs/07_troubleshooting_and_faq/troubleshooting.md`