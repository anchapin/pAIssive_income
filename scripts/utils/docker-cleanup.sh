#!/bin/bash
# Enhanced Docker cleanup script with better error handling and diagnostics

# Enable error handling
set -e

# Log with timestamp
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check disk space
check_disk_space() {
  available_space=$(df -m / | awk 'NR==2 {print $4}')
  log "Available disk space: ${available_space}MB"
  
  if [ "$available_space" -lt 1000 ]; then
    log "⚠️ Low disk space warning: less than 1GB available"
    return 1
  fi
  return 0
}

# Function to check Docker status
check_docker_status() {
  log "Checking Docker daemon status..."
  if ! docker info >/dev/null 2>&1; then
    log "❌ Docker daemon is not responding"
    return 1
  fi
  log "✅ Docker daemon is running"
  return 0
}

# Function to clean up Docker resources
cleanup_docker() {
  log "Cleaning up Docker resources..."
  
  # Stop all running containers
  if [ "$(docker ps -q | wc -l)" -gt 0 ]; then
    log "Stopping running containers..."
    docker stop $(docker ps -q) || log "⚠️ Failed to stop some containers"
  else
    log "No running containers to stop"
  fi
  
  # Remove all containers
  if [ "$(docker ps -a -q | wc -l)" -gt 0 ]; then
    log "Removing all containers..."
    docker rm -f $(docker ps -a -q) || log "⚠️ Failed to remove some containers"
  else
    log "No containers to remove"
  fi
  
  # Remove all images
  if [ "$(docker images -q | wc -l)" -gt 0 ]; then
    log "Removing all images..."
    docker rmi -f $(docker images -q) || log "⚠️ Failed to remove some images"
  else
    log "No images to remove"
  fi
  
  # Prune everything
  log "Pruning Docker system..."
  docker system prune -a -f --volumes
  
  return 0
}

# Function to perform aggressive cleanup
aggressive_cleanup() {
  log "Performing aggressive cleanup..."
  
  # Remove temporary files
  log "Removing temporary files..."
  rm -rf /tmp/* || true
  
  # Clean apt cache
  log "Cleaning apt cache..."
  sudo apt-get clean
  sudo apt-get autoremove -y
  
  # Remove additional large directories
  log "Removing additional large directories..."
  sudo rm -rf /var/lib/apt/lists/* || true
  sudo rm -rf /usr/share/dotnet || true
  sudo rm -rf /usr/local/lib/android || true
  sudo rm -rf /opt/ghc || true
  
  return 0
}

# Main function
main() {
  log "Starting Docker cleanup process..."
  
  # Check Docker status
  if ! check_docker_status; then
    log "Attempting to restart Docker daemon..."
    sudo systemctl restart docker || true
    sleep 10
    if ! check_docker_status; then
      log "❌ Failed to restart Docker daemon. Exiting."
      exit 1
    fi
  fi
  
  # Check initial disk space
  check_disk_space
  initial_space=$?
  
  # Clean up Docker resources
  cleanup_docker
  
  # Check disk space after Docker cleanup
  check_disk_space
  after_docker_cleanup=$?
  
  # If still low on disk space, perform aggressive cleanup
  if [ $after_docker_cleanup -eq 1 ]; then
    log "Still low on disk space after Docker cleanup. Performing aggressive cleanup..."
    aggressive_cleanup
    
    # Final disk space check
    check_disk_space
    final_space=$?
    
    if [ $final_space -eq 1 ]; then
      log "⚠️ Still low on disk space after all cleanup operations. This may cause issues."
    else
      log "✅ Disk space is now sufficient after aggressive cleanup."
    fi
  else
    log "✅ Disk space is sufficient after Docker cleanup."
  fi
  
  log "Docker cleanup completed successfully."
  df -h
}

# Run the main function
main
