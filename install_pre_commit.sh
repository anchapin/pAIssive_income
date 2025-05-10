#!/bin/bash
# Shell script to install pre-commit hooks

echo "Installing pre-commit hooks..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python not found in PATH!"
    exit 1
fi

# Check if the script exists
if [ ! -f install_pre_commit.py ]; then
    echo "Error: install_pre_commit.py not found!"
    exit 1
fi

# Run the script
python install_pre_commit.py

# Check exit code
if [ $? -ne 0 ]; then
    echo "Error: install_pre_commit.py failed!"
    exit 1
fi

echo "Pre-commit hooks installed successfully."
exit 0
