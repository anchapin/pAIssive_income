# Unified Code Quality and Security Makefile

.PHONY: lint format fix docstring-fix syntax-fix security test pre-commit all

lint:
	python3 scripts/manage_quality.py incremental

format:
	python3 scripts/manage_quality.py incremental

fix:
	python3 scripts/manage_quality.py incremental

docstring-fix:
	python3 scripts/manage_quality.py incremental

syntax-fix:
	python3 scripts/manage_quality.py incremental

security:
	python3 scripts/manage_quality.py incremental

test:
	python3 scripts/manage_quality.py incremental

pre-commit:
	python3 scripts/manage_quality.py incremental

all: lint format fix docstring-fix syntax-fix security test pre-commit
	@echo "All code quality, security, and pre-commit checks have been run."

# --- Standardized Python/JS/TS quality targets (chore/config-consolidation) ---

# Python linting/formatting
lint-py:
	uv run ruff .
format-py:
	uv run ruff format .
	uv run black .

# JS/TS linting/formatting (pnpm required)
lint-js:
	pnpm eslint "**/*.{js,jsx,ts,tsx}"
format-js:
	pnpm prettier --write "**/*.{js,jsx,ts,tsx,json,css,md}"

# Unified test target (Python & JS/TS)
test-all:
	uv run python -m pytest
	pnpm vitest run
