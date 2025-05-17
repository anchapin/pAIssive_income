# GitHub Actions

This section describes our CI/CD implementation with GitHub Actions.

## Overview

- All CI, linting, coverage, and deployment workflows run via GitHub Actions.
- Uses Docker Buildx for reproducible builds.
- Handles security scans (Bandit, CodeQL, Trivy) and test coverage gates.
- Automated pre-commit and Ruff checks on push and PR.

## Key Practices

- All workflows are defined in `.github/workflows/`.
- Security scan and linting workflows must pass before merge.
- Local workflow dry-runs are documented in [github_actions_local_testing.md](../../github_actions_local_testing.md) (archived for advanced reference).
- See `run_github_actions_locally.py` for local workflow emulation.

## Troubleshooting & Fixes

- See [docs/07_troubleshooting_and_faq/troubleshooting.md](../07_troubleshooting_and_faq/troubleshooting.md) for common workflow issues and fixes.
- Historical fixes, optimization notes, and migration plans are archived in the [Archive & Notes](../09_archive_and_notes/claude_coding_best_practices.md).

## Optimization & History

- Workflow optimization and consolidation history are available in:
  - [github_actions_fixes_summary.md](../../github_actions_fixes_summary.md)
  - [github_actions_consolidation.md](../../github_actions_consolidation.md)
  - [github_actions_workflow_optimization.md](../../github_actions_workflow_optimization.md)

Relevant, up-to-date workflow practices are maintained in this document.