# Enhanced PowerShell utilities for cross-platform GitHub Actions
# Provides better timeout handling, error management, and cross-platform compatibility

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

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [switch]$NoTimestamp
    )
    
    if (-not $NoTimestamp) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "[$timestamp] [$Level] $Message"
    } else {
        Write-Host "[$Level] $Message"
    }
}

function Get-PlatformTimeoutMultiplier {
    # Windows typically needs more time than Unix systems
    return 1.5
}

function Get-AdjustedTimeout {
    param([int]$BaseTimeoutSeconds)
    
    $multiplier = Get-PlatformTimeoutMultiplier
    return [int]($BaseTimeoutSeconds * $multiplier)
}

function Invoke-CommandWithTimeout {
    param(
        [scriptblock]$ScriptBlock,
        [int]$TimeoutSeconds = $DefaultTimeoutSeconds,
        [string]$Description = "Command",
        [hashtable]$ArgumentList = @{}
    )
    
    $adjustedTimeout = Get-AdjustedTimeout -BaseTimeoutSeconds $TimeoutSeconds
    Write-Log "Running $Description with timeout of $adjustedTimeout seconds"
    
    try {
        $job = Start-Job -ScriptBlock $ScriptBlock -ArgumentList $ArgumentList.Values
        $completed = Wait-Job $job -Timeout $adjustedTimeout
        
        if ($completed) {
            $result = Receive-Job $job
            $exitCode = $job.State -eq "Completed" ? 0 : 1
            Remove-Job $job
            
            Write-Log "$Description completed successfully"
            return @{
                Success = $true
                Result = $result
                ExitCode = $exitCode
                TimedOut = $false
            }
        } else {
            Write-Log "$Description timed out after $adjustedTimeout seconds" "WARN"
            Remove-Job $job -Force
            
            return @{
                Success = $false
                Result = $null
                ExitCode = 124  # Standard timeout exit code
                TimedOut = $true
            }
        }
    }
    catch {
        Write-Log "$Description failed: $_" "ERROR"
        return @{
            Success = $false
            Result = $null
            ExitCode = 1
            TimedOut = $false
            Error = $_
        }
    }
}

function Install-PythonPackageWithRetry {
    param(
        [string]$PackageName,
        [string[]]$ExtraArgs = @(),
        [int]$MaxAttempts = 3,
        [int]$TimeoutSeconds = 600
    )
    
    Write-Log "Installing Python package: $PackageName"
    
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        Write-Log "Attempt $attempt/$MaxAttempts for $PackageName"
        
        $scriptBlock = {
            param($pkg, $args)
            $allArgs = @("-m", "pip", "install") + $args + @($pkg)
            $process = Start-Process -FilePath "python" -ArgumentList $allArgs -Wait -PassThru -NoNewWindow
            return $process.ExitCode
        }
        
        $result = Invoke-CommandWithTimeout -ScriptBlock $scriptBlock -TimeoutSeconds $TimeoutSeconds -Description "pip install $PackageName" -ArgumentList @{pkg = $PackageName; args = $ExtraArgs}
        
        if ($result.Success -and $result.ExitCode -eq 0) {
            Write-Log "Successfully installed $PackageName"
            return $true
        }
        
        if ($attempt -lt $MaxAttempts) {
            $delay = 5 * $attempt
            Write-Log "Installation failed, retrying in $delay seconds..."
            Start-Sleep -Seconds $delay
            
            # Clear pip cache on retry
            try {
                python -m pip cache purge 2>$null
            } catch {
                # Ignore cache clear errors
            }
        }
    }
    
    Write-Log "Failed to install $PackageName after $MaxAttempts attempts" "ERROR"
    return $false
}

