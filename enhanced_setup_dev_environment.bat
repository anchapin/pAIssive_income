@echo off
REM Enhanced Setup Development Environment Script for Windows
REM This script runs enhanced_setup_dev_environment.py to set up the development environment

echo Setting up development environment...

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    exit /b 1
)

REM Check Python version
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python 3.8 or higher is required.
    echo Current Python version:
    python --version
    exit /b 1
)

REM Parse command-line arguments
set ARGS=

:parse_args
if "%~1"=="" goto run_script
set ARGS=%ARGS% %1
shift
goto parse_args

:run_script
REM Run the setup script
python enhanced_setup_dev_environment.py %ARGS%

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

exit /b 0
