# Security Fixes & Case Studies (Archive)

This file archives detailed security fix notes, workflow changes, and lessons learned from the project’s security and code scanning history.

---

## Bandit Security Scan Fixes

See the full details in [BANDIT_SECURITY_SCAN_FIX.md](../../../BANDIT_SECURITY_SCAN_FIX.md).

- Improved Bandit workflow robustness by pre-creating SARIF files and handling errors when output directories do not exist.
- Scripts updated: `fix_bandit_security_scan.ps1`, `generate_bandit_config.py`, `run_bandit_scan.ps1`.
- Switched Bandit output to JSON for reliability.
- Documented workflow troubleshooting for SARIF and Bandit.

---

## CodeQL Fixes

See [codeql_fix_summary.md](../../../codeql_fix_summary.md).

- Excluded venv/third-party code from scans.
- Automated fix scripts: `fix_codeql_issues.py`, `fix_codeql_venv_issues.py`.
- Hardcoded credentials, insecure regex, and logging of secrets remediated.
- Local CodeQL scan workflows improved.

---

## Input Validation and Syntax Fixes

See [syntax_fix_readme.md](../../../syntax_fix_readme.md).

- Enforced input validation for all subprocess and user inputs.
- Documented migration from ad-hoc validation to Pydantic/FastAPI-based schemas.

---

## Miscellaneous Fixes

- Docker Compose, MCP Adapter, and workflow fixes are archived in:
  - [docker-compose-fix-README.md](../../../docker-compose-fix-README.md)
  - [MCP_ADAPTER_FIX.md](../../../MCP_ADAPTER_FIX.md)
  - [MCP_WORKFLOW_FIX.md](../../../MCP_WORKFLOW_FIX.md)

For full details, see the individual archived files.

---

This archive preserves the history of major fixes for future audits and onboarding.