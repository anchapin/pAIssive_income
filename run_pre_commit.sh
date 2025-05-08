#!/bin/bash
# Run pre-commit hooks on all files

echo "Running pre-commit hooks on all files..."

pre-commit run --all-files

if [ $? -eq 0 ]; then
    echo ""
    echo "All pre-commit hooks passed successfully!"
else
    echo ""
    echo "Some pre-commit hooks failed. Please fix the issues and try again."
fi

echo ""
