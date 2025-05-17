@echo off
REM Batch file to install pre-commit hooks

echo Installing pre-commit hooks...

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found in PATH!
    exit /b 1
)

REM Check if the script exists
if not exist install_pre_commit.py (
    echo Error: install_pre_commit.py not found!
    exit /b 1
)

REM Run the script
python install_pre_commit.py

REM Check exit code
if %ERRORLEVEL% neq 0 (
    echo Error: install_pre_commit.py failed!
    exit /b 1
)

echo Pre-commit hooks installed successfully.
exit /b 0
