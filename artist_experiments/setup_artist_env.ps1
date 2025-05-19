# Setup script for ARTIST experiment environment
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

# Install uv if not already installed
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
        python -m venv artist_experiments/.venv-artist
        .\artist_experiments\.venv-artist\Scripts\Activate.ps1
        python -m pip install -r artist_experiments/requirements-artist.txt
        exit 1
    }
}

# Create virtual environment with uv
Write-Host "Creating ARTIST virtual environment with uv..."
uv venv artist_experiments/.venv-artist
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create virtual environment with uv. Falling back to Python's venv module..."
    python -m venv artist_experiments/.venv-artist
}

# Activate virtual environment
.\artist_experiments\.venv-artist\Scripts\Activate.ps1

# Install dependencies with uv
Write-Host "Installing ARTIST dependencies with uv..."
if (Test-Path "artist_experiments/requirements-artist.txt") {
    uv pip install -r artist_experiments/requirements-artist.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies with uv pip. Falling back to regular pip..."
        python -m pip install -r artist_experiments/requirements-artist.txt
    }
}

Write-Host "ARTIST environment setup complete!"
Write-Host "To activate the ARTIST environment, run: .\artist_experiments\.venv-artist\Scripts\Activate.ps1"
