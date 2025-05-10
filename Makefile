# Unified Code Quality and Security Makefile

.PHONY: lint format fix docstring-fix syntax-fix security test pre-commit all

lint:
	python scripts/manage_quality.py lint

format:
	python scripts/manage_quality.py format

fix:
	python scripts/manage_quality.py fix

docstring-fix:
	python scripts/manage_quality.py docstring-fix

syntax-fix:
	python scripts/manage_quality.py syntax-fix

security:
	python scripts/manage_quality.py security-scan

test:
	python scripts/manage_quality.py test

pre-commit:
	python scripts/manage_quality.py pre-commit

all: lint format fix docstring-fix syntax-fix security test pre-commit
	@echo "All code quality, security, and pre-commit checks have been run."
