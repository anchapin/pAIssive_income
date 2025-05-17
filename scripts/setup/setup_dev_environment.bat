@echo off
REM Setup Development Environment Script for Windows
REM This script runs setup_dev_environment.py to set up the development environment

echo Setting up development environment...

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    exit /b 1
)

REM Run the setup script
python setup_dev_environment.py %*

if %ERRORLEVEL% neq 0 (
    echo Error: Failed to set up development environment.
    exit /b 1
)

echo.
echo Development environment setup complete!
echo.
echo To activate the virtual environment, run:
echo .venv\Scripts\activate
echo.
