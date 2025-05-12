# GitHub Actions Disk Space Management

This document provides guidance on managing disk space in GitHub Actions workflows, particularly for workflows that use Docker and Docker Compose.

## Common Disk Space Issues

GitHub Actions runners have limited disk space (typically around 14GB for Ubuntu runners). Workflows that use Docker can quickly exhaust this space due to:

1. **Docker images and layers**: Docker images, especially large ones, can consume significant disk space.
2. **Docker volumes**: Persistent volumes can accumulate data over time.
3. **Build artifacts**: Generated artifacts, logs, and temporary files can fill up disk space.
4. **Concurrent processes**: Multiple processes running simultaneously can compete for disk space.

## Implemented Solutions

The following solutions have been implemented in our workflows to address disk space issues:

### 1. Early Cleanup

At the beginning of the workflow, we perform cleanup operations to free up disk space:

```yaml
- name: Clean up runner workspace
  run: |
    echo "Cleaning up runner workspace..."
    rm -rf /tmp/* || true
    sudo apt-get clean
    echo "Disk space after workspace cleanup:"
    df -h

- name: Clean up Docker system
  run: |
    echo "Cleaning up unused Docker images, containers, and volumes..."
    docker system prune -a -f --volumes
    echo "Disk space after Docker cleanup:"
    df -h
```

### 2. Disk Space Monitoring

We monitor disk space at critical points throughout the workflow:

```yaml
- name: Check disk space before pulling images
  run: |
    echo "Disk space before pulling images:"
    df -h
```

### 3. Enhanced Docker Image Pulling

We've implemented enhanced retry logic for pulling Docker images with disk space checks:

```yaml
- name: Pull Docker images
  run: |
    # Function to check if we have enough disk space
    check_disk_space() {
      available_space=$(df -m / | awk 'NR==2 {print $4}')
      if [ "$available_space" -lt 500 ]; then
        echo "WARNING: Low disk space detected ($available_space MB). Cleaning up..."
        docker system prune -a -f --volumes
        return 1
      fi
      return 0
    }

    while [ $attempt -le $max_attempts ]; do
      # Check disk space before pulling
      check_disk_space
      
      # Try to pull with a timeout to handle network issues
      if timeout 300s docker pull postgres:15.3-alpine; then
        echo "Successfully pulled postgres:15.3-alpine"
        break
      else
        # Check if we're out of disk space
        available_space=$(df -m / | awk 'NR==2 {print $4}')
        echo "Available disk space: $available_space MB"
        
        if [ "$available_space" -lt 100 ]; then
          echo "CRITICAL: Extremely low disk space. Performing emergency cleanup..."
          docker system prune -a -f --volumes
          rm -rf /tmp/* || true
          sudo apt-get clean
        fi
        
        # Fallback to smaller image if all attempts fail
        if [ $attempt -eq $max_attempts ]; then
          echo "Trying to use a smaller alternative image as fallback..."
          if docker pull postgres:14-alpine; then
            echo "Successfully pulled postgres:14-alpine as fallback"
            sed -i 's/postgres:15.3-alpine/postgres:14-alpine/g' docker-compose.yml
            break
          fi
        fi
      fi
    done
```

### 4. Emergency Cleanup During Health Checks

During health checks, we periodically check disk space and perform emergency cleanup if needed:

```yaml
# Check disk space during health checks
if [ $((i % 5)) -eq 0 ]; then  # Check every 5 attempts
  echo "Disk space during Flask app health check (attempt $i):"
  df -h
  
  # If disk space is critically low, perform emergency cleanup
  available_space=$(df -m / | awk 'NR==2 {print $4}')
  if [ "$available_space" -lt 100 ]; then
    echo "CRITICAL: Low disk space during Flask app health check. Performing emergency cleanup..."
    docker system prune -a -f --volumes
    rm -rf /tmp/* || true
    sudo apt-get clean
  fi
fi
```

### 5. Comprehensive Debugging Information

We collect comprehensive debugging information, including disk space usage, to help diagnose issues:

```yaml
- name: Debugging logs (always run)
  if: always()
  run: |
    echo "Collecting comprehensive debugging information..."
    
    echo "===== SYSTEM INFORMATION ====="
    echo "Disk space:"
    df -h
    echo "Memory usage:"
    free -m
    # Additional system information...
    
    echo "===== DOCKER INFORMATION ====="
    echo "Docker disk usage:"
    docker system df -v || true
    # Additional Docker information...
    
    # Final cleanup to free space for artifact uploads
    echo "===== FINAL CLEANUP ====="
    echo "Performing final cleanup to free space for artifact uploads..."
    docker system prune -a -f --volumes || true
    rm -rf /tmp/* || true
    sudo apt-get clean || true
    echo "Final disk space:"
    df -h
```

## Best Practices for Future Workflows

1. **Monitor disk space**: Add disk space monitoring steps at critical points in your workflow.
2. **Clean up early**: Perform cleanup operations at the beginning of the workflow.
3. **Use smaller images**: Use Alpine-based images when possible to reduce disk space usage.
4. **Implement retry logic**: Add retry logic with disk space checks for operations that might fail due to disk space issues.
5. **Add fallback mechanisms**: Implement fallback mechanisms for critical operations.
6. **Collect comprehensive debugging information**: Collect detailed information to help diagnose issues.
7. **Set Docker Hub credentials**: Set `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets to avoid rate limiting.

## Troubleshooting

If you encounter disk space issues in GitHub Actions workflows:

1. Check the disk space usage at different points in the workflow using `df -h`.
2. Check Docker disk usage using `docker system df -v`.
3. Identify large files or directories using `du -h --max-depth=1 /path/to/directory`.
4. Add cleanup steps before operations that consume significant disk space.
5. Consider using self-hosted runners with more disk space for workflows that require it.
