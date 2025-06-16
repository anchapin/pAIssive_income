#!/bin/bash
# Setup script for ARTIST experiment environment using only 'uv'
set -e

# Create necessary directories
echo "Creating ARTIST experiment directories..."
mkdir -p artist_experiments/data
mkdir -p artist_experiments/logs
mkdir -p artist_experiments/models

# Ensure uv is installed
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
echo "Creating ARTIST virtual environment with uv..."
if ! uv venv artist_experiments/.venv-artist; then
    echo "ERROR: Failed to create virtual environment with 'uv'."
    exit 1
fi

# Activate virtual environment
source artist_experiments/.venv-artist/bin/activate

# Install dependencies with uv pip (no fallback)
echo "Installing ARTIST dependencies with uv pip..."
if [ -f "artist_experiments/requirements-artist.txt" ]; then
    if ! uv pip install -r artist_experiments/requirements-artist.txt; then
        echo "ERROR: Failed to install dependencies from requirements-artist.txt with 'uv'."
        exit 1
    fi
fi

echo "ARTIST environment setup complete!"
echo "To activate the ARTIST environment, run: source artist_experiments/.venv-artist/bin/activate"
