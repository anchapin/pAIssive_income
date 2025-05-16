#!/bin/bash
# Script to run pre-commit with proper exclusions for .venv directory

echo "Running pre-commit with proper exclusions..."

# Get all Python files excluding .venv directory
FILES=$(find . -name "*.py" | grep -v ".venv")

# Run pre-commit on the files
pre-commit run --files $FILES

if [ $? -ne 0 ]; then
    echo "Pre-commit checks failed. Please fix the issues and try again."
    exit 1
fi

echo "Pre-commit checks passed successfully."
exit 0
