@echo off
REM Batch file to run fix_linting_issues.py with the provided arguments

echo Running fix_linting_issues.py...

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found in PATH!
    exit /b 1
)

REM Check if the script exists
if not exist fix_linting_issues.py (
    echo Error: fix_linting_issues.py not found!
    exit /b 1
)

REM Run the script with all arguments passed to this batch file
python fix_linting_issues.py %*

REM Check exit code
if %ERRORLEVEL% neq 0 (
    echo Error: fix_linting_issues.py failed!
    exit /b 1
)

echo Script completed successfully.
exit /b 0
