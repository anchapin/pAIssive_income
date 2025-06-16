# Setup script for ARTIST experiment environment using only 'uv'
$ErrorActionPreference = "Stop"

# Create necessary directories
Write-Host "Creating ARTIST experiment directories..."
if (-not (Test-Path "artist_experiments/data")) {
    New-Item -Path "artist_experiments/data" -ItemType Directory -Force | Out-Null
}
if (-not (Test-Path "artist_experiments/logs")) {
    New-Item -Path "artist_experiments/logs" -ItemType Directory -Force | Out-Null
}
if (-not (Test-Path "artist_experiments/models")) {
    New-Item -Path "artist_experiments/models" -ItemType Directory -Force | Out-Null
}

# Ensure uv is installed
Write-Host "Checking for uv installation..."
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..."
    try {
        Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -OutFile install-uv.ps1
        .\install-uv.ps1
        Remove-Item install-uv.ps1
    }
    catch {
        Write-Host "ERROR: Failed to install 'uv'. Please install 'uv' manually and re-run this script."
        exit 1
    }
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: 'uv' still not found after install attempt. Please install 'uv' manually and re-run this script."
        exit 1
    }
}

# Create virtual environment with uv (no fallback)
Write-Host "Creating ARTIST virtual environment with uv..."
uv venv artist_experiments/.venv-artist
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment with 'uv'."
    exit 1
}

# Activate virtual environment
.\artist_experiments\.venv-artist\Scripts\Activate.ps1

# Install dependencies with uv pip (no fallback)
Write-Host "Installing ARTIST dependencies with uv pip..."
if (Test-Path "artist_experiments/requirements-artist.txt") {
    uv pip install -r artist_experiments/requirements-artist.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies from requirements-artist.txt with 'uv'."
        exit 1
    }
}

Write-Host "ARTIST environment setup complete!"
Write-Host "To activate the ARTIST environment, run: .\artist_experiments\.venv-artist\Scripts\Activate.ps1"
