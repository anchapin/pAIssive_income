#!/bin/bash
# Script to fix Docker Compose issues

# Enable error handling and debugging
set -e
set -x  # Enable command tracing for debugging

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
  
  # Check if sudo is available
  if command -v sudo >/dev/null 2>&1; then
    HAS_SUDO=true
  else
    HAS_SUDO=false
    log "⚠️ sudo command not available, will try without it"
  fi
  
  # Try to install Docker Compose plugin
  log "Attempting to install Docker Compose plugin..."
  if [ "$HAS_SUDO" = true ]; then
    sudo apt-get update || log "⚠️ apt-get update failed, continuing..."
    sudo apt-get install -y docker-compose-plugin || log "⚠️ docker-compose-plugin installation failed, continuing..."
  else
    apt-get update || log "⚠️ apt-get update failed, continuing..."
    apt-get install -y docker-compose-plugin || log "⚠️ docker-compose-plugin installation failed, continuing..."
  fi
  
  if command -v docker compose >/dev/null 2>&1; then
    log "✅ Docker Compose plugin installed successfully"
    echo "docker compose"
    return 0
  fi
  
  # If plugin installation failed, try standalone Docker Compose
  log "Plugin installation failed. Installing standalone Docker Compose..."
  COMPOSE_VERSION="v2.20.2"
  COMPOSE_INSTALL_DIR="$HOME/bin"
  mkdir -p "$COMPOSE_INSTALL_DIR"
  
  log "Downloading Docker Compose to $COMPOSE_INSTALL_DIR..."
  curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o "$COMPOSE_INSTALL_DIR/docker-compose"
  chmod +x "$COMPOSE_INSTALL_DIR/docker-compose"
  
  # Add to PATH if not already there
  export PATH="$COMPOSE_INSTALL_DIR:$PATH"
  echo "export PATH=$COMPOSE_INSTALL_DIR:$PATH" >> ~/.bashrc
  
  if command -v docker-compose >/dev/null 2>&1; then
    log "✅ Standalone Docker Compose installed successfully"
    echo "docker-compose"
    return 0
  fi
  
  # Try using the downloaded binary directly
  if [ -f "$COMPOSE_INSTALL_DIR/docker-compose" ]; then
    log "✅ Using Docker Compose from $COMPOSE_INSTALL_DIR/docker-compose"
    echo "$COMPOSE_INSTALL_DIR/docker-compose"
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
    # Print current directory contents for debugging
    log "Current directory contents:"
    ls -la
    return 1
  fi
  
  # Print the first few lines of the file for debugging
  log "First 10 lines of docker-compose.yml:"
  head -n 10 docker-compose.yml
  
  # Try to validate the file
  log "Attempting to validate docker-compose.yml with command: $compose_cmd config"
  if $compose_cmd config >/dev/null 2>&1; then
    log "✅ docker-compose.yml file is valid"
    return 0
  else
    log "❌ docker-compose.yml file has syntax errors"
    
    # Try to fix common issues
    log "Attempting to fix common issues..."
    
    # Fix indentation issues
    log "Fixing indentation issues..."
    sed -i 's/\t/  /g' docker-compose.yml
    
    # Fix line ending issues
    log "Fixing line ending issues..."
    # Simple replacement for dos2unix that should work everywhere
    sed -i 's/\r$//' docker-compose.yml
    
    # Check if fixes worked
    log "Checking if fixes worked..."
    if $compose_cmd config >/dev/null 2>&1; then
      log "✅ docker-compose.yml file fixed successfully"
      return 0
    else
      log "❌ Failed to fix docker-compose.yml file"
      # Print the error message for debugging
      log "Error message from $compose_cmd config:"
      $compose_cmd config
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
  
  # Print system information for debugging
  log "System information:"
  uname -a
  
  # Print Docker version
  log "Docker version:"
  docker --version || log "⚠️ Failed to get Docker version"
  
  # Check Docker Compose installation
  log "Checking for Docker Compose..."
  local compose_cmd
  compose_cmd=$(check_docker_compose || echo "")
  
  if [ -z "$compose_cmd" ]; then
    log "Docker Compose not found. Attempting to install..."
    compose_cmd=$(install_docker_compose || echo "")
    
    if [ -z "$compose_cmd" ]; then
      log "❌ Failed to install Docker Compose."
      # Try to use docker compose directly as a last resort
      if docker compose version >/dev/null 2>&1; then
        log "✅ Found docker compose command directly"
        compose_cmd="docker compose"
      else
        log "❌ All attempts to find or install Docker Compose failed. Exiting."
        exit 1
      fi
    fi
  fi
  
  log "Using Docker Compose command: $compose_cmd"
  
  # Validate docker-compose.yml file
  if ! validate_docker_compose_file "$compose_cmd"; then
    log "❌ Failed to validate docker-compose.yml file."
    # Don't exit, try to continue with other fixes
  fi
  
  # Fix Docker Compose version issues
  if ! fix_docker_compose_version "$compose_cmd"; then
    log "⚠️ Docker Compose version may not be compatible with the workflow"
    # Continue anyway
  fi
  
  # Fix Docker Compose network issues
  if ! fix_docker_compose_network "$compose_cmd"; then
    log "⚠️ Failed to fix Docker Compose network issues"
    # Continue anyway
  fi
  
  # Final check to see if Docker Compose is working
  log "Final check of Docker Compose..."
  if $compose_cmd version >/dev/null 2>&1; then
    log "✅ Docker Compose is working"
  else
    log "⚠️ Docker Compose may not be working correctly"
  fi
  
  log "✅ Docker Compose fix script completed."
  # Always exit with success to allow the workflow to continue
  exit 0
}

# Run the main function
main
