#!/bin/bash
# This script is executed when the OpenHands runtime container starts.
# It installs custom dependencies needed for this repository.

set -e
echo "--- Starting custom setup.sh ---"

# Use sudo to run commands with root privileges
# Update the package list, install dependencies, and clean up in one layer
sudo apt-get update && sudo apt-get install -y \
    nodejs \
    npm \
    python3-pip \
    && sudo rm -rf /var/lib/apt/lists/*

# Install pnpm globally using npm
sudo npm install -g pnpm

# Use pip to install the 'uv' package and clean up the cache
sudo pip install uv \
    && sudo rm -rf /root/.cache/pip

echo "--- Custom setup.sh complete ---"