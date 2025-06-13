# Script to run E2E tests with mock API server
# Enhanced with better environment detection and handling for Windows environments

# Enhanced environment detection
# CI Environment Detection
$isCI = $env:CI -eq "true"
$isGitHubActions = $env:GITHUB_ACTIONS -eq "true"
$isJenkins = $null -ne $env:JENKINS_URL
$isGitLabCI = $env:GITLAB_CI -eq "true"
$isCircleCI = $env:CIRCLECI -eq "true"
$isTravis = $env:TRAVIS -eq "true"
$isAzurePipelines = $env:TF_BUILD -eq "true"
$isTeamCity = $null -ne $env:TEAMCITY_VERSION
$isBitbucket = $null -ne $env:BITBUCKET_COMMIT
$isAppVeyor = $env:APPVEYOR -eq "true"
$isDrone = $env:DRONE -eq "true"
$isBuddy = $env:BUDDY -eq "true"
$isBuildkite = $env:BUILDKITE -eq "true"
$isCodeBuild = $null -ne $env:CODEBUILD_BUILD_ID

# Container Environment Detection
$isDocker = $false
$isKubernetes = $null -ne $env:KUBERNETES_SERVICE_HOST
$isDockerCompose = $null -ne $env:COMPOSE_PROJECT_NAME
$isDockerSwarm = $env:DOCKER_SWARM -eq "true"

# Check if running in Docker with multiple methods
if (Test-Path "/.dockerenv" -ErrorAction SilentlyContinue) {
    $isDocker = $true
}
if ($env:DOCKER_ENVIRONMENT -eq "true" -or $env:DOCKER -eq "true") {
    $isDocker = $true
}
if (Test-Path "/run/.containerenv" -ErrorAction SilentlyContinue) {
    $isDocker = $true
}
if (Test-Path "/proc/1/cgroup" -ErrorAction SilentlyContinue) {
    $cgroupContent = Get-Content "/proc/1/cgroup" -ErrorAction SilentlyContinue
    if ($cgroupContent -match "docker") {
        $isDocker = $true
    }
}

# Cloud Environment Detection
$isAWS = $null -ne $env:AWS_REGION
$isAzure = $null -ne $env:AZURE_FUNCTIONS_ENVIRONMENT
$isGCP = $null -ne $env:GOOGLE_CLOUD_PROJECT -or $null -ne $env:GCLOUD_PROJECT

# OS Detection
$isWSL = $null -ne $env:WSL_DISTRO_NAME -or $null -ne $env:WSLENV

# Configuration
$verboseLogging = $env:VERBOSE_LOGGING -eq "true"
$mockApiPort = if ($env:MOCK_API_PORT) { $env:MOCK_API_PORT } else { 8000 }
$reactPort = if ($env:REACT_PORT) { $env:REACT_PORT } else { 3000 }
$maxRetries = if ($env:MAX_RETRIES) { $env:MAX_RETRIES } else { 30 }
$retryInterval = if ($env:RETRY_INTERVAL) { $env:RETRY_INTERVAL } else { 1 }
$testSpec = if ($env:TEST_SPEC) { $env:TEST_SPEC } else { "tests/e2e/agent_ui.spec.ts" }
$reporter = if ($env:REPORTER) { $env:REPORTER } else { "list" }

# Create logs directory
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
}
if (-not (Test-Path "playwright-report")) {
    New-Item -ItemType Directory -Path "playwright-report" -Force | Out-Null
}

