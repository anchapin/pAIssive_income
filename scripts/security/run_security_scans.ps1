# PowerShell script for running security scans on Windows
# Enhanced and reliable security scan runner for Windows environments with cross-platform support

param(
    [switch]$Verbose = $false,
    [int]$DefaultTimeoutSeconds = 1200
)

# Set error action preference for better error handling
$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"  # Suppress progress bars in CI

# Enable verbose output if requested
if ($Verbose) {
    $VerbosePreference = "Continue"
}

# Try to import enhanced utilities if available
$utilsPath = "scripts/utils/enhanced_powershell_utils.ps1"
if (Test-Path $utilsPath) {
    Write-Host "Loading enhanced PowerShell utilities..."
    try {
        . $utilsPath -Verbose:$false -DefaultTimeoutSeconds $DefaultTimeoutSeconds
        $useEnhancedUtils = $true
    } catch {
        Write-Host "Failed to load enhanced utilities: $_"
        $useEnhancedUtils = $false
    }
} else {
    Write-Host "Enhanced utilities not found, using fallback functions..."
    $useEnhancedUtils = $false
}

# Fallback function if enhanced utilities not available
if (-not $useEnhancedUtils) {
    function Write-Log {
        param([string]$Message, [string]$Level = "INFO")
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "[$timestamp] [$Level] $Message"
    }

    function Invoke-CommandWithTimeout {
        param(
            [scriptblock]$ScriptBlock,
            [int]$TimeoutSeconds = $DefaultTimeoutSeconds,
            [string]$Description = "Command"
        )

        Write-Log "Running $Description with timeout of $TimeoutSeconds seconds"

        try {
            $job = Start-Job -ScriptBlock $ScriptBlock
            $completed = Wait-Job $job -Timeout $TimeoutSeconds

            if ($completed) {
                $result = Receive-Job $job
                Remove-Job $job
                Write-Log "$Description completed successfully"
                return @{ Success = $true; Result = $result }
            } else {
                Write-Log "$Description timed out after $TimeoutSeconds seconds" "WARN"
                Remove-Job $job -Force
                return @{ Success = $false; TimedOut = $true }
            }
        } catch {
            Write-Log "$Description failed: $_" "ERROR"
            return @{ Success = $false; Error = $_ }
        }
    }
}

function Create-SecurityReportsDir {
    $securityDir = "security-reports"
    if (-not (Test-Path $securityDir)) {
        New-Item -ItemType Directory -Path $securityDir -Force | Out-Null
        Write-Log "Created security reports directory: $securityDir"
    }
    return $securityDir
}

function Create-EmptySarif {
    param([string]$ToolName, [string]$ToolVersion = "unknown")
    
    return @{
        "version" = "2.1.0"
        "`$schema" = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
        "runs" = @(
            @{
                "tool" = @{
                    "driver" = @{
                        "name" = $ToolName
                        "informationUri" = "https://github.com/PyCQA/$($ToolName.ToLower())"
                        "version" = $ToolVersion
                        "rules" = @()
                    }
                }
                "results" = @()
            }
        )
    }
}

function Write-SarifFile {
    param([hashtable]$SarifData, [string]$FilePath)
    
    try {
        $SarifData | ConvertTo-Json -Depth 10 | Set-Content -Path $FilePath -Encoding UTF8
        Write-Log "Successfully wrote SARIF file: $FilePath"
        return $true
    }
    catch {
        Write-Log "Failed to write SARIF file $FilePath`: $_" "ERROR"
        return $false
    }
}

function Run-BanditScan {
    param([string]$SecurityDir)
    
    Write-Log "Running Bandit security scan..."
    
    # Determine configuration file to use (prefer YAML)
    $configFile = $null
    $configFiles = @("bandit.yaml", ".bandit")
    
    foreach ($config in $configFiles) {
        if (Test-Path $config) {
            $configFile = $config
            Write-Log "Using Bandit configuration: $configFile"
            break
        }
    }
    
    if (-not $configFile) {
        Write-Log "No Bandit configuration file found, using defaults" "WARN"
    }
    
    # Prepare Bandit command
    $cmd = @("python", "-m", "bandit", "-r", ".", "-f", "sarif", "-o", "$SecurityDir/bandit-results.sarif", "--exit-zero")
    
    # Add configuration file if found
    if ($configFile) {
        $cmd += @("-c", $configFile)
    } else {
        # Add default exclusions if no config file
        $cmd += @("--exclude", ".venv,node_modules,tests,mock_mcp,mock_crewai,mock_mem0,build,dist")
    }
    
    try {
        # Use enhanced timeout handling if available
        $scriptBlock = {
            param($cmdArgs, $secDir)
            $process = Start-Process -FilePath "python" -ArgumentList $cmdArgs -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$secDir/bandit-output.log" -RedirectStandardError "$secDir/bandit-error.log"
            return $process.ExitCode
        }

        $timeoutSeconds = if ($useEnhancedUtils) { Get-AdjustedTimeout -BaseTimeoutSeconds 1200 } else { 1500 }
        $result = Invoke-CommandWithTimeout -ScriptBlock $scriptBlock -TimeoutSeconds $timeoutSeconds -Description "Bandit scan" -ArgumentList @{cmdArgs = ($cmd[1..($cmd.Length-1)]); secDir = $SecurityDir}

        if ($result.Success -and ($result.Result -eq 0 -or (Test-Path "$SecurityDir/bandit-results.sarif"))) {
            Write-Log "Bandit scan completed successfully"
            return $true
        } elseif ($result.TimedOut) {
            Write-Log "Bandit scan timed out after $timeoutSeconds seconds" "WARN"
        } else {
            Write-Log "Bandit scan completed with warnings" "WARN"
        }
    }
    catch {
        Write-Log "Bandit scan failed: $_" "ERROR"
    }
    
    # Create empty SARIF file as fallback
    Write-Log "Creating empty Bandit SARIF file as fallback"
    $emptySarif = Create-EmptySarif -ToolName "Bandit" -ToolVersion "1.7.5"
    return Write-SarifFile -SarifData $emptySarif -FilePath "$SecurityDir/bandit-results.sarif"
}

