#!/bin/bash
set -e

# This script sets up the Python and Node.js environment using only 'uv' for Python and 'pnpm' for Node.js.
# No pip or venv fallback is used. If 'uv' is not available or fails to install, the script will exit.

echo "Checking for uv installation..."
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    if ! command -v uv &> /dev/null; then
        echo "ERROR: Failed to install 'uv'. Please install 'uv' manually and re-run this script."
        exit 1
    fi
fi

# Create virtual environment with uv (no fallback)
echo "Creating virtual environment with uv..."
if ! uv venv .venv; then
    echo "ERROR: Failed to create virtual environment with 'uv'."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies with uv pip (no fallback)
echo "Installing Python dependencies with uv pip..."
if [ -f "requirements-dev.txt" ]; then
    if ! uv pip install -r requirements-dev.txt; then
        echo "ERROR: Failed to install dependencies from requirements-dev.txt with 'uv'."
        exit 1
    fi
fi
if [ -f "requirements.txt" ]; then
    if ! uv pip install -r requirements.txt; then
        echo "ERROR: Failed to install dependencies from requirements.txt with 'uv'."
        exit 1
    fi
fi

# Install Node.js dependencies (pnpm only)
echo "Installing Node.js dependencies with pnpm..."
if ! command -v pnpm &> /dev/null; then
    echo "pnpm not found, bootstrapping with npm..."
    npm install -g pnpm
fi
pnpm install --reporter=default
