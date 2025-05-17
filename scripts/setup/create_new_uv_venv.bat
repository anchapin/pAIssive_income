@echo off
echo Creating a new virtual environment using uv...

:: Try to deactivate any active virtual environment
call deactivate 2>nul

:: Check if uv is available
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo uv executable not found in PATH.
    echo Please install uv using: pip install uv
    exit /b 1
)

:: Create a new virtual environment with uv
echo Creating a new virtual environment...
uv venv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment with uv.
    exit /b 1
)

:: Activate the virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)

:: Install dependencies using uv
echo Installing dependencies with uv...
if exist requirements.txt (
    uv pip install -r requirements.txt
)
if exist requirements-dev.txt (
    uv pip install -r requirements-dev.txt
)

echo Virtual environment created and activated successfully!
echo Dependencies installed using uv.
