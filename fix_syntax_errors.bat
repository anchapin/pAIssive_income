@echo off
echo Running syntax error fixes...

python fix_syntax_errors.py %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All syntax errors fixed successfully!
) else (
    echo.
    echo Some files could not be fixed automatically. Please check the output above.
)

echo.
echo Done!
