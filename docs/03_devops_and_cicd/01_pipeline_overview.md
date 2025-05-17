# Pipeline Overview

The project uses a robust CI/CD pipeline built on GitHub Actions, Docker, and security scanning.

---

## Tools Used

- **GitHub Actions:** All CI, linting, test, coverage, and deployment workflows
- **Docker & Docker Compose:** Local and CI environments, reproducible builds
- **Security Scanning:** Bandit, CodeQL, Trivy
- **pnpm audit:** Node.js dependency checks

---

## Key Lessons from Past Fixes

- **Workflow failures due to missing directories/files:** Always pre-create output directories and placeholder files for scan results (see [BANDIT_SECURITY_SCAN_FIX.md](../../BANDIT_SECURITY_SCAN_FIX.md)).
- **Local workflow testing:** Use `run_github_actions_locally.py` (see [github_actions_local_testing.md](../../github_actions_local_testing.md)) and always test locally before pushing workflow changes.
- **Windows-specific path issues:** Normalize paths and use cross-platform scripts in CI.
- **Scan result uploads:** Always check that SARIF/JSON files exist before uploading.
- **CI status monitoring:** Track all workflow runs and fixes in [github_actions_fixes_summary.md](../../github_actions_fixes_summary.md) and [update_github_actions_progress.md](../../update_github_actions_progress.md).

---

For workflow troubleshooting and optimization, see [docs/07_troubleshooting_and_faq/troubleshooting.md](../07_troubleshooting_and_faq/troubleshooting.md).