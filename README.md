# pAIssive Income

[![codecov](https://codecov.io/gh/anchapin/pAIssive_income/branch/main/graph/badge.svg)](https://codecov.io/gh/anchapin/pAIssive_income)

> **CI will fail if coverage drops compared to the base branch (enforced by Codecov).**
>
> **Pull Requests will receive automated coverage comments from the [Codecov](https://about.codecov.io/) bot when Codecov integration is enabled for your repository.**

Framework for generating passive income by utilizing a team of AI agents to generate niche software and AI bots for customers.

[![Build Status](https://github.com/anchapin/pAIssive_income/actions/workflows/ci.yml/badge.svg)](https://github.com/anchapin/pAIssive_income/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/anchapin/pAIssive_income/badge.svg?branch=main)](https://coveralls.io/github/anchapin/pAIssive_income?branch=main)

## Features

- **AI Agent Team**: Utilize a team of AI agents to generate niche software and AI bots
- **CrewAI Integration**: Use CrewAI to create and manage AI agent teams
- **CopilotKit Integration**: Add AI copilot features to the React frontend
- **Multi-Chain Protocol (MCP) Support**: Connect to various AI providers through a unified interface
  - *Note: As of May 2025, the unused `mcp-use` dependency has been removed while maintaining full MCP functionality via the `modelcontextprotocol` package*
- **mem0 Memory Integration**: Enhance agents with persistent memory capabilities

**pAIssive Income** is a modular, extensible platform for AI-powered content generation, market analysis, monetization, and automation. It combines advanced AI models, multi-agent orchestration, and robust APIs with a focus on developer experience and security.

---

## 🚀 Quick Start

- **Getting Started:**
  See [docs/getting-started.md](docs/getting-started.md) for installation and setup instructions.

- **Global Logging Configuration:**
  All main scripts should use the project-wide logging setup. At the start of your main script, add:
  ```python
  from logging_config import configure_logging

  if __name__ == "__main__":
      configure_logging()
      # ... your main logic ...
  ```
  This ensures consistent logging across all modules.

---

## 📚 Documentation

All project documentation is now centralized in [docs/](docs/):

- [Project Overview](docs/00_introduction/01_overview.md)
- [Getting Started](docs/00_introduction/02_getting_started.md)
- [User Guide](docs/01_user_guide/)
- [Developer Guide](docs/02_developer_guide/)
  - [Development Workflow & Contributing](docs/02_developer_guide/01_development_workflow.md)
  - [API Reference](docs/02_developer_guide/05_api_reference/)
  - [Module Deep Dives](docs/02_developer_guide/06_module_deep_dives/)
- [DevOps & CI/CD](docs/03_devops_and_cicd/)
- [Security & Compliance](docs/04_security_and_compliance/)
- [SDKs & Integrations](docs/05_sdk_and_integrations/)
- [Tooling & Scripts](docs/06_tooling_and_scripts/)
- [Troubleshooting & FAQ](docs/07_troubleshooting_and_faq/)
- [Team & Collaboration](docs/08_team_and_collaboration/)
- [Archive & Historical Notes](docs/09_archive_and_notes/)
- [Changelog](docs/changelog.md)

For a full directory map, see [docs/project-structure.md](docs/project-structure.md).

---

## 🛠️ Minimal Agent & Tool Registry Demo

A minimal demonstration script is provided to show how an agent can pick and use tools (such as a calculator or text analyzer) via a simple registry.

**What the demo does:**
- Instantiates an `ArtistAgent`
- Lists available tools
- Supports both example prompts and interactive mode
- Example mode: runs three prompts—one handled by the calculator, one by the text analyzer, one unhandled
- Interactive mode: enter your own prompts in a loop

**How to run:**
```bash
# Example-based demo (default)
python scripts/artist_demo.py

# Interactive mode (enter prompts manually)
python scripts/artist_demo.py -i
```

**Expected output:**
- The list of available tools (calculator, text_analyzer, etc.)
- The prompt that is sent to the agent
- The agent's output (e.g., calculation result, analysis, or a message indicating no tool can handle the prompt)

Example (output will vary by implementation):

```
=== ArtistAgent Tool Use Demo ===

Available tools:
  - calculator
  - text_analyzer
-----------------------------
Prompt: What is 12 * 8?
Agent output: 96
-----------------------------
Prompt: Analyze the sentiment of this phrase: 'This is a fantastic development!'
Agent output: Sentiment: positive | Words: 6 | Characters: 35 | Positive indicators: 1 | Negative indicators: 0
-----------------------------
Prompt: Translate hello to French
Agent output: No suitable tool found for this prompt.
```

**Note:**  
The agent and tool registry are easily extensible—new tools can be added with minimal code changes, allowing the agent to handle more types of tasks.

## 🤝 Contributing

See [Development Workflow](docs/02_developer_guide/01_development_workflow.md) for contribution guidelines and coding standards.
Module-specific deep dives are in [docs/02_developer_guide/06_module_deep_dives/](docs/02_developer_guide/06_module_deep_dives/).

---

## 🔒 Security

Security policy, reporting, and compliance:
[docs/04_security_and_compliance/01_security_overview.md](docs/04_security_and_compliance/01_security_overview.md)
Historical fixes and audit notes: [docs/09_archive_and_notes/security_fixes_summaries.md](docs/09_archive_and_notes/security_fixes_summaries.md)

---

## 📝 License

See [LICENSE](LICENSE).

---


## JavaScript Testing and Coverage

This project enforces at least **80% code coverage** for JavaScript files using [nyc (Istanbul)](https://github.com/istanbuljs/nyc) and [Mocha](https://mochajs.org/).

### How to Run JavaScript Tests

Install dependencies (if not already done):

```sh
pnpm install
```

Run JavaScript tests and check coverage:

```sh
pnpm test
```

- If code coverage falls below 80%, the test run will fail.
- Coverage reports will be printed to the console and an HTML report will be generated in the `coverage/` directory (if running locally).

To generate a detailed lcov report:

```sh
pnpm coverage
```

**Coverage thresholds for statements, branches, functions, and lines are all set to 80%.**

You can find example JS source and tests in the `src/` directory.

---

## Writing Advanced JavaScript Tests (React Component Example)

For more complex JavaScript code, such as React components, you can write tests to verify rendering, user interaction, and state updates.

**Example: Testing a React Component with Mocha and Enzyme**

First, install additional test utilities:

```sh
pnpm add --save-dev enzyme enzyme-adapter-react-16 @wojtekmaj/enzyme-adapter-react-17
```

Example component (`src/Hello.js`):

```jsx
import React from 'react';

export function Hello({ name }) {
  return <div>Hello, {name}!</div>;
}
```

Example test (`src/Hello.test.js`):

```js
const React = require('react');
const { shallow, configure } = require('enzyme');
const Adapter = require('@wojtekmaj/enzyme-adapter-react-17');
const { Hello } = require('./Hello');

configure({ adapter: new Adapter() });

describe('Hello component', () => {
  it('renders the correct greeting', () => {
    const wrapper = shallow(<Hello name="World" />);
    if (!wrapper.text().includes('Hello, World!')) {
      throw new Error('Greeting not rendered correctly');
    }
  });
});
```

> **Tip:** For React projects, [Jest](https://jestjs.io/) with [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) is very popular and may offer a smoother setup for component and hook testing.

**Best Practices:**
- Test both rendering and user events/interactions.
- Mock API calls and external dependencies.
- Use coverage reports to identify untested code paths.
- Place tests next to source files or in a dedicated test directory.

---

## Dependency Updates (via Dependabot)

This project uses [Dependabot](https://docs.github.com/en/code-security/dependabot) to keep dependencies up-to-date for all major ecosystems:

- **JavaScript/Node (pnpm):** Updates to packages in `package.json`
- **Python:** Updates to packages in `requirements-ci.txt`, `requirements_filtered.txt`
- **Docker:** Updates to base images in `Dockerfile`, `main_Dockerfile`, and `ui/react_frontend/Dockerfile.dev`
- **GitHub Actions:** Updates to workflow actions in `.github/workflows/`

**How it works:**
- Dependabot will automatically open pull requests for version updates on a weekly schedule.
- PRs are labeled by ecosystem (e.g., `dependencies`, `javascript`, `python`, `docker`, `github-actions`).
- Some dependencies (e.g., `react`, `flask`, `pytest`) will not be updated for major releases automatically.

**Maintainer action:**
- Review Dependabot PRs promptly.
- Ensure CI/tests pass before merging.
- For major upgrades, review changelogs for breaking changes.

For more details, see `.github/dependabot.yml`.

> **Tip for maintainers:**
> Periodically review and adjust the `.github/dependabot.yml` configuration (update schedules, ignored dependencies, PR limits) to ensure it fits the project's evolving needs.

---

For any questions, see the [FAQ](docs/07_troubleshooting_and_faq/faq.md) or open an issue.

## Docker Compose Integration

> **Tip:** To enable advanced build graph features (Compose BuildKit Bake), set `COMPOSE_BAKE=true` in your `.env` file.
> This requires Docker Compose v2.10+ and will use the BuildKit bake engine for improved build performance and caching.

For more details on the Docker Compose integration and Compose Bake, see [DOCKER_COMPOSE.md](DOCKER_COMPOSE.md).

## CrewAI + CopilotKit Integration

This project includes integration with CrewAI and CopilotKit to enable powerful multi-agent AI features in the React frontend.

### Features

- **Agentic Chat**: Chat with AI copilots and call frontend tools
- **Human-in-the-Loop**: Collaborate with the AI, plan tasks, and decide actions interactively
- **Agentic/Generative UI**: Assign long-running tasks to agents and see real-time progress

### Usage

To use the CrewAI + CopilotKit integration:

1. Install the required dependencies:
   ```bash
   # Backend (CrewAI)
   pip install '.[agents]'

   # Frontend (CopilotKit)
   cd ui/react_frontend
   npm install
   ```

2. Start the application:
   ```bash
   # Using Docker Compose
   docker compose up --build

   # Or manually
   python app.py
   ```

For more details on the CrewAI + CopilotKit integration, see:
- [docs/CrewAI_CopilotKit_Integration.md](docs/CrewAI_CopilotKit_Integration.md) - Main integration guide
- [ui/react_frontend/CopilotKit_CrewAI.md](ui/react_frontend/CopilotKit_CrewAI.md) - Frontend implementation details
- [docs/examples/CrewAI_CopilotKit_Advanced_Examples.md](docs/examples/CrewAI_CopilotKit_Advanced_Examples.md) - Advanced usage examples

## mem0 Memory Integration

This project includes integration with [mem0](https://mem0.ai), a memory layer for AI agents that enables persistent memory capabilities across conversations and sessions.

### Features

- **Persistent Memory**: Agents remember user preferences, past interactions, and important information
- **Memory Search**: Retrieve relevant memories based on context and queries
- **Conversation Storage**: Store entire conversations for future reference
- **Memory-Enhanced Agents**: Both ADK and CrewAI agents are enhanced with memory capabilities

### Usage

To use the mem0 integration:

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key (required by mem0):
   ```bash
   # Linux/macOS
   export OPENAI_API_KEY='your-api-key'

   # Windows (PowerShell)
   $env:OPENAI_API_KEY='your-api-key'

   # Windows (Command Prompt)
   set OPENAI_API_KEY=your-api-key
   ```

3. Use memory-enhanced agents in your code:
   ```python
   # For ADK agents
   from adk_demo.mem0_enhanced_adk_agents import MemoryEnhancedDataGathererAgent

   agent = MemoryEnhancedDataGathererAgent(name="DataGatherer", user_id="user123")

   # For CrewAI agents
   from agent_team.mem0_enhanced_agents import MemoryEnhancedCrewAIAgentTeam

   team = MemoryEnhancedCrewAIAgentTeam(user_id="user123")
   ```

For more details on the mem0 integration and best practices for combining mem0 with Retrieval-Augmented Generation (RAG):

- [README_mem0_integration.md](README_mem0_integration.md) – Main integration guide (now includes best practices for mem0 + RAG)
- [docs/mem0_rag_best_practices.md](docs/mem0_rag_best_practices.md) – Detailed guide on when and how to use mem0 and RAG, with examples
- [docs/README_mem0.md](docs/README_mem0.md) – Overview of mem0 investigation
- [docs/mem0_core_apis.md](docs/mem0_core_apis.md) – Documentation of mem0's core APIs

## 🚀 Getting Started

For installation, setup, and usage, see our [Getting Started Guide](docs/getting-started.md).

---

## 📚 Documentation

- [Project Overview](docs/00_introduction/01_overview.md)
- [Getting Started](docs/getting-started.md)
- [User Guide](docs/01_user_guide/01_application_ui_manual.md)
- [Developer Guide](docs/02_developer_guide/01_development_workflow.md)
- [API Reference](docs/02_developer_guide/05_api_reference/README.md)
- [Security & Compliance](docs/04_security_and_compliance/01_security_overview.md)
- [Troubleshooting & FAQ](docs/07_troubleshooting_and_faq/faq.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](docs/changelog.md)

For a full breakdown of directory structure and module deep dives, see [docs/project-structure.md](docs/project-structure.md) and [docs/02_developer_guide/06_module_deep_dives/README.md](docs/02_developer_guide/06_module_deep_dives/README.md).

---

## 🛡️ Security

See [Security Policy](SECURITY.md) and [Security Overview](docs/04_security_and_compliance/01_security_overview.md).

---

## 💡 Key Directories

- `ai_models/` — Model management and utilities
- `agent_team/` — CrewAI agent orchestration
- `api/` — API server and endpoints
- `docs/` — All documentation (user, developer, security, CI/CD, SDKs, etc.)
- `tests/` — Unit and integration tests

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

# Run tests with coverage (will fail if coverage is below 15%)
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

All code must maintain a minimum of 15% test coverage. This is enforced by:

- The GitHub Actions workflow in `.github/workflows/python-tests.yml`
- The pytest configuration with `--cov-fail-under=15`
- The coverage configuration in `.coveragerc` and `pyproject.toml`

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

- Python 3.10+ (required for CrewAI compatibility)
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

### Logging Best Practices

The project follows specific logging best practices to ensure consistent and effective logging throughout the codebase. Key principles include:

- Always initialize loggers at the top of each module
- Use module-specific loggers with `__name__`
- Never use the root logger directly
- Use appropriate logging levels

See [Logging Best Practices](docs/logging-best-practices.md) for detailed guidelines and examples.

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

- Python 3.10+ (required for CrewAI compatibility)
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

---

## 🧑‍💻 Contributing

All development uses [uv](https://github.com/astral-sh/uv) (Python) and [pnpm](https://pnpm.io/) (Node.js). See the [Developer Workflow](docs/02_developer_guide/01_development_workflow.md) for guidelines, linting, and the contribution checklist.

---

## 📢 Need Help?

- For common issues, see the [FAQ](docs/07_troubleshooting_and_faq/faq.md).
- For in-depth troubleshooting, see [docs/07_troubleshooting_and_faq/troubleshooting.md](docs/07_troubleshooting_and_faq/troubleshooting.md).

---

## Agentic Reasoning Tests & Benchmarking

This project now includes advanced tests and benchmarking for agentic reasoning and tool use:

- **Agentic Reasoning Unit Tests:**
  - See `tests/test_artist_agent.py` for tests validating the ability of agents to select and use tools (such as the calculator) and to handle multi-step reasoning prompts.
- **Benchmarking:**
  - See `tests/performance/test_artist_agent_benchmark.py` for automated benchmarking of the ARTIST agent against other agent frameworks.
  - Benchmark results are output to `tests/performance/artist_agent_benchmark.md` after running the benchmark script.

These additions help ensure robust, measurable progress in agentic reasoning and tool integration in this codebase.

---

## 📝 License

See [LICENSE](LICENSE) for license details.

## Recent Changes

### uv and pnpm Implementation Updates
- Updated `.uv.toml` configuration with improved cache management, timeout settings, and parallel installation support
- Enhanced GitHub workflow configurations for better cross-platform compatibility
- Improved uv virtual environment handling and dependency management
