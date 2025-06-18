# Enhanced Development Environment Setup

This document describes the development environment setup scripts for the pAIssive Income project.

## Overview

We provide multiple setup scripts to accommodate different development environments:

1. **Enhanced Setup Script** - Full-featured setup with extensive configuration options
2. **Jules Environment Setup Script** - Optimized for Jules VM environment with streamlined setup

### Enhanced Setup Script

The enhanced setup script automates the setup of a development environment for the pAIssive Income project. It performs the following tasks:

1. Checks for and installs system dependencies (Node.js, Git, etc.)
2. Creates a virtual environment
3. Installs Python dependencies
4. Installs Node.js dependencies
5. Sets up pre-commit hooks
6. Creates IDE configuration files
7. Provides instructions for manual steps

### Jules Environment Setup Script

The Jules setup script (`setup-jules.sh`) is specifically optimized for Jules VM environments and provides:

1. Streamlined dependency checking and installation
2. Automatic installation of `uv` and `pnpm` if not present
3. Virtual environment creation using `uv`
4. Python and Node.js dependency installation
5. Environment configuration (.env setup)
6. Basic validation testing
7. Environment summary and status reporting

## Usage

### Enhanced Setup (Windows)

```batch
enhanced_setup_dev_environment.bat [options]
```

### Enhanced Setup (Unix/Linux/macOS)

```bash
./enhanced_setup_dev_environment.sh [options]
```

### Jules Environment Setup

```bash
./setup-jules.sh
```

**Note:** The Jules setup script is designed to work out-of-the-box without command-line options and is optimized for Jules VM environments.

## Jules Environment Setup Details

The `setup-jules.sh` script is specifically designed for Jules VM environments and provides a streamlined setup experience. Here's what it does:

### Prerequisites Check
- Verifies Python 3 is installed
- Verifies Node.js is installed
- Exits with clear error messages if prerequisites are missing

### Automatic Tool Installation
- Installs `uv` (fast Python package installer) if not present
- Installs `pnpm` (fast Node.js package manager) if not present
- Updates PATH to include newly installed tools

### Environment Setup
- Creates a Python virtual environment using `uv venv`
- Activates the virtual environment for the session
- Installs Python dependencies from `requirements.txt` and `requirements-dev.txt`
- Installs Node.js dependencies using `pnpm install`

### Configuration
- Copies `.env.example` to `.env` if it doesn't exist
- Preserves existing `.env` files

### Validation Testing
- Tests Python environment with basic imports
- Checks for common packages (PyYAML, requests)
- Validates Node.js environment
- Runs existing tests if available
- Reports pytest availability

### Status Reporting
- Provides clear status messages with emojis
- Shows environment summary with versions
- Confirms successful setup completion

### When to Use Jules Setup

Use `setup-jules.sh` when:
- Working in a Jules VM environment
- You want a quick, streamlined setup
- You prefer automatic tool installation
- You don't need extensive configuration options
- You're setting up for the first time

Use the enhanced setup script when:
- You need custom configuration options
- You're setting up on various platforms
- You need IDE-specific configurations
- You want to control which components are installed

## Enhanced Setup Options

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
