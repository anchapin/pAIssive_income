#!/bin/bash
set -e

echo "Setting up pAIssive Income project environment..."

# Set shell environment
export SHELL=/bin/bash

# Update system packages
sudo apt-get update -qq

# Install Python 3.10+ and pip
sudo apt-get install -y python3 python3-pip python3-venv python3-dev

# Install Node.js 20+ (required by package.json)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install pnpm globally
sudo npm install -g pnpm

# Install uv for Python package management
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> $HOME/.profile
export PATH="$HOME/.cargo/bin:$PATH"

# Create Python virtual environment using uv
uv venv .venv
echo 'source .venv/bin/activate' >> $HOME/.profile
source .venv/bin/activate

# Install Python dependencies with all extras
echo "Installing Python dependencies..."
uv pip install -e ".[dev,agents,memory,ml]"

# Install additional missing dependencies
uv pip install flask-migrate sqlalchemy psycopg2-binary bcrypt cryptography sympy requests PyJWT

# Install JavaScript dependencies
echo "Installing JavaScript dependencies..."
pnpm install

# Install nyc and mocha locally in the project
pnpm add --save-dev nyc mocha

# Build Tailwind CSS (required for tests)
echo "Building Tailwind CSS..."
pnpm tailwind:build

# Create necessary directories
mkdir -p security-reports
mkdir -p coverage
mkdir -p test-results
mkdir -p logs

# Set environment variables for tests
export PYTHONNOUSERSITE=1
export SKIP_VENV_CHECK=1
export CI=1

echo "Environment setup completed successfully!"
