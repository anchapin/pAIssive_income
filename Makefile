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
