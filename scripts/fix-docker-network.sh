#!/bin/bash
# Script to fix Docker network issues

# Enable error handling
set -e

# Log with timestamp
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check Docker daemon status
check_docker_status() {
  log "Checking Docker daemon status..."
  if ! docker info >/dev/null 2>&1; then
    log "❌ Docker daemon is not responding"
    return 1
  fi
  log "✅ Docker daemon is running"
  return 0
}

# Function to create Docker network
create_docker_network() {
  local network_name="$1"
  log "Creating Docker network '$network_name'..."
  
  # Check if network already exists
  if docker network inspect "$network_name" >/dev/null 2>&1; then
    log "✅ Network '$network_name' already exists"
    return 0
  fi
  
  # Create network
  if docker network create "$network_name"; then
    log "✅ Network '$network_name' created successfully"
    return 0
  else
    log "❌ Failed to create network '$network_name'"
    return 1
  fi
}

# Function to check network connectivity
check_network_connectivity() {
  local network_name="$1"
  log "Checking network connectivity for '$network_name'..."
  
  # Create a temporary container to test network connectivity
  local container_id=$(docker run --rm -d --network "$network_name" alpine:latest sleep 30)
  
  if [ -z "$container_id" ]; then
    log "❌ Failed to create test container"
    return 1
  fi
  
  log "✅ Test container created with ID: $container_id"
  
  # Check if container is running
  if docker inspect --format='{{.State.Running}}' "$container_id" | grep -q "true"; then
    log "✅ Test container is running on network '$network_name'"
    
    # Clean up
    docker stop "$container_id" >/dev/null
    return 0
  else
    log "❌ Test container is not running"
    return 1
  fi
}

# Main function
main() {
  log "Starting Docker network fix script..."
  
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
  
  # Create Docker network
  if ! create_docker_network "paissive-network"; then
    log "Attempting to fix network issues..."
    
    # Try to remove existing network if it's in a bad state
    docker network rm paissive-network >/dev/null 2>&1 || true
    sleep 5
    
    # Try to create network again
    if ! create_docker_network "paissive-network"; then
      log "❌ Failed to create network after cleanup. Trying with different driver..."
      
      # Try with different driver
      if docker network create --driver bridge paissive-network; then
        log "✅ Network created successfully with bridge driver"
      else
        log "❌ All attempts to create network failed. Exiting."
        exit 1
      fi
    fi
  fi
  
  # Check network connectivity
  if ! check_network_connectivity "paissive-network"; then
    log "❌ Network connectivity check failed. Network may not be functioning properly."
    exit 1
  fi
  
  log "✅ Docker network fix completed successfully."
}

# Run the main function
main
