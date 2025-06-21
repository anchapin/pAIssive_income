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

### Jules Environment Setup

For developers using [Jules](https://jules.google/docs/environment/) VM environments, the project includes a specialized setup script optimized for Jules environments.

**Setup Script:** `setup-jules.sh`

This script provides a streamlined setup experience specifically designed for Jules VM environments:

**Features:**
- **System Package Installation:** Installs Python 3.10+, Node.js 20+, and development tools
- **Automatic Tool Installation:** Installs `uv` and `pnpm` package managers
- **Virtual Environment Creation:** Uses `uv` for fast virtual environment setup
- **Comprehensive Dependency Installation:** Installs all project extras and additional required packages
- **Build Process:** Builds Tailwind CSS and creates necessary directories
- **CI Environment Configuration:** Sets up environment variables for automated testing

**Usage:**
```bash
./setup-jules.sh
```

**What it does:**
1. Checks for Python 3 and Node.js prerequisites
2. Installs `uv` (Python package manager) if not present
3. Installs `pnpm` (Node.js package manager) if not present
4. Creates a Python virtual environment using `uv`
5. Installs Python dependencies from `requirements.txt` and `requirements-dev.txt`
6. Installs Node.js dependencies using `pnpm`
7. Sets up `.env` configuration files
8. Runs validation tests to ensure everything works
9. Provides an environment summary with tool versions

**When to use:**
- Working in a Jules VM environment
- Need a quick, streamlined setup
- Prefer automatic tool installation without configuration options
- Setting up for the first time in a clean environment

For more detailed setup options and configuration, use the enhanced setup script described above.

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

### Python Testing
- Minimum 90% line coverage required (enforced in CI).
- Run `python scripts/run/run_tests.py --with-coverage` before PRs.
- All new features/bugfixes must have unit and/or integration tests, covering edge/error cases.
- Use pytest markers to organize tests (`unit`, `integration`, `slow`, etc.).
- Place tests in the appropriate `tests/` subdirectory.
- Mock external dependencies in unit tests.
- All tests must pass in CI.

### Frontend Testing (React/JavaScript)
- Use Vitest for unit testing React components and JavaScript/TypeScript code.
- Test files for React components should use `.jsx` extensions for better tooling support.
- Run frontend tests with `pnpm test` from the `ui/react_frontend` directory.
- Use the enhanced test setup (`tests/setup.ts`) which provides:
  - TypeScript support for better type safety
  - Comprehensive browser API mocking (matchMedia, localStorage, sessionStorage)
  - Global fetch API mocking with typed implementations
  - Proper test isolation and cleanup
  - Environment variable handling for cross-platform testing
- Include React imports in JSX test files and use proper wrapper components.
- Mock external dependencies and APIs appropriately.
- Ensure tests work in both local development and CI environments.

---

## Contribution Checklist

- [ ] Code includes tests covering new/changed logic and edge/error cases.
- [ ] Ran `python scripts/run/run_tests.py --with-coverage` and coverage is ≥90%.
- [ ] For frontend changes: Ran `pnpm test` from `ui/react_frontend` directory.
- [ ] Code passes all linting and type checks (`ruff`, `mypy`, etc.).
- [ ] All automated tests pass in CI.
- [ ] Documentation and docstrings are updated.
- [ ] For React components: Used `.jsx` extensions and proper test setup.

---

For additional details, see the [Project Overview & Getting Started](../00_introduction/01_overview.md).