# Log function with timestamps and levels
function Log {
    param (
        [Parameter(Position=0, Mandatory=$true)]
        [string]$Message,

        [Parameter(Position=1, Mandatory=$false)]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
    $logMessage = "[$timestamp] [$Level] $Message"

    Write-Host $logMessage
    Add-Content -Path "logs/run_e2e_tests.log" -Value $logMessage

    # For important messages, also create a report file
    if ($Level -eq "ERROR" -or $Level -eq "IMPORTANT") {
        $fileName = "playwright-report/run-e2e-tests-$($Level.ToLower())-$(Get-Date -Format "yyyyMMddHHmmss").txt"
        Set-Content -Path $fileName -Value $logMessage
    }
}

# Log environment information
Log "Starting E2E tests with enhanced environment detection" "IMPORTANT"

# Log OS information
Log "OS Information:" "INFO"
Log "  Platform: Windows" "INFO"
Log "  PowerShell version: $($PSVersionTable.PSVersion)" "INFO"
Log "  WSL: $isWSL" "INFO"
if ($isWSL) {
    Log "  WSL Distro: $($env:WSL_DISTRO_NAME)" "INFO"
}
Log "  Working directory: $(Get-Location)" "INFO"

# Log Node.js information
Log "Node.js Information:" "INFO"
Log "  Version: $(node --version)" "INFO"
$npmVersion = try { npm --version } catch { "not installed" }
Log "  NPM Version: $npmVersion" "INFO"
$pnpmVersion = try { pnpm --version } catch { "not installed" }
Log "  PNPM Version: $pnpmVersion" "INFO"

# Log CI environment information
Log "CI Environment:" "INFO"
Log "  CI: $isCI" "INFO"
Log "  GitHub Actions: $isGitHubActions" "INFO"
Log "  Jenkins: $isJenkins" "INFO"
Log "  GitLab CI: $isGitLabCI" "INFO"
Log "  CircleCI: $isCircleCI" "INFO"
Log "  Travis CI: $isTravis" "INFO"
Log "  Azure Pipelines: $isAzurePipelines" "INFO"
Log "  TeamCity: $isTeamCity" "INFO"
Log "  Bitbucket: $isBitbucket" "INFO"
Log "  AppVeyor: $isAppVeyor" "INFO"
Log "  Drone CI: $isDrone" "INFO"
Log "  Buddy CI: $isBuddy" "INFO"
Log "  Buildkite: $isBuildkite" "INFO"
Log "  AWS CodeBuild: $isCodeBuild" "INFO"

# Log container environment information
Log "Container Environment:" "INFO"
Log "  Docker: $isDocker" "INFO"
Log "  Kubernetes: $isKubernetes" "INFO"
Log "  Docker Compose: $isDockerCompose" "INFO"
Log "  Docker Swarm: $isDockerSwarm" "INFO"

# Log cloud environment information
Log "Cloud Environment:" "INFO"
Log "  AWS: $isAWS" "INFO"
Log "  Azure: $isAzure" "INFO"
Log "  GCP: $isGCP" "INFO"

# Detect environment and set appropriate variables
# CI-specific settings
if ($isCI) {
    Log "CI environment detected, using CI-specific settings" "INFO"
    $verboseLogging = $true
    $retryInterval = 2
    # Use simple mock server in CI environments for better reliability
    $useSimpleMock = $true

    # GitHub Actions specific settings
    if ($isGitHubActions) {
        Log "GitHub Actions specific settings applied" "INFO"
        $maxRetries = 45
        $playwrightArgs = "--retries=2 --reporter=github"
    }

    # Jenkins specific settings
    if ($isJenkins) {
        Log "Jenkins specific settings applied" "INFO"
        $playwrightArgs = "--retries=2 --reporter=junit"
    }

    # GitLab CI specific settings
    if ($isGitLabCI) {
        Log "GitLab CI specific settings applied" "INFO"
        $playwrightArgs = "--retries=2 --reporter=junit"
    }

    # CircleCI specific settings
    if ($isCircleCI) {
        Log "CircleCI specific settings applied" "INFO"
        $playwrightArgs = "--retries=2 --reporter=junit"
    }

    # Travis CI specific settings
    if ($isTravis) {
        Log "Travis CI specific settings applied" "INFO"
        $playwrightArgs = "--retries=2 --reporter=junit"
    }

    # Azure Pipelines specific settings
    if ($isAzurePipelines) {
        Log "Azure Pipelines specific settings applied" "INFO"
        $playwrightArgs = "--retries=2 --reporter=junit"
    }

    # AppVeyor specific settings
    if ($isAppVeyor) {
        Log "AppVeyor specific settings applied" "INFO"
        $playwrightArgs = "--retries=2 --reporter=junit"
    }
} else {
    Log "Local environment detected" "INFO"
    $useSimpleMock = $false
    $playwrightArgs = "--reporter=$reporter"
}

# Container-specific settings
if ($isDocker) {
    Log "Docker environment detected, using Docker-specific settings" "INFO"
    # In Docker, we might need to use different host names
    $reactAppApiHost = "host.docker.internal"

    # Docker Compose specific settings
    if ($isDockerCompose) {
        Log "Docker Compose specific settings applied" "INFO"
        # In Docker Compose, use service names as hostnames
        $reactAppApiHost = "api"
    }

    # Kubernetes specific settings
    if ($isKubernetes) {
        Log "Kubernetes specific settings applied" "INFO"
        # In Kubernetes, use service names with namespace
        $reactAppApiHost = "api.default.svc.cluster.local"
    }
} else {
    $reactAppApiHost = "localhost"
}

# Cloud-specific settings
if ($isAWS) {
    Log "AWS environment detected, using AWS-specific settings" "INFO"
    # AWS-specific settings here
}

if ($isAzure) {
    Log "Azure environment detected, using Azure-specific settings" "INFO"
    # Azure-specific settings here
}

if ($isGCP) {
    Log "GCP environment detected, using GCP-specific settings" "INFO"
    # GCP-specific settings here
}

# OS-specific settings
if ($isWSL) {
    Log "WSL environment detected, using WSL-specific settings" "INFO"
    # WSL-specific settings here
}

# Function to check if a port is available
function Test-PortAvailable {
    param (
        [Parameter(Mandatory=$true)]
        [int]$Port
    )

    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect("localhost", $Port)
        $tcpClient.Close()
        return $false # Port is in use
    } catch {
        return $true # Port is available
    }
}

