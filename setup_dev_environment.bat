@echo off
echo Setting up development environment...

:: Create/recreate virtual environment
python scripts/recreate_venv.py
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment
    exit /b 1
)

:: Activate virtual environment and run pre-commit setup
call venv\Scripts\activate.bat && (
    echo Setting up pre-commit hooks...
    python setup_pre_commit.py
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to set up pre-commit hooks
        exit /b 1
    )
)
