@echo off
setlocal enabledelayedexpansion

REM Check if uv is available in the user's path
set UV_PATH=C:\Users\ancha\.local\bin\uv.exe
if not exist "%UV_PATH%" (
    set UV_PATH=C:\Users\ancha\AppData\Roaming\Python\Python313\Scripts\uv.exe
)

if not exist "%UV_PATH%" (
    echo ERROR: uv is not installed. Please install it first using 'pip install uv'
    exit /b 1
)

REM Create and activate virtual environment using uv
echo Creating virtual environment using uv...
"%UV_PATH%" venv .venv

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies using uv
echo Installing dependencies...
"%UV_PATH%" pip install -r requirements.txt
if exist requirements-dev.txt (
    "%UV_PATH%" pip install -r requirements-dev.txt
)

echo Virtual environment setup complete. To activate it, run: .venv\Scripts\activate.bat
endlocal
