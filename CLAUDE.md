# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pAIssive_income** is a comprehensive platform that empowers individuals to identify profitable markets for AI agents and facilitates the creation and deployment of those agents. The platform enables users to generate passive income by offering personalized AI solutions to small businesses and individuals.

**Target User:** Tech-savvy individuals (like Alex, the Tech-Savvy Side Hustler) who can follow GitHub READMEs and run local servers but may not be experts in marketing or advanced AI development. They seek to generate passive income through AI agent creation and sales.

## Development Commands

### Python Environment Setup

**Quick Setup (Recommended):**
```bash
# Run the local environment setup script
./setup_local_env.sh
```

**Manual Setup:**
```bash
# Set up PATH for local pip installation
export PATH="$HOME/.local/bin:$PATH"

# Install with optional dependencies (if full environment available)
uv pip install -e ".[dev,agents,memory,ml]"

# Alternative: using pip
pip install -e ".[dev,agents,memory,ml]"

# Minimal setup (essential tools only)
pip install --break-system-packages ruff pytest pyright sqlalchemy fastapi pydantic
```

### Build & Test Commands
```bash
# Unified quality management (preferred)
make lint           # Lint all code
make format         # Format all code  
make security       # Run security scans
make test          # Run all tests
make all           # Run complete quality pipeline

# Direct script usage
python scripts/manage_quality.py lint
python scripts/manage_quality.py test

# Python tests
python run_tests.py                    # Optimized test runner
pytest tests/ -v --cov=.             # Direct pytest
pytest -m unit                       # Unit tests only
pytest -m integration               # Integration tests only

# Frontend tests (from ui/react_frontend/)
pnpm start                          # Start React development server
pnpm build                          # Build React app for production
pnpm test                           # Run Jest/React tests with coverage
pnpm test:unit                      # Run Vitest unit tests
pnpm test:e2e                       # Run Playwright e2e tests
pnpm test:ci                        # CI-optimized tests
pnpm test:environments              # Test multiple environment configurations
pnpm test:mock-api                  # Run mock API server tests
pnpm tailwind:build                 # Build Tailwind CSS
pnpm tailwind:watch                 # Watch Tailwind changes for development
```

### Running the Application
```bash
# Development (Flask UI)
python run_ui.py

# API server (FastAPI)
python -m api.main

# Full stack with Docker
docker-compose up --build

# CI environment
docker-compose -f docker-compose.yml -f docker-compose.ci.yml up
```

## Architecture Overview

### Core Design Patterns

**Adapter Pattern for AI Models** (`ai_models/adapters/`):
- Factory-based model adapter creation supporting Ollama, OpenAI, LMStudio, TensorRT, MCP
- Graceful fallbacks for missing adapters
- Extensible design for new AI providers

**Memory-Enhanced Agent Orchestration** (`agent_team/`):
- CrewAI integration with optional dependency handling
- mem0 persistent memory layer using vector databases
- Specialized agent profiles: researcher, developer, marketing, monetization, feedback

**Service-Oriented API Architecture** (`api/`):
- Domain-driven route separation (analytics, marketing, monetization, niche analysis)
- Repository pattern for data access abstraction
- Comprehensive middleware pipeline (auth, CORS, rate limiting, logging)

**Plugin Architecture**:
- Optional dependencies with graceful degradation (CrewAI, mem0, ADK)
- Interface-based design enabling easy plugin development
- Feature flags based on available dependencies

### Module Integration Patterns

**Configuration Management**:
- Pydantic-based configuration validation
- Environment-specific settings (dev/prod)
- Centralized secret management through `common_utils/secrets/`

**Caching Strategy** (`ai_models/caching/`, `common_utils/caching/`):
- Multiple backends: Redis, SQLite, memory, disk
- Version-aware cache invalidation
- Configurable TTL and cache statistics

**Database Abstraction** (`common_utils/db/`):
- Factory pattern for SQL/NoSQL backends
- Migration support via Flask-Migrate
- Connection pooling and health monitoring

### Domain-Specific Modules

