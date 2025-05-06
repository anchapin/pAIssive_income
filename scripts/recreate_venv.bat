@echo off
echo Recreating virtual environment...

: Run the Python script
python scripts\recreate_venv.py %*

: Return the exit code from the Python script
exit /b %ERRORLEVEL%
