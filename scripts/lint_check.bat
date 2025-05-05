@echo off
echo Running linting checks...

:: Activate the virtual environment
call .venv\Scripts\activate.bat

:: Run the linting checks
python scripts\lint_check.py %*

:: Return the exit code from the Python script
exit /b %ERRORLEVEL%
