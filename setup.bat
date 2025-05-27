@echo off
REM Main setup script for pAIssive Income (Windows)

echo Starting pAIssive Income development environment setup...

REM 1. Run the enhanced Python environment setup script
echo ----------------------------------------------------
echo STEP 1: Setting up Python environment and dependencies...
echo ----------------------------------------------------
if exist "scripts\setup\enhanced_setup_dev_environment.py" (
    python scripts\setup\enhanced_setup_dev_environment.py --full
) else (
    echo ERROR: scripts\setup\enhanced_setup_dev_environment.py not found!
    exit /b 1
)
echo Python environment setup complete.
echo.

REM 2. Install Node.js dependencies using pnpm
echo ----------------------------------------------------
echo STEP 2: Installing Node.js dependencies...
echo ----------------------------------------------------
where pnpm >nul 2>nul
if %ERRORLEVEL% == 0 (
    pnpm install
    echo Node.js dependencies installed via pnpm.
) else (
    echo WARNING: pnpm command not found. Skipping Node.js dependency installation.
    echo Please install pnpm (https://pnpm.io/installation) and then run 'pnpm install' manually in the project root.
)
echo.

REM 3. Setup .env file
echo ----------------------------------------------------
echo STEP 3: Setting up .env file...
echo ----------------------------------------------------
if exist ".env.example" (
    if exist ".env" (
        echo .env file already exists. Skipping creation.
    ) else (
        copy .env.example .env
        echo .env file created from .env.example.
        echo IMPORTANT: Please review and update .env with your specific configurations.
    )
) else (
    echo WARNING: .env.example not found. Cannot create .env file.
)
echo.

REM 4. Database Initialization Reminder
echo ----------------------------------------------------
echo STEP 4: Database Initialization (Manual Step)
echo ----------------------------------------------------
echo If this is your first time setting up or you need a fresh database, run:
echo   python init_db.py
echo Ensure your .env file is configured correctly before running this.
echo.

REM 5. Final Instructions
echo ----------------------------------------------------
echo Setup Complete! Next Steps:
echo ----------------------------------------------------
echo 1. Activate the Python virtual environment:
echo    .venv\Scripts\activate
echo.
echo 2. Configure your .env file with necessary API keys and settings.
echo.
echo 3. Initialize the database (if you haven't already):
echo    python init_db.py
echo.
echo 4. To run the application or tests, please refer to the project documentation.
echo.
echo For the jules.google.com setup, the command to run this script is:
echo   setup.bat
echo ----------------------------------------------------

exit /b 0
