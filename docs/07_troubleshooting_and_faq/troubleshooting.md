# Troubleshooting

Common issues, fixes, and lessons learned.

---

## Agent/Adapter & Workflow Issues

- **Agent Adapter (MCP) Problems:** Ensure agent servers are started *after* core services and database initialization.  
  - For sequencing issues, see [MCP_ADAPTER_FIX.md](../../MCP_ADAPTER_FIX.md) (archive).
- **Workflow orchestration:** Avoid race conditions by using explicit health checks and retries in workflow scripts ([MCP_WORKFLOW_FIX.md](../../MCP_WORKFLOW_FIX.md)).

---

## Syntax, Linting, and Formatting

- **Fixing syntax errors:** Use `python fix_syntax_errors.py` for quick bulk fixes.
- **Common syntax issues:**  
  - Unmatched quotes, missing colons, indentation errors, and line length violations (see [syntax_fix_readme.md](../../syntax_fix_readme.md)).
- **Formatting:** Always run `python fix_formatting.py` and use pre-commit hooks.

---

## GitHub Actions & CI

- **Workflow failures due to missing outputs:** Ensure required directories and files (e.g., SARIF, log outputs) are pre-created.
- **Platform differences:** Use only cross-platform shell and path constructs in scripts.
- **Debugging workflows:** Test locally with `run_github_actions_locally.py` before pushing; see [github_actions_local_testing.md](../../github_actions_local_testing.md).
- **Summary of past fixes:** See [github_actions_fixes_summary.md](../../github_actions_fixes_summary.md) and [workflow_fixes_summary.md](../../workflow_fixes_summary.md).

---

## Security & Scanning

- **Bandit/CodeQL/Trivy scan workflow issues:**  
  - Pre-create output files, handle errors on upload, and check for platform-specific path bugs.  
  - See [security_scan_readme.md](../../security_scan_readme.md) and [BANDIT_SECURITY_SCAN_FIX.md](../../BANDIT_SECURITY_SCAN_FIX.md).
- **Suppressing false positives:** Use `.bandit`, `.codeqlignore`, `.trivyignore` with documented justification.

---

## Docker & DevOps

- **Docker Compose startup issues:**  
  - Set explicit container dependencies (`depends_on`), and use healthchecks.  
  - Do not hardcode credentials in compose files; use env vars instead ([docker-compose-fix-README.md](../../docker-compose-fix-README.md)).
- **Kubernetes deployment:** Ensure secrets/configmaps are mounted correctly.

---

## General

- **Improvement plans and test status:** See [improvement_plan.md](../../improvement_plan.md) and [test_status_report.md](../../test_status_report.md) for historical tracking and context.
- **Track DevOps tasks:** [devops_tasks_status.md](../../devops_tasks_status.md) logs DevOps issues and resolutions.

---

If you encounter issues not covered here, see [docs/09_archive_and_notes/](../09_archive_and_notes/) for full details and audit trails, or open an issue.