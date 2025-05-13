# Docker Compose Workflows

This document provides detailed information about the Docker Compose workflows used in our GitHub Actions CI/CD pipeline.

## Overview

Our project uses two main Docker Compose workflows:

1. **docker-compose-integration.yml**: A comprehensive workflow for Docker Compose integration testing with robust error handling, health checks, and disk space management.
2. **docker-compose-alternative.yml**: An alternative approach using Docker's official GitHub Action with improved health checks.

## docker-compose-integration.yml

The `docker-compose-integration.yml` workflow is designed to provide a robust and reliable Docker Compose integration testing environment with comprehensive error handling, health checks, and resource management.

### Key Features

#### 1. Resource Management

- **Initial Cleanup**: Performs cleanup of runner workspace and Docker system before starting
  ```yaml
  - name: Clean up runner workspace
    run: |
      echo "Cleaning up runner workspace..."
      rm -rf /tmp/* || true
      sudo apt-get clean
  ```

- **Proactive Disk Space Monitoring**: Regularly checks available disk space throughout the workflow
  ```yaml
  - name: Check disk space before pulling images
    run: |
      echo "Disk space before pulling images:"
      df -h
  ```

- **Automatic Cleanup**: Performs cleanup when disk space is low
  ```yaml
  available_space=$(df -m / | awk 'NR==2 {print $4}')
  if [ "$available_space" -lt 1000 ]; then
    echo "WARNING: Low disk space detected ($available_space MB). Performing cleanup..."
    docker system prune -a -f --volumes
    rm -rf /tmp/* || true
    sudo apt-get clean
  fi
  ```

#### 2. Docker Image Management

- **Enhanced Image Pulling**: Robust image pulling with retry logic and exponential backoff
  ```yaml
  while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt of $max_attempts to pull postgres:15.3-alpine"
    
    # Calculate backoff time (exponential with jitter)
    backoff_time=$((5 * 2 ** (attempt - 1) + RANDOM % 5))
    
    if timeout 300s docker pull postgres:15.3-alpine; then
      echo "Successfully pulled postgres:15.3-alpine"
      break
    else
      echo "Failed to pull postgres:15.3-alpine on attempt $attempt"
      sleep $backoff_time
      attempt=$((attempt+1))
    fi
  done
  ```

- **Fallback Mechanisms**: Uses alternative registries and image versions when primary options fail
  ```yaml
  # Try multiple fallback images in order of preference
  for fallback_image in "postgres:14-alpine" "postgres:13-alpine" "postgres:alpine"; do
    echo "Trying fallback image: $fallback_image"
    if timeout 180s docker pull $fallback_image; then
      echo "Successfully pulled $fallback_image as fallback"
      # Update docker-compose.yml to use the fallback image
      sed -i "s|postgres:15.3-alpine|$fallback_image|g" docker-compose.yml
      break
    fi
  done
  ```

#### 3. Health Checks

- **Database Health Verification**: Comprehensive database health checks with detailed diagnostics
  ```yaml
  # Check database readiness with more detailed diagnostics
  echo "Checking if PostgreSQL is accepting connections..."
  if docker compose exec db pg_isready -U myuser -d mydb -h db; then
    echo "Database is ready and accepting connections."
    
    # Verify we can actually connect and run a simple query
    echo "Verifying database connection with a simple query..."
    if docker compose exec db psql -U myuser -d mydb -c "SELECT 1"; then
      echo "Database connection verified successfully."
      break
    fi
  fi
  ```

- **Application Health Verification**: Robust application health checks with multiple verification methods
  ```yaml
  # Try different methods to check health
  if curl -v -f -m $timeout http://localhost:5000/health 2>/dev/null; then
    echo "SUCCESS: Flask app is healthy!"
    exit 0
  elif wget -O- -T $timeout http://localhost:5000/health 2>/dev/null; then
    echo "SUCCESS: Flask app is healthy (verified with wget)!"
    exit 0
  else
    echo "Health check failed on attempt $i/$max_attempts"
  fi
  ```

#### 4. Comprehensive Diagnostics

- **Detailed Logging**: Extensive logging at each stage of the workflow
  ```yaml
  echo "===== SYSTEM INFORMATION ====="
  echo "Disk space:"
  df -h
  echo "Memory usage:"
  free -m
  echo "CPU information:"
  lscpu || cat /proc/cpuinfo
  echo "System load:"
  uptime
  ```

- **Container Inspection**: Detailed container inspection for troubleshooting
  ```yaml
  echo "Docker container inspection (app):"
  docker inspect $(docker ps -q -f name=paissive-income-app) || true
  echo "Docker container health status (app):"
  docker inspect --format='{{json .State.Health}}' $(docker ps -q -f name=paissive-income-app) || true
  ```

## docker-compose-alternative.yml

The `docker-compose-alternative.yml` workflow provides an alternative approach using Docker's official GitHub Action with improved health checks.

### Key Features

#### 1. Official Docker Buildx Action

- Uses Docker's official GitHub Action to set up Docker Buildx
  ```yaml
  - name: Set up Docker Buildx
    uses: docker/setup-buildx-action@v2
    with:
      version: latest
  ```

#### 2. Network Creation

- Explicitly creates Docker network before starting services
  ```yaml
  - name: Create Docker network
    run: |
      echo "Creating Docker network paissive-network..."
      docker network inspect paissive-network >/dev/null 2>&1 || docker network create paissive-network
  ```

#### 3. Enhanced Health Checks

- Improved health checks with detailed diagnostics
  ```yaml
  - name: Wait for Flask app to be healthy
    run: |
      echo "Waiting for Flask app to be healthy..."
      max_attempts=50  # Increased from 30 to 50
      for i in $(seq 1 $max_attempts); do
        # More verbose curl for better diagnostics
        echo "Attempt $i: Checking Flask app health..."
        if curl -v -f -m 10 http://localhost:5000/health; then
          echo "Flask app is healthy."
          exit 0
        else
          echo "Waiting for Flask app... (attempt $i/$max_attempts)"
          
          # Check container status
          echo "Container status:"
          docker compose ps app || docker-compose ps app || true
          
          # On every 5th attempt, check the logs
          if [ $(($i % 5)) -eq 0 ]; then
            echo "Checking Flask app logs at attempt $i:"
            docker compose logs app || docker-compose logs app
          fi
          
          sleep 10  # Increased from 5 to 10 seconds
        fi
      done
  ```

## Best Practices

Based on our Docker Compose workflows, we recommend the following best practices:

1. **Use Official Docker Actions**: Leverage Docker's official GitHub Actions for the most reliable setup
2. **Implement Robust Health Checks**: Use comprehensive health checks with multiple verification methods
3. **Manage Resources Proactively**: Monitor and manage disk space throughout the workflow
4. **Implement Fallback Mechanisms**: Provide fallback options for critical operations
5. **Use Exponential Backoff**: Implement retry logic with exponential backoff for network operations
6. **Provide Detailed Diagnostics**: Include comprehensive logging and diagnostics for troubleshooting
7. **Support Command Compatibility**: Support both `docker compose` and `docker-compose` commands for maximum compatibility
8. **Always Clean Up Resources**: Ensure resources are cleaned up even if the workflow fails

## Conclusion

Our Docker Compose workflows provide robust and reliable integration testing environments with comprehensive error handling, health checks, and resource management. By following the best practices outlined in this document, you can ensure your Docker Compose workflows are reliable and maintainable.
