#!/bin/bash
# Script to fix Docker Compose issues

# Enable error handling
set -e

# Log with timestamp
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check Docker Compose installation
check_docker_compose() {
  log "Checking Docker Compose installation..."
  
  if command -v docker compose >/dev/null 2>&1; then
    log "✅ Docker Compose plugin is available"
    echo "docker compose"
    return 0
  elif command -v docker-compose >/dev/null 2>&1; then
    log "✅ Standalone Docker Compose is available"
    echo "docker-compose"
    return 0
  else
    log "❌ Docker Compose not found"
    return 1
  fi
}

# Function to install Docker Compose
install_docker_compose() {
  log "Installing Docker Compose..."
  
  # Try to install Docker Compose plugin
  log "Attempting to install Docker Compose plugin..."
  sudo apt-get update
  sudo apt-get install -y docker-compose-plugin
  
  if command -v docker compose >/dev/null 2>&1; then
    log "✅ Docker Compose plugin installed successfully"
    echo "docker compose"
    return 0
  fi
  
  # If plugin installation failed, try standalone Docker Compose
  log "Plugin installation failed. Installing standalone Docker Compose..."
  COMPOSE_VERSION="v2.20.2"
  sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
  
  if command -v docker-compose >/dev/null 2>&1; then
    log "✅ Standalone Docker Compose installed successfully"
    echo "docker-compose"
    return 0
  fi
  
  log "❌ All Docker Compose installation attempts failed"
  return 1
}

# Function to validate docker-compose.yml
validate_docker_compose_file() {
  local compose_cmd="$1"
  log "Validating docker-compose.yml file..."
  
  if [ ! -f "docker-compose.yml" ]; then
    log "❌ docker-compose.yml file not found"
    return 1
  fi
  
  if $compose_cmd config >/dev/null 2>&1; then
    log "✅ docker-compose.yml file is valid"
    return 0
  else
    log "❌ docker-compose.yml file has syntax errors"
    
    # Try to fix common issues
    log "Attempting to fix common issues..."
    
    # Fix indentation issues
    sed -i 's/\t/  /g' docker-compose.yml
    
    # Fix line ending issues
    if command -v dos2unix >/dev/null 2>&1; then
      dos2unix docker-compose.yml
    else
      # Simple replacement for dos2unix
      sed -i 's/\r$//' docker-compose.yml
    fi
    
    # Check if fixes worked
    if $compose_cmd config >/dev/null 2>&1; then
      log "✅ docker-compose.yml file fixed successfully"
      return 0
    else
      log "❌ Failed to fix docker-compose.yml file"
      return 1
    fi
  fi
}

# Function to fix Docker Compose version issues
fix_docker_compose_version() {
  local compose_cmd="$1"
  log "Checking Docker Compose version..."
  
  # Get Docker Compose version
  local version
  if [ "$compose_cmd" = "docker compose" ]; then
    version=$(docker compose version --short 2>/dev/null || echo "unknown")
  else
    version=$(docker-compose --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
  fi
  
  log "Docker Compose version: $version"
  
  # Check if version is compatible with the workflow
  if [ "$version" = "unknown" ]; then
    log "⚠️ Could not determine Docker Compose version"
    return 1
  fi
  
  # Add version compatibility check if needed
  
  return 0
}

# Function to fix Docker Compose network issues
fix_docker_compose_network() {
  local compose_cmd="$1"
  log "Fixing Docker Compose network issues..."
  
  # Check if docker-compose.yml contains network configuration
  if grep -q "networks:" docker-compose.yml; then
    log "✅ docker-compose.yml contains network configuration"
    
    # Check if the network exists
    if ! docker network inspect paissive-network >/dev/null 2>&1; then
      log "Creating paissive-network..."
      docker network create paissive-network || {
        log "❌ Failed to create paissive-network"
        return 1
      }
    fi
    
    return 0
  else
    log "⚠️ docker-compose.yml does not contain network configuration"
    return 1
  fi
}

# Main function
main() {
  log "Starting Docker Compose fix script..."
  
  # Check Docker Compose installation
  local compose_cmd
  compose_cmd=$(check_docker_compose)
  
  if [ $? -ne 0 ]; then
    log "Docker Compose not found. Attempting to install..."
    compose_cmd=$(install_docker_compose)
    
    if [ $? -ne 0 ]; then
      log "❌ Failed to install Docker Compose. Exiting."
      exit 1
    fi
  fi
  
  log "Using Docker Compose command: $compose_cmd"
  
  # Validate docker-compose.yml file
  if ! validate_docker_compose_file "$compose_cmd"; then
    log "❌ Failed to validate docker-compose.yml file. Exiting."
    exit 1
  fi
  
  # Fix Docker Compose version issues
  if ! fix_docker_compose_version "$compose_cmd"; then
    log "⚠️ Docker Compose version may not be compatible with the workflow"
  fi
  
  # Fix Docker Compose network issues
  if ! fix_docker_compose_network "$compose_cmd"; then
    log "⚠️ Failed to fix Docker Compose network issues"
  fi
  
  log "✅ Docker Compose fix completed successfully."
}

# Run the main function
main
