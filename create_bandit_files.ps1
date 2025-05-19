# Create Bandit configuration files for GitHub Actions workflows

# Create directories
New-Item -Path ".github/bandit" -ItemType Directory -Force | Out-Null
New-Item -Path "security-reports" -ItemType Directory -Force | Out-Null

Write-Host "Created directories: .github/bandit, security-reports"

# Create template file
$templateContent = @"
# Bandit Configuration Template
# This configuration is used by GitHub Advanced Security for Bandit scanning

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
  - docs
  - docs_source
  - junit
  - bin
  - dev_tools
  - scripts
  - tool_templates

# Skip specific test IDs
skips:
  # B101: Use of assert detected
  - B101
  # B311: Standard pseudo-random generators are not suitable for security/cryptographic purposes
  - B311

# Set the output format for GitHub Advanced Security
output_format: sarif

# Output file for GitHub Advanced Security
output_file: security-reports/bandit-results.sarif

# Set the severity level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
severity: MEDIUM

# Set the confidence level for GitHub Advanced Security
# Options: LOW, MEDIUM, HIGH
confidence: MEDIUM

# Simplified shell configuration
shell_injection:
  no_shell: []
  shell: []
"@

Set-Content -Path ".github/bandit/bandit-config-template.yaml" -Value $templateContent
Write-Host "Created template file: .github/bandit/bandit-config-template.yaml"

# Create platform-specific files
$platforms = @("windows", "linux", "macos")
foreach ($platform in $platforms) {
    # Regular config
    Copy-Item -Path ".github/bandit/bandit-config-template.yaml" -Destination ".github/bandit/bandit-config-$platform.yaml"
    Write-Host "Created configuration file: .github/bandit/bandit-config-$platform.yaml"

    # Test run ID config
    Copy-Item -Path ".github/bandit/bandit-config-template.yaml" -Destination ".github/bandit/bandit-config-$platform-test_run_id.yaml"
    Write-Host "Created test run ID configuration file: .github/bandit/bandit-config-$platform-test_run_id.yaml"
}

# Create empty SARIF file
$sarifContent = @"
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

Set-Content -Path "empty-sarif.json" -Value $sarifContent
Write-Host "Created empty SARIF file: empty-sarif.json"
Write-Host "Successfully created all Bandit configuration files"
