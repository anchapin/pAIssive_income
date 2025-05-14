#!/bin/bash
# Enhanced Setup Development Environment Script (Shell Wrapper)
# This script is a robust wrapper around enhanced_setup_dev_environment.py
# It handles error conditions, provides better logging, and ensures proper execution

# Enable error handling
set -e

# Define colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log levels
INFO="${BLUE}[INFO]${NC}"
WARNING="${YELLOW}[WARNING]${NC}"
ERROR="${RED}[ERROR]${NC}"
SUCCESS="${GREEN}[SUCCESS]${NC}"

# Function to log messages
log() {
    local level="$1"
    local message="$2"
    echo -e "${level} ${message}"
}

# Function to log and exit on error
error_exit() {
    log "$ERROR" "$1"
    exit "${2:-1}" # Default exit code is 1
}

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Display script header
log "$INFO" "Enhanced Setup Development Environment Script (Shell Wrapper)"
log "$INFO" "Version: 1.1.0"
log "$INFO" "=============================================================="

# Check if running from repository root
if [ ! -f "enhanced_setup_dev_environment.py" ]; then
    error_exit "enhanced_setup_dev_environment.py not found in the current directory.\nPlease make sure you are running this script from the repository root." 2
fi

# Detect Python executable
PYTHON_CMD=""
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    # Check if python is Python 3
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
    fi
fi

# Exit if no Python 3 is found
if [ -z "$PYTHON_CMD" ]; then
    error_exit "Python 3 is not installed or not in PATH.\nPlease install Python 3 and try again." 3
fi

# Log Python version
PYTHON_FULL_VERSION=$($PYTHON_CMD --version 2>&1)
log "$INFO" "Using $PYTHON_FULL_VERSION"

# Install uv using the detected Python command
log "$INFO" "Installing uv..."
if ! "$PYTHON_CMD" -m pip install --upgrade pip; then
    log "$WARNING" "Failed to upgrade pip. Continuing anyway."
fi
if ! "$PYTHON_CMD" -m pip install uv; then
    log "$ERROR" "Failed to install uv. Virtual environment creation and dependency installation may fall back to standard venv/pip."
fi

# Make the Python script executable
if ! chmod +x enhanced_setup_dev_environment.py; then
    error_exit "Failed to make enhanced_setup_dev_environment.py executable.\nPlease check file permissions." 4
fi

# Display the arguments being passed
if [ $# -eq 0 ]; then
    log "$INFO" "Running enhanced_setup_dev_environment.py with default settings"
else
    log "$INFO" "Running enhanced_setup_dev_environment.py with arguments: $*"
fi

# Run the Python script with all arguments
"$PYTHON_CMD" enhanced_setup_dev_environment.py "$@"
PYTHON_EXIT_CODE=$?

# Check the exit code of the Python script
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    error_exit "The Python script exited with code $PYTHON_EXIT_CODE.\nCheck the output above for more details." $PYTHON_EXIT_CODE
fi

# Success message
log "$SUCCESS" "Setup completed successfully!"

# Provide hint about next steps
log "$INFO" "To activate the virtual environment, run:"
if [ "$(uname)" == "Darwin" ] || [ "$(uname)" == "Linux" ]; then
    log "$INFO" "  source .venv/bin/activate"
else
    log "$INFO" "  .venv\\Scripts\\activate"
fi

exit 0
