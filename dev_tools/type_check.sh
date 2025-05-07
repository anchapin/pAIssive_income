#!/bin/bash
# Run mypy static type checking

if command -v mypy &>/dev/null; then
  echo "Running mypy..."
  mypy .
else
  echo "mypy not found."
fi