#!/usr/bin/env pwsh
# PowerShell script to ensure fixed CodeQL workflow files are used
# This script validates and fixes CodeQL workflow configurations

param(
    [switch]$Verbose = $false
)

# Set error action preference
$ErrorActionPreference = "Continue"

Write-Host "=== Ensuring Fixed CodeQL Workflow Files ==="

# Function to write verbose output
function Write-VerboseOutput {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "[VERBOSE] $Message" -ForegroundColor Cyan
    }
}

# Check if CodeQL configuration directory exists
$codeqlConfigDir = ".github/codeql"
if (-not (Test-Path $codeqlConfigDir)) {
    Write-Host "Creating CodeQL configuration directory: $codeqlConfigDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $codeqlConfigDir -Force | Out-Null
}

# Check if security-os-config.yml exists
$securityConfigFile = "$codeqlConfigDir/security-os-config.yml"
if (-not (Test-Path $securityConfigFile)) {
    Write-Host "Creating missing security-os-config.yml" -ForegroundColor Yellow
    
    $configContent = @"
name: "Security and Quality Analysis"
disable-default-queries: false
queries:
  - uses: security-and-quality
  - uses: security-extended
paths-ignore:
  - "**/*.md"
  - "**/*.txt"
  - "**/*.rst"
  - "**/docs/**"
  - "**/test/**"
  - "**/tests/**"
  - "**/__pycache__/**"
  - "**/node_modules/**"
  - "**/.git/**"
  - "**/.github/workflows/archive/**"
"@
    
    Set-Content -Path $securityConfigFile -Value $configContent -Encoding UTF8
    Write-Host "Created $securityConfigFile" -ForegroundColor Green
}

# Validate CodeQL workflow files
$workflowFiles = @(
    ".github/workflows/codeql-windows.yml",
    ".github/workflows/codeql-ubuntu.yml", 
    ".github/workflows/codeql-macos.yml",
    ".github/workflows/codeql.yml"
)

foreach ($workflowFile in $workflowFiles) {
    if (Test-Path $workflowFile) {
        Write-VerboseOutput "Validating $workflowFile"
        
        # Check if the workflow file references the correct config
        $content = Get-Content $workflowFile -Raw
        if ($content -match "security-os-config\.yml") {
            Write-VerboseOutput "$workflowFile references correct config file"
        } else {
            Write-Host "WARNING: $workflowFile may not reference the correct config file" -ForegroundColor Yellow
        }
    } else {
        Write-VerboseOutput "$workflowFile not found (may be expected)"
    }
}

# Check for SARIF results directory
$sarifDir = "sarif-results"
if (-not (Test-Path $sarifDir)) {
    Write-Host "Creating SARIF results directory: $sarifDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $sarifDir -Force | Out-Null
}

# Validate that required CodeQL queries exist
$queryFiles = @(
    "$codeqlConfigDir/javascript-security-queries.qls",
    "$codeqlConfigDir/python-security-queries.qls"
)

foreach ($queryFile in $queryFiles) {
    if (-not (Test-Path $queryFile)) {
        Write-Host "Creating missing query file: $queryFile" -ForegroundColor Yellow
        
        $language = if ($queryFile -match "javascript") { "javascript" } else { "python" }
        $queryContent = @"
- description: Security and quality queries for $language
- queries: .
- from: codeql/$language-queries
"@
        Set-Content -Path $queryFile -Value $queryContent -Encoding UTF8
        Write-Host "Created $queryFile" -ForegroundColor Green
    }
}

Write-Host "=== CodeQL Workflow Files Check Complete ===" -ForegroundColor Green

# Return success
exit 0
