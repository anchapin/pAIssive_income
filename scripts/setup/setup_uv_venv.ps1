# Setup UV virtual environment
$ErrorActionPreference = "Stop"

# Check if uv is available in the user's path
$uvPath = "C:\Users\ancha\.local\bin\uv.exe"
if (-not (Test-Path $uvPath)) {
    $uvPath = "C:\Users\ancha\AppData\Roaming\Python\Python313\Scripts\uv.exe"
}

if (-not (Test-Path $uvPath)) {
    Write-Error "ERROR: uv is not installed. Please install it first using 'pip install uv'"
    exit 1
}

# Create and activate virtual environment using uv
Write-Host "Creating virtual environment using uv..."
& $uvPath venv .venv

# Activate the virtual environment
. .\.venv\Scripts\Activate.ps1

# Install dependencies using uv
Write-Host "Installing dependencies..."
& $uvPath pip install -r requirements.txt
if (Test-Path requirements-dev.txt) {
    & $uvPath pip install -r requirements-dev.txt
}

Write-Host "Virtual environment setup complete. To activate it, run: .\.venv\Scripts\Activate.ps1"