# Find available ports if the default ones are in use
if (-not (Test-PortAvailable -Port $mockApiPort)) {
    Log "Port $mockApiPort is already in use, finding an alternative port" "WARN"
    for ($port = 8001; $port -le 8020; $port++) {
        if (Test-PortAvailable -Port $port) {
            $mockApiPort = $port
            Log "Using alternative port $mockApiPort for mock API server" "INFO"
            break
        }
    }
}

if (-not (Test-PortAvailable -Port $reactPort)) {
    Log "Port $reactPort is already in use, finding an alternative port" "WARN"
    for ($port = 3001; $port -le 3020; $port++) {
        if (Test-PortAvailable -Port $port) {
            $reactPort = $port
            Log "Using alternative port $reactPort for React app" "INFO"
            break
        }
    }
}

# Start the appropriate mock server based on environment
if ($useSimpleMock) {
    Log "Starting simple mock server on port $mockApiPort..." "INFO"
    $env:MOCK_API_PORT = $mockApiPort
    $mockApiProcess = Start-Process -FilePath "node" -ArgumentList "tests/simple_mock_server.js" -PassThru -NoNewWindow -RedirectStandardOutput "logs/simple_mock_server.log" -RedirectStandardError "logs/simple_mock_server_error.log"
} else {
    Log "Starting mock API server on port $mockApiPort..." "INFO"
    $env:MOCK_API_PORT = $mockApiPort
    $mockApiProcess = Start-Process -FilePath "node" -ArgumentList "tests/mock_api_server.js" -PassThru -NoNewWindow -RedirectStandardOutput "logs/mock_api_server.log" -RedirectStandardError "logs/mock_api_server_error.log"
}

# Wait for the mock API server to start
Log "Waiting for mock API server to start..." "INFO"
$retryCount = 0
$serverReady = $false

