# Create required directories
New-Item -ItemType Directory -Force -Path @(
    "tests/unit",
    "tests/e2e",
    "tests/mock-api",
    "tests/__mocks__",
    "ci-reports",
    "ci-artifacts",
    "ci-logs",
    "ci-temp",
    "ci-cache",
    "test-results/github",
    "logs"
)

# Set CI environment variables
$env:CI = "true"
$env:CI_ENVIRONMENT = "true"
$env:CI_TYPE = "github"
$env:GITHUB_ACTIONS = "true"
$env:CI_PLATFORM = "github"
$env:CI_OS = "Windows"
$env:CI_ARCH = "x64"
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
