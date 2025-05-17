# Setup Script Documentation

## Overview

The enhanced setup development environment script is designed to automate the setup of a development environment for the pAIssive Income project. It provides a consistent and reliable way to set up the project across different platforms (Windows, macOS, and Linux).

## Scripts

There are two main scripts:

1. **enhanced_setup_dev_environment.py** - The main Python script that handles the setup process
2. **enhanced_setup_dev_environment.sh** - A shell script wrapper for the Python script (for Unix-like systems)

## Features

The setup script provides the following features:

- **System dependency checks**: Verifies that required system dependencies (Node.js, Git, etc.) are installed
- **Virtual environment creation**: Creates a Python virtual environment for the project
- **Dependency installation**: Installs Python and Node.js dependencies
- **Pre-commit hook setup**: Sets up pre-commit hooks for code quality checks
- **IDE configuration**: Creates configuration files for popular IDEs (VS Code, PyCharm)

## Usage

### Basic Usage

```bash
# On Unix-like systems (Linux, macOS)
./enhanced_setup_dev_environment.sh

# On Windows
enhanced_setup_dev_environment.bat
```

### Command-line Options

The script supports various command-line options to customize the setup process:

#### System Dependencies

- `--no-system-deps`: Skip system dependency checks
- `--node-version=<ver>`: Specify Node.js version to install (e.g., 18.x, 20.x)
- `--force-install-deps`: Force installation of missing dependencies

#### Environment Setup

- `--no-venv`: Skip virtual environment creation
- `--no-deps`: Skip dependency installation
- `--no-pre-commit`: Skip pre-commit hook setup
- `--no-ide-config`: Skip IDE configuration
- `--ide=<name>`: Configure specific IDE (vscode, pycharm, all)

#### Setup Profiles

- `--ui-only`: Set up only UI-related dependencies
- `--backend-only`: Set up only backend-related dependencies
- `--minimal`: Minimal setup with essential dependencies only
- `--full`: Full setup with all dependencies (default)

#### Configuration

- `--config-file=<path>`: Specify a configuration file for setup options
- `--help`: Show help message

#### CI Mode

- `--ci-mode`: Special mode for CI environments (skips system dependency checks, disables pre-commit hooks)

### Examples

```bash
# Minimal setup with only essential dependencies
./enhanced_setup_dev_environment.sh --minimal

# Backend-only setup
./enhanced_setup_dev_environment.sh --backend-only

# UI-only setup
./enhanced_setup_dev_environment.sh --ui-only

# Full setup with specific Node.js version
./enhanced_setup_dev_environment.sh --full --node-version=20.x

# Skip system dependency checks
./enhanced_setup_dev_environment.sh --no-system-deps

# Skip virtual environment creation
./enhanced_setup_dev_environment.sh --no-venv

# Configure only VS Code
./enhanced_setup_dev_environment.sh --ide=vscode
```

## Troubleshooting

### Common Issues

#### Virtual Environment Creation Fails

If virtual environment creation fails, try the following:

1. Make sure Python is installed and in your PATH
2. Try creating the virtual environment manually:
   ```bash
   python -m venv .venv
   ```
3. Check if you have write permissions in the project directory

#### Dependency Installation Fails

If dependency installation fails, try the following:

1. Check your internet connection
2. Try installing dependencies manually:
   ```bash
   # Activate the virtual environment
   source .venv/bin/activate  # On Unix-like systems
   .venv\Scripts\activate     # On Windows
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
3. Check if the required dependencies are available for your Python version

#### Pre-commit Hook Setup Fails

If pre-commit hook setup fails, try the following:

1. Make sure Git is installed and initialized in the project directory
2. Try installing pre-commit manually:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

#### IDE Configuration Fails

If IDE configuration fails, try the following:

1. Make sure you have write permissions in the project directory
2. Try creating the configuration files manually:
   ```bash
   mkdir -p .vscode
   touch .vscode/settings.json
   touch .editorconfig
   ```

### Platform-Specific Issues

#### Windows

- If you encounter permission issues, try running the script as administrator
- If you encounter path issues, make sure you're using the correct path separator (`\`)
- If you encounter encoding issues, make sure the script files are saved with UTF-8 encoding

#### macOS

- If you encounter permission issues, try running `chmod +x enhanced_setup_dev_environment.sh` to make the script executable
- If you encounter issues with Homebrew, try running `brew doctor` to diagnose and fix issues

#### Linux

- If you encounter permission issues, try running `chmod +x enhanced_setup_dev_environment.sh` to make the script executable
- If you encounter issues with package managers, try updating your package manager (e.g., `apt update`, `dnf update`)

## Advanced Configuration

### Configuration File

You can create a configuration file (`setup_config.yaml`) to customize the setup process:

```yaml
system_dependencies:
  check_system_deps: true
  node_version: 18.x
  force_install_deps: false

environment_setup:
  create_venv: true
  install_deps: true
  setup_pre_commit: true
  configure_ide: true
  ide: all

setup_profile:
  profile: full  # Options: minimal, backend_only, ui_only, full

dependencies:
  backend: ["requirements.txt", "requirements-dev.txt"]
  ui: ["ui/react_frontend/package.json"]
  minimal: ["requirements.txt"]
```

### Environment Variables

The script respects the following environment variables:

- `PYTHON_PATH`: Path to the Python executable
- `NODE_PATH`: Path to the Node.js executable
- `GIT_PATH`: Path to the Git executable
- `VENV_PATH`: Path to the virtual environment

## Contributing

If you encounter issues or have suggestions for improving the setup script, please open an issue or submit a pull request on GitHub.

## License

This script is part of the pAIssive Income project and is licensed under the same license as the project.
