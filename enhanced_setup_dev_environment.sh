#!/bin/bash
# Enhanced Setup Development Environment Script for Unix/Linux
# This script runs enhanced_setup_dev_environment.py to set up the development environment

echo "Setting up development environment..."

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

# Run the setup script
python3 enhanced_setup_dev_environment.py "$@"

if [ $? -ne 0 ]; then
    echo "Error: Failed to set up development environment."
    exit 1
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
