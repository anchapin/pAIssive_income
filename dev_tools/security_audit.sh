#!/bin/bash
# Run bandit for Python security scanning

if command -v bandit &>/dev/null; then
  echo "Running bandit..."
  bandit -r . -x tests
else
  echo "bandit not found."
fi