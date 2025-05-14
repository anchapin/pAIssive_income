# Docker cleanup script with enhanced features
# Check if Docker is running
function Test-DockerRunning {
    try {
        $null = docker info
        return $true
    }
    catch {
        return $false
    }
}

function Format-ByteSize {
    param([double]$bytes)
    $sizes = 'GB','TB'
    $index = 0
    while ($bytes -ge 1024 -and $index -lt ($sizes.Count - 1)) {
        $bytes /= 1024
        $index++
    }
    return "$([math]::Round($bytes, 2)) $($sizes[$index])"
}

function Get-DockerStats {
    $diskBefore = Get-PSDrive C | Select-Object Used,Free
    $imagesCount = (docker images -q).Count
    $containersCount = (docker ps -aq).Count
    $volumesCount = (docker volume ls -q).Count
    
    return @{
        DiskUsed = $diskBefore.Used
        DiskFree = $diskBefore.Free
        Images = $imagesCount
        Containers = $containersCount
        Volumes = $volumesCount
    }
}

# Initialize error log
$ErrorActionPreference = "Stop"
$logFile = "docker_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$errorCount = 0

Write-Host "🧹 Starting Docker cleanup process..." -ForegroundColor Cyan

# Check if Docker is running
if (-not (Test-DockerRunning)) {
    Write-Host "❌ Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

# Get initial stats
Write-Host "`n📊 Gathering initial statistics..." -ForegroundColor Yellow
$statsBefore = Get-DockerStats

Write-Host "Current system state:"
Write-Host "- Disk Usage: $(Format-ByteSize $statsBefore.DiskUsed) used, $(Format-ByteSize $statsBefore.DiskFree) free"
Write-Host "- Docker Resources:"
Write-Host "  - Images: $($statsBefore.Images)"
Write-Host "  - Containers: $($statsBefore.Containers)"
Write-Host "  - Volumes: $($statsBefore.Volumes)"

# Optional: Backup important containers
Write-Host "`n💾 Would you like to backup any running containers before cleanup? (y/n)" -ForegroundColor Yellow
$backup = Read-Host
if ($backup -eq 'y') {
    docker ps --format "{{.Names}}" | ForEach-Object {
        Write-Host "Backing up container: $_"
        try {
            docker commit $_ "${_}_backup_$(Get-Date -Format 'yyyyMMdd')"
        }
        catch {
            Write-Host "⚠️ Failed to backup container: $_" -ForegroundColor Yellow
            $_ | Out-File -Append $logFile
            $errorCount++
        }
    }
}

# Stop all running containers
Write-Host "`n🛑 Stopping all running containers..." -ForegroundColor Yellow
$runningContainers = docker ps -q
if ($runningContainers) {
    $runningContainers | ForEach-Object {
        try {
            docker stop $_ 
            Write-Host "Stopped container: $_"
        }
        catch {
            Write-Host "⚠️ Failed to stop container: $_" -ForegroundColor Yellow
            $_ | Out-File -Append $logFile
            $errorCount++
        }
    }
}
else {
    Write-Host "No running containers found."
}

# Remove Docker resources
Write-Host "`n🗑️ Removing unused Docker resources..." -ForegroundColor Yellow
try {
    # Remove unused containers, networks, images and optionally volumes
    Write-Host "Removing unused Docker resources (containers, networks, images, build cache)..."
    docker system prune -af --volumes

    # Clean up any remaining volumes
    Write-Host "Removing unused volumes..."
    docker volume prune -f
}
catch {
    Write-Host "⚠️ Error during cleanup process" -ForegroundColor Red
    $_ | Out-File -Append $logFile
    $errorCount++
}

# Get final stats
Write-Host "`n📊 Gathering final statistics..." -ForegroundColor Green
$statsAfter = Get-DockerStats

# Calculate differences
$diskSaved = $statsAfter.DiskFree - $statsBefore.DiskFree
$imagesRemoved = $statsBefore.Images - $statsAfter.Images
$containersRemoved = $statsBefore.Containers - $statsAfter.Containers
$volumesRemoved = $statsBefore.Volumes - $statsAfter.Volumes

Write-Host "`nCleanup Summary:"
Write-Host "---------------"
Write-Host "Disk space freed: $(Format-ByteSize $diskSaved)"
Write-Host "Resources removed:"
Write-Host "- Images: $imagesRemoved"
Write-Host "- Containers: $containersRemoved"
Write-Host "- Volumes: $volumesRemoved"

if ($errorCount -gt 0) {
    Write-Host "`n⚠️ Cleanup completed with $errorCount errors. See $logFile for details." -ForegroundColor Yellow
}
else {
    Write-Host "`n✨ Docker cleanup completed successfully!" -ForegroundColor Cyan
}

# Final disk space
Write-Host "`n💿 Current disk space:"
Write-Host "Used: $(Format-ByteSize $statsAfter.DiskUsed)"
Write-Host "Free: $(Format-ByteSize $statsAfter.DiskFree)"
