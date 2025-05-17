# pAIssive Income

Framework for generating passive income by utilizing a team of AI agents to generate niche software and AI bots for customers.

[![Build Status](https://github.com/your-org/pAIssive_income/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/pAIssive_income/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/your-org/pAIssive_income/badge.svg?branch=main)](https://coveralls.io/github/your-org/pAIssive_income?branch=main)

## Features

- **AI Agent Team**: Utilize a team of AI agents to generate niche software and AI bots
- **CrewAI Integration**: Use CrewAI to create and manage AI agent teams
- **CopilotKit Integration**: Add AI copilot features to the React frontend
- **Multi-Chain Protocol (MCP) Support**: Connect to various AI providers through a unified interface

**pAIssive Income** is a modular, extensible platform for AI-powered content generation, market analysis, monetization, and automation. It combines advanced AI models, multi-agent orchestration, and robust APIs with a focus on developer experience and security.

---

## 🚀 Quick Start

- **Getting Started:**
  See [docs/00_introduction/02_getting_started.md](docs/00_introduction/02_getting_started.md) for installation and setup instructions.

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

For a full directory map, see [docs/00_introduction/03_project_structure.md](docs/00_introduction/03_project_structure.md).

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

For any questions, see the [FAQ](docs/07_troubleshooting_and_faq/faq.md) or open an issue.

**pAIssive Income** is a modular, extensible platform for AI-powered content generation, market analysis, monetization, automation, and more. It features advanced agent orchestration, robust APIs, secure development practices, and a developer-friendly workflow. The project is organized for clarity, maintainability, and rapid onboarding.

---

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

---

## 📢 Need Help?

- For common issues, see the [FAQ](docs/07_troubleshooting_and_faq/faq.md).
- For in-depth troubleshooting, see [docs/07_troubleshooting_and_faq/troubleshooting.md](docs/07_troubleshooting_and_faq/troubleshooting.md).

---

## 📝 License

See [LICENSE](LICENSE) for license details.

