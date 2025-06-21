# Project Configuration: Linting, Formatting, Type/Security Checking, and Testing

This document explains how to run all major code quality and testing tools for this project. **Configuration is consolidated and standardized for Python and JavaScript/TypeScript codebases.** Below are the main tools, what they do, and how to run them.

---

## Linting

### Python (ruff)
- **Command:** `make lint-py` or `uv run ruff .`
- **Config:** See `[tool.ruff]` in `pyproject.toml`

### JavaScript/TypeScript (eslint)
- **Command:** `make lint-js` or `pnpm eslint "**/*.{js,jsx,ts,tsx}"`
- **Config:** See `eslint.config.js` (Prettier plugin runs after ESLint rules)

---

## Formatting

### Python (black & ruff format)
- **Command:** `make format-py` or `uv run ruff format . && uv run black .`
- **Config:** See `[tool.black]` and `[tool.ruff.format]` in `pyproject.toml`

### JavaScript/TypeScript/JSON/CSS/Markdown (prettier)
- **Command:** `make format-js` or `pnpm prettier --write "**/*.{js,jsx,ts,tsx,json,css,md}"`
- **Config:** `.prettierrc.json`, `.prettierignore`

---

## Security

### Python (bandit)
- **Command:** `uv run bandit -c bandit.yaml -r .`
- **Config:** `bandit.yaml` at project root (canonical config)
- **Pre-commit:** Runs as part of pre-commit hooks

---

## Testing

### Python (pytest)
- **Command:** `uv run python -m pytest`
- **Config:** `[tool.pytest.ini_options]` in `pyproject.toml`
- **Markers:** Custom markers like `unit`, `integration`, `smoke`, etc. are documented in `pyproject.toml`

### JavaScript/TypeScript (vitest)
- **Command:** `pnpm vitest run`
- **Config:** `vitest.config.js`

- **Unified Test Runner:**  
  `make test`  (runs both Python and JS/TS tests)

---

## Type Safety

### Python (pyright, mypy)
- **Pyright:**  
  `uv run pyright`
- **Mypy:**  
  `uv run mypy .`
- **Config:**  
  - Pyright: `pyrightconfig.json`
  - Mypy: `[tool.mypy]` in `pyproject.toml`

### JavaScript/TypeScript
- **TypeScript:**  
  `pnpm tsc --noEmit`
- **Config:**  
  - TypeScript: `tsconfig.json` (if present)

---

## Pre-commit Hooks

- **Run on All Files:**  
  `pre-commit run --all-files`
- **Config:**  
  `.pre-commit-config.yaml`

- **Hooks enabled:**  
  - Ruff (lint/format)
  - Black (format)
  - Bandit (security)
  - Additional custom hooks

---

## Dependency Management

- **Python:**  
  Use `uv` (not pip/venv) for dependency management:
  - Install: `uv pip install -r requirements.txt`
  - Add: `uv pip install <package>`

- **JavaScript/TypeScript:**  
  Use `pnpm` (not npm):
  - Install: `pnpm install`
  - Add: `pnpm add <package>`

---

## Quick Reference (Makefile targets)

| Task         | Command                 |
|--------------|-------------------------|
| Lint Python  | `make lint-py`          |
| Format Python| `make format-py`        |
| Lint JS/TS   | `make lint-js`          |
| Format JS/TS | `make format-js`        |
| Run tests    | `make test`             |
| Type check Py| `uv run pyright`/`mypy` |
| Type check JS| `pnpm tsc --noEmit`     |
| Security     | `uv run bandit ...`     |

---

**See config files in project root for further details.**