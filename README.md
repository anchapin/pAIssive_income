# Project Environment & Dependency Management

## Python

> **Note:** Documentation for this project has been centralized. Please see the [docs/](docs/) directory for additional onboarding, development, deployment, security, and contribution information.

---

## TL;DR Quickstart

1. **Clone the repo and enter it:**

   ```bash
   git clone https://github.com/anchapin/pAIssive_income.git
   cd pAIssive_income
   ```

2. **Install `uv` (if not already installed):**
   `uv` is a fast Python package installer and resolver, written in Rust.

   ```bash
   # Using pip (recommended if you have Python/pip)
   pip install uv

   # Or using the standalone installer (Linux/macOS)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   Ensure `uv` is in your PATH.

3. **Set up development environment (Python, dependencies, pre-commit hooks, IDE config):**
   (Requires Python 3.8+ and `uv`)

   ```bash
   # On Windows
   enhanced_setup_dev_environment.bat

   # On Unix/Linux
   ./enhanced_setup_dev_environment.sh
   # If you used setup_dev_environment.py directly before, use enhanced_setup_dev_environment.py
   # python enhanced_setup_dev_environment.py
   ```

   This script will use `uv` to:
   - Create a virtual environment (`.venv`)
   - Install dependencies from `requirements.txt` and `requirements-dev.txt`
   - Install the project in editable mode (`-e .`)
   - Set up pre-commit hooks (installing `pre-commit` via `uv`)
   - Configure IDE settings for VS Code and PyCharm
   - Create .editorconfig for editor-agnostic settings

   For manual setup using `uv`:

   ```bash
   # Create virtual environment (specify your Python interpreter if needed)
   uv venv .venv --python python3.12
   # Activate virtual environment
   source .venv/bin/activate  # Or: .venv\Scripts\activate (Windows)
   # Install dependencies
   uv pip install -r requirements.txt -r requirements-dev.txt -e .
   # Install pre-commit and hooks
   uv pip install pre-commit
   pre-commit install
   ```

4. **Start the modern web UI (requires Node.js 14+ and pnpm):**

   ```bash
   python ui/run_ui.py
   ```

   If your browser doesn't open, visit [http://localhost:3000](http://localhost:3000).
   > **Frontend dependencies are now managed with [pnpm](https://pnpm.io/).**
   > To install pnpm, the recommended way is to use Corepack (included with Node.js v16.10+):
>
   > ```bash
   > corepack enable
   > ```
>
   > If Corepack is not available, you can install pnpm globally using npm:
>
   > ```bash
   > npm install -g pnpm
   > ```
>
5. **Run all tests (unit, integration, frontend):**
   See the "Running Tests" section below.

---

## Overview

- **Dependency Locking**:
  This project uses a `requirements.lock` file to ensure reproducible environments. After updating dependencies, **install both `requirements.txt` and `requirements-dev.txt`**, then regenerate the lockfile:
  ```sh
  pip install -r requirements.txt -r requirements-dev.txt
  pip freeze > requirements.lock
  ```

- **Development dependencies** are managed with `requirements-dev.txt`.

## Node.js

- **Install dependencies**:
  ```sh
  npm ci
  ```
- Dependencies are pinned via `package-lock.json`.
- **Security scanning**: `npm audit` is run automatically in CI to detect vulnerabilities.

## Automated Dependency Updates

- [Dependabot](https://docs.github.com/en/code-security/dependabot) is enabled for Python, Node.js, Docker, and GitHub Actions dependencies. Update PRs are created automatically, including for the Python lockfile (`requirements.lock`).

## Vulnerability Scanning

- Security scanning runs automatically on pushes and pull requests:
  - Python: `pip-audit`, `safety`
  - Node.js: `npm audit`
  - Static analysis: `bandit`, `semgrep`, `pylint`
  - Container: `trivy`
  - Secret scanning: `gitleaks`

## Best Practices

- Regularly review and address Dependabot and security scan PRs.
- Regenerate the Python lockfile after any dependency updates.
- See `.github/workflows/security_scan.yml` for the full list of automated checks.

## Keeping Dependencies Healthy

- When adding or removing Python dependencies, update both `requirements.txt`/`requirements-dev.txt` and **regenerate `requirements.lock`**.
- For Node.js, always use `npm ci` for installation and let Dependabot update `package-lock.json`.
- Review and merge Dependabot PRs and address security alerts promptly.

## Dependency Upgrade and Removal Workflow

This repository contains a summary of the project and high-level information. The main onboarding guide, including development setup, installation, and usage details, is maintained in the documentation directory for consistency and easier updates.

If you are new to this project, start here:

- [Getting Started Guide](docs/getting-started.md)

For quick reference, the following topics are included in the full guide:

- Development environment setup (Python, Node, etc.)
- Installing dependencies
- Running and developing with the framework
- Using the CLI and web UI
- Pre-commit hooks and code quality
- Linting, syntax fixes, and CI workflows

**Note:** This README is intentionally concise. See the documentation for complete and up-to-date instructions.

---

## Running Tests

The project includes Python and JavaScript/TypeScript tests.

### Python Unit/Integration Tests

From the repo root, after environment setup:

```bash
pytest
# or
python -m pytest
```

### Frontend End-to-End (E2E) Tests

> **Requires:** Node.js 14+, [pnpm](https://pnpm.io/), and the UI dev server running at `http://localhost:3000`

