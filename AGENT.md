# AGENT.md - AI Agent Guide for pAIssive Income

## Build/Test/Lint Commands
- **Test (all)**: `pytest` or `python -m pytest` 
- **Test (single file)**: `pytest tests/test_filename.py` or `pytest tests/test_filename.py::test_function_name`
- **Test (parallel)**: `pytest -n auto` (requires pytest-xdist)
- **Coverage**: `pytest --cov=. --cov-report=term-missing`
- **Lint**: `make lint` or `python scripts/manage_quality.py lint` or `ruff check .`
- **Format**: `make format` or `python scripts/manage_quality.py format` or `ruff format .`
- **Build (Node.js)**: `pnpm test` for JS tests, `pnpm tailwind:build` for CSS
- **Security**: `make security` or `python scripts/manage_quality.py security-scan`
- **Pre-commit**: `make pre-commit` or `python scripts/manage_quality.py pre-commit`

## Architecture & Structure
- **Hybrid Python/Node.js**: Python backend (FastAPI/Flask), React frontend with TailwindCSS
- **Core directories**: `src/` (JS), `services/` (Python microservices), `api/` (FastAPI), `tests/` (pytest), `ui/` (React)
- **AI/ML stack**: CrewAI for agents, mem0 for memory, MCP protocol support, custom AI models in `ai_models/`
- **Database**: Config supports Redis, various SQL backends
- **Key services**: AI models service, niche analysis, message queue, API gateway, UI service

## Code Style & Conventions
- **Python**: Ruff formatter (88 char lines), double quotes, type hints encouraged, imports: standard/third-party/local with single-line style
- **Naming**: snake_case for Python, camelCase for JS/React, descriptive variable names
- **Error handling**: Use custom error classes in `services/errors.py`, proper exception chaining
- **Testing**: pytest with fixtures, use markers (unit, integration, slow, etc.), aim for 70%+ coverage
- **Async**: Use `asyncio_mode = auto` for async tests, proper async/await patterns
- **Dependencies**: Poetry/pip for Python, pnpm for Node.js, use optional deps groups (agents, memory, ml, dev)
