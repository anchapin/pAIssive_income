#!/bin/bash
echo "Running linting checks..."

# Activate the virtual environment
source .venv/bin/activate

# Run the linting checks
python scripts/lint_check.py "$@"

# Return the exit code from the Python script
exit $?
