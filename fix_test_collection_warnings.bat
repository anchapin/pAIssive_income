@echo off
echo ======== Starting Syntax Error Fix ========
python fix_test_collection_warnings.py

echo ======== Running Linting Checks ========
python run_linting.py

echo ======== Attempting to run tests ========
python run_tests.py --verbose

echo.
echo If tests still fail, you may need to run fix_test_collection_warnings.py again to fix more errors