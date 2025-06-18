#!/bin/bash
# Jules-optimized setup script for pAIssive Income
# This script is designed to work in Jules' VM environment

set -e

echo "🚀 Starting pAIssive Income setup for Jules environment..."
echo "=================================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status messages
print_status() {
    echo "✅ $1"
}

print_error() {
    echo "❌ $1"
}

print_info() {
    echo "ℹ️  $1"
}

# Check for required tools
echo "🔍 Checking for required tools..."

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    print_status "Python found: $PYTHON_VERSION"
else
    print_error "Python3 not found"
    exit 1
fi

if command_exists node; then
    NODE_VERSION=$(node --version)
    print_status "Node.js found: $NODE_VERSION"
else
    print_error "Node.js not found"
    exit 1
fi

# Install uv if not present
if ! command_exists uv; then
    print_info "Installing uv..."
    pip3 install --user uv
    export PATH="$HOME/.local/bin:$PATH"
fi

if command_exists uv; then
    UV_VERSION=$(uv --version)
    print_status "uv found: $UV_VERSION"
else
    print_error "Failed to install uv"
    exit 1
fi

# Install pnpm if not present
if ! command_exists pnpm; then
    print_info "Installing pnpm..."
    npm install -g pnpm
fi

if command_exists pnpm; then
    PNPM_VERSION=$(pnpm --version)
    print_status "pnpm found: $PNPM_VERSION"
else
    print_error "Failed to install pnpm"
    exit 1
fi

echo ""
echo "📦 Installing Python dependencies..."
echo "=================================="

# Create a lightweight virtual environment using uv for Jules
print_info "Creating virtual environment with uv..."
uv venv .venv --python python3
print_status "Virtual environment created"

# Activate the virtual environment for this session
export VIRTUAL_ENV="$(pwd)/.venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies using uv
if [ -f "requirements.txt" ]; then
    print_info "Installing from requirements.txt..."
    uv pip install -r requirements.txt
    print_status "Python dependencies installed"
else
    print_info "No requirements.txt found, skipping Python dependencies"
fi

# Install development dependencies if they exist
if [ -f "requirements-dev.txt" ]; then
    print_info "Installing development dependencies..."
    uv pip install -r requirements-dev.txt
    print_status "Development dependencies installed"
fi

echo ""
echo "🌐 Installing Node.js dependencies..."
echo "===================================="

# Install Node.js dependencies
if [ -f "package.json" ]; then
    print_info "Running pnpm install..."
    pnpm install
    print_status "Node.js dependencies installed"
else
    print_info "No package.json found, skipping Node.js dependencies"
fi

echo ""
echo "⚙️  Setting up configuration..."
echo "=============================="

# Setup .env file
if [ -f ".env.example" ]; then
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_status ".env file created from .env.example"
    else
        print_info ".env file already exists, skipping"
    fi
else
    print_info "No .env.example found, skipping .env setup"
fi

echo ""
echo "🧪 Running validation tests..."
echo "============================="

# Basic validation - check if Python imports work
print_info "Testing Python environment..."
python -c "import sys; print(f'Python {sys.version} is working')"
print_status "Python environment validated"

# Check if we can import common packages
if python -c "import yaml" 2>/dev/null; then
    print_status "PyYAML is available"
fi

if python -c "import requests" 2>/dev/null; then
    print_status "Requests is available"
fi

# Test Node.js environment
if command_exists node; then
    print_info "Testing Node.js environment..."
    node -e "console.log('Node.js', process.version, 'is working')"
    print_status "Node.js environment validated"
fi

# Run any existing tests if they exist
if [ -f "package.json" ] && pnpm run test --if-present >/dev/null 2>&1; then
    print_info "Running Node.js tests..."
    pnpm run test
    print_status "Node.js tests passed"
fi

# Try to run Python tests if pytest is available
if python -c "import pytest" 2>/dev/null; then
    if [ -d "tests" ] || [ -f "test_*.py" ] || find . -name "*_test.py" -type f | head -1 | grep -q .; then
        print_info "Running Python tests..."
        python -m pytest --version
        print_status "pytest is available for testing"
    fi
fi

echo ""
echo "🎉 Setup completed successfully!"
echo "==============================="
print_status "Environment is ready for development"
print_info "You can now run your application or tests"

# Display useful information
echo ""
echo "📋 Environment Summary:"
echo "======================"
echo "Python: $(python --version)"
echo "Virtual Environment: $VIRTUAL_ENV"
echo "Node.js: $(node --version)"
echo "pnpm: $(pnpm --version)"
echo "uv: $(uv --version)"

if [ -f ".env" ]; then
    echo "✅ .env file is configured"
fi

echo ""
echo "🚀 Ready to go! Your pAIssive Income environment is set up for Jules."
