@echo off
REM Enhanced Setup Development Environment Script for Windows
REM This script runs enhanced_setup_dev_environment.py to set up the development environment

echo Setting up development environment...

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    exit /b 1
)

REM Check Python version
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python 3.8 or higher is required.
    echo Current Python version:
    python --version
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Node.js is not installed or not in PATH.
    echo Please install Node.js 18 or higher from https://nodejs.org/
    exit /b 1
)

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: npm is not installed or not in PATH.
    echo Please ensure npm is installed with Node.js.
    exit /b 1
)

REM Check Node.js version
node -v | find "v18." >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Node.js 18.x is required.
    echo Current Node.js version:
    node -v
    exit /b 1
)

REM Check npm version
npm -v | find "8." >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: npm 8.x is required.
    echo Current npm version:
    npm -v
    exit /b 1
)

REM Parse command-line arguments
set ARGS=

:parse_args
if "%~1"=="" goto run_script
set ARGS=%ARGS% %1
shift
goto parse_args

:run_script
REM Run the setup script
python enhanced_setup_dev_environment.py %ARGS%

if %ERRORLEVEL% neq 0 (
    echo Error: Failed to set up development environment.
    exit /b 1
)

REM Create IDE configuration files
echo Creating .editorconfig file...
echo # EditorConfig helps maintain consistent coding styles across different editors > .editorconfig
echo # https://editorconfig.org/ >> .editorconfig
echo. >> .editorconfig
echo root = true >> .editorconfig
echo. >> .editorconfig
echo [*] >> .editorconfig
echo end_of_line = lf >> .editorconfig
echo insert_final_newline = true >> .editorconfig
echo trim_trailing_whitespace = true >> .editorconfig
echo charset = utf-8 >> .editorconfig
echo. >> .editorconfig
echo [*.{py,pyi}] >> .editorconfig
echo indent_style = space >> .editorconfig
echo indent_size = 4 >> .editorconfig
echo max_line_length = 88 >> .editorconfig
echo. >> .editorconfig
echo [*.{json,yml,yaml,toml}] >> .editorconfig
echo indent_style = space >> .editorconfig
echo indent_size = 2 >> .editorconfig
echo. >> .editorconfig
echo [*.md] >> .editorconfig
echo trim_trailing_whitespace = false >> .editorconfig
echo. >> .editorconfig
echo [Makefile] >> .editorconfig
echo indent_style = tab >> .editorconfig

echo Creating .vscode directory and settings.json...
if not exist .vscode mkdir .vscode
echo { > .vscode\settings.json
echo     "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python", >> .vscode\settings.json
echo     "python.formatting.provider": "none", >> .vscode\settings.json
echo     "editor.formatOnSave": true, >> .vscode\settings.json
echo     "editor.codeActionsOnSave": { >> .vscode\settings.json
echo         "source.fixAll": true, >> .vscode\settings.json
echo         "source.organizeImports": true >> .vscode\settings.json
echo     }, >> .vscode\settings.json
echo     "[python]": { >> .vscode\settings.json
echo         "editor.defaultFormatter": "charliermarsh.ruff", >> .vscode\settings.json
echo         "editor.formatOnSave": true, >> .vscode\settings.json
echo         "editor.codeActionsOnSave": { >> .vscode\settings.json
echo             "source.fixAll": true, >> .vscode\settings.