1. Install Playwright and its browsers (first time only):

   ```bash
   cd ui/react_frontend
   pnpm install
   pnpm exec playwright install
   ```

2. Run all E2E tests:

   ```bash
   pnpm exec playwright test
   ```

3. See `ui/react_frontend/tests/e2e/` for sample E2E tests.
   To run a specific test:

   ```bash
   pnpm exec playwright test tests/e2e/niche_analysis.spec.ts
   ```

Test output and screenshots will appear in the Playwright reports directory.

---

## Example Output

Running the main script generates a complete project plan including:

- Niche analysis with opportunity scores
- Detailed user problem analysis
- Solution design with features and architecture
- Monetization strategy with subscription tiers and revenue projections
- Marketing plan with user personas and channel strategies

## Requirements

- Python 3.8+
- `uv` (Python package installer and resolver). Install via `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- Node.js 14.0+ (for modern UI and frontend tests)
- [pnpm](https://pnpm.io/) (for frontend dependencies)
  To install pnpm, the recommended way is to use Corepack (included with Node.js v16.10+):

  ```bash
  corepack enable
  ```

  If Corepack is not available, you can install pnpm globally using npm:

  ```bash
  npm install -g pnpm
  ```

- PostgreSQL 15+ (for database)
  The project uses PostgreSQL as the database backend. See [DATABASE.md](DATABASE.md) for setup and migration instructions.

- Dependencies listed in each module's README

## Code Style and Formatting

The project enforces consistent code style and formatting through pre-commit hooks and automated tools. Here are the key formatting guidelines and tools:

### IDE Setup

We recommend configuring your IDE or editor to use Ruff as the primary formatter for a smooth development experience. Configuration files are provided for VS Code, PyCharm, and other editors.

See the [IDE Setup Guide](docs/ide_setup.md) for detailed instructions on configuring your development environment.

### Common Formatting Issues to Watch For

- Trailing whitespace at the end of lines
- Missing newline at end of files
- Inconsistent indentation (use 4 spaces, not tabs)
- Type annotation issues caught by MyPy
- Ruff linting violations (see .ruff.toml for rules)

### Ruff Linting

To ensure consistent code formatting and prevent CI pipeline failures:

1. Before committing changes, run Ruff locally to fix any formatting issues:

   ```bash
   ruff check . --fix
   ```

2. The CI pipeline has been configured to:
   - Automatically fix and commit Ruff formatting issues
   - Continue execution even if Ruff check-only mode finds issues

This helps maintain code quality while preventing pipeline failures due to formatting issues.

### Using Pre-commit Hooks

The project uses pre-commit hooks to automatically check and fix common issues. The hooks are installed automatically when setting up the development environment, but you can also install them manually:

```bash
uv pip install pre-commit
pre-commit install
```

To run all pre-commit hooks manually on all files:

```bash
# Using the provided scripts (recommended)
# On Windows
run_pre_commit.bat

