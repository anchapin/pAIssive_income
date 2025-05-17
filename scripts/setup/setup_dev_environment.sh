#!/bin/bash
# Setup Development Environment Script for Unix/Linux
# This script runs setup_dev_environment.py to set up the development environment

echo "Setting up development environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.8 or higher from your package manager or https://www.python.org/downloads/"
    exit 1
fi

# Run the setup script
python3 setup_dev_environment.py "$@"

if [ $? -ne 0 ]; then
    echo "Error: Failed to set up development environment."
    exit 1
fi

echo
echo "Development environment setup complete!"
echo
echo "To activate the virtual environment, run:"
echo "source .venv/bin/activate"
echo

exit 0
