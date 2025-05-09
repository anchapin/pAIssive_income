#!/bin/bash
echo "Regenerating virtual environment..."

# Try to deactivate any active virtual environment
deactivate 2>/dev/null || true

# Check if .venv directory exists
if [ -d ".venv" ]; then
    echo "Attempting to remove existing virtual environment..."

    # Try to remove the directory
    rm -rf .venv 2>/dev/null

    # Check if the directory still exists
    if [ -d ".venv" ]; then
        echo "Could not remove .venv directory. It might be in use by another process."
        echo "Trying alternative approach..."

        # Try using the Python script
        python3 regenerate_venv.py
        if [ $? -ne 0 ]; then
            echo "Failed to regenerate virtual environment."
            echo ""
            echo "Please try the following steps:"
            echo "1. Close all terminals, IDEs, and applications that might be using the virtual environment"
            echo "2. Run this script again"
            echo ""
            exit 1
        fi
    else
        # Directory was successfully removed, create a new one
        echo "Creating new virtual environment..."
        python3 -m venv .venv
        if [ $? -ne 0 ]; then
            echo "Failed to create virtual environment."
            exit 1
        fi

        # Install dependencies
        echo "Installing dependencies..."
        source .venv/bin/activate
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
        if [ -f "requirements-dev.txt" ]; then
            python -m pip install -r requirements-dev.txt
        fi
        deactivate
    fi
else
    # No existing virtual environment, create a new one
    echo "Creating new virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi

    # Install dependencies
    echo "Installing dependencies..."
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if [ -f "requirements-dev.txt" ]; then
        python -m pip install -r requirements-dev.txt
    fi
    deactivate
fi

echo ""
echo "Virtual environment regenerated successfully!"
echo ""
echo "To activate the virtual environment, run:"
echo "    source .venv/bin/activate"
echo ""
