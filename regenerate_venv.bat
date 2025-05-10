@echo off
echo Regenerating virtual environment...

:: First, try to deactivate any active virtual environment
call deactivate 2>nul

:: Check if .venv directory exists
if exist .venv (
    echo Attempting to remove existing virtual environment...

    :: Try to remove the directory using rd command
    rd /s /q .venv 2>nul

    :: Check if the directory still exists
    if exist .venv (
        echo Could not remove .venv directory. It might be in use by another process.
        echo Trying alternative approach...

        :: Try using the Python script
        python regenerate_venv.py
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to regenerate virtual environment.
            echo.
            echo Please try the following steps:
            echo 1. Close all terminals, IDEs, and applications that might be using the virtual environment
            echo 2. Run this script again
            echo.
            exit /b 1
        )
    ) else (
        :: Directory was successfully removed, create a new one
        echo Creating new virtual environment...

        :: Check if Python is available
        where python >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            echo Python executable not found in PATH.
            echo Please ensure Python is installed and added to your PATH.
            exit /b 1
        )

        :: Check if venv module is available
        python -c "import venv" >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            echo Python venv module not available.
            echo Trying to install it...
            python -m pip install virtualenv

            :: Try using virtualenv instead
            echo Creating virtual environment using virtualenv...
            python -m virtualenv .venv
            if %ERRORLEVEL% NEQ 0 (
                echo Failed to create virtual environment with virtualenv.
                echo.
                echo Please try the following:
                echo 1. Ensure Python is properly installed
                echo 2. Run: python -m pip install --user virtualenv
                echo 3. Run this script again
                exit /b 1
            )
        ) else (
            :: Try creating the virtual environment with verbose output
            echo Creating virtual environment with verbose output...
            python -m venv .venv --verbose
            if %ERRORLEVEL% NEQ 0 (
                echo Failed to create virtual environment with venv.

                :: Try using virtualenv as a fallback
                echo Trying virtualenv as a fallback...
                python -m pip install virtualenv
                python -m virtualenv .venv
                if %ERRORLEVEL% NEQ 0 (
                    echo All attempts to create a virtual environment failed.
                    echo.
                    echo Please try the following:
                    echo 1. Ensure you have administrator privileges
                    echo 2. Try creating the virtual environment manually:
                    echo    python -m venv .venv_manual
                    echo 3. If successful, rename .venv_manual to .venv
                    exit /b 1
                )
            )
        )

        :: Install dependencies
        echo Installing dependencies...
        call .venv\Scripts\activate
        python -m pip install --upgrade uv
        python -m uv pip install -r requirements.txt
        if exist requirements-dev.txt (
            python -m uv pip install -r requirements-dev.txt
        )
        call deactivate
    )
) else (
    :: No existing virtual environment, create a new one
    echo Creating new virtual environment...

    :: Check if Python is available
    where python >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Python executable not found in PATH.
        echo Please ensure Python is installed and added to your PATH.
        exit /b 1
    )

    :: Check if venv module is available
    python -c "import venv" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Python venv module not available.
        echo Trying to install it...
        python -m pip install virtualenv

        :: Try using virtualenv instead
        echo Creating virtual environment using virtualenv...
        python -m virtualenv .venv
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to create virtual environment with virtualenv.
            echo.
            echo Please try the following:
            echo 1. Ensure Python is properly installed
            echo 2. Run: python -m pip install --user virtualenv
            echo 3. Run this script again
            exit /b 1
        )
    ) else (
        :: Try creating the virtual environment with verbose output
        echo Creating virtual environment with verbose output...
        python -m venv .venv --verbose
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to create virtual environment with venv.

            :: Try using virtualenv as a fallback
            echo Trying virtualenv as a fallback...
            python -m pip install virtualenv
            python -m virtualenv .venv
            if %ERRORLEVEL% NEQ 0 (
                echo All attempts to create a virtual environment failed.
                echo.
                echo Please try the following:
                echo 1. Ensure you have administrator privileges
                echo 2. Try creating the virtual environment manually:
                echo    python -m venv .venv_manual
                echo 3. If successful, rename .venv_manual to .venv
                exit /b 1
            )
        )
    )

    :: Install dependencies
    echo Installing dependencies...
    call .venv\Scripts\activate
    python -m pip install --upgrade uv
    python -m uv pip install -r requirements.txt
    if exist requirements-dev.txt (
        python -m uv pip install -r requirements-dev.txt
    )
    call deactivate
)

echo.
echo Virtual environment regenerated successfully!
echo.
echo To activate the virtual environment, run:
echo     .venv\Scripts\activate
echo.
