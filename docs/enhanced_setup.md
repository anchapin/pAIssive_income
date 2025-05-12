# Enhanced Development Environment Setup

This document describes the enhanced development environment setup script for the pAIssive Income project.

## Overview

The enhanced setup script automates the setup of a development environment for the pAIssive Income project. It performs the following tasks:

1. Checks for and installs system dependencies (Node.js, Git, etc.)
2. Creates a virtual environment
3. Installs Python dependencies
4. Installs Node.js dependencies
5. Sets up pre-commit hooks
6. Creates IDE configuration files
7. Provides instructions for manual steps

## Usage

### Windows

```batch
enhanced_setup_dev_environment.bat [options]
```

### Unix/Linux/macOS

```bash
./enhanced_setup_dev_environment.sh [options]
```

## Options

### System Dependencies

- `--no-system-deps`: Skip system dependency checks
- `--node-version=<ver>`: Specify Node.js version to install (e.g., 18.x, 20.x)
- `--force-install-deps`: Force installation of missing dependencies

### Environment Setup

- `--no-venv`: Skip virtual environment creation
- `--no-deps`: Skip dependency installation
- `--no-pre-commit`: Skip pre-commit hook setup
- `--no-ide-config`: Skip IDE configuration
- `--ide=<name>`: Configure specific IDE (vscode, pycharm, all)

### Setup Profiles

- `--ui-only`: Set up only UI-related dependencies
- `--backend-only`: Set up only backend-related dependencies
- `--minimal`: Minimal setup with essential dependencies only
- `--full`: Full setup with all dependencies (default)

### Configuration

- `--config-file=<path>`: Specify a configuration file for setup options

## Configuration File

You can use a configuration file to specify setup options. The configuration file can be in YAML or JSON format. Here's an example:

```yaml
system_dependencies:
  check_system_deps: true
  node_version: "18.x"
  force_install_deps: false

environment_setup:
  create_venv: true
  install_deps: true
  setup_pre_commit: true
  configure_ide: true
  ide: "all"

setup_profile:
  profile: "full"  # Options: minimal, backend_only, ui_only, full

dependencies:
  backend: ["requirements.txt", "requirements-dev.txt"]
  ui: ["ui/react_frontend/package.json"]
  minimal: ["requirements.txt"]
```

## System Dependencies

The script checks for the following system dependencies:

- Python 3.8 or higher (required)
- `uv` (Python package installer and resolver, required). Install via `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- Node.js (for UI development)
- pnpm (for UI development)
- Git (for version control)

If `uv` or other critical dependencies are missing, the script will guide you to install them. The script uses `uv` for Python virtual environment creation and dependency installation.

## IDE Configuration

The script configures the following IDEs:

- VS Code
- PyCharm

It also creates an `.editorconfig` file for editor-agnostic settings.

### VS Code Extensions

The script recommends installing the following VS Code extensions:

- [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)
- [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)

### PyCharm Plugins

The script recommends installing the following PyCharm plugins:

- [Ruff](https://plugins.jetbrains.com/plugin/20574-ruff)
- [Node.js](https://plugins.jetbrains.com/plugin/6098-node-js)

## Next Steps

After running the setup script, you should:

1. Activate the virtual environment
2. Install IDE extensions
3. Run pre-commit hooks on all files
4. Run tests to verify the setup
5. Start the development server

## Troubleshooting

If you encounter any issues during setup, check the following:

- Make sure you have the required system dependencies installed
- Check that you have sufficient permissions to create files and directories
- Verify that your internet connection is working (for downloading dependencies)
- Try running the script with the `--minimal` option to see if a minimal setup works

If you continue to have issues, please open an issue on the GitHub repository.
