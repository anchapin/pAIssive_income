#!/bin/bash
# Run ruff, flake8, and black check (if installed) for quick code quality check

if command -v ruff &>/dev/null; then
  echo "Running ruff..."
  ruff check .
fi

if command -v flake8 &>/dev/null; then
  echo "Running flake8..."
  flake8 .
fi

if command -v black &>/dev/null; then
  echo "Running black --check..."
  black --check .
fi
