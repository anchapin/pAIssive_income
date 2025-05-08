@echo off
REM Batch file to run find_syntax_errors.py with the provided arguments

echo Running find_syntax_errors.py...

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found in PATH!
    exit /b 1
)

REM Check if the script exists
if not exist find_syntax_errors.py (
    echo Error: find_syntax_errors.py not found!
    exit /b 1
)

REM Run the script with all arguments passed to this batch file
python find_syntax_errors.py %*

REM Check exit code
if %ERRORLEVEL% neq 0 (
    echo Syntax errors found! See above for details.
    exit /b 1
)

echo No syntax errors found.
exit /b 0
