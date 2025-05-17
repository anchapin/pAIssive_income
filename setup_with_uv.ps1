# Install uv if not already installed
$ErrorActionPreference = "Stop"

Write-Host "Checking for uv installation..."
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..."
    try {
        Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -OutFile install-uv.ps1
        .\install-uv.ps1
        Remove-Item install-uv.ps1
    }
    catch {
        Write-Host "Failed to install uv. Falling back to traditional venv and pip..."
        python -m pip install --upgrade pip
        python -m venv .venv
        .\.venv\Scripts\Activate.ps1
        python -m pip install -r requirements-dev.txt
        exit 1
    }
}

# Create virtual environment with uv
Write-Host "Creating virtual environment with uv..."
uv venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create virtual environment with uv. Falling back to Python's venv module..."
    python -m venv .venv
}

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies with uv
Write-Host "Installing dependencies with uv..."
if (Test-Path "requirements-dev.txt") {
    uv pip install -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies with uv pip. Falling back to regular pip..."
        python -m pip install -r requirements-dev.txt
    }
}
if (Test-Path "requirements.txt") {
    uv pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies with uv pip. Falling back to regular pip..."
        python -m pip install -r requirements.txt
    }
}

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..."
npm install -g pnpm
pnpm install --reporter=default
