# Docker Compose in GitHub Actions

This document provides guidance on setting up and using Docker Compose in GitHub Actions workflows.

## Recommended Approach

The recommended approach is to use Docker's official GitHub Action to set up Docker Buildx, which includes Docker Compose:

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v2

# Docker Compose is included with Docker Buildx setup
# Verify Docker Compose installation
- name: Verify Docker Compose installation
  run: |
    docker compose version || docker-compose --version
```

This approach:

1. Uses the official Docker Buildx GitHub Action
2. Avoids dependency conflicts with `containerd`
3. Ensures Docker Compose is properly installed and available
4. Works with both the `docker compose` (new) and `docker-compose` (legacy) commands

## Alternative Approaches

### Manual Installation (Not Recommended)

This approach installs Docker and Docker Compose directly in the runner, but may cause dependency conflicts:

```yaml
- name: Set up Docker Compose
  run: |
    # Update package lists
    sudo apt-get update

    # Install Docker CLI only (avoid containerd conflicts)
    sudo apt-get install -y --no-install-recommends docker.io

    # Install Docker Compose directly from GitHub releases
    DOCKER_COMPOSE_VERSION="v2.20.2"
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose

    # Verify installation
    docker-compose --version
```

## Troubleshooting

### Common Issues

1. **Dependency Conflicts**:
   - Problem: `containerd.io` conflicts with `containerd` when installing Docker CLI manually
   - Solution: Use the official Docker Buildx GitHub Action instead of manual installation

2. **Docker Compose Command Not Found**:
   - Problem: `docker-compose: command not found` or `docker compose: command not found`
   - Solution: Verify installation with both command formats and provide fallbacks:

     ```bash
     docker compose version || docker-compose --version
     ```

3. **Command Compatibility**:
   - Problem: Different versions of Docker Compose use different command formats
   - Solution: Support both command formats in your workflow:

     ```bash
     docker compose up -d || docker-compose up -d
     ```

4. **Health Check Failures**:
   - Problem: Flask app or other services not becoming healthy in time
   - Solution: Increase wait time, add more detailed logging, and check container logs:

     ```bash
     docker compose logs || docker-compose logs
     ```

5. **Resource Cleanup**:
   - Problem: Resources not being cleaned up after workflow completion
   - Solution: Use the `always()` condition to ensure cleanup runs even if previous steps fail:

     ```yaml
     - name: Tear down Docker Compose
       if: always()
       run: docker compose down -v || docker-compose down -v
     ```

## Best Practices

1. **Use Official Actions**: Use the official Docker Buildx GitHub Action for the most reliable setup
2. **Command Compatibility**: Support both `docker compose` and `docker-compose` commands for maximum compatibility
3. **Version Pinning**: Pin the Docker Buildx action version to ensure consistent behavior
4. **Verification**: Always verify the installation with version checks
5. **Cleanup**: Always clean up resources with `docker compose down -v` in an `always()` step
6. **Error Handling**: Use fallback mechanisms and proper error handling in all Docker Compose commands

## Enhanced Health Check Mechanisms

Recent updates to our Docker Compose workflows include improved health check mechanisms:

1. **Progressive Timeouts**:
   - Gradually increasing timeouts for health checks to allow slower services more time to start
   - Example:

     ```yaml
     timeout=$((10 + i / 5))
     echo "Attempt $i of $max_attempts: Checking Flask app health with $timeout second timeout..."
     ```

2. **Detailed Diagnostics**:
   - More verbose health check output for better troubleshooting
   - Container status checks at regular intervals
   - Process verification inside containers
   - Example:

     ```yaml
     # Check if the container is actually running
     echo "Checking if Flask app container is running:"
     docker ps | grep paissive-income-app

     # Check if Flask process is running
     echo "Checking for Python/Flask process:"
     docker compose exec app ps aux | grep python
     ```

3. **Fallback Health Check Methods**:
   - Multiple methods to verify service health (curl, wget, netcat)
   - Example:

     ```yaml
     if curl -v -f -m $timeout http://localhost:5000/health 2>/dev/null; then
       echo "SUCCESS: Flask app is healthy!"
     elif wget -O- -T $timeout http://localhost:5000/health 2>/dev/null; then
       echo "SUCCESS: Flask app is healthy (verified with wget)!"
     else
       echo "Health check failed on attempt $i/$max_attempts"
     fi
     ```

## Disk Space Management

Our Docker Compose workflows now include proactive disk space management:

1. **Monitoring**:
   - Regular disk space checks throughout the workflow
   - Example:

     ```yaml
     echo "Disk space before pulling images:"
     df -h
     ```

2. **Cleanup Operations**:
   - Automatic cleanup when disk space is low
   - Progressive cleanup strategies based on severity
   - Example:

     ```yaml
     available_space=$(df -m / | awk 'NR==2 {print $4}')
     if [ "$available_space" -lt 1000 ]; then
       echo "WARNING: Low disk space detected ($available_space MB). Performing cleanup..."
       docker system prune -a -f --volumes
       rm -rf /tmp/* || true
       sudo apt-get clean
     fi
     ```

3. **Emergency Measures**:
   - Aggressive cleanup for critical disk space situations
   - Removal of non-essential large directories
   - Example:

     ```yaml
     if [ "$available_space" -lt 500 ]; then
       echo "CRITICAL: Still low on disk space. Removing additional files..."
       sudo rm -rf /var/lib/apt/lists/* || true
       sudo rm -rf /usr/share/dotnet || true
       sudo rm -rf /usr/local/lib/android || true
     fi
     ```

## Robust Error Handling

Our workflows now include enhanced error handling mechanisms:

1. **Exponential Backoff**:
   - Retry logic with exponential backoff for network operations
   - Example:

     ```yaml
     backoff_time=$((5 * 2 ** (attempt - 1) + RANDOM % 5))
     echo "Using backoff time of $backoff_time seconds if this attempt fails"
     ```

2. **Fallback Mechanisms**:
   - Multiple fallback options for critical operations
   - Alternative registries for Docker images
   - Example:

     ```yaml
     if [ $attempt -ge 3 ] && [ $attempt -lt $max_attempts ]; then
       echo "Trying alternative registry for postgres:15.3-alpine..."
       if timeout 300s docker pull mcr.microsoft.com/mirror/docker/library/postgres:15.3-alpine 2>/dev/null; then
         echo "Successfully pulled postgres:15.3-alpine from Microsoft mirror"
         docker tag mcr.microsoft.com/mirror/docker/library/postgres:15.3-alpine postgres:15.3-alpine
         break
       fi
     fi
     ```

3. **Comprehensive Diagnostics**:
   - Detailed logging at each stage
   - System status reporting for failures
   - Example:

     ```yaml
     echo "===== SYSTEM INFORMATION ====="
     echo "Disk space:"
     df -h
     echo "Memory usage:"
     free -m
     echo "CPU information:"
     lscpu || cat /proc/cpuinfo
     ```

## Example Workflows

See the following workflow files for examples:

- `.github/workflows/docker-compose-integration.yml` - Enhanced integration workflow with robust health checks, disk space management, and error handling
- `.github/workflows/docker-compose-alternative.yml` - Alternative approach using Docker's official GitHub Action with improved health checks
