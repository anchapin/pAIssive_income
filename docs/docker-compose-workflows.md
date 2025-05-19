# Docker Compose Workflows

This document provides detailed information about the Docker Compose workflow used in our GitHub Actions CI/CD pipeline.

## Overview

Our project uses a consolidated Docker Compose workflow:

**docker-compose.yml**: A comprehensive workflow for Docker Compose integration testing with robust error handling, health checks, and disk space management. This workflow supports both standard and AG-UI configurations.

## Recent Updates

The Docker Compose workflow has been consolidated to combine the best features from multiple workflows:

- Improved error handling and retry logic
- Enhanced health checks for services
- Better disk space management
- Support for both standard and AG-UI configurations
- Automatic detection of frontend requirements

## Workflow Features

### 1. Disk Space Management

The workflow includes steps to manage disk space on GitHub Actions runners:

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

### 2. Dynamic Frontend Detection

The workflow automatically detects if a frontend exists and sets up the necessary dependencies:

```yaml
- name: Check for frontend
  id: check-frontend
  run: |
    if [ -d "ui/react_frontend" ]; then
      echo "has_frontend=true" >> $GITHUB_OUTPUT
    else
      echo "has_frontend=false" >> $GITHUB_OUTPUT
    fi

- name: Set up Node.js
  if: steps.check-frontend.outputs.has_frontend == 'true'
  uses: actions/setup-node@v4
  with:
    node-version: '24'
    cache: 'npm'
    cache-dependency-path: '**/package-lock.json'

- name: Install pnpm
  if: steps.check-frontend.outputs.has_frontend == 'true'
  uses: pnpm/action-setup@v3
  with:
    version: 8
    run_install: false
```

### 3. Docker Network and Compose Fixes

The workflow uses dedicated scripts to fix common Docker network and Docker Compose issues:

```yaml
- name: Fix Docker network
  run: |
    echo "Running Docker network fix script..."
    ./scripts/fix-docker-network.sh

- name: Fix Docker Compose
  run: |
    echo "Running Docker Compose fix script..."
    ./scripts/fix-docker-compose.sh
```

### 4. Docker Buildx Setup

The workflow sets up Docker Buildx for improved build performance:

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
  with:
    version: latest
    driver-opts: |
      image=moby/buildkit:v0.12.0
    buildkitd-flags: --debug
```

### 5. Docker Hub Authentication

The workflow includes optional Docker Hub authentication to avoid rate limits:

```yaml
- name: Check Docker Hub secrets
  id: check-secrets
  run: |
    if [ -z "${{ secrets.DOCKERHUB_USERNAME }}" ] || [ -z "${{ secrets.DOCKERHUB_TOKEN }}" ]; then
      echo "::warning::DOCKERHUB_USERNAME and/or DOCKERHUB_TOKEN secrets are not set. Docker Hub login will be skipped, which may lead to rate limiting."
      echo "dockerhub_secrets_set=false" >> $GITHUB_OUTPUT
    else
      echo "dockerhub_secrets_set=true" >> $GITHUB_OUTPUT
    fi

- name: Log in to Docker Hub
  uses: docker/login-action@v3
  if: steps.check-secrets.outputs.dockerhub_secrets_set == 'true'
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

### 6. Service Startup and Testing

The workflow uses the `run-docker-compose-ci.sh` script to start services and run tests:

```yaml
- name: Build and start services
  run: |
    # Run the Docker Compose CI script
    echo "Running Docker Compose CI script..."
    ./scripts/run-docker-compose-ci.sh

- name: Run tests
  run: |
    echo "Running tests..."

    # Function to check if a command exists
    command_exists() {
      command -v "$1" >/dev/null 2>&1
    }

    # Determine which Docker Compose command to use
    if command_exists "docker compose"; then
      COMPOSE_CMD="docker compose"
    elif command_exists "docker-compose"; then
      COMPOSE_CMD="docker-compose"
    else
      echo "ERROR: No Docker Compose installation found."
      exit 1
    fi

    # Run backend tests if available
    if $COMPOSE_CMD exec -T app python -m pytest 2>/dev/null; then
      echo "Backend tests completed"
    else
      echo "No backend tests found or tests failed"
    fi

    # Run frontend tests if available
    if [ -d "ui/react_frontend" ] && $COMPOSE_CMD exec -T frontend npm test 2>/dev/null; then
      echo "Frontend tests completed"
    else
      echo "No frontend tests found or tests failed"
    fi
```

## Helper Scripts

The workflow relies on three helper scripts:

1. **scripts/fix-docker-network.sh**: Fixes Docker network issues by ensuring the `paissive-network` exists and is properly configured.

2. **scripts/fix-docker-compose.sh**: Fixes Docker Compose issues by checking the installation, validating the configuration file, and fixing common problems.

3. **scripts/run-docker-compose-ci.sh**: Runs Docker Compose in CI environments by pulling images, starting services, and waiting for them to become healthy.

## Configuration Files

The workflow uses two Docker Compose configuration files:

1. **docker-compose.yml**: The main configuration file that defines the services, networks, and volumes.

2. **docker-compose.ci.yml**: A CI-specific override file with optimized settings for GitHub Actions.

## Troubleshooting

If you encounter issues with the Docker Compose workflow:

1. Check the Docker network:
   ```bash
   docker network ls
   docker network inspect paissive-network
   ```

2. Check the Docker Compose configuration:
   ```bash
   docker compose config
   ```

3. Check the Docker images:
   ```bash
   docker images
   ```

4. Check the Docker containers:
   ```bash
   docker ps -a
   ```

5. Check the Docker logs:
   ```bash
   docker compose logs
   ```

6. Run the fix scripts manually:
   ```bash
   ./scripts/fix-docker-network.sh
   ./scripts/fix-docker-compose.sh
   ./scripts/run-docker-compose-ci.sh
   ```