**Niche Analysis Module** (`niche_analysis/`): Market analysis and competitive research, AI-powered opportunity scoring, target user analysis, keyword research, competitor tracking, trend visualization

**Marketing Module** (`marketing/`): Strategy pattern for different marketing approaches, AI-powered content generation, ROI analysis, A/B testing framework, content templates, social media integration

**Monetization Module** (`monetization/`): Multiple subscription models, payment gateway abstraction, usage tracking with metered billing, revenue analytics, subscription management, invoice generation

**UI Module** (`ui/react_frontend/`): React-based frontend with CopilotKit AI chat integration, Material-UI components, comprehensive testing infrastructure (Jest, Vitest, Playwright), environment-aware testing, mock API server architecture, Tailwind CSS styling, TypeScript support

## Development Guidelines

### Core Principles
The platform is designed with these key principles from the PRD:
- **Quick startup with smart defaults**: Minimize configuration overhead for users
- **Flexibility and adaptability**: Easy swapping of AI tools and frameworks
- **User-centric design**: Intuitive for tech-savvy but non-expert users
- **Passive income focus**: All features should support the income generation goal

### Optional Dependencies
Many features are optional. Install only what you need:
- `pip install ".[agents]"` for CrewAI integration
- `pip install ".[memory]"` for mem0 memory capabilities  
- `pip install ".[ml]"` for ML/AI model features

### Adding New AI Models
Extend the adapter factory pattern in `ai_models/adapters/`:
1. Create new adapter class inheriting from `BaseAdapter`
2. Register in `adapter_factory.py`
3. Add configuration parameters to settings

### Service Layer Pattern
Business logic should go in service classes, not directly in API routes. Follow the pattern established in `api/services/`.

### Memory Enhancement
For AI agents, leverage the mem0 integration for persistent context:
```python
from agent_team.mem0_enhanced_agents import MemoryEnhancedCrewAIAgentTeam
team = MemoryEnhancedCrewAIAgentTeam(user_id="user123")
```

### Configuration-First Development
Always add new settings to the Config class with proper Pydantic validation. Use the centralized configuration system in `common_utils/config_loader.py`.

### Security Patterns
- Use centralized input validation via Pydantic models
- Follow the security patterns established in `common_utils/validation/`
- All API endpoints should use the middleware authentication system
- Secrets management through the dedicated `common_utils/secrets/` module

### Testing Strategy

