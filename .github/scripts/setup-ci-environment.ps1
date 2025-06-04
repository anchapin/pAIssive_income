# Create necessary directories
New-Item -ItemType Directory -Force -Path ci-reports, ci-artifacts, ci-logs, ci-temp, ci-cache
New-Item -ItemType Directory -Force -Path test-results/github
New-Item -ItemType Directory -Force -Path logs
New-Item -ItemType Directory -Force -Path coverage

# Set environment variables
$env:CI = "true"
$env:CI_ENVIRONMENT = "true"
$env:CI_TYPE = "github"
$env:GITHUB_ACTIONS = "true"
$env:CI_PLATFORM = "github"
$env:CI_OS = [System.Environment]::OSVersion.Platform
$env:CI_ARCH = [System.Environment]::GetEnvironmentVariable("PROCESSOR_ARCHITECTURE")
$env:CI_PYTHON_VERSION = (python --version).Split(" ")[1]
$env:CI_NODE_VERSION = (node --version).Substring(1)
$env:CI_RUNNER_OS = $env:RUNNER_OS
$env:CI_WORKSPACE = $env:GITHUB_WORKSPACE
$env:FLASK_ENV = "development"
$env:DATABASE_URL = "sqlite:///:memory:"
$env:TESTING = "true"
$env:REACT_APP_API_BASE_URL = "http://localhost:3001"
$env:MOCK_API_PORT = "3001"
$env:MOCK_API_TIMEOUT = "5000"
$env:VITEST_TIMEOUT = "10000"
$env:E2E_TIMEOUT = "30000"

# Create dummy test files if they don't exist
New-Item -ItemType File -Force -Path test-results/junit.xml
New-Item -ItemType File -Force -Path coverage/coverage.xml
New-Item -ItemType File -Force -Path ci-reports/test-report.json
New-Item -ItemType File -Force -Path ci-logs/test.log

# Set permissions (Windows equivalent)
$acl = Get-Acl "ci-reports"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone","FullControl","ContainerInherit,ObjectInherit","None","Allow")
$acl.SetAccessRule($accessRule)
Set-Acl "ci-reports" $acl

# Apply same permissions to other directories
Get-ChildItem -Directory | ForEach-Object {
    $acl = Get-Acl $_.FullName
    $acl.SetAccessRule($accessRule)
    Set-Acl $_.FullName $acl
}

# Generate environment report
$report = @"
=== CI Environment Report ===
Date: $(Get-Date)
OS: $([System.Environment]::OSVersion)
Python: $(python --version)
Node: $(node --version)
npm: $(npm --version)
pnpm: $(pnpm --version)
Runner OS: $env:RUNNER_OS
Workspace: $env:GITHUB_WORKSPACE
Event: $env:GITHUB_EVENT_NAME
Repository: $env:GITHUB_REPOSITORY
Ref: $env:GITHUB_REF
SHA: $env:GITHUB_SHA
==========================
"@

$report | Out-File -FilePath "ci-reports/environment-report.txt" -Encoding UTF8

# Display environment report
Get-Content "ci-reports/environment-report.txt"
