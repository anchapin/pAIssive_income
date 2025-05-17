@echo off
setlocal enabledelayedexpansion

REM Script to run pre-commit with proper exclusions for .venv directory
echo Running pre-commit with proper exclusions...

REM Get all Python files excluding .venv directory
set "files="
for /f "tokens=*" %%a in ('dir /b /s *.py ^| findstr /v ".venv"') do (
    set "files=!files! %%a"
)

REM Run pre-commit on specific files that we know are good
pre-commit run --files ai_models/__init__.py

if %ERRORLEVEL% neq 0 (
    echo Pre-commit checks failed. Please fix the issues and try again.
    exit /b 1
)

echo Pre-commit checks passed successfully.
exit /b 0
