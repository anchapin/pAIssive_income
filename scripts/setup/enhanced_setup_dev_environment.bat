@echo off
REM Batch script wrapper for enhanced_setup_dev_environment.py
REM This script passes all arguments to the Python script

echo Enhanced Setup Development Environment Script (Batch Wrapper)
echo This is a wrapper around the Python script enhanced_setup_dev_environment.py
echo ==============================================================

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python and try again.
    exit /b 1
)

REM Check if the Python script exists
if not exist enhanced_setup_dev_environment.py (
    echo Error: enhanced_setup_dev_environment.py not found in the current directory.
    echo Please make sure you are running this script from the repository root.
    exit /b 1
)

REM Pass all arguments to the Python script
echo Running enhanced_setup_dev_environment.py with arguments: %*
python enhanced_setup_dev_environment.py %*

REM Check the exit code of the Python script
if %ERRORLEVEL% neq 0 (
    echo Error: The Python script exited with code %ERRORLEVEL%.
    exit /b %ERRORLEVEL%
)

echo Setup completed successfully!
exit /b 0