function Install-RequirementsFileWithRetry {
    param(
        [string]$RequirementsFile,
        [int]$MaxAttempts = 3,
        [int]$TimeoutSeconds = 1800
    )
    
    if (-not (Test-Path $RequirementsFile)) {
        Write-Log "Requirements file not found: $RequirementsFile" "WARN"
        return $true  # Not an error if file doesn't exist
    }
    
    Write-Log "Installing requirements from: $RequirementsFile"
    
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        Write-Log "Attempt $attempt/$MaxAttempts for $RequirementsFile"
        
        $scriptBlock = {
            param($file)
            $process = Start-Process -FilePath "python" -ArgumentList @("-m", "pip", "install", "-r", $file, "--no-deps", "--force-reinstall") -Wait -PassThru -NoNewWindow
            return $process.ExitCode
        }
        
        $result = Invoke-CommandWithTimeout -ScriptBlock $scriptBlock -TimeoutSeconds $TimeoutSeconds -Description "pip install -r $RequirementsFile" -ArgumentList @{file = $RequirementsFile}
        
        if ($result.Success -and $result.ExitCode -eq 0) {
            Write-Log "Successfully installed requirements from $RequirementsFile"
            return $true
        }
        
        if ($attempt -lt $MaxAttempts) {
            $delay = 10 * $attempt
            Write-Log "Requirements installation failed, retrying in $delay seconds..."
            Start-Sleep -Seconds $delay
            
            # Clear pip cache on retry
            try {
                python -m pip cache purge 2>$null
            } catch {
                # Ignore cache clear errors
            }
        }
    }
    
    # Try without dependencies as last resort
    Write-Log "Attempting installation without dependencies as fallback..."
    $fallbackScriptBlock = {
        param($file)
        $process = Start-Process -FilePath "python" -ArgumentList @("-m", "pip", "install", "-r", $file, "--no-deps") -Wait -PassThru -NoNewWindow
        return $process.ExitCode
    }
    
    $fallbackResult = Invoke-CommandWithTimeout -ScriptBlock $fallbackScriptBlock -TimeoutSeconds 900 -Description "pip install -r $RequirementsFile (no deps)" -ArgumentList @{file = $RequirementsFile}
    
    if ($fallbackResult.Success) {
        Write-Log "Fallback installation completed for $RequirementsFile" "WARN"
        return $true
    }
    
    Write-Log "Failed to install requirements from $RequirementsFile after all attempts" "ERROR"
    return $false
}

function New-CrossPlatformPath {
    param([string]$Path)
    
    # Convert forward slashes to backslashes on Windows
    return $Path.Replace("/", [System.IO.Path]::DirectorySeparatorChar)
}

function Test-CommandAvailable {
    param([string]$CommandName)
    
    try {
        $null = Get-Command $CommandName -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

function Write-PlatformInfo {
    Write-Log "=== Platform Information ===" "INFO" -NoTimestamp
    Write-Log "OS: $($PSVersionTable.OS)" "INFO" -NoTimestamp
    Write-Log "PowerShell Version: $($PSVersionTable.PSVersion)" "INFO" -NoTimestamp
    Write-Log "Platform: $($PSVersionTable.Platform)" "INFO" -NoTimestamp
    Write-Log "Architecture: $($PSVersionTable.PSArchitecture)" "INFO" -NoTimestamp
    
    # Check available commands
    $commands = @("python", "pip", "git", "node", "npm", "pnpm")
    Write-Log "=== Available Commands ===" "INFO" -NoTimestamp
    foreach ($cmd in $commands) {
        $available = Test-CommandAvailable -CommandName $cmd
        $status = $available ? "✓" : "✗"
        Write-Log "$status $cmd" "INFO" -NoTimestamp
    }
}

# Export functions for use in other scripts
Export-ModuleMember -Function @(
    'Write-Log',
    'Get-AdjustedTimeout',
    'Invoke-CommandWithTimeout',
    'Install-PythonPackageWithRetry',
    'Install-RequirementsFileWithRetry',
    'New-CrossPlatformPath',
    'Test-CommandAvailable',
    'Write-PlatformInfo'
)

# If script is run directly, show platform info
if ($MyInvocation.InvocationName -eq $MyInvocation.MyCommand.Name) {
    Write-PlatformInfo
}
