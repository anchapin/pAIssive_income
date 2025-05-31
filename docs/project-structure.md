# Project Structure

This document provides a comprehensive overview of the pAIssive Income project structure and organization.

## Repository Root Structure

```
pAIssive_income/
├── .github/                    # GitHub Actions workflows and templates
├── .vscode/                    # VS Code configuration
├── adk_demo/                   # Agent Development Kit (ADK) demonstration
├── agent_team/                 # CrewAI agent orchestration
├── ai_models/                  # AI model management and utilities
├── api/                        # API server and endpoints
├── common_utils/               # Shared utilities and common functions
├── docs/                       # All project documentation
├── scripts/                    # Development and utility scripts
├── tests/                      # Unit and integration tests
├── ui/                         # User interface components
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── package.json               # Node.js dependencies
├── pyproject.toml             # Python project configuration
├── .uv.toml                   # uv package manager configuration
└── README.md                  # Main project documentation
```

## Key Directories

### `/docs/` - Documentation

Centralized documentation organized by topic:

- `00_introduction/` - Project overview and getting started
- `01_user_guide/` - User manuals and guides
- `02_developer_guide/` - Development workflow and API reference
- `03_devops_and_cicd/` - CI/CD and deployment documentation
- `04_security_and_compliance/` - Security policies and compliance
- `05_sdk_and_integrations/` - SDK documentation and integrations
- `06_tooling_and_scripts/` - Development tools and scripts
- `07_troubleshooting_and_faq/` - Troubleshooting and FAQ
- `08_team_and_collaboration/` - Team guidelines and collaboration
- `09_archive_and_notes/` - Historical notes and archived content

### `/agent_team/` - AI Agent Orchestration

CrewAI-based agent team implementation:

- Agent definitions and configurations
- Team coordination and workflow management
- Memory-enhanced agents with mem0 integration
- Agent communication and task delegation

### `/ai_models/` - AI Model Management

AI model utilities and management:

- Model configuration and loading
- Model abstraction layers
- Integration with various AI providers
- Model performance monitoring

### `/api/` - API Server

REST API implementation:

- Flask-based API server
- Endpoint definitions and routing
- Authentication and authorization
- API documentation and testing

### `/ui/` - User Interface

Frontend components and interfaces:

- `react_frontend/` - React-based web interface
- CopilotKit integration for AI-powered UI
- Component library and styling
- E2E testing with Playwright

### `/tests/` - Testing

Comprehensive test suite:

- Unit tests for individual components
- Integration tests for system interactions
- Performance benchmarks
- Security testing
- Coverage reporting

### `/scripts/` - Development Scripts

Development and utility scripts:

- Code quality management
- Testing automation
- Deployment scripts
- Development environment setup

### `/common_utils/` - Shared Utilities

Common utilities and helper functions:

- Logging configuration
- Error handling
- Data validation
- Utility functions

### `/adk_demo/` - Agent Development Kit

Demonstration of the Agent Development Kit:

- Example agent implementations
- Tool registry and usage examples
- Memory-enhanced agent examples
- Integration demonstrations

## Configuration Files

### Python Configuration

- `pyproject.toml` - Python project metadata and build configuration
- `.uv.toml` - uv package manager configuration
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies
- `mypy.ini` - Type checking configuration
- `.ruff.toml` - Linting and formatting configuration

### Node.js Configuration

- `package.json` - Node.js project metadata and dependencies
- `pnpm-lock.yaml` - Dependency lock file
- `ui/react_frontend/package.json` - Frontend-specific dependencies

### CI/CD Configuration

- `.github/workflows/` - GitHub Actions workflow definitions
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `Dockerfile` - Container build configuration
- `docker-compose.yml` - Multi-service orchestration

### Development Tools

- `.vscode/` - VS Code editor configuration
- `.gitignore` - Git ignore patterns
- `Makefile` - Common development tasks
- `.env.example` - Environment variable template

## Architecture Overview

The project follows a microservices-inspired architecture with clear separation of concerns:

1. **Frontend Layer** - React-based UI with AI integration
2. **API Layer** - RESTful API for frontend-backend communication
3. **Agent Layer** - AI agent orchestration and coordination
4. **Model Layer** - AI model management and inference
5. **Data Layer** - Database and vector storage
6. **Utility Layer** - Shared utilities and common functions

## Development Workflow

1. **Setup** - Use automated setup scripts for environment configuration
2. **Development** - Follow TDD practices with comprehensive testing
3. **Quality** - Automated linting, formatting, and security scanning
4. **Testing** - Unit, integration, and E2E testing with coverage requirements
5. **Documentation** - Maintain up-to-date documentation alongside code changes
6. **Deployment** - Automated CI/CD pipeline with quality gates

For detailed development guidelines, see [Development Workflow](02_developer_guide/01_development_workflow.md).

## Getting Started

For new developers and contributors:

1. Review the [Getting Started Guide](getting-started.md)
2. Set up your development environment
3. Explore the [Developer Guide](02_developer_guide/)
4. Review the [Contributing Guidelines](../CONTRIBUTING.md)
5. Check the [Troubleshooting Guide](07_troubleshooting_and_faq/troubleshooting.md)

## Additional Resources

- [API Reference](02_developer_guide/05_api_reference/)
- [Security Overview](04_security_and_compliance/01_security_overview.md)
- [Deployment Guide](03_devops_and_cicd/)
- [FAQ](07_troubleshooting_and_faq/faq.md)