**Python Testing:**
- Write tests for new features (the project has extensive CI/CD)
- Use the test categorization system: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.api`
- Mock external dependencies appropriately
- Follow the test patterns in `tests/` directory

**React Frontend Testing:**
- **Multi-Framework Setup**: Jest for React components, Vitest for utility functions, Playwright for e2e
- **Environment-Aware Testing**: Tests adapt to CI, Docker, Kubernetes, cloud environments
- **Mock API Architecture**: Comprehensive mock server system for isolated frontend testing
- **Component Testing**: Test React components with @testing-library/react
- **E2E Testing**: Playwright tests for user workflows and interactions
- **Visual Regression**: Screenshots and visual comparisons for UI changes
- **Test Commands**:
  - `pnpm test` - Run all Jest/React tests
  - `pnpm test:unit` - Run Vitest unit tests
  - `pnpm test:e2e` - Run Playwright e2e tests
  - `pnpm test:environments` - Test environment detection logic
  - `pnpm test:mock-api` - Test mock server functionality

### Cursor Rules Integration
The project includes comprehensive Cursor rules in `.cursor/rules/`:
- Follow the task-driven development workflow described in `dev_workflow.mdc`
- Use the Task Master MCP server for project management when available
- Reference file using `[filename](mdc:path/to/file)` format in rules
- Update rules when establishing new code patterns

## Key Configuration Files

- `pyproject.toml`: Python dependencies, tool configuration (Ruff, pyright, pytest) - **Primary configuration source**
- `ui/react_frontend/package.json`: React dependencies, frontend build scripts, comprehensive test configurations
- `ui/react_frontend/vitest.config.js`: Vitest configuration for unit testing
- `ui/react_frontend/playwright.config.ts`: Playwright configuration for e2e testing
- `ui/react_frontend/tailwind.config.js`: Tailwind CSS configuration
- `docker-compose.yml`: Multi-service orchestration with PostgreSQL, optional Redis
- `Makefile`: Unified command interface for all quality operations
- `.cursor/rules/*.mdc`: Development workflow and coding standards

### Linting Configuration Note
Ruff configuration is centralized in `pyproject.toml` to avoid confusion. The separate `ruff.toml` file exists for specific performance optimizations but `pyproject.toml` serves as the authoritative configuration source.

## Common Workflows

### Adding a New Feature Module
1. Create directory structure following existing patterns
2. Implement service layer with proper error handling
3. Add API routes with authentication middleware
4. Create Pydantic schemas for validation
5. Add appropriate tests with categorization markers
6. Update configuration if needed
7. Document in module README

### React Frontend Development
1. **Component Development**:
   - Create component in `ui/react_frontend/src/components/`
   - Add corresponding test file with `.test.jsx` extension
   - Use Material-UI components for consistency
   - Follow existing component patterns for props and styling

2. **Adding New Pages**:
   - Create page component in `ui/react_frontend/src/pages/`
   - Add route in main App.js router configuration
   - Include authentication guards if needed (`AuthGuard`, `ProtectedRoute`)
   - Add navigation links in Layout component

3. **Testing New Features**:
   - Run `pnpm tailwind:build` before testing to ensure styles are compiled
   - Use `pnpm test:unit` for isolated component testing
   - Use `pnpm test:e2e` for full user workflow testing
   - Add mock API responses in `tests/mock_api_server.js` if needed
   - Test across different environments using `pnpm test:environments`

4. **CopilotKit Integration**:
   - Extend existing CopilotKit components in `src/components/`
   - Follow patterns in `CopilotChat.jsx` and `CopilotKitIntegration.jsx`
   - Test AI chat functionality with backend agent integration

### Working with Memory-Enhanced Agents
1. Ensure mem0 dependencies are installed
2. Set `OPENAI_API_KEY` environment variable (required by mem0)
3. Use existing memory-enhanced agent classes as templates
4. Store conversation context for persistent memory

### Security Development
- Run `make security` before commits
- Use the comprehensive security scanning pipeline
- Handle sensitive data through the secrets management system
- Follow input validation patterns established in `common_utils/validation/`

## Tool Preferences
- Use 'uv' and 'pnpm' for this project
- Use pyright instead of pyrefly
- For React frontend work, always run from `ui/react_frontend/` directory
- Use Tailwind CSS classes instead of custom CSS when possible
- Prefer Material-UI components for consistent design system
- Use Playwright for e2e tests over other testing frameworks

## Frontend Technology Stack

### Core Technologies
- **React 18.3+**: Modern React with hooks and concurrent features
- **TypeScript**: Mixed JS/TS environment with gradual adoption
- **Material-UI v7**: Component library for consistent UI design
- **Tailwind CSS**: Utility-first CSS framework for custom styling
- **React Router v6**: Client-side routing and navigation

### AI Integration
- **CopilotKit**: AI chat interface and copilot functionality
- **Backend Agent Integration**: Connected to CrewAI agents via API

### Testing Infrastructure
- **Jest**: React component testing with @testing-library/react
- **Vitest**: Fast unit testing for utilities and services
- **Playwright**: End-to-end testing with multiple browser support
- **Mock API Server**: Comprehensive mocking for isolated testing

### Development Tools
- **React App Rewired**: Custom webpack configuration
- **PostCSS**: CSS processing with Tailwind integration
- **ESBuild**: Fast JavaScript bundling and compilation

### Environment Detection
The frontend includes sophisticated environment detection capabilities:
- **CI Environment**: GitHub Actions, Jenkins, other CI platforms
- **Container Environment**: Docker, Kubernetes deployment detection
- **Cloud Platforms**: AWS, Azure, GCP environment detection
- **Development Environment**: Local development server detection
