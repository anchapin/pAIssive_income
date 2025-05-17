#!/bin/bash
# Enhanced Docker Compose installation script with better error handling

# Enable error handling
set -e

# Log with timestamp
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to install Docker Compose plugin
install_docker_compose_plugin() {
  log "Installing Docker Compose plugin..."
  sudo apt-get update
  sudo apt-get install -y docker-compose-plugin
  
  # Verify installation
  if command_exists "docker compose"; then
    log "✅ Docker Compose plugin installed successfully"
    docker compose version
    return 0
  else
    log "❌ Failed to install Docker Compose plugin"
    return 1
  fi
}

# Function to install standalone Docker Compose
install_docker_compose_standalone() {
  log "Installing standalone Docker Compose..."
  
  # Get latest release version
  COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
  log "Latest Docker Compose version: $COMPOSE_VERSION"
  
  # Download and install
  sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  
  # Create symbolic link
  sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
  
  # Verify installation
  if command_exists "docker-compose"; then
    log "✅ Standalone Docker Compose installed successfully"
    docker-compose --version
    return 0
  else
    log "❌ Failed to install standalone Docker Compose"
    return 1
  fi
}

# Function to install Docker Compose using apt
install_docker_compose_apt() {
  log "Installing Docker Compose using apt..."
  sudo apt-get update
  sudo apt-get install -y docker-compose
  
  # Verify installation
  if command_exists "docker-compose"; then
    log "✅ Docker Compose installed successfully using apt"
    docker-compose --version
    return 0
  else
    log "❌ Failed to install Docker Compose using apt"
    return 1
  fi
}

# Main function
main() {
  log "Starting Docker Compose installation..."
  
  # Check if Docker is installed
  if ! command_exists "docker"; then
    log "❌ Docker is not installed. Please install Docker first."
    exit 1
  fi
  
  # Check if Docker Compose plugin is already installed
  if command_exists "docker compose"; then
    log "✅ Docker Compose plugin is already installed"
    docker compose version
  else
    log "Docker Compose plugin is not installed. Attempting to install..."
    install_docker_compose_plugin
  fi
  
  # Check if standalone Docker Compose is already installed
  if command_exists "docker-compose"; then
    log "✅ Standalone Docker Compose is already installed"
    docker-compose --version
  else
    log "Standalone Docker Compose is not installed. Attempting to install..."
    
    # Try apt installation first
    if ! install_docker_compose_apt; then
      # If apt installation fails, try direct download
      if ! install_docker_compose_standalone; then
        log "❌ All installation methods failed. Please install Docker Compose manually."
        exit 1
      fi
    fi
  fi
  
  # Final verification
  log "Verifying Docker Compose installations..."
  
  # Check plugin version
  if command_exists "docker compose"; then
    log "Docker Compose plugin version:"
    docker compose version
  else
    log "⚠️ Docker Compose plugin is not available"
  fi
  
  # Check standalone version
  if command_exists "docker-compose"; then
    log "Standalone Docker Compose version:"
    docker-compose --version
  else
    log "⚠️ Standalone Docker Compose is not available"
  fi
  
  # Ensure at least one version is installed
  if command_exists "docker compose" || command_exists "docker-compose"; then
    log "✅ Docker Compose installation completed successfully"
    return 0
  else
    log "❌ Docker Compose installation failed"
    return 1
  fi
}

# Run the main function
main