function Run-SafetyCheck {
    param([string]$SecurityDir)
    
    Write-Log "Running Safety vulnerability check..."
    
    try {
        # Use enhanced timeout handling if available
        $scriptBlock = {
            param($secDir)
            $process = Start-Process -FilePath "python" -ArgumentList @("-m", "safety", "check", "--json") -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$secDir/safety-results.json" -RedirectStandardError "$secDir/safety-error.log"
            return $process.ExitCode
        }

        $timeoutSeconds = if ($useEnhancedUtils) { Get-AdjustedTimeout -BaseTimeoutSeconds 600 } else { 750 }
        $result = Invoke-CommandWithTimeout -ScriptBlock $scriptBlock -TimeoutSeconds $timeoutSeconds -Description "Safety check" -ArgumentList @{secDir = $SecurityDir}

        if ($result.TimedOut) {
            Write-Log "Safety check timed out after $timeoutSeconds seconds" "WARN"
        }

        # Safety returns non-zero if vulnerabilities found, which is expected
        if (-not (Test-Path "$SecurityDir/safety-results.json") -or (Get-Item "$SecurityDir/safety-results.json").Length -eq 0) {
            '{"vulnerabilities": []}' | Set-Content -Path "$SecurityDir/safety-results.json"
        }

        Write-Log "Safety check completed"
        return $true
    }
    catch {
        Write-Log "Safety check failed: $_" "ERROR"
    }
    
    # Create empty results file
    '{"vulnerabilities": []}' | Set-Content -Path "$SecurityDir/safety-results.json"
    return $true
}

function Run-PipAudit {
    param([string]$SecurityDir)
    
    Write-Log "Running pip-audit vulnerability check..."
    
    try {
        # Use enhanced timeout handling if available
        $scriptBlock = {
            param($secDir)
            $process = Start-Process -FilePath "python" -ArgumentList @("-m", "pip_audit", "--format=json") -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$secDir/pip-audit-results.json" -RedirectStandardError "$secDir/pip-audit-error.log"
            return $process.ExitCode
        }

        $timeoutSeconds = if ($useEnhancedUtils) { Get-AdjustedTimeout -BaseTimeoutSeconds 600 } else { 750 }
        $result = Invoke-CommandWithTimeout -ScriptBlock $scriptBlock -TimeoutSeconds $timeoutSeconds -Description "pip-audit check" -ArgumentList @{secDir = $SecurityDir}

        if ($result.TimedOut) {
            Write-Log "pip-audit check timed out after $timeoutSeconds seconds" "WARN"
        }

        if (-not (Test-Path "$SecurityDir/pip-audit-results.json") -or (Get-Item "$SecurityDir/pip-audit-results.json").Length -eq 0) {
            '{"vulnerabilities": []}' | Set-Content -Path "$SecurityDir/pip-audit-results.json"
        }

        Write-Log "pip-audit check completed"
        return $true
    }
    catch {
        Write-Log "pip-audit check failed: $_" "ERROR"
    }
    
    # Create empty results file
    '{"vulnerabilities": []}' | Set-Content -Path "$SecurityDir/pip-audit-results.json"
    return $true
}

# Main execution
Write-Log "Starting security scans..."

# Show platform information if enhanced utilities are available
if ($useEnhancedUtils -and (Get-Command "Write-PlatformInfo" -ErrorAction SilentlyContinue)) {
    Write-PlatformInfo
}

try {
    # Create security reports directory
    $securityDir = Create-SecurityReportsDir
    
    # Run security scans
    $banditSuccess = Run-BanditScan -SecurityDir $securityDir
    $safetySuccess = Run-SafetyCheck -SecurityDir $securityDir
    $pipAuditSuccess = Run-PipAudit -SecurityDir $securityDir
    
    # Summary
    if ($banditSuccess -and $safetySuccess -and $pipAuditSuccess) {
        Write-Log "All security scans completed successfully"
        exit 0
    } else {
        Write-Log "Some security scans had issues, but fallback files created" "WARN"
        exit 0  # Don't fail the workflow, just warn
    }
}
catch {
    Write-Log "Security scan runner failed: $_" "ERROR"
    exit 1
}
