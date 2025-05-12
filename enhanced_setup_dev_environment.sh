#!/bin/bash
# Enhanced Setup Development Environment Script for Unix/Linux
# This script runs enhanced_setup_dev_environment.py to set up the development environment

echo "Setting up development environment..."
echo "Running with arguments: $@"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.8 or higher from your package manager or https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Error: Python 3.8 or higher is required."
    echo "Current Python version:"
    python3 --version
    exit 1
fi

# Check if enhanced_setup_dev_environment.py exists
if [ ! -f "enhanced_setup_dev_environment.py" ]; then
    echo "Error: enhanced_setup_dev_environment.py not found in the current directory."
    echo "Current directory contents:"
    ls -la
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Warning: uv is not installed or not in PATH."
    echo "Will attempt to proceed without uv. Some features may not work correctly."
    # Not exiting, will try to continue without uv
fi

# Check if Ruff is installed (Ruff is still used for linting/formatting, uv handles installation)
if ! command -v ruff &> /dev/null; then
    echo "Warning: Ruff is not installed globally or not in PATH."
    echo "The setup script will attempt to install it into the virtual environment."
    # Not exiting, as setup_dev_environment.py will handle installing ruff
fi

# The Python script enhanced_setup_dev_environment.py will handle dependency installation using uv.
# No need to pip install requirements-dev.txt here directly.

echo # Add a newline for better readability before Python script output

# Run the setup script with all arguments passed to this script
echo "Executing: python3 enhanced_setup_dev_environment.py $@"

# Check if --minimal flag is passed
if [[ "$*" == *"--minimal"* ]]; then
    echo "Detected --minimal flag, ensuring minimal profile is used"
    python3 enhanced_setup_dev_environment.py --minimal --no-system-deps
else
    python3 enhanced_setup_dev_environment.py "$@"
fi

PYTHON_EXIT_CODE=$?
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    echo "Error: Python script failed with exit code $PYTHON_EXIT_CODE"
    echo "Trying to run with default arguments..."
    python3 enhanced_setup_dev_environment.py

    if [ $? -ne 0 ]; then
        echo "Error: Failed to set up development environment even with default arguments."
        exit 1
    fi
fi

# Create IDE configuration files
echo "Creating .editorconfig file..."
cat <<EOL > .editorconfig
# EditorConfig helps maintain consistent coding styles across different editors
# https://editorconfig.org/

root = true

[*]
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
charset = utf-8

[*.{py,pyi}]
indent_style = space
indent_size = 4
max_line_length = 88

[*.{json,yml,yaml,toml}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
EOL

echo "Creating .vscode directory and settings.json..."
mkdir -p .vscode
cat <<EOL > .vscode/settings.json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.formatting.provider": "none",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll": true,
        "source.organizeImports": true
    },
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll": true,
            "source.organizeImports": true
        }
    },
    "ruff.format.args": [],
    "ruff.lint.run": "onSave"
}
EOL

echo
echo "Development environment setup complete!"
echo
echo "To activate the virtual environment, run:"
echo "source .venv/bin/activate"
echo

exit 0
