# Docker Compose Integration Fix

This directory contains scripts and configuration files to fix Docker Compose integration issues in GitHub Actions workflows.

## Problem

The Docker Compose integration workflow was failing with the following issues:

1. **Network Creation Issues**: The workflow was failing to create the Docker network.
2. **Docker Compose Version Compatibility**: There were issues with the Docker Compose version being used.
3. **Docker Buildx Cache Restoration Failure**: The error showed "Failed to restore: Cache service responded with 422".
4. **Frontend Integration Issues**: The PR added a React frontend with ag-ui integration, which was causing compatibility issues.
5. **Docker Image Pulling Issues**: There were issues with pulling the required Docker images.

## Solution

The solution includes the following components:

### 1. Fixed Workflow Files

- `.github/workflows/docker-compose-integration-fixed.yml`: An updated version of the Docker Compose integration workflow with improved error handling and retry logic.
- `.github/workflows/test-docker-compose-fix.yml`: A workflow to test the Docker Compose fix.

### 2. Fix Scripts

- `scripts/fix-docker-network.sh`: A script to fix Docker network issues.
- `scripts/fix-docker-compose.sh`: A script to fix Docker Compose issues.
- `scripts/run-docker-compose-ci.sh`: A script to run Docker Compose in CI environments.

### 3. Updated Configuration Files

- `docker-compose.yml`: Updated with improved network configuration and CI compatibility.
- `docker-compose.ci.yml`: A CI-specific override file with optimized settings for GitHub Actions.

## How to Use

### Option 1: Use the Fixed Workflow

1. Replace the existing workflow file with the fixed version:

   ```bash
   cp .github/workflows/docker-compose-integration-fixed.yml .github/workflows/docker-compose-integration.yml
   ```

2. Commit and push the changes:

   ```bash
   git add .github/workflows/docker-compose-integration.yml
   git commit -m "Use fixed Docker Compose integration workflow"
   git push
   ```

### Option 2: Use the Fix Scripts

1. Make the scripts executable:

   ```bash
   chmod +x scripts/fix-docker-network.sh
   chmod +x scripts/fix-docker-compose.sh
   chmod +x scripts/run-docker-compose-ci.sh
   ```

2. Run the scripts in order:

   ```bash
   ./scripts/fix-docker-network.sh
   ./scripts/fix-docker-compose.sh
   ./scripts/run-docker-compose-ci.sh
   ```

### Option 3: Manual Fixes

If you prefer to make the changes manually, follow these steps:

1. Update the Docker Compose file with the changes in `docker-compose.yml`.
2. Create a CI-specific override file using `docker-compose.ci.yml`.
3. Update the workflow file with the changes in `.github/workflows/docker-compose-integration-fixed.yml`.

## Testing

To test the fix, you can run the test workflow:

```bash
gh workflow run test-docker-compose-fix.yml
```

Or manually trigger it from the GitHub Actions tab.

## Troubleshooting

If you encounter issues with the fix, check the following:

1. **Docker Network Issues**: Run `docker network ls` to check if the network exists. If not, run `docker network create paissive-network`.
2. **Docker Compose Version**: Run `docker compose version` or `docker-compose --version` to check the version. The fix is tested with Docker Compose v2.x.
3. **Docker Image Pulling Issues**: Check if you can pull the images manually with `docker pull postgres:15.3-alpine` and `docker pull node:18-alpine`.
4. **Frontend Integration Issues**: Check if the frontend Dockerfile.dev exists and is correctly configured.
5. **Logs**: Check the logs in the `logs` directory for more information.

## Contributing

If you find issues with the fix or have suggestions for improvements, please open an issue or submit a pull request.