# On Unix/Linux
./run_pre_commit.sh

# Or manually
pre-commit run --all-files
```

To run specific hooks:

```bash
pre-commit run trailing-whitespace --all-files
pre-commit run ruff --all-files
```

### Unified Workflow (Recommended)

We now provide a **unified entrypoint** for all code quality, linting, formatting, syntax, docstring, and security tasks.

**Use the Makefile for common developer tasks:**

```bash
make all           # Run all checks and fixes
make lint          # Lint codebase
make format        # Format codebase
make fix           # Run all automated code fixers
make docstring-fix # Fix docstring issues
make syntax-fix    # Fix syntax issues
make security      # Run security scans
make test          # Run all tests
make pre-commit    # Run all pre-commit checks
```

Or, run tasks directly with the unified CLI:

```bash
python scripts/manage_quality.py lint
python scripts/manage_quality.py fix
python scripts/manage_quality.py security-scan
# ...and more
```

The `.pre-commit-config.yaml` is configured to use this unified entrypoint for code quality hooks.

### Local Linting Commands

Use these commands to check and fix linting issues:

1. Check for issues without fixing:

```bash
scripts\lint_check.bat  # Windows
./scripts/lint_check.sh  # Unix/Linux
```

2. Fix issues automatically:

```bash
# Windows
fix_linting_issues.bat

# Unix/Linux
./fix_linting_issues.sh

# Or directly with Python
python fix_linting_issues.py
```

You can also fix specific files:

```bash
python fix_linting_issues.py path/to/file1.py path/to/file2.py
```

Or run with specific options:

```bash
python fix_linting_issues.py # No isort option needed
python fix_linting_issues.py --no-ruff   # Skip Ruff linter
python fix_linting_issues.py --check     # Check only, don't fix
python fix_linting_issues.py --verbose   # Show detailed output
```

3. Run specific checks:

```bash
scripts\lint_check.bat --ruff  # Run only Ruff
scripts\lint_check.bat --mypy  # Run only MyPy
```

### Code Formatter Configuration

- **Ruff**: The project uses Ruff as the primary tool for both linting and formatting. Configuration is in `.ruff.toml`
- **MyPy**: Type checking configuration is in `mypy.ini`
- **Pre-commit**: Hook configuration is in `.pre-commit-config.yaml`

All configuration files are version controlled to ensure consistent formatting across the project.

## Configuration & Environment

- Most features work out-of-the-box.
- No secrets or special environment variables are required for basic functionality.
- For advanced features, see the relevant module's README.

---

## Claude Agentic Coding Best Practices

This project follows [Claude Agentic Coding Best Practices](claude_coding_best_practices.md) for safe, reliable, and auditable automation. All contributors are expected to review and adhere to these standards.

Key principles include:

- Explicit state and input/output handling
- Modular, testable decomposition
- Strong input validation
- Deterministic, auditable steps
- Idempotency and recovery
- Human oversight and review
- Comprehensive documentation
- Unit/integration testing (including edge/failure modes)
- Security and permissions best practices

See [claude_coding_best_practices.md](claude_coding_best_practices.md) for the full checklist and details. Please review this document before submitting changes or pull requests.

## Documentation

The project includes comprehensive API documentation that can be built from source:

1. Navigate to the docs_source directory:

   ```bash
   cd docs_source
   ```

### Documentation Updates Policy

This project enforces a policy that documentation must be updated whenever code changes are made. A GitHub Actions workflow automatically checks that documentation files are updated when non-documentation files are changed in pull requests.

Documentation files are defined as:

- Any Markdown (*.md) file at the repository root
- Any file (of any type) within the 'docs/' or 'docs_source/' directories

When submitting a pull request that changes code or configuration, be sure to update the relevant documentation to reflect those changes.
