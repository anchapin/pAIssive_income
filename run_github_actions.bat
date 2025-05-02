@echo off
echo Running GitHub Actions locally...

REM Fix failing tests
python fix_failing_tests.py

REM Run tests
python run_local_tests.py --test-path tests/ai_models --verbose

REM Run GitHub Actions locally using Act
echo.
echo Running GitHub Actions with Act...
echo.
echo Running test workflow...
act -j test -W .github/workflows/act-local-test.yml

echo.
echo Running lint workflow...
act -j lint -W .github/workflows/act-local-test.yml

echo.
echo Done!
