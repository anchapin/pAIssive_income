@echo off
echo Running pre-commit hooks on all files...

pre-commit run --all-files

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All pre-commit hooks passed successfully!
) else (
    echo.
    echo Some pre-commit hooks failed. Please fix the issues and try again.
)

echo.
pause
