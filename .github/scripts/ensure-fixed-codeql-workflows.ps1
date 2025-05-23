# Script to ensure fixed versions of CodeQL workflow files are used

# Define the workflow files
$CODEQL_WORKFLOW = ".github/workflows/codeql.yml"
$CODEQL_WINDOWS_WORKFLOW = ".github/workflows/codeql-windows.yml"
$CODEQL_MACOS_WORKFLOW = ".github/workflows/codeql-macos.yml"
$CODEQL_UBUNTU_WORKFLOW = ".github/workflows/codeql-ubuntu.yml"

# Define the fixed workflow files
$CODEQL_FIXED_WORKFLOW = ".github/workflows/codeql-fixed.yml"
$CODEQL_WINDOWS_FIXED_WORKFLOW = ".github/workflows/codeql-windows-fixed.yml"
$CODEQL_MACOS_FIXED_WORKFLOW = ".github/workflows/codeql-macos-fixed.yml"
$CODEQL_UBUNTU_FIXED_WORKFLOW = ".github/workflows/codeql-ubuntu-fixed.yml"

# Function to log messages
function Log {
    param (
        [string]$message
    )
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $message"
}

# Function to check and replace a workflow file with its fixed version
function Replace-Workflow {
    param (
        [string]$originalFile,
        [string]$fixedFile,
        [string]$description
    )

    if (Test-Path $fixedFile) {
        Log "Fixed $description workflow file exists: $fixedFile"
        
        if (Test-Path $originalFile) {
            Log "Replacing $originalFile with $fixedFile"
            Copy-Item -Path $fixedFile -Destination $originalFile -Force
            Log "Successfully replaced $description workflow file"
        }
        else {
            Log "Original $description workflow file does not exist: $originalFile"
            Log "Creating $originalFile from $fixedFile"
            Copy-Item -Path $fixedFile -Destination $originalFile -Force
            Log "Successfully created $description workflow file"
        }
    }
    else {
        Log "Fixed $description workflow file does not exist: $fixedFile"
        Log "Cannot replace $description workflow file"
    }
}

# Main script
Log "Starting workflow file replacement..."

# Replace the workflow files
Replace-Workflow -originalFile $CODEQL_WORKFLOW -fixedFile $CODEQL_FIXED_WORKFLOW -description "CodeQL"
Replace-Workflow -originalFile $CODEQL_WINDOWS_WORKFLOW -fixedFile $CODEQL_WINDOWS_FIXED_WORKFLOW -description "CodeQL Windows"
Replace-Workflow -originalFile $CODEQL_MACOS_WORKFLOW -fixedFile $CODEQL_MACOS_FIXED_WORKFLOW -description "CodeQL macOS"
Replace-Workflow -originalFile $CODEQL_UBUNTU_WORKFLOW -fixedFile $CODEQL_UBUNTU_FIXED_WORKFLOW -description "CodeQL Ubuntu"

Log "Workflow file replacement completed"
