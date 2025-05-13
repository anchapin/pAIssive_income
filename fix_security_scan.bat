@echo off
REM Script to fix security scan issues
REM Usage: fix_security_scan.bat [scan_results_file]

echo ===== Security Scan Fix Script for Windows =====

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python first.
    exit /b 1
)

REM Check if the virtual environment exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment.
        exit /b 1
    )
)

REM Activate the virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM Install required packages
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install pylint pylint-security

echo Running security scan fix script...

if "%1"=="" (
    echo No scan results file provided, running with default options
    python fix_security_scan_issues.py --update-config --add-comments --verbose
) else (
    echo Using scan results from %1
    python fix_security_scan_issues.py --scan-results "%1" --update-config --add-comments --verbose
)

REM Run Pylint security scan with the correct plugin
echo Running Pylint security scan...
pylint --disable=all --load-plugins=pylint_security --enable=security .

echo.
echo Done!
echo.
echo Next steps:
echo 1. Review the changes made to the files
echo 2. Review the updated .gitleaks.toml file
echo 3. Run the security scan again to verify the issues are fixed
echo.

REM Deactivate the virtual environment
call .venv\Scripts\deactivate.bat
