#\!/bin/bash
# OpenHands setup script
echo "Setting up OpenHands environment..."

# Install common dependencies if needed
which git >/dev/null 2>&1 || (echo "Git not found" && exit 1)

echo "OpenHands setup completed successfully."
