#!/bin/bash
# This script is executed when the OpenHands runtime container starts.
# It installs custom dependencies needed for this repository.
#
# Dependencies installed:
# - Node.js 18.x (LTS)
# - npm (comes with Node.js)
# - python3-pip
# - pnpm 8.6.0 (pinned version for reproducibility)
# - uv 0.4.30 (pinned version for reproducibility)

set -e
echo "--- Starting custom setup.sh ---"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to handle errors
handle_error() {
    log "ERROR: $1"
    exit 1
}

log "Installing system dependencies..."

# Use sudo to run commands with root privileges in a single subshell
# Update the package list, install dependencies, and clean up in one layer
sudo bash -c 'apt-get update && apt-get install -y \
    nodejs=18.* \
    npm \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*' || handle_error "Failed to install system dependencies"

log "System dependencies installed successfully"

# Install pnpm globally using npm with pinned version
log "Installing pnpm 8.6.0..."
sudo npm install -g pnpm@8.6.0 || handle_error "Failed to install pnpm"

log "pnpm installed successfully"

# Use pip to install the 'uv' package with pinned version and clean up the cache
log "Installing uv 0.4.30..."
sudo pip install uv==0.4.30 || handle_error "Failed to install uv"

# Clean up pip cache using the recommended method
log "Cleaning up pip cache..."
sudo pip cache purge || log "Warning: Failed to purge pip cache, but continuing"

log "uv installed successfully"

# Verify installations
log "Verifying installations..."
node --version || handle_error "Node.js verification failed"
npm --version || handle_error "npm verification failed"
pnpm --version || handle_error "pnpm verification failed"
uv --version || handle_error "uv verification failed"

log "All installations verified successfully"
echo "--- Custom setup.sh complete ---"