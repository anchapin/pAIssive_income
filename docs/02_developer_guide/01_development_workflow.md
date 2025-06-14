# Development Workflow

This document describes the standard development process, coding standards, and contribution requirements for the pAIssive Income project.

---

## Environment Tooling

- **Python:** All Python dependencies and environments must be managed using [`uv`](https://github.com/astral-sh/uv). Do not use `pip` or `venv` directly.
- **Node.js:** All Node.js dependencies and scripts must be managed using [`pnpm`](https://pnpm.io/). Do not use `npm` or `yarn`.

All contributions must use `uv` (for Python) and `pnpm` (for Node.js). Other tools are not supported for development or CI.

### OpenHands Development Environment

For developers using [OpenHands](https://github.com/All-Hands-AI/OpenHands) (formerly SWE-Agent), the project includes an automated setup script that configures the development environment with all required dependencies.

**Setup Script:** `.openhands/setup.sh`

This script automatically installs:
- **Node.js 18.x (LTS)** - JavaScript runtime
- **npm** - Node.js package manager (comes with Node.js)
- **python3-pip** - Python package installer
- **pnpm 8.6.0** - Fast, disk space efficient package manager (pinned version)
- **uv 0.4.30** - Ultra-fast Python package installer and resolver (pinned version)

**Features:**
- **Pinned Versions:** All packages use specific versions for reproducible builds
- **Error Handling:** Comprehensive error checking and logging with timestamps
- **Verification:** Automatic verification of all installed tools
- **Optimized Installation:** Uses consolidated sudo commands for efficiency
- **Cache Management:** Proper cleanup of package manager caches

**Usage:**
The setup script runs automatically when the OpenHands runtime container starts. No manual intervention is required.

**Verification:**
After setup completion, the script verifies all installations:
```bash
node --version    # Should show Node.js 18.x
npm --version     # Should show npm version
pnpm --version    # Should show 8.6.0
uv --version      # Should show 0.4.30
```

This ensures a consistent development environment across all OpenHands instances and maintains compatibility with the project's tooling requirements.

---

## Branching & PR Process

- Use feature branches or bugfix branches for all changes.
- All PRs must pass CI (tests, linting, type checks) and undergo code review.
- Security review is required for all PRs.
- Update documentation and add usage examples/docstrings for new features.

---

## Linting & Formatting

### Ruff for Python

- Ruff is used for both linting and formatting Python code, configured via `ruff.toml`.
- Run `python scripts/fix/fix_linting_issues.py` to fix linting issues, or use the pre-commit hook.
- Exclude files by adding patterns to `.lintignore`.
- Parallel processing is supported (`--jobs` flag).

> **Note:** All up-to-date linting, formatting, and pre-commit standards are maintained in this document. Code quality utility scripts (including `fix_linting_issues.py`) are in the `scripts/fix/` directory. Update all references and CI/CD examples to use `scripts/fix/fix_linting_issues.py` instead of any old root path.

### Formatting

- Use `python scripts/fix/fix_formatting.py` to auto-fix formatting.
- Do **not** use Black; Ruff is the canonical formatter.
- Pre-commit hooks (see `.pre-commit-config.yaml`) enforce linting/formatting before each commit.

### Best Practices

- Run linting and formatting before committing.
- Use the `--check` flag for preview.
- Configure your IDE to use Ruff.

---

## Testing Standards

- Minimum 90% line coverage required (enforced in CI).
- Run `python scripts/run/run_tests.py --with-coverage` before PRs.
- All new features/bugfixes must have unit and/or integration tests, covering edge/error cases.
- Use pytest markers to organize tests (`unit`, `integration`, `slow`, etc.).
- Place tests in the appropriate `tests/` subdirectory.
- Mock external dependencies in unit tests.
- All tests must pass in CI.

---

## Contribution Checklist

- [ ] Code includes tests covering new/changed logic and edge/error cases.
- [ ] Ran `python scripts/run/run_tests.py --with-coverage` and coverage is ≥90%.
- [ ] Code passes all linting and type checks (`ruff`, `mypy`, etc.).
- [ ] All automated tests pass in CI.
- [ ] Documentation and docstrings are updated.

---

For additional details, see the [Project Overview & Getting Started](../00_introduction/01_overview.md).