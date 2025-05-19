#!/bin/bash
# Setup script for ARTIST experiment environment
set -e

# Create necessary directories
echo "Creating ARTIST experiment directories..."
mkdir -p artist_experiments/data
mkdir -p artist_experiments/logs
mkdir -p artist_experiments/models

# Install uv if not already installed
echo "Checking for uv installation..."
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    try {
        curl -LsSf https://astral.sh/uv/install.sh | sh
    } || {
        echo "Failed to install uv. Falling back to traditional venv and pip..."
        python -m pip install --upgrade pip
        python -m venv artist_experiments/.venv-artist
        source artist_experiments/.venv-artist/bin/activate
        python -m pip install -r artist_experiments/requirements-artist.txt
        exit 1
    }
fi

# Create virtual environment with uv
echo "Creating ARTIST virtual environment with uv..."
uv venv artist_experiments/.venv-artist || {
    echo "Failed to create virtual environment with uv. Falling back to Python's venv module..."
    python -m venv artist_experiments/.venv-artist
}

# Activate virtual environment
source artist_experiments/.venv-artist/bin/activate

# Install dependencies with uv
echo "Installing ARTIST dependencies with uv..."
if [ -f "artist_experiments/requirements-artist.txt" ]; then
    uv pip install -r artist_experiments/requirements-artist.txt || {
        echo "Failed to install dependencies with uv pip. Falling back to regular pip..."
        python -m pip install -r artist_experiments/requirements-artist.txt
    }
fi

echo "ARTIST environment setup complete!"
echo "To activate the ARTIST environment, run: source artist_experiments/.venv-artist/bin/activate"
