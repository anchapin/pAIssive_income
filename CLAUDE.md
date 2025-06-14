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

# Frontend tests
pnpm test                           # Run JS tests with coverage
pnpm test:ci                        # CI-optimized tests
pnpm tailwind:build                 # Build Tailwind CSS
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

**UI Module** (`ui/`): Web-based interface designed for tech-savvy users, intuitive dashboards, data visualization, forms for input, user-friendly navigation for non-experts in marketing/AI

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
- Write tests for new features (the project has extensive CI/CD)
- Use the test categorization system: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.api`
- Mock external dependencies appropriately
- Follow the test patterns in `tests/` directory

### Cursor Rules Integration
The project includes comprehensive Cursor rules in `.cursor/rules/`:
- Follow the task-driven development workflow described in `dev_workflow.mdc`
- Use the Task Master MCP server for project management when available
- Reference file using `[filename](mdc:path/to/file)` format in rules
- Update rules when establishing new code patterns

## Key Configuration Files

- `pyproject.toml`: Python dependencies, tool configuration (Ruff, pyright, pytest) - **Primary configuration source**
- `package.json`: Node.js dependencies, Tailwind build scripts, test coverage settings
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
