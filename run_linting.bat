@echo off
echo Running linting checks...

python run_linting.py %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All linting checks passed!
) else (
    echo.
    echo Some linting checks failed. Please fix the issues and try again.
)

echo.
echo Done!
