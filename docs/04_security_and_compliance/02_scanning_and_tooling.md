# Security Scanning and Tooling

This section documents the use of Bandit, CodeQL, Trivy, and pnpm audit for comprehensive security scanning.

## Tools Used

- **Bandit**: Static analysis for Python code
- **CodeQL**: Deep code scanning for vulnerabilities, secrets, and insecure patterns
- **Trivy**: Vulnerability scanning for containers and filesystems
- **pnpm audit**: Node.js dependency vulnerability scanning

## Bandit Scan Workflow Improvements

- Explicit directory creation with error handling for SARIF results
- Pre-create empty SARIF files to prevent workflow errors
- Custom Bandit config generation for each scan run
- Changed default output to JSON for reliability
- Scripts: `fix_bandit_security_scan.ps1`, `generate_bandit_config.py`, `run_bandit_scan.ps1`
- Robust error handling and verification steps before uploading scan results

See [BANDIT_SECURITY_SCAN_FIX.md](../../BANDIT_SECURITY_SCAN_FIX.md) for implementation and troubleshooting.

## CodeQL Fixes and Recommendations

- `.codeqlignore` and `.gitignore` exclude venv/third-party code from scans
- Added scripts: `fix_codeql_issues.py`, `fix_codeql_venv_issues.py` for automated security fixes
- Secure regex, remove hardcoded credentials, mask sensitive log output
- Run security scans locally before pushing
- Store all secrets in environment variables

See [codeql_fix_summary.md](../../codeql_fix_summary.md) for full details.

## Trivy & Node.js Dependency Scanning

- `pnpm audit` for JavaScript/TypeScript dependencies (see [pnpm docs](https://pnpm.io/cli/audit))
- Trivy scans all container builds and published images

See [security_scan_readme.md](../../security_scan_readme.md) for details.

## Handling False Positives

- Use `.bandit`, `.codeqlignore`, and `.trivyignore` to suppress known-safe findings
- Document reasoning for each ignore in version control

## Troubleshooting

- For persistent scan workflow issues, see `docs/07_troubleshooting_and_faq/troubleshooting.md`