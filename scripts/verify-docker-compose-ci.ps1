# PowerShell script to verify Docker Compose CI setup
# This script checks that all required scripts exist and are properly set up

# Log with timestamp
function Log {
    param (
        [string]$Message
    )
    Write-Host "[$([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss'))] $Message"
}

# Main function
function Main {
    Log "Starting Docker Compose CI verification script..."

    # List of required scripts
    $scripts = @(
        "scripts/fix-docker-network.sh",
        "scripts/fix-docker-compose.sh",
        "scripts/fix-docker-compose-improved.sh",
        "scripts/fix-docker-compose-errors.sh",
        "scripts/run-docker-compose-ci.sh",
        "docker-healthcheck.sh",
        "wait-for-db.sh"
    )

    # Check all scripts exist
    $allScriptsExist = $true
    foreach ($script in $scripts) {
        if (Test-Path $script) {
            Log "✅ Script $script exists"
        } else {
            Log "❌ Script $script does not exist"
            $allScriptsExist = $false
        }
    }

    # Check necessary directories exist
    $directories = @("logs", "data", "test-results", "playwright-report")
    $allDirectoriesExist = $true
    foreach ($dir in $directories) {
        if (Test-Path $dir) {
            Log "✅ Directory $dir exists"
        } else {
            Log "❌ Directory $dir does not exist"
            $allDirectoriesExist = $false
        }
    }

    # Check Docker Compose workflow file
    $workflowFile = ".github/workflows/docker-compose.yml"
    if (Test-Path $workflowFile) {
        Log "✅ Docker Compose workflow file exists"
        
        # Check if our branch is included in the workflow
        $workflowContent = Get-Content $workflowFile -Raw
        if ($workflowContent -match "cosine/improve-frontend-tests-y4hwd5") {
            Log "✅ Branch 'cosine/improve-frontend-tests-y4hwd5' is included in the workflow"
        } else {
            Log "❌ Branch 'cosine/improve-frontend-tests-y4hwd5' is not included in the workflow"
        }
    } else {
        Log "❌ Docker Compose workflow file does not exist"
    }

    # Final status
    if ($allScriptsExist -and $allDirectoriesExist) {
        Log "✅ Docker Compose CI verification completed successfully. All required files and directories exist."
        return 0
    } else {
        Log "❌ Docker Compose CI verification failed. Some required files or directories are missing."
        return 1
    }
}

# Run the main function
Main
