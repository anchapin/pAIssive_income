#!/bin/bash
# Setup pre-commit hooks for Unix/Linux

echo "Setting up pre-commit hooks..."

python setup_pre_commit.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Pre-commit hooks setup completed successfully!"
else
    echo ""
    echo "Failed to set up pre-commit hooks. Please check the error messages above."
fi

echo ""
