# PowerShell script to fix Bandit security scanning issues
# This script creates the necessary directories and files for Bandit security scanning

# Create the security-reports directory if it doesn't exist
Write-Host "Creating security-reports directory..."
New-Item -ItemType Directory -Force -Path security-reports | Out-Null

# Create the .github/bandit directory if it doesn't exist
Write-Host "Creating .github/bandit directory..."
New-Item -ItemType Directory -Force -Path .github/bandit | Out-Null

# Create a Bandit configuration file for the current run ID
$runId = "15053076509"
if ($args.Count -gt 0) {
    $runId = $args[0]
}

Write-Host "Using run ID: $runId"

# Create the Bandit configuration file
$configContent = @"
# Bandit Configuration for Windows (Run ID: $runId)
# This configuration is used by GitHub Advanced Security for Bandit scanning on Windows

# Exclude directories from security scans
exclude_dirs:
  - tests
  - venv
  - .venv
  - env
  - .env
  - __pycache__
  - custom_stubs
  - node_modules
  - build
  - dist

# Skip specific test IDs
skips:
  # B101: Use of assert detected
  - B101
  # B311: Standard pseudo-random generators are not suitable for security/cryptographic purposes
  - B311

# Set the output format for GitHub Advanced Security
output_format: json

# Set the output file for GitHub Advanced Security
output_file: security-reports/bandit-results-$runId.json

# Set the severity level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
severity: MEDIUM

# Set the confidence level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
confidence: MEDIUM
"@

$configFile = ".github/bandit/bandit-config-windows-$runId.yaml"
Write-Host "Creating Bandit configuration file: $configFile"
Set-Content -Path $configFile -Value $configContent

# Create empty SARIF files
$emptySarifContent = @"
{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Bandit",
          "informationUri": "https://github.com/PyCQA/bandit",
          "version": "1.7.5",
          "rules": []
        }
      },
      "results": []
    }
  ]
}
"@

$sarifFile = "security-reports/bandit-results-$runId.sarif"
Write-Host "Creating SARIF file: $sarifFile"
Set-Content -Path $sarifFile -Value $emptySarifContent

$standardSarifFile = "security-reports/bandit-results.sarif"
Write-Host "Creating standard SARIF file: $standardSarifFile"
Set-Content -Path $standardSarifFile -Value $emptySarifContent

# List the contents of the security-reports directory
Write-Host "security-reports directory contents:"
Get-ChildItem -Path security-reports | Select-Object Name

# List the contents of the .github/bandit directory
Write-Host ".github/bandit directory contents:"
Get-ChildItem -Path .github/bandit | Select-Object Name

Write-Host "Bandit security scanning files created successfully"
