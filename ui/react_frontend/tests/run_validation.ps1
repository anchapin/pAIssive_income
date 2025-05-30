# PowerShell script to run validation of mock implementations

# Set CI environment variable
$env:CI = "true"

# Create log directory if it doesn't exist
if (-not (Test-Path -Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Create report directory if it doesn't exist
if (-not (Test-Path -Path "test-results")) {
    New-Item -ItemType Directory -Path "test-results" | Out-Null
}

# Log file
$LOG_FILE = "logs\run-validation.log"
"Starting validation at $(Get-Date)" | Out-File -FilePath $LOG_FILE

# Run the validation script
Write-Host "Running validation script..."
node tests/validate_mock_implementations.js

# Store the exit code
$EXIT_CODE = $LASTEXITCODE

# Log the result
if ($EXIT_CODE -eq 0) {
    "Validation successful" | Tee-Object -FilePath $LOG_FILE -Append
} else {
    "Validation failed with exit code $EXIT_CODE" | Tee-Object -FilePath $LOG_FILE -Append
}

# Create a marker file to indicate validation was run
"Validation run at $(Get-Date)" | Out-File -FilePath "test-results\validation-run.txt"
"Exit code: $EXIT_CODE" | Out-File -FilePath "test-results\validation-run.txt" -Append

# Exit with the validation exit code
exit $EXIT_CODE
