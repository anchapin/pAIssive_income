# pAIssive Income

[![codecov](https://codecov.io/gh/anchapin/pAIssive_income/branch/main/graph/badge.svg)](https://codecov.io/gh/anchapin/pAIssive_income)
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

## 📋 Prerequisites

Before getting started, ensure you have the following installed on your system:

### Required Dependencies

- **Python 3.8+** - Core runtime for the application
- **Git** - Version control (for cloning the repository)
- **Virtual Environment Tools** - For Python dependency isolation:
  - [`uv`](https://github.com/astral-sh/uv) (recommended) - Fast Python package installer and resolver
  - Or `venv` (built into Python 3.3+)
- **Node.js 16.10+** - For UI components and frontend development
- **pnpm** - Node.js package manager (preferred over npm/yarn)

### Installation Quick Reference

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install pnpm (Node.js package manager)
npm install -g pnpm

# Verify installations
python --version    # Should be 3.8+
uv --version
node --version      # Should be 16.10+
pnpm --version
git --version
```

### Optional Dependencies

- **Docker & Docker Compose** - For containerized development
- **VS Code** - Recommended IDE with project-specific configurations

---

## 🚀 Quick Start

The easiest way to get your development environment set up is by using our new setup scripts:

-   **For Linux/macOS:**
    ```bash
    bash setup.sh
    ```
-   **For Windows:**
    ```bat
    setup.bat
    ```
These scripts will guide you through the installation of dependencies, environment configuration, and other necessary setup tasks.

For manual setup steps or more details, please refer to [docs/00_introduction/02_getting_started.md](docs/00_introduction/02_getting_started.md).

---

## 📚 Documentation

- **Project Overview & User Guide**: [docs/00_introduction/01_overview.md](docs/00_introduction/01_overview.md)
- **Quick Start**: [docs/00_introduction/02_getting_started.md](docs/00_introduction/02_getting_started.md)
- **Developer Guide**: [docs/02_developer_guide/01_development_workflow.md](docs/02_developer_guide/01_development_workflow.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security**: [docs/04_security_and_compliance/01_security_overview.md](docs/04_security_and_compliance/01_security_overview.md)
- **FAQ/Troubleshooting**: [docs/07_troubleshooting_and_faq/faq.md](docs/07_troubleshooting_and_faq/faq.md)
- **Changelog**: [docs/changelog.md](docs/changelog.md)

Full documentation and advanced usage are organized in [docs/](docs/).

---

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

## Python Testing and Coverage

This project enforces at least **15% code coverage** for Python files using [pytest](https://pytest.org/) and [pytest-cov](https://pytest-cov.readthedocs.io/).

### How to Run Python Tests

First, install dependencies:

```sh
# Using uv (recommended)
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt

# Or using pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Run Python tests and check coverage:

```sh
# Run all tests with coverage
python run_tests.py --with-coverage

# Or use pytest directly
pytest --cov=. --cov-report=xml --cov-report=term-missing --cov-fail-under=15
```

- If code coverage falls below 15%, the test run will fail.
- Coverage reports will be printed to the console and an XML report will be generated as `coverage.xml`.

### Python Test Structure

Tests are located in the `tests/` directory and follow these conventions:

- **Unit tests:** Test individual functions and classes in isolation (`tests/unit/`)
- **Integration tests:** Test interactions between components (`tests/integration/`)
- **API tests:** Test API endpoints and schemas (`tests/api/`)
- **Security tests:** Test security features and validations (`tests/security/`)

### Python Testing Tools

- **[pytest](https://pytest.org/):** Test framework
- **[pytest-cov](https://pytest-cov.readthedocs.io/):** Code coverage tool
- **[pytest-asyncio](https://pytest-asyncio.readthedocs.io/):** Async test support
- **[pytest-xdist](https://pytest-xdist.readthedocs.io/):** Parallel test execution

### Python Testing Best Practices

- Write tests for all new functions and classes
- Aim for meaningful test coverage (15%+ enforced, higher encouraged)
- Use descriptive test names that explain the expected behavior
- Mock external dependencies and API calls
- Test both success and error scenarios
- Use pytest markers for test organization (`@pytest.mark.unit`, `@pytest.mark.integration`)

### Troubleshooting Python Tests

If tests fail:

1. Check that all dependencies are installed: `pip install -r requirements-dev.txt`
2. Verify Python version compatibility (3.12+ recommended)
3. Check for import errors and missing modules
4. Review test output for specific error messages
5. Ensure test files follow naming conventions (`test_*.py`)

For more detailed testing information, see [docs/02_developer_guide/03_testing_strategy.md](docs/02_developer_guide/03_testing_strategy.md).

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

For more details on the Docker Compose integration and Compose Bake, see [docs/03_devops_and_cicd/DOCKER_COMPOSE.md](docs/03_devops_and_cicd/DOCKER_COMPOSE.md).

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

For more details on the mem0 integration, see:
- [README_mem0_integration.md](README_mem0_integration.md) - Main integration guide
- [docs/README_mem0.md](docs/README_mem0.md) - Overview of mem0 investigation
- [docs/mem0_core_apis.md](docs/mem0_core_apis.md) - Documentation of mem0's core APIs
- [docs/memory_rag_coordinator.md](docs/memory_rag_coordinator.md) - MemoryRAGCoordinator documentation

- [docs/05_sdk_and_integrations/mem0_integration.md](docs/05_sdk_and_integrations/mem0_integration.md) – Main integration guide (now includes best practices for mem0 + RAG)
- [docs/mem0_rag_best_practices.md](docs/mem0_rag_best_practices.md) – Detailed guide on when and how to use mem0 and RAG, with examples
- [docs/README_mem0.md](docs/README_mem0.md) – Overview of mem0 investigation
- [docs/mem0_core_apis.md](docs/mem0_core_apis.md) – Documentation of mem0's core APIs

## ARTIST (Agentic Reasoning) Integration

This project supports [ARTIST](https://arxiv.org/abs/2402.00838) (Agentic Reasoning and Tool Integration in Self-improving Transformers), an advanced framework for agentic reasoning and dynamic tool use in LLM-driven systems.

- **Agentic Reasoning**: Leverage ARTIST's self-improving agent architecture to orchestrate complex reasoning and multi-tool workflows, enhancing both automation and adaptability.
- **Integration Points**: Core logic resides in `ai_models/artist_agent.py`, with tool registry support and experiments in `artist_experiments/`.
- **Experiments & Extensibility**: Run or extend experiments such as math problem solving and multi-API orchestration, or integrate ARTIST agents into your own workflows.

See [docs/ARTIST_integration.md](docs/ARTIST_integration.md) for setup instructions, usage examples, troubleshooting, and demo checklists.

## 🚀 Getting Started

For installation, setup, and usage, see our [Getting Started Guide](docs/00_introduction/02_getting_started.md).

---

## 📚 Documentation

- [Project Overview](docs/00_introduction/01_overview.md)
- [Getting Started](docs/00_introduction/02_getting_started.md)
- [User Guide](docs/01_user_guide/01_application_ui_manual.md)
- [Developer Guide](docs/02_developer_guide/01_development_workflow.md)
- [API Reference](docs/02_developer_guide/05_api_reference/README.md)
- [Security & Compliance](docs/04_security_and_compliance/01_security_overview.md)
- [Troubleshooting & FAQ](docs/07_troubleshooting_and_faq/faq.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](docs/changelog.md)

For a full breakdown of directory structure and module deep dives, see [docs/00_introduction/03_project_structure.md](docs/00_introduction/03_project_structure.md) and [docs/02_developer_guide/06_module_deep_dives/README.md](docs/02_developer_guide/06_module_deep_dives/README.md).

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

---

## 🧑‍💻 Contributing

All development uses [uv](https://github.com/astral-sh/uv) (Python) and [pnpm](https://pnpm.io/) (Node.js). See the [Developer Workflow](docs/02_developer_guide/01_development_workflow.md) for guidelines, linting, and the contribution checklist.

### OpenHands Development Environment

This project includes automated setup for [OpenHands](https://github.com/All-Hands-AI/OpenHands) development environments. The `.openhands/setup.sh` script automatically configures all required dependencies (Node.js, pnpm, uv) with pinned versions for reproducible builds. See the [Development Workflow](docs/02_developer_guide/01_development_workflow.md#openhands-development-environment) for details.

---

## 📢 Need Help?

- For common issues, see the [FAQ](docs/07_troubleshooting_and_faq/faq.md).
- For in-depth troubleshooting, see [docs/07_troubleshooting_and_faq/troubleshooting.md](docs/07_troubleshooting_and_faq/troubleshooting.md).

---

## 📝 License

See [LICENSE](LICENSE) for license details.

## Recent Changes

### uv and pnpm Implementation Updates
- Updated `.uv.toml` configuration with improved cache management, timeout settings, and parallel installation support
- Enhanced GitHub workflow configurations for better cross-platform compatibility
- Improved uv virtual environment handling and dependency management
