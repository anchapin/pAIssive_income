#!/bin/bash
# Run ruff for linting and formatting checks

if command -v ruff &>/dev/null; then
  echo "Running ruff linting..."
  ruff check .

  echo "Running ruff formatting check..."
  ruff format --check .
else
  echo "Ruff not found. Please install with: pip install ruff"
  exit 1
fi
