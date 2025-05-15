#!/bin/bash
# Script to run Docker Compose in CI environment

# Enable error handling
set -e

# Log with timestamp
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to determine Docker Compose command
get_compose_cmd() {
  if command -v docker compose >/dev/null 2>&1; then
    echo "docker compose"
  elif command -v docker-compose >/dev/null 2>&1; then
    echo "docker-compose"
  else
    log "❌ Docker Compose not found"
    return 1
  fi
}

# Function to check if network exists
check_network() {
  local network_name="$1"
  if docker network inspect "$network_name" >/dev/null 2>&1; then
    log "✅ Network '$network_name' exists"
    return 0
  else
    log "❌ Network '$network_name' does not exist"
    return 1
  fi
}

# Function to create network
create_network() {
  local network_name="$1"
  log "Creating network '$network_name'..."
  if docker network create "$network_name"; then
    log "✅ Network '$network_name' created"
    return 0
  else
    log "❌ Failed to create network '$network_name'"
    return 1
  fi
}

# Function to pull images
pull_images() {
  log "Pulling Docker images..."
  
  # Pull PostgreSQL image
  log "Pulling PostgreSQL image..."
  if ! docker pull postgres:15.3-alpine; then
    log "⚠️ Failed to pull postgres:15.3-alpine, trying fallback images..."
    
    # Try fallback images
    for fallback_image in "postgres:14-alpine" "postgres:13-alpine" "postgres:alpine"; do
      log "Trying fallback image: $fallback_image"
      if docker pull "$fallback_image"; then
        log "✅ Successfully pulled fallback image: $fallback_image"
        
        # Update docker-compose.yml to use fallback image
        log "Updating docker-compose.yml to use fallback image..."
        sed -i "s|postgres:15.3-alpine|$fallback_image|g" docker-compose.yml
        
        break
      fi
    done
  else
    log "✅ Successfully pulled postgres:15.3-alpine"
  fi
  
  # Pull Node.js image if frontend exists
  if [ -d "ui/react_frontend" ]; then
    log "Pulling Node.js image..."
    if ! docker pull node:18-alpine; then
      log "⚠️ Failed to pull node:18-alpine, trying fallback images..."
      
      # Try fallback images
      for fallback_image in "node:16-alpine" "node:14-alpine"; do
        log "Trying fallback image: $fallback_image"
        if docker pull "$fallback_image"; then
          log "✅ Successfully pulled fallback image: $fallback_image"
          
          # Update Dockerfile.dev to use fallback image
          if [ -f "ui/react_frontend/Dockerfile.dev" ]; then
            log "Updating Dockerfile.dev to use fallback image..."
            sed -i "s|FROM node:18-alpine|FROM $fallback_image|g" ui/react_frontend/Dockerfile.dev
          fi
          
          break
        fi
      done
    else
      log "✅ Successfully pulled node:18-alpine"
    fi
  fi
}

# Function to start services
start_services() {
  local compose_cmd="$1"
  log "Starting services with $compose_cmd..."
  
  # Use CI-specific configuration if available
  if [ -f "docker-compose.ci.yml" ]; then
    log "Using CI-specific configuration..."
    $compose_cmd -f docker-compose.yml -f docker-compose.ci.yml up -d --build
  else
    log "Using default configuration..."
    $compose_cmd up -d --build
  fi
  
  # Check if services started
  log "Checking if services started..."
  $compose_cmd ps
}

# Function to wait for services to be healthy
wait_for_services() {
  local compose_cmd="$1"
  local max_attempts=30
  local attempt=1
  
  log "Waiting for services to be healthy..."
  
  while [ $attempt -le $max_attempts ]; do
    log "Attempt $attempt of $max_attempts..."
    
    # Check if all services are running
    local running_services=$($compose_cmd ps --services --filter "status=running" | wc -l)
    local total_services=$($compose_cmd ps --services | wc -l)
    
    log "Running services: $running_services of $total_services"
    
    if [ "$running_services" -eq "$total_services" ]; then
      log "✅ All services are running"
      
      # Check if database is ready
      if docker exec paissive-postgres pg_isready -U myuser -d mydb >/dev/null 2>&1; then
        log "✅ Database is ready"
        return 0
      else
        log "⚠️ Database is not ready yet"
      fi
    fi
    
    # Sleep before next attempt
    sleep 10
    attempt=$((attempt + 1))
  done
  
  log "❌ Services did not become healthy within the timeout period"
  return 1
}

# Main function
main() {
  log "Starting Docker Compose CI script..."
  
  # Get Docker Compose command
  local compose_cmd
  compose_cmd=$(get_compose_cmd)
  
  if [ $? -ne 0 ]; then
    log "❌ Docker Compose not found. Exiting."
    exit 1
  fi
  
  log "Using Docker Compose command: $compose_cmd"
  
  # Check if network exists
  if ! check_network "paissive-network"; then
    # Create network
    if ! create_network "paissive-network"; then
      log "❌ Failed to create network. Exiting."
      exit 1
    fi
  fi
  
  # Pull images
  pull_images
  
  # Start services
  start_services "$compose_cmd"
  
  # Wait for services to be healthy
  if ! wait_for_services "$compose_cmd"; then
    log "❌ Services did not become healthy. Showing logs..."
    $compose_cmd logs
    exit 1
  fi
  
  log "✅ Docker Compose CI script completed successfully."
}

# Run the main function
main
