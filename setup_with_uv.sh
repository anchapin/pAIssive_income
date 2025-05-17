#!/bin/bash
set -e

echo "Checking for uv installation..."
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    if ! command -v uv &> /dev/null; then
        echo "Failed to install uv. Falling back to traditional venv and pip..."
        python -m pip install --upgrade pip
        python -m venv .venv
        source .venv/bin/activate
        python -m pip install -r requirements-dev.txt
        exit 1
    fi
fi

# Create virtual environment with uv
echo "Creating virtual environment with uv..."
uv venv .venv || {
    echo "Failed to create virtual environment with uv. Falling back to Python's venv module..."
    python -m venv .venv
}

# Activate virtual environment
source .venv/bin/activate

# Install dependencies with uv
echo "Installing dependencies with uv..."
if [ -f "requirements-dev.txt" ]; then
    uv pip install -r requirements-dev.txt || {
        echo "Failed to install dependencies with uv pip. Falling back to regular pip..."
        python -m pip install -r requirements-dev.txt
    }
fi
if [ -f "requirements.txt" ]; then
    uv pip install -r requirements.txt || {
        echo "Failed to install dependencies with uv pip. Falling back to regular pip..."
        python -m pip install -r requirements.txt
    }
fi

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install -g pnpm
pnpm install --reporter=default
