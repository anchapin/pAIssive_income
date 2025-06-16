#!/bin/bash

# Setup Local Development Environment for pAIssive_income
# This script sets up the local environment so development commands work

set -e

echo "Setting up local development environment..."

# Add local bin to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"

# Check if pip is installed, if not install it
if ! command -v pip &> /dev/null; then
    echo "Installing pip..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3 - --break-system-packages
fi

# Install essential development tools
echo "Installing essential development dependencies..."
pip install --break-system-packages \
    ruff \
    pytest \
    pytest-cov \
    mypy \
    sqlalchemy \
    fastapi \
    pydantic \
    httpx \
    flask \
    flask-migrate

echo "Environment setup complete!"
echo ""
echo "To use the development commands in the future, run:"
echo '  export PATH="$HOME/.local/bin:$PATH"'
echo ""
echo "Or reload your shell to make the PATH change permanent:"
echo "  source ~/.bashrc"
echo ""
echo "You can now run:"
echo "  make lint    # Run code linting"
echo "  make test    # Run tests"
echo "  pytest       # Run tests directly"
echo "  ruff check . # Run linting directly"