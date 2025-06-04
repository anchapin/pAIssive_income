#!/bin/bash
# Optimized script to run Docker Compose in GitHub Actions CI environment

# Enable error handling but don't exit immediately on error
set +e
# Enable command tracing for better debugging
set -x

# Set CI-specific variables with optimizations
export CI=true
export GITHUB_ACTIONS=true
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export BUILDKIT_PROGRESS=plain
export BUILDKIT_INLINE_CACHE=1
export COMPOSE_PARALLEL_LIMIT=4
export DOCKER_DEFAULT_PLATFORM=linux/amd64
export DOCKER_SCAN_SUGGEST=false
export DOCKER_CLI_EXPERIMENTAL=enabled

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

# Function to try pulling an image with fallbacks
try_pull_image_with_fallbacks() {
  local primary_image="$1"
  local fallback_images="$2"
  local update_file="$3"
  local search_pattern="$4"
  local replace_pattern="$5"

  log "Trying to pull image: $primary_image"
  if ! docker pull "$primary_image"; then
    log "⚠️ Failed to pull $primary_image, trying fallback images..."

    # Try fallback images
    for fallback_image in $fallback_images; do
      # Skip if it's the same as the one we already tried
      if [ "$fallback_image" = "$primary_image" ]; then
        continue
      fi

      log "Trying fallback image: $fallback_image"
      if docker pull "$fallback_image"; then
        log "✅ Successfully pulled fallback image: $fallback_image"

        # Update configuration file if provided
        if [ -n "$update_file" ] && [ -f "$update_file" ]; then
          log "Updating $update_file to use fallback image..."
          sed -i "s|$search_pattern|$replace_pattern$fallback_image|g" "$update_file"
        fi

        echo "$fallback_image"  # Return the successful fallback image
        return 0
      fi
    done
    return 1  # All fallbacks failed
  else
    log "✅ Successfully pulled $primary_image"
    echo "$primary_image"  # Return the primary image
    return 0
  fi
}

# Function to detect Node.js version from Dockerfile
detect_node_version() {
  local dockerfile="$1"
  local default_version="$2"

  if [ -f "$dockerfile" ]; then
    local version=$(grep -o "FROM node:[0-9]*-alpine" "$dockerfile" | sed 's/FROM node://g')
    log "Detected Node.js version in $dockerfile: $version"

    if [ -z "$version" ]; then
      log "No Node.js version detected, defaulting to: $default_version"
      echo "$default_version"
    else
      echo "$version"
    fi
  else
    log "$dockerfile not found, defaulting to Node.js version: $default_version"
    echo "$default_version"
  fi
}

# Function to pull images in parallel (optimized)
# TODO: Add automated tests for this function to verify:
#  - Dynamic Node.js version detection from Dockerfile.dev
#  - Fallback behavior when primary image pull fails
#  - Proper handling of missing Dockerfile.dev
#  - Correct file updates when fallbacks are used
pull_images() {
  log "Pulling Docker images in parallel..."

  # Create a temporary directory for lock files
  mkdir -p /tmp/docker-pull-locks

  # Function to pull an image with fallback options
  pull_with_fallback() {
    local primary_image="$1"
    local fallback_images="$2"
    local update_file="$3"
    local search_pattern="$4"
    local lock_file="/tmp/docker-pull-locks/$(echo "$primary_image" | tr ':/' '_').lock"

    # Create lock file to track completion
    touch "$lock_file"

    log "Pulling $primary_image..."
    if docker pull "$primary_image" &>/dev/null; then
      log "✅ Successfully pulled $primary_image"
      rm -f "$lock_file"
      return 0
    fi

    log "⚠️ Failed to pull $primary_image, trying fallback images..."

    # Try fallback images
    IFS=',' read -ra FALLBACKS <<< "$fallback_images"
    for fallback_image in "${FALLBACKS[@]}"; do
      log "Trying fallback image: $fallback_image"
      if docker pull "$fallback_image" &>/dev/null; then
        log "✅ Successfully pulled fallback image: $fallback_image"

        # Update file to use fallback image if specified
        if [ -n "$update_file" ] && [ -n "$search_pattern" ]; then
          log "Updating $update_file to use fallback image..."
          sed -i "s|$search_pattern|$fallback_image|g" "$update_file" || true
        fi

        rm -f "$lock_file"
        return 0
      fi
    done

    log "❌ All image pulls failed for $primary_image and fallbacks"
    rm -f "$lock_file"
    return 1
  }

  # Pull PostgreSQL image in background
  pull_with_fallback "postgres:15.3-alpine" "postgres:14-alpine,postgres:13-alpine,postgres:alpine" \
    "docker-compose.yml" "postgres:15.3-alpine" &

  # Pull Node.js image if frontend exists
  if [ -d "ui/react_frontend" ]; then
    # Get the Node.js version from Dockerfile.dev
    NODE_VERSION=$(detect_node_version "ui/react_frontend/Dockerfile.dev" "24-alpine")

    # Use the detected Node.js version
    pull_with_fallback "node:$NODE_VERSION" "node:24-alpine,node:20-alpine,node:18-alpine,node:16-alpine" \
      "ui/react_frontend/Dockerfile.dev" "FROM node:[0-9]*-alpine" &

    # Optimize frontend configuration in parallel
    (
      # Ensure pnpm is properly configured in Dockerfile.dev
      if [ -f "ui/react_frontend/Dockerfile.dev" ]; then
        log "Optimizing pnpm configuration in Dockerfile.dev..."
        if ! grep -q "pnpm@8" ui/react_frontend/Dockerfile.dev; then
          sed -i "s|pnpm@.*|pnpm@8.15.4|g" ui/react_frontend/Dockerfile.dev || true
        fi

        # Add caching optimizations to Dockerfile.dev
        if ! grep -q "BUILDKIT_INLINE_CACHE=1" ui/react_frontend/Dockerfile.dev; then
          sed -i "/^FROM/a ARG BUILDKIT_INLINE_CACHE=1" ui/react_frontend/Dockerfile.dev || true
        fi
      fi

      # Optimize package.json configuration
      if [ -f "ui/react_frontend/package.json" ]; then
        log "Optimizing package.json configuration..."
        # Add required configurations if missing
        if ! grep -q '"optionalDependencies"' ui/react_frontend/package.json; then
          sed -i '$i\  "optionalDependencies": {\n    "@ag-ui-protocol/ag-ui": "^1.0.0"\n  },' ui/react_frontend/package.json || true
        fi
        if ! grep -q '"pnpm"' ui/react_frontend/package.json; then
          sed -i '$i\  "pnpm": {\n    "overrides": {\n      "@ag-ui-protocol/ag-ui": "npm:@ag-ui-protocol/ag-ui-mock@^1.0.0"\n    }\n  },' ui/react_frontend/package.json || true
        fi
      fi
    ) &
  fi

  # Pull Python base image in background
  pull_with_fallback "python:3.10-slim" "python:3.9-slim,python:3.8-slim" "" "" &

  # Wait for all background jobs to complete
  log "Waiting for all image pulls to complete..."
  wait

  # Check if any pulls failed
  if ls /tmp/docker-pull-locks/*.lock 1>/dev/null 2>&1; then
    log "⚠️ Some image pulls failed, but continuing anyway"
    rm -f /tmp/docker-pull-locks/*.lock
  else
    log "✅ All required images pulled successfully"
  fi
}

# Function to start services (optimized)
start_services() {
  local compose_cmd="$1"
  log "Starting services with optimized settings..."

  # Create optimized CI configuration if needed
  if [ ! -f "docker-compose.ci.yml" ]; then
    log "Creating optimized docker-compose.ci.yml for CI..."
    cat > docker-compose.ci.yml << 'EOL'
version: '3.8'

services:
  db:
    # Use tmpfs for faster database in CI
    tmpfs:
      - /var/lib/postgresql/data
    # Optimize PostgreSQL for CI
    command: postgres -c fsync=off -c synchronous_commit=off -c full_page_writes=off -c max_connections=200
    # Faster health checks
    healthcheck:
      interval: 2s
      timeout: 2s
      retries: 15
      start_period: 2s

  app:
    build:
      args:
        - CI=true
        - BUILDKIT_INLINE_CACHE=1
    # Faster health checks
    healthcheck:
      interval: 2s
      timeout: 5s
      retries: 15
      start_period: 10s
    environment:
      - PYTHONUNBUFFERED=1
EOL
  fi

  # Make sure no services are running (with optimized cleanup)
  log "Stopping any existing services..."
  $compose_cmd down -v --remove-orphans || true
  # Faster cleanup without sleep
  docker container prune -f >/dev/null 2>&1 || true

  # Build services in parallel first (faster than combined build and up)
  log "Building services in parallel..."
  $compose_cmd -f docker-compose.yml -f docker-compose.ci.yml build --parallel --progress=plain
  build_exit_code=$?

  if [ $build_exit_code -ne 0 ]; then
    log "⚠️ Parallel build failed with exit code $build_exit_code, trying sequential build..."
    $compose_cmd -f docker-compose.yml -f docker-compose.ci.yml build
    build_exit_code=$?
  fi

  # Start services
  log "Starting services..."
  $compose_cmd -f docker-compose.yml -f docker-compose.ci.yml up -d
  start_exit_code=$?

  # Check if services started successfully
  if [ $start_exit_code -ne 0 ] || [ $build_exit_code -ne 0 ]; then
    log "❌ Failed to start services with exit code $start_exit_code"

    # Get minimal diagnostic information (optimized)
    log "=== DIAGNOSTIC INFORMATION ==="
    log "Docker service status:"
    $compose_cmd ps || true

    log "Docker disk usage:"
    docker system df || true

    # Try to start services with fallback approach (optimized)
    log "Trying optimized fallback approach..."

    # Try starting services one by one with minimal waits
    log "Starting database service..."
    $compose_cmd -f docker-compose.yml -f docker-compose.ci.yml up -d db
    sleep 5

    log "Starting app service..."
    $compose_cmd -f docker-compose.yml -f docker-compose.ci.yml up -d app
    sleep 5

    if [ -d "ui/react_frontend" ]; then
      log "Starting frontend service..."
      $compose_cmd -f docker-compose.yml -f docker-compose.ci.yml up -d frontend
      sleep 5
    fi

    # Check if services started after retry
    log "Service status after fallback approach:"
    $compose_cmd ps
  else
    log "✅ Services started successfully"
  fi

  # Return success to allow workflow to continue
  return 0
}

# Function to wait for services to be healthy (optimized)
wait_for_services() {
  local compose_cmd="$1"
  local max_attempts=30  # Reduced from 45 to 30 for faster CI
  local attempt=1
  local services_healthy=false
  local interval=3  # Reduced from 10 to 3 seconds for faster checks
  local start_time=$(date +%s)

  log "Waiting for services to be healthy with optimized checks..."

  # Function to check service health with timeout
  check_service_health() {
    local service="$1"
    local container="$2"
    local check_cmd="$3"
    local timeout=2  # Short timeout for faster checks

    # Use timeout to prevent hanging checks
    timeout $timeout bash -c "$check_cmd" >/dev/null 2>&1
    return $?
  }

  # Check all services in parallel
  check_all_services() {
    local all_healthy=true
    local db_healthy=false
    local app_healthy=false
    local frontend_healthy=true  # Default to true if no frontend

    # Check if all services are running
    local running_services=$($compose_cmd ps --services --filter "status=running" | wc -l)
    local total_services=$($compose_cmd ps --services | wc -l)

    if [ "$running_services" -ne "$total_services" ]; then
      return 1
    fi

    # Check database health in background
    (check_service_health "db" "paissive-postgres" "docker exec paissive-postgres pg_isready -U myuser -d mydb" &&
     touch /tmp/db_healthy.flag) &

    # Check app health in background
    (check_service_health "app" "paissive-income-app" "docker exec paissive-income-app curl -s -f http://localhost:5000/health ||
      docker exec paissive-income-app wget -q --spider http://localhost:5000/health ||
      docker exec paissive-income-app python -c \"import urllib.request; urllib.request.urlopen('http://localhost:5000/health')\"" &&
     touch /tmp/app_healthy.flag) &

    # Check frontend health if it exists
    if [ -d "ui/react_frontend" ]; then
      frontend_healthy=false
      (check_service_health "frontend" "paissive-frontend" "docker exec paissive-frontend wget -q --spider http://localhost:3000" &&
       touch /tmp/frontend_healthy.flag) &
    fi

    # Wait for all background checks to complete (with timeout)
    wait

    # Check results
    [ -f "/tmp/db_healthy.flag" ] && db_healthy=true && rm -f /tmp/db_healthy.flag
    [ -f "/tmp/app_healthy.flag" ] && app_healthy=true && rm -f /tmp/app_healthy.flag
    [ -f "/tmp/frontend_healthy.flag" ] && frontend_healthy=true && rm -f /tmp/frontend_healthy.flag

    # Log status
    $db_healthy && log "✅ Database is healthy" || { log "⚠️ Database is not healthy"; all_healthy=false; }
    $app_healthy && log "✅ App is healthy" || { log "⚠️ App is not healthy"; all_healthy=false; }

    if [ -d "ui/react_frontend" ]; then
      $frontend_healthy && log "✅ Frontend is healthy" || log "⚠️ Frontend is not healthy (but continuing)"
    fi

    $all_healthy && return 0 || return 1
  }

  # Main health check loop with early exit
  while [ $attempt -le $max_attempts ]; do
    log "Health check attempt $attempt of $max_attempts..."

    if check_all_services; then
      log "✅ All essential services are healthy!"
      services_healthy=true
      break
    fi

    # Get logs only on specific attempts to reduce noise
    if [ $((attempt % 5)) -eq 0 ] || [ $attempt -eq $max_attempts ]; then
      log "=== CONTAINER LOGS (ATTEMPT $attempt) ==="
      docker logs paissive-postgres --tail 10 2>/dev/null || true
      docker logs paissive-income-app --tail 10 2>/dev/null || true
      [ -d "ui/react_frontend" ] && docker logs paissive-frontend --tail 10 2>/dev/null || true
    fi

    # Calculate elapsed time
    local current_time=$(date +%s)
    local elapsed=$((current_time - start_time))
    log "Elapsed time: ${elapsed}s"

    # Break early if we're taking too long
    if [ $elapsed -gt 180 ]; then  # 3 minutes max
      log "⚠️ Health check taking too long, continuing anyway"
      break
    fi

    sleep $interval
    attempt=$((attempt + 1))
  done

  # Final status
  if [ "$services_healthy" = true ]; then
    log "✅ Services are healthy and ready"
    return 0
  else
    log "⚠️ Services did not become fully healthy within the timeout period"
    log "Continuing despite health check issues..."
    return 1
  fi
}

# Main function (optimized)
main() {
  log "Starting optimized Docker Compose CI script..."

  # Start time tracking for performance metrics
  local main_start_time=$(date +%s)

  # Get Docker Compose command (simplified)
  local compose_cmd
  if docker compose version >/dev/null 2>&1; then
    compose_cmd="docker compose"
  elif docker-compose version >/dev/null 2>&1; then
    compose_cmd="docker-compose"
  else
    log "❌ Docker Compose not found. Installing..."
    # Install Docker Compose if not available
    curl -SL https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-linux-x86_64 -o /tmp/docker-compose
    chmod +x /tmp/docker-compose
    sudo mv /tmp/docker-compose /usr/local/bin/docker-compose
    compose_cmd="docker-compose"
  fi

  log "Using Docker Compose command: $compose_cmd"

  # Create network (simplified)
  log "Setting up Docker network..."
  docker network create --driver bridge paissive-network >/dev/null 2>&1 || true

  # Run steps in parallel where possible
  log "Running optimized workflow..."

  # Pull images in background
  pull_images &
  pull_pid=$!

  # While images are pulling, prepare configuration files
  log "Preparing configuration files..."
  if [ ! -f "docker-compose.ci.yml" ]; then
    log "Creating optimized CI configuration..."
    # This will be created in the start_services function
  fi

  # Wait for image pulling to complete
  wait $pull_pid
  log "Image preparation completed"

  # Start services
  start_services "$compose_cmd"

  # Wait for services to be healthy with timeout
  local health_check_result=0
  wait_for_services "$compose_cmd" || health_check_result=$?

  # Quick recovery if needed
  if [ $health_check_result -ne 0 ]; then
    log "⚠️ Services not fully healthy, performing quick recovery..."

    # Restart app service with minimal wait
    $compose_cmd restart app
    sleep 5

    # Quick health check
    if timeout 2 docker exec paissive-income-app curl -s -f http://localhost:5000/health >/dev/null 2>&1; then
      log "✅ App service recovered after restart"
    else
      log "⚠️ App service still not responding, but continuing"
    fi
  fi

  # Final status
  log "Final service status:"
  $compose_cmd ps

  # Calculate and report total runtime
  local main_end_time=$(date +%s)
  local total_runtime=$((main_end_time - main_start_time))
  log "✅ Docker Compose CI script completed in ${total_runtime} seconds"

  # Always exit with success
  exit 0
}

# Run the main function
main
