# pAIssive Income

A comprehensive framework for developing and monetizing niche AI agents to generate passive income through subscription-based software tools powered by local AI models.

> **Note:** Documentation for this project has been centralized. Please see the [docs/](docs/) directory for additional onboarding, development, deployment, security, and contribution information.

---

## TL;DR Quickstart

1. **Clone the repo and enter it:**
   ```bash
   git clone https://github.com/anchapin/pAIssive_income.git
   cd pAIssive_income
   ```
2. **Set up Python environment and install dependencies:**
   (Requires Python 3.8+)
   ```bash
   # On Windows
   scripts\recreate_venv.bat

   # On Unix/Linux
   ./scripts/recreate_venv.sh
   ```
   Or manually:
   ```bash
   uv venv .venv
   source .venv/bin/activate  # Or: .venv\Scripts\activate (Windows)
   uv pip install -r requirements.txt
   uv pip install -r requirements-dev.txt
   uv pip install -e .
   ```
3. **Set up pre-commit hooks for code quality:**
   ```bash
   uv pip install pre-commit
   pre-commit install
   ```
4. **Start the modern web UI (requires Node.js 14+ and npm):**
   ```bash
   python ui/run_ui.py
   ```
   If your browser doesn't open, visit [http://localhost:3000](http://localhost:3000).
5. **Run all tests (unit, integration, frontend):**
   See the "Running Tests" section below.

---

## Overview

This project provides a structured approach to creating specialized AI-powered software tools that solve specific problems for targeted user groups. By focusing on niche markets with specific needs, these tools can provide high value to users while generating recurring subscription revenue.

The framework uses a team of specialized AI agents that collaborate to identify profitable niches, develop solutions, create monetization strategies, and market the products to target users.

## Project Structure

- **Agent Team**: A team of specialized AI agents that collaborate on different aspects of the product development and monetization process.
- **Niche Analysis**: Tools and methodologies for identifying profitable niches and user pain points.
- **Tool Templates**: Development templates for creating AI-powered software solutions.
- **Monetization**: Subscription models and pricing strategies for maximizing recurring revenue.
- **Marketing**: Strategies for reaching target users and promoting the AI tools.
- **UI**: Web interface for interacting with the framework components.

## Agent Team

The project is built around a team of specialized AI agents:

1. **Research Agent**: Identifies market opportunities and user needs in specific niches.
2. **Developer Agent**: Creates AI-powered software solutions to address identified needs.
3. **Monetization Agent**: Designs subscription models and pricing strategies.
4. **Marketing Agent**: Develops strategies for reaching and engaging target users.
5. **Feedback Agent**: Gathers and analyzes user feedback for product improvement.

## Key Features

- **Niche Identification**: Sophisticated analysis tools to identify profitable niches with specific user problems that can be solved with AI.
- **Problem Analysis**: Detailed analysis of user problems and pain points to ensure solutions address real needs.
- **Solution Design**: Templates and frameworks for designing AI-powered software solutions.
- **Monetization Strategy**: Subscription models and pricing strategies optimized for recurring revenue.
- **Marketing Plan**: Comprehensive marketing strategies tailored to each niche and target user group.
- **Feedback Loop**: Tools for gathering and analyzing user feedback to continuously improve products.

## Example Niches

The framework has identified several promising niches for AI-powered tools:

1. **YouTube Script Generator**: AI tools to help YouTube creators write engaging scripts faster.
2. **Study Note Generator**: AI tools to help students create comprehensive study notes from lectures.
3. **Freelance Proposal Writer**: AI tools to help freelancers write compelling client proposals.
4. **Property Description Generator**: AI tools to help real estate agents write compelling property descriptions.
5. **Inventory Management for Small E-commerce**: AI tools to help small e-commerce businesses manage inventory efficiently.

## Getting Started

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

> **Requires:** Node.js 14+, npm, and the UI dev server running at `http://localhost:3000`

1. Install Playwright and its browsers (first time only):
   ```bash
   cd ui/react_frontend
   npm install
   npx playwright install
   ```

2. Run all E2E tests:
   ```bash
   npx playwright test
   ```

3. See `ui/react_frontend/tests/e2e/` for sample E2E tests.
   To run a specific test:
   ```bash
   npx playwright test tests/e2e/niche_analysis.spec.ts
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
- Node.js 14.0+ (for modern UI and frontend tests)
- npm (comes with Node.js)
- Dependencies listed in each module's README

## Code Style and Formatting

The project enforces consistent code style and formatting through pre-commit hooks and automated tools. Here are the key formatting guidelines and tools:

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
python fix_all_issues_final.py
```

3. Run specific checks:

```bash
scripts\lint_check.bat --ruff  # Run only Ruff
scripts\lint_check.bat --mypy  # Run only MyPy
```

### Code Formatter Configuration

- **Ruff**: The project uses Ruff for both linting and formatting. Configuration is in `.ruff.toml`
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

2. Generate the API documentation from source code:

   ```bash
   python generate_api_docs.py
   ```
