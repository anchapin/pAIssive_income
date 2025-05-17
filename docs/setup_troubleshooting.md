# Setup Script Troubleshooting Guide

This guide provides solutions for common issues encountered when using the enhanced setup development environment script.

## Table of Contents

1. [General Issues](#general-issues)
2. [Python and Virtual Environment Issues](#python-and-virtual-environment-issues)
3. [Dependency Installation Issues](#dependency-installation-issues)
4. [Node.js and UI Setup Issues](#nodejs-and-ui-setup-issues)
5. [Git and Pre-commit Issues](#git-and-pre-commit-issues)
6. [IDE Configuration Issues](#ide-configuration-issues)
7. [Platform-Specific Issues](#platform-specific-issues)
   - [Windows](#windows)
   - [macOS](#macos)
   - [Linux](#linux)
8. [Advanced Troubleshooting](#advanced-troubleshooting)

## General Issues

### Script Won't Run

**Symptoms:**
- Permission denied error
- Script not found error

**Solutions:**
1. Make sure the script is executable:
   ```bash
   chmod +x enhanced_setup_dev_environment.sh
   ```
2. Make sure you're running the script from the project root directory.
3. Try running the Python script directly:
   ```bash
   python enhanced_setup_dev_environment.py
   ```

### Script Crashes Without Error Message

**Symptoms:**
- Script exits without any error message
- No setup is performed

**Solutions:**
1. Run the script with verbose logging:
   ```bash
   ./enhanced_setup_dev_environment.sh --verbose
   ```
2. Check the log file (if created) in the `.logs` directory.
3. Try running the script with Python's debug mode:
   ```bash
   python -d enhanced_setup_dev_environment.py
   ```

### Script Takes Too Long to Complete

**Symptoms:**
- Script runs for an unusually long time
- Progress seems to be stuck

**Solutions:**
1. Run the script with verbose logging to see what step it's stuck on:
   ```bash
   ./enhanced_setup_dev_environment.sh --verbose
   ```
2. Try running the script with specific steps disabled:
   ```bash
   ./enhanced_setup_dev_environment.sh --no-system-deps --no-pre-commit
   ```
3. Check your internet connection, as dependency downloads might be slow.

## Python and Virtual Environment Issues

### Python Not Found

**Symptoms:**
- "Python not found" error
- "Command not found: python" error

**Solutions:**
1. Make sure Python is installed and in your PATH.
2. Try specifying the Python path explicitly:
   ```bash
   PYTHON_PATH=/path/to/python ./enhanced_setup_dev_environment.sh
   ```
3. On Windows, try using `py` instead of `python`:
   ```bash
   py enhanced_setup_dev_environment.py
   ```

### Virtual Environment Creation Fails

**Symptoms:**
- "Error creating virtual environment" message
- venv module not found

**Solutions:**
1. Make sure the `venv` module is available:
   ```bash
   python -m venv --help
   ```
2. Try creating the virtual environment manually:
   ```bash
   python -m venv .venv
   ```
3. Check if you have write permissions in the project directory.
4. On some Linux distributions, you might need to install the `python3-venv` package:
   ```bash
   sudo apt install python3-venv  # For Debian/Ubuntu
   sudo dnf install python3-venv  # For Fedora
   ```

### Virtual Environment Activation Fails

**Symptoms:**
- "Cannot activate virtual environment" message
- Activation script not found

**Solutions:**
1. Make sure the virtual environment was created successfully.
2. Try activating the virtual environment manually:
   ```bash
   # On Unix-like systems
   source .venv/bin/activate
   
   # On Windows
   .venv\Scripts\activate
   ```
3. Check if the activation script exists and has the correct permissions.

## Dependency Installation Issues

### Pip Installation Fails

**Symptoms:**
- "pip not found" error
- "Error installing pip" message

**Solutions:**
1. Make sure pip is installed:
   ```bash
   python -m pip --version
   ```
2. Try upgrading pip:
   ```bash
   python -m pip install --upgrade pip
   ```
3. If pip is not installed, try installing it:
   ```bash
   python -m ensurepip
   ```

### Package Installation Fails

**Symptoms:**
- "Error installing package X" message
- Dependency resolution conflicts

**Solutions:**
1. Check your internet connection.
2. Try installing the package manually:
   ```bash
   pip install package-name
   ```
3. Check if the package is available for your Python version.
4. Try using a different package index:
   ```bash
   pip install package-name --index-url https://pypi.org/simple
   ```

### Requirements File Not Found

**Symptoms:**
- "Requirements file not found" error
- "No such file or directory" error

**Solutions:**
1. Make sure you're running the script from the project root directory.
2. Check if the requirements file exists:
   ```bash
   ls -la requirements.txt
   ```
3. Try specifying the requirements file path explicitly:
   ```bash
   ./enhanced_setup_dev_environment.sh --requirements-file=/path/to/requirements.txt
   ```

## Node.js and UI Setup Issues

### Node.js Not Found

**Symptoms:**
- "Node.js not found" error
- "Command not found: node" error

**Solutions:**
1. Make sure Node.js is installed and in your PATH.
2. Try specifying the Node.js path explicitly:
   ```bash
   NODE_PATH=/path/to/node ./enhanced_setup_dev_environment.sh
   ```
3. Try installing Node.js using a version manager like nvm:
   ```bash
   nvm install 18
   nvm use 18
   ```

### npm Installation Fails

**Symptoms:**
- "npm not found" error
- "Error installing npm packages" message

**Solutions:**
1. Make sure npm is installed:
   ```bash
   npm --version
   ```
2. Try using a different package manager:
   ```bash
   ./enhanced_setup_dev_environment.sh --package-manager=pnpm
   ```
3. Check your internet connection.
4. Try clearing the npm cache:
   ```bash
   npm cache clean --force
   ```

### UI Dependencies Installation Fails

**Symptoms:**
- "Error installing UI dependencies" message
- npm/pnpm/yarn errors

**Solutions:**
1. Try installing the dependencies manually:
   ```bash
   cd ui/react_frontend
   npm install
   ```
2. Check if the `package.json` file exists and is valid:
   ```bash
   cd ui/react_frontend
   cat package.json
   ```
3. Try using a different Node.js version:
   ```bash
   ./enhanced_setup_dev_environment.sh --node-version=16.x
   ```

## Git and Pre-commit Issues

### Git Not Found

**Symptoms:**
- "Git not found" error
- "Command not found: git" error

**Solutions:**
1. Make sure Git is installed and in your PATH.
2. Try specifying the Git path explicitly:
   ```bash
   GIT_PATH=/path/to/git ./enhanced_setup_dev_environment.sh
   ```

### Pre-commit Installation Fails

**Symptoms:**
- "Error installing pre-commit" message
- pre-commit not found

**Solutions:**
1. Try installing pre-commit manually:
   ```bash
   pip install pre-commit
   ```
2. Check if pre-commit is available for your Python version.
3. Try skipping pre-commit installation:
   ```bash
   ./enhanced_setup_dev_environment.sh --no-pre-commit
   ```

### Pre-commit Hook Setup Fails

**Symptoms:**
- "Error setting up pre-commit hooks" message
- Git hooks directory not found

**Solutions:**
1. Make sure Git is initialized in the project directory:
   ```bash
   git status
   ```
2. Try setting up pre-commit hooks manually:
   ```bash
   pre-commit install
   ```
3. Check if you have write permissions in the `.git/hooks` directory.

## IDE Configuration Issues

### IDE Configuration Files Creation Fails

**Symptoms:**
- "Error creating IDE configuration files" message
- Permission denied errors

**Solutions:**
1. Make sure you have write permissions in the project directory.
2. Try creating the configuration files manually:
   ```bash
   mkdir -p .vscode
   touch .vscode/settings.json
   touch .editorconfig
   ```
3. Try skipping IDE configuration:
   ```bash
   ./enhanced_setup_dev_environment.sh --no-ide-config
   ```

### VS Code Extensions Installation Fails

**Symptoms:**
- "Error installing VS Code extensions" message
- VS Code not found

**Solutions:**
1. Make sure VS Code is installed and in your PATH.
2. Try installing the extensions manually using VS Code.
3. Try skipping VS Code extensions installation:
   ```bash
   ./enhanced_setup_dev_environment.sh --no-vscode-extensions
   ```

## Platform-Specific Issues

### Windows

#### Path Separator Issues

**Symptoms:**
- "File not found" errors with incorrect path separators
- Paths with mixed separators

**Solutions:**
1. Make sure you're using the correct path separator (`\`) in Windows paths.
2. Try using forward slashes (`/`) in paths, as Python can handle them on Windows.
3. Use the Windows batch script (`enhanced_setup_dev_environment.bat`) instead of the shell script.

#### Permission Issues

**Symptoms:**
- "Access denied" errors
- "Permission denied" errors

**Solutions:**
1. Try running the script as administrator.
2. Check if you have write permissions in the project directory.
3. Disable any antivirus or security software that might be blocking the script.

#### Line Ending Issues

**Symptoms:**
- Syntax errors in scripts
- "Bad interpreter" errors

**Solutions:**
1. Make sure the script files have the correct line endings (CRLF for Windows).
2. Try converting the line endings:
   ```bash
   dos2unix enhanced_setup_dev_environment.sh
   unix2dos enhanced_setup_dev_environment.bat
   ```

### macOS

#### Homebrew Installation Issues

**Symptoms:**
- "Homebrew not found" error
- "Error installing Homebrew packages" message

**Solutions:**
1. Make sure Homebrew is installed:
   ```bash
   brew --version
   ```
2. Try fixing Homebrew issues:
   ```bash
   brew doctor
   ```
3. Try updating Homebrew:
   ```bash
   brew update
   ```

#### Xcode Command Line Tools Issues

**Symptoms:**
- "Xcode Command Line Tools not found" error
- Compilation errors for native extensions

**Solutions:**
1. Make sure Xcode Command Line Tools are installed:
   ```bash
   xcode-select --install
   ```
2. Try reinstalling Xcode Command Line Tools:
   ```bash
   sudo rm -rf /Library/Developer/CommandLineTools
   xcode-select --install
   ```

### Linux

#### Package Manager Issues

**Symptoms:**
- "Package manager not found" error
- "Error installing system packages" message

**Solutions:**
1. Make sure your package manager is working:
   ```bash
   # For Debian/Ubuntu
   apt update
   
   # For Fedora
   dnf check-update
   
   # For Arch Linux
   pacman -Sy
   ```
2. Try updating your package manager's cache:
   ```bash
   # For Debian/Ubuntu
   sudo apt update
   
   # For Fedora
   sudo dnf check-update
   
   # For Arch Linux
   sudo pacman -Sy
   ```

#### Missing Development Libraries

**Symptoms:**
- Compilation errors for native extensions
- "Missing header file" errors

**Solutions:**
1. Install development libraries:
   ```bash
   # For Debian/Ubuntu
   sudo apt install build-essential python3-dev
   
   # For Fedora
   sudo dnf install gcc gcc-c++ python3-devel
   
   # For Arch Linux
   sudo pacman -S base-devel python-pip
   ```

## Advanced Troubleshooting

### Debugging the Setup Script

If you're still experiencing issues, you can debug the setup script:

1. Enable verbose logging:
   ```bash
   ./enhanced_setup_dev_environment.sh --verbose
   ```

2. Run the script with Python's debug mode:
   ```bash
   python -d enhanced_setup_dev_environment.py
   ```

3. Add debug print statements to the script:
   ```python
   print(f"Debug: {variable_name}")
   ```

4. Check the log file (if created) in the `.logs` directory.

### Reporting Issues

If you've tried the solutions in this guide and are still experiencing issues, please report the issue on GitHub with the following information:

1. Operating system and version
2. Python version
3. Node.js version (if applicable)
4. Error messages and logs
5. Steps to reproduce the issue
6. Any other relevant information

This will help us improve the setup script and documentation.
