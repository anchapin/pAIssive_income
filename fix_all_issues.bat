@echo off
echo ======== Starting Comprehensive Fix ========
python fix_all_issues_final.py %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All issues fixed successfully!
) else (
    echo.
    echo Some files could not be fixed automatically. Please check the output above.
)

echo.
echo ======== Running Linting Checks ========
python run_linting.py

echo.
echo ======== Attempting to run tests ========
python run_tests.py --verbose

echo.
echo Done!
