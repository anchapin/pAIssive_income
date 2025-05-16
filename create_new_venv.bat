@echo off
echo Creating a new virtual environment...

:: Try to deactivate any active virtual environment
call deactivate 2>nul

:: Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python executable not found in PATH.
    echo Please ensure Python is installed and added to your PATH.
    exit /b 1
)

:: Create a new virtual environment with a different name
echo Creating a new virtual environment with a temporary name...
python -m venv .venv_new
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment with venv.
    echo Trying with virtualenv...

    :: Try using virtualenv as a fallback    python -m pip install uv
    python -m uv pip install virtualenv
    python -m virtualenv .venv_new
    if %ERRORLEVEL% NEQ 0 (
        echo All attempts to create a virtual environment failed.
        echo.
        echo Please try the following:
        echo 1. Ensure you have administrator privileges
        echo 2. Try creating the virtual environment manually:
        echo    python -m venv .venv_manual
        exit /b 1
    )
)

:: Install dependencies
echo Installing dependencies...
call .venv_new\Scripts\activate
python -m pip install --upgrade uv
python -m uv pip install -r requirements.txt
if exist requirements-dev.txt (
    python -m uv pip install -r requirements-dev.txt
)
call deactivate

echo.
echo New virtual environment created successfully at .venv_new
echo.
echo Please follow these steps:
echo 1. Close all applications that might be using the old .venv
echo 2. Delete the old .venv directory manually (if it exists)
echo 3. Rename .venv_new to .venv
echo.
echo Commands to run:
echo    rd /s /q .venv
echo    ren .venv_new .venv
echo.
echo Then activate the new environment with:
echo    .venv\Scripts\activate
echo.
