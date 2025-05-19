# Run pytest with the specified arguments

# Create security-reports directory
New-Item -ItemType Directory -Force -Path security-reports | Out-Null
Write-Host "Created security-reports directory"

# Set environment variables to bypass virtual environment checks
$env:PYTHONNOUSERSITE = "1"
$env:SKIP_VENV_CHECK = "1"

# Set CI environment variable if running in GitHub Actions
if ($env:GITHUB_ACTIONS) {
    $env:CI = "1"
    Write-Host "GitHub Actions environment detected"
}

# Run pytest with the specified arguments
try {
    python -m pytest $args
    exit $LASTEXITCODE
} catch {
    Write-Host "Error running pytest: $_"
    exit 1
}
