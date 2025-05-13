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

## Example Workflows

See the following workflow files for examples:

- `.github/workflows/docker-compose-check.yml`
- `.github/workflows/docker-compose-integration.yml`
- `.github/workflows/docker-compose-alternative.yml` (alternative approach using Docker's official GitHub Action)
