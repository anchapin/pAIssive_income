# Script to run E2E tests with mock API server
Write-Host "Starting mock API server..."

# Start the mock API server in the background
$mockApiProcess = Start-Process -FilePath "node" -ArgumentList "tests/mock_api_server.js" -PassThru -NoNewWindow

# Wait for the mock API server to start
Write-Host "Waiting for mock API server to start..."
$maxRetries = 30
$retryCount = 0
$serverReady = $false

while (-not $serverReady -and $retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "Mock API server is ready."
            $serverReady = $true
        }
    } catch {
        Write-Host "Waiting for mock API server to be ready... (Attempt $($retryCount+1)/$maxRetries)"
        Start-Sleep -Seconds 1
    }
    $retryCount++
}

if (-not $serverReady) {
    Write-Host "Mock API server failed to start within 30 seconds. Exiting..."
    exit 1
}

# Start the React app in the background
Write-Host "Starting React app..."
$reactProcess = Start-Process -FilePath "pnpm" -ArgumentList "start", "--", "--port=3000" -PassThru -NoNewWindow

# Wait for the React app to start
Write-Host "Waiting for React app to start..."
$maxRetries = 30
$retryCount = 0
$appReady = $false

while (-not $appReady -and $retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "React app is ready."
            $appReady = $true
        }
    } catch {
        Write-Host "Waiting for React app to be ready... (Attempt $($retryCount+1)/$maxRetries)"
        Start-Sleep -Seconds 1
    }
    $retryCount++
}

if (-not $appReady) {
    Write-Host "React app failed to start within 30 seconds. Exiting..."
    Stop-Process -Id $mockApiProcess.Id -Force
    exit 1
}

# Run the Playwright tests
Write-Host "Running Playwright tests..."
npx playwright test tests/e2e/agent_ui.spec.ts --reporter=list

# Capture the exit code
$testExitCode = $LASTEXITCODE

# Clean up processes
Write-Host "Cleaning up processes..."
Stop-Process -Id $mockApiProcess.Id -Force
Stop-Process -Id $reactProcess.Id -Force

# Exit with the test exit code
exit $testExitCode
