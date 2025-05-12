@echo off
REM Batch file to run the fix_pre_commit_issues.py script

echo Running fix_pre_commit_issues.py...

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found in PATH!
    exit /b 1
)

REM Check if the script exists
if not exist fix_pre_commit_issues.py (
    echo Error: fix_pre_commit_issues.py not found!
    exit /b 1
)

REM Run the script with verbose output
python fix_pre_commit_issues.py --verbose %*

REM Check exit code
if %ERRORLEVEL% neq 0 (
    echo Error: fix_pre_commit_issues.py failed!
    exit /b 1
)

echo Pre-commit issues fixed successfully.
exit /b 0
