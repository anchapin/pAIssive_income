# Docker Compose in GitHub Actions

This document provides guidance on setting up and using Docker Compose in GitHub Actions workflows.

## Available Approaches

There are two main approaches to setting up Docker Compose in GitHub Actions:

### 1. Direct Installation (Recommended)

This approach installs Docker and Docker Compose directly in the runner:

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
    docker-compose --version || {
      echo "Docker Compose installation failed. Trying alternative method..."
      sudo mkdir -p /usr/local/lib/docker/cli-plugins
      sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker-compose
      sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
      docker compose version
    }
```

### 2. Using Docker's Official GitHub Action

This approach uses Docker's official GitHub Action to set up Docker and Docker Compose:

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v2
  with:
    version: latest
```

## Troubleshooting

### Common Issues

1. **Dependency Conflicts**:
   - Problem: `containerd.io` conflicts with `containerd`
   - Solution: Use `--no-install-recommends` flag with `apt-get install` to avoid installing unnecessary dependencies

2. **Docker Compose Not Found**:
   - Problem: `docker-compose: command not found`
   - Solution: Ensure Docker Compose is installed in a directory that's in the PATH, or use the full path to the executable

3. **Permission Issues**:
   - Problem: Permission denied when running Docker Compose
   - Solution: Ensure the Docker Compose binary is executable with `chmod +x`

4. **Network Issues**:
   - Problem: Unable to download Docker Compose
   - Solution: Add retry logic or use a mirror

## Best Practices

1. **Version Pinning**: Always pin the Docker Compose version to ensure consistent behavior
2. **Verification**: Always verify the installation with `docker-compose --version`
3. **Fallback Mechanisms**: Implement fallback mechanisms for installation
4. **Cleanup**: Always clean up resources with `docker-compose down -v` in an `always()` step

## Example Workflows

See the following workflow files for examples:
- `.github/workflows/docker-compose-check.yml`
- `.github/workflows/docker-compose-integration.yml`
- `.github/workflows/docker-compose-alternative.yml` (alternative approach using Docker's official GitHub Action)
