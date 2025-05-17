@echo off
setlocal enabledelayedexpansion

echo Searching for Python installation...

:: Try to find Python in common installation locations
set PYTHON_FOUND=0
set PYTHON_EXE=

:: Check if Python is in PATH
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_FOUND=1
    for /f "tokens=*" %%i in ('where python') do (
        set PYTHON_EXE=%%i
        goto :found_python
    )
)

:: Check common installation locations
set PYTHON_LOCATIONS=^
C:\Python39\python.exe^
C:\Python310\python.exe^
C:\Python311\python.exe^
C:\Python312\python.exe^
C:\Program Files\Python39\python.exe^
C:\Program Files\Python310\python.exe^
C:\Program Files\Python311\python.exe^
C:\Program Files\Python312\python.exe^
C:\Program Files (x86)\Python39\python.exe^
C:\Program Files (x86)\Python310\python.exe^
C:\Program Files (x86)\Python311\python.exe^
C:\Program Files (x86)\Python312\python.exe^
%LOCALAPPDATA%\Programs\Python\Python39\python.exe^
%LOCALAPPDATA%\Programs\Python\Python310\python.exe^
%LOCALAPPDATA%\Programs\Python\Python311\python.exe^
%LOCALAPPDATA%\Programs\Python\Python312\python.exe

for %%p in (%PYTHON_LOCATIONS%) do (
    if exist "%%p" (
        set PYTHON_EXE=%%p
        set PYTHON_FOUND=1
        goto :found_python
    )
)

:: Check Windows Store Python installations
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    set PYTHON_EXE=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe
    set PYTHON_FOUND=1
    goto :found_python
)

:: Check Python Launcher registrations
for /f "tokens=*" %%i in ('py -0p') do (
    echo Found Python via launcher: %%i
    for /f "tokens=2 delims=:" %%j in ("%%i") do (
        set PYTHON_PATH=%%j
        set PYTHON_PATH=!PYTHON_PATH:~1!
        if exist "!PYTHON_PATH!\python.exe" (
            set PYTHON_EXE=!PYTHON_PATH!\python.exe
            set PYTHON_FOUND=1
            goto :found_python
        )
    )
)

:found_python
if %PYTHON_FOUND% EQU 0 (
    echo Python not found. Please install Python and try again.
    echo You can download Python from https://www.python.org/downloads/
    exit /b 1
)

echo Found Python at: %PYTHON_EXE%

:: Try to deactivate any active virtual environment
call deactivate 2>nul

:: Create a new virtual environment with a different name
echo Creating a new virtual environment with a temporary name...

:: First check if the old .venv directory exists and try to remove it
if exist .venv (
    echo Attempting to remove existing virtual environment...
    rd /s /q .venv 2>nul

    :: Check if removal was successful
    if exist .venv (
        echo Could not remove existing .venv directory.
        echo It might be in use by another process.
        echo Will create a new environment with a different name.
    ) else (
        echo Successfully removed old virtual environment.
    )
)

:: Determine the target directory name
set VENV_DIR=.venv
if exist .venv (
    set VENV_DIR=.venv_new
)

:: Create the virtual environment
echo Creating virtual environment in %VENV_DIR%...
"%PYTHON_EXE%" -m venv %VENV_DIR%
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment with venv.
    echo Trying with virtualenv...

    :: Try using virtualenv as a fallback
    "%PYTHON_EXE%" -m pip install virtualenv
    "%PYTHON_EXE%" -m virtualenv %VENV_DIR%
    if %ERRORLEVEL% NEQ 0 (
        echo All attempts to create a virtual environment failed.
        echo.
        echo Please try the following:
        echo 1. Ensure you have administrator privileges
        echo 2. Try creating the virtual environment manually
        exit /b 1
    )
)

:: Install uv and dependencies
echo Installing uv and dependencies...
call %VENV_DIR%\Scripts\activate
python -m pip install --upgrade uv
echo Using uv to install dependencies...
uv pip install -r requirements.txt
if exist requirements-dev.txt (
    uv pip install -r requirements-dev.txt
)
call deactivate

echo.
echo Virtual environment created successfully at %VENV_DIR%
echo.

:: If we created a new environment because we couldn't delete the old one
if "%VENV_DIR%" == ".venv_new" (
    echo Please follow these steps:
    echo 1. Close all applications that might be using the old .venv
    echo 2. Delete the old .venv directory manually
    echo 3. Rename .venv_new to .venv
    echo.
    echo Commands to run:
    echo    rd /s /q .venv
    echo    ren .venv_new .venv
    echo.
) else (
    echo Your virtual environment is ready to use.
)

echo To activate the virtual environment, run:
echo    %VENV_DIR%\Scripts\activate
echo.

endlocal