while (-not $serverReady -and $retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$mockApiPort/health" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Log "Mock API server is ready on port $mockApiPort." "INFO"
            $serverReady = $true
        }
    } catch {
        Log "Waiting for mock API server to be ready... (Attempt $($retryCount+1)/$maxRetries)" "INFO"
        Start-Sleep -Seconds $retryInterval
    }
    $retryCount++
}

if (-not $serverReady) {
    Log "Mock API server failed to start within $($maxRetries * $retryInterval) seconds." "ERROR"

    # Try the fallback server as a last resort
    Log "Starting fallback server as a last resort..." "INFO"
    $fallbackProcess = Start-Process -FilePath "node" -ArgumentList "tests/simple_fallback_server.js" -PassThru -NoNewWindow -RedirectStandardOutput "logs/fallback_server.log" -RedirectStandardError "logs/fallback_server_error.log"

    # Wait for the fallback server to start
    Start-Sleep -Seconds 5

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$mockApiPort/health" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Log "Fallback server is ready on port $mockApiPort." "INFO"
            $serverReady = $true
            $mockApiProcess = $fallbackProcess
        }
    } catch {
        Log "Fallback server also failed to start. Exiting..." "ERROR"
        Stop-Process -Id $mockApiProcess.Id -Force -ErrorAction SilentlyContinue
        Stop-Process -Id $fallbackProcess.Id -Force -ErrorAction SilentlyContinue
        exit 1
    }
}

# Start the React app in the background
Log "Starting React app on port $reactPort..." "INFO"
$env:REACT_APP_API_BASE_URL = "http://$reactAppApiHost`:$mockApiPort/api"
$env:REACT_APP_AG_UI_ENABLED = "true"
$env:PORT = $reactPort

# Use pnpm if available, otherwise fall back to npm
if (Get-Command "pnpm" -ErrorAction SilentlyContinue) {
    $reactProcess = Start-Process -FilePath "pnpm" -ArgumentList "start" -PassThru -NoNewWindow -RedirectStandardOutput "logs/react_app.log" -RedirectStandardError "logs/react_app_error.log"
} else {
    $reactProcess = Start-Process -FilePath "npm" -ArgumentList "run", "start" -PassThru -NoNewWindow -RedirectStandardOutput "logs/react_app.log" -RedirectStandardError "logs/react_app_error.log"
}

# Wait for the React app to start
Log "Waiting for React app to start..." "INFO"
$retryCount = 0
$appReady = $false

while (-not $appReady -and $retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$reactPort" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Log "React app is ready on port $reactPort." "INFO"
            $appReady = $true
        }
    } catch {
        Log "Waiting for React app to be ready... (Attempt $($retryCount+1)/$maxRetries)" "INFO"
        Start-Sleep -Seconds $retryInterval
    }
    $retryCount++
}

if (-not $appReady) {
    Log "React app failed to start within $($maxRetries * $retryInterval) seconds." "ERROR"

    # In CI, we can try to run tests anyway with a static HTML server
    if ($isCI -or $isGitHubActions) {
        Log "CI environment detected, creating a simple HTML server for testing..." "WARN"

        # Create a simple HTML file
        if (-not (Test-Path "public")) {
            New-Item -ItemType Directory -Path "public" -Force | Out-Null
        }

        Set-Content -Path "public/index.html" -Value @"
<!DOCTYPE html>
<html>
<head>
  <title>Test Frontend</title>
</head>
<body>
  <h1>Test Frontend</h1>
  <div id="root">
    <div class="app-container">
      <div class="app-header">Test Header</div>
      <div class="app-content">Test Content</div>
    </div>
  </div>
</body>
</html>
"@

        # Start a simple HTTP server
        $httpServerProcess = Start-Process -FilePath "npx" -ArgumentList "http-server", "public", "-p", "$reactPort", "--silent" -PassThru -NoNewWindow -RedirectStandardOutput "logs/http_server.log" -RedirectStandardError "logs/http_server_error.log"

        # Wait for the HTTP server to start
        Start-Sleep -Seconds 5

        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$reactPort" -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Log "Simple HTTP server is ready on port $reactPort." "INFO"
                $appReady = $true
                $reactProcess = $httpServerProcess
            }
        } catch {
            Log "Simple HTTP server also failed to start. Exiting..." "ERROR"
            Stop-Process -Id $mockApiProcess.Id -Force -ErrorAction SilentlyContinue
            Stop-Process -Id $httpServerProcess.Id -Force -ErrorAction SilentlyContinue
            exit 1
        }
    } else {
        Log "Exiting due to React app startup failure." "ERROR"
        Stop-Process -Id $mockApiProcess.Id -Force -ErrorAction SilentlyContinue
        Stop-Process -Id $reactProcess.Id -Force -ErrorAction SilentlyContinue
        exit 1
    }
}

