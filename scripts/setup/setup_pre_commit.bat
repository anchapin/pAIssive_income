@echo off
echo Setting up pre-commit hooks...

python setup_pre_commit.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Pre-commit hooks setup completed successfully!
) else (
    echo.
    echo Failed to set up pre-commit hooks. Please check the error messages above.
)

echo.
pause
