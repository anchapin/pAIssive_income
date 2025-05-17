# Speeding Up Python Tests

This project is configured for fast test runs. Here are some tips:

> **Note:** Documentation for this project has been centralized. Please see the [docs/](docs/) directory for additional onboarding, development, deployment, security, contribution information, and UI architecture ([docs/ui-architecture.md](docs/ui-architecture.md)).

## 1. Install Dev Dependencies (including pytest-xdist)

To enable parallel test execution and all developer/testing features, install the dev dependencies using [uv](https://github.com/astral-sh/uv):

```sh
uv pip install -e .[dev]
```
This will install `pytest`, `pytest-xdist`, and all plugins required for advanced testing.

## 2. Run Tests in Parallel (recommended)

We use [pytest-xdist](https://pypi.org/project/pytest-xdist/) to run tests in parallel across all available CPU cores:

```sh
pytest -n auto
```
By default, `-n auto` uses all available CPU cores. You can override with e.g. `pytest -n 4` to use 4 workers.

## 3. Skip Slow Tests During Development

Tests that take a long time to run are marked with `@pytest.mark.slow`. You can skip these tests during development to speed up your test runs:

```sh
pytest -m "not slow"
```

To run only the slow tests:

```sh
pytest -m "slow"
```

See `tests/examples/test_slow_test_example.py` for examples of how to mark slow tests.

## 4. Profile Slow Tests

Find the slowest tests to identify candidates for optimization or marking as slow:

```sh
pytest --durations=10
```

## 5. Only Collect Tests from `tests/`

Test collection is limited to the `tests/` directory for speed.

## Docker Compose Integration

**Start PostgreSQL database, application, and frontend with Docker Compose:**
```bash
# Using Docker Compose plugin
docker compose up --build

# Or using standalone Docker Compose
docker-compose up --build
```
This will launch the Flask backend, React frontend with ag-ui integration, and PostgreSQL database.

For more details on the Docker Compose integration, see [DOCKER_COMPOSE.md](DOCKER_COMPOSE.md).

## 6. Mock External Calls for Speed

Mock out network/database/API calls in your tests to keep them fast and reliable. This avoids actual external calls during testing, which can significantly speed up your test suite.

Example:
```python
@patch("requests.get")
def test_api_call(mock_get):
    # Configure the mock
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response

    # Test your function that uses requests.get
    result = my_function()
    assert result == expected_result
```

See `tests/examples/test_mocking_example.py` for more detailed examples of mocking.

## 7. Using Test Markers Effectively

The project uses various pytest markers to categorize tests:

- `@pytest.mark.unit`: Unit tests for individual components
- `@pytest.mark.integration`: Tests for interactions between components
- `@pytest.mark.slow`: Tests that take more than 1 second to run
- `@pytest.mark.api`: Tests related to API functionality
- `@pytest.mark.webhook`: Tests related to webhook functionality
- `@pytest.mark.security`: Tests related to security features
- `@pytest.mark.model`: Tests related to AI model functionality
- `@pytest.mark.performance`: Performance-sensitive tests

Run tests with specific markers:

```sh
# Run only unit tests
pytest -m unit

# Run tests that are both API-related and slow
pytest -m "api and slow"


## Automated Dependency Updates

- [Dependabot](https://docs.github.com/en/code-security/dependabot) is enabled for Python, Node.js, Docker, and GitHub Actions dependencies. Update PRs are created automatically, including for the Python lockfile (`requirements.lock`).

## Vulnerability Scanning

- Security scanning runs automatically on pushes and pull requests:
  - Python: `pip-audit`, `safety`
  - Node.js: `npm audit`
  - Static analysis: `bandit`, `semgrep`, `pylint`
  - Container: `trivy`
  - Secret scanning: `gitleaks`

## GitHub Actions Secrets

The following secrets are used by GitHub Actions workflows:

- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token (not your password)

These secrets are used for Docker Hub authentication to avoid rate limits when pulling images. Set these in your repository settings under Settings > Secrets and variables > Actions.

## Best Practices

- Regularly review and address Dependabot and security scan PRs.
- Regenerate the Python lockfile after any dependency updates.
- See `.github/workflows/security_scan.yml` for the full list of automated checks.

## Keeping Dependencies Healthy

- When adding or removing Python dependencies, update both `requirements.txt`/`requirements-dev.txt` and **regenerate `requirements.lock`** using `uv`.
- For Node.js, always use `pnpm install` for installation and let Dependabot update `pnpm-lock.yaml`.
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

> **Summary:**
> - Use **`uv`** for all Python dependency and environment management.
> - Use **`pnpm`** for all Node.js/JavaScript/TypeScript dependencies and scripts.
> - Do **not** use `pip`, `venv`, `npm`, or `yarn` for any development or CI/CD steps.
> - For any questions, see the top of this document or ask a maintainer.

---

## Running Tests

The project includes Python and JavaScript/TypeScript tests with coverage requirements.

### Python Unit/Integration Tests

From the repo root, after environment setup:

```bash
# Run tests without coverage
pytest

# Run tests with coverage (will fail if coverage is below 80%)
python run_tests.py --with-coverage
```

### Frontend Unit Tests

From the frontend directory:

```bash
cd ui/react_frontend
pnpm install
pnpm run test:unit         # Run unit tests
pnpm run test:unit:coverage # Run unit tests with coverage (will fail if coverage is below 80%)
```

### Frontend End-to-End (E2E) Tests

> **Requires:** Node.js 16.10+ and [pnpm](https://pnpm.io/), and the UI dev server running at `http://localhost:3000`

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

### Test Coverage Requirements

All code must maintain a minimum of 80% test coverage. This is enforced by:

- The GitHub Actions workflow in `.github/workflows/test-coverage.yml`
- The pytest configuration with `--cov-fail-under=80`
- The Vitest configuration with coverage thresholds

For more details, see [Test Coverage Workflow](docs/test-coverage-workflow.md).

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
- [`uv`](https://github.com/astral-sh/uv) (Python package installer and resolver; **required for all Python environments/dependencies**)
  - Install via: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - If `curl` is unavailable, you may use `pip install uv` ONLY for initial installation.
- Node.js 16.10+ (**required for modern UI and frontend tests**)
- [`pnpm`](https://pnpm.io/) (**required for all Node.js/JavaScript/TypeScript dependencies**)
  - To install pnpm, use [Corepack](https://nodejs.org/api/corepack.html) (recommended; included with Node.js v16.10+):
    ```bash
    corepack enable
    ```
  - If Corepack is not available, you can bootstrap pnpm with npm:
    ```bash
    npm install -g pnpm
    ```
    > **Note:** Use npm only for this initial installation of pnpm. For all other package management tasks, use pnpm.
    > Refer to the [Corepack documentation](https://nodejs.org/api/corepack.html) for more details on managing package managers in Node.js.

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

---

## MCP Server Integration

This project supports the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for connecting AI agents to a wide range of external tool and data servers.

### What is MCP?

MCP is an open protocol for secure, extensible communication between AI agents and a wide ecosystem of servers providing data, tools, and capabilities. MCP lets you supercharge your agents by connecting them to hundreds of community and official servers (e.g., GitHub, databases, web search, automation, etc.).

### Adding MCP Servers

You can add, list, and remove MCP servers using the REST API:

- **List all MCP servers:**
  ```
  GET /api/mcp_servers
  ```
- **Add an MCP server:**
  ```
  POST /api/mcp_servers
  Content-Type: application/json
  {
    "name": "my-github-server",
    "host": "localhost",
    "port": 1337,
    "description": "GitHub integration server"
  }
  ```
- **Remove an MCP server:**
  ```
  DELETE /api/mcp_servers/<name>
  ```

Server configurations are stored in `cline_mcp_settings.json` and are loaded dynamically for agent use.

### Example and Recommended Servers

An extensive list of official, third-party, and community MCP servers can be found here:
- [https://github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)

You can deploy your own server or connect to one of the many public options.

### Requirements

- Python 3.8+
- The [`mcp-use`](https://pypi.org/project/mcp-use/) Python library (already included in requirements)
- (Optional) See [modelcontextprotocol.io](https://modelcontextprotocol.io/) for protocol and SDK docs

### Usage

Agents can enumerate and use MCP servers as tools or resources via the agent runtime. See the codebase and [docs/](docs/) for integration details.

---

### Documentation Updates Policy

This project enforces a policy that documentation must be updated whenever code changes are made. A GitHub Actions workflow automatically checks that documentation files are updated when non-documentation files are changed in pull requests.

Documentation files are defined as:

- Any Markdown (*.md) file at the repository root
- Any file (of any type) within the 'docs/' or 'docs_source/' directories

When submitting a pull request that changes code or configuration, be sure to update the relevant documentation to reflect those changes.

For specific documentation on configuration files and environment setup, see:

- [Environment Variables](docs/environment_variables.md) - Documentation of all environment variables used in the project
- [Cursor Integration](docs/cursor_integration.md) - Details about the Cursor AI integration and configuration
- [.gitignore Configuration](docs/gitignore_configuration.md) - Information about the .gitignore file and excluded patterns

### UI Documentation

For information about the React frontend components and UI features, see:

- [UI Components Guide](docs/ui_components_guide.md) - Detailed documentation of React components, styling, and accessibility features
- [UI Accessibility Guide](docs/ui_accessibility_guide.md) - Comprehensive guide to accessibility features and best practices
- [React Frontend Updates](docs/react_frontend_updates.md) - Details of recent updates to React components

---

## Demo: Vector RAG

The `demo_vector_rag.py` script demonstrates a basic Vector Database + RAG (Retrieval-Augmented Generation) implementation using ChromaDB and Sentence Transformers.

### Prerequisites

1.  Install the required libraries:

    ```bash
    pip install chromadb sentence-transformers
    ```

### Usage

1.  Run the script:

    ```bash
    python demo_vector_rag.py
    ```

### Explanation

This script performs the following steps:

1.  Initializes a ChromaDB client (local, in-memory for demo).
2.  Prepares demo data (texts with metadata).
3.  Loads an embedding model (Sentence Transformers).
4.  Creates/gets a collection in ChromaDB.
5.  Embeds and adds documents to the collection.
6.  Performs a query and retrieves the most relevant context.

Retrieval-Augmented Generation (RAG) enhances LLMs with external knowledge. This script embeds example texts, stores them in a local vector DB, then retrieves the most relevant context for a query.
# Run API tests that are not slow
pytest -m "api and not slow"
```