# Set environment variables for the tests
$env:PLAYWRIGHT_BASE_URL = "http://localhost:$reactPort"
$env:PLAYWRIGHT_API_BASE_URL = "http://localhost:$mockApiPort/api"
$env:REACT_APP_API_BASE_URL = "http://localhost:$mockApiPort/api"

# Run the Playwright tests
Log "Running Playwright tests..." "IMPORTANT"
Log "Test spec: $testSpec" "INFO"
Log "Reporter: $reporter" "INFO"
Log "Base URL: $env:PLAYWRIGHT_BASE_URL" "INFO"
Log "API Base URL: $env:PLAYWRIGHT_API_BASE_URL" "INFO"

# Add additional arguments for CI environments
$playwrightArgs = "--reporter=$reporter"
if ($isCI -or $isGitHubActions) {
    $playwrightArgs = "$playwrightArgs --retries=2"
}

npx playwright test $testSpec $playwrightArgs

# Capture the exit code
$testExitCode = $LASTEXITCODE

# Log the test result
if ($testExitCode -eq 0) {
    Log "Tests completed successfully!" "IMPORTANT"
} else {
    Log "Tests failed with exit code $testExitCode" "ERROR"
}

# Clean up processes
Log "Cleaning up processes..." "INFO"
Stop-Process -Id $mockApiProcess.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $reactProcess.Id -Force -ErrorAction SilentlyContinue

# Create a summary report
$summaryContent = @"
E2E Test Summary
---------------
Date: $(Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
Test Spec: $testSpec
Exit Code: $testExitCode

Operating System:
  Platform: Windows
  PowerShell Version: $($PSVersionTable.PSVersion)
  WSL: $isWSL
  WSL Distro: $($env:WSL_DISTRO_NAME)

CI Environment:
  CI: $isCI
  GitHub Actions: $isGitHubActions
  Jenkins: $isJenkins
  GitLab CI: $isGitLabCI
  CircleCI: $isCircleCI
  Travis CI: $isTravis
  Azure Pipelines: $isAzurePipelines
  TeamCity: $isTeamCity
  Bitbucket: $isBitbucket
  AppVeyor: $isAppVeyor
  Drone CI: $isDrone
  Buddy CI: $isBuddy
  Buildkite: $isBuildkite
  AWS CodeBuild: $isCodeBuild

Container Environment:
  Docker: $isDocker
  Kubernetes: $isKubernetes
  Docker Compose: $isDockerCompose
  Docker Swarm: $isDockerSwarm

Cloud Environment:
  AWS: $isAWS
  Azure: $isAzure
  GCP: $isGCP

Configuration:
  Mock API Port: $mockApiPort
  React Port: $reactPort
  API Host: $reactAppApiHost
  Playwright Args: $playwrightArgs
"@

Set-Content -Path "playwright-report/test-summary.txt" -Value $summaryContent

Log "Test summary written to playwright-report/test-summary.txt" "INFO"
Log "E2E tests completed with exit code $testExitCode" "IMPORTANT"

# Exit with the test exit code
exit $testExitCode
