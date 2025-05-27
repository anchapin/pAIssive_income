#!/bin/bash
# Main setup script for pAIssive Income (Linux/macOS)

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting pAIssive Income development environment setup..."

# 1. Run the enhanced Python environment setup script
echo "----------------------------------------------------"
echo "STEP 1: Setting up Python environment and dependencies..."
echo "----------------------------------------------------"
if [ -f "scripts/setup/enhanced_setup_dev_environment.py" ]; then
    python3 scripts/setup/enhanced_setup_dev_environment.py --full
else
    echo "ERROR: scripts/setup/enhanced_setup_dev_environment.py not found!"
    exit 1
fi
echo "Python environment setup complete."
echo ""

# 2. Install Node.js dependencies using pnpm
echo "----------------------------------------------------"
echo "STEP 2: Installing Node.js dependencies..."
echo "----------------------------------------------------"
if command -v pnpm &> /dev/null; then
    pnpm install
    echo "Node.js dependencies installed via pnpm."
else
    echo "WARNING: pnpm command not found. Skipping Node.js dependency installation."
    echo "Please install pnpm (https://pnpm.io/installation) and then run 'pnpm install' manually in the project root."
fi
echo ""

# 3. Setup .env file
echo "----------------------------------------------------"
echo "STEP 3: Setting up .env file..."
echo "----------------------------------------------------"
if [ -f ".env.example" ]; then
    if [ -f ".env" ]; then
        echo ".env file already exists. Skipping creation."
    else
        cp .env.example .env
        echo ".env file created from .env.example."
        echo "IMPORTANT: Please review and update .env with your specific configurations."
    fi
else
    echo "WARNING: .env.example not found. Cannot create .env file."
fi
echo ""

# 4. Database Initialization Reminder
echo "----------------------------------------------------"
echo "STEP 4: Database Initialization (Manual Step)"
echo "----------------------------------------------------"
echo "If this is your first time setting up or you need a fresh database, run:"
echo "  python3 init_db.py"
echo "Ensure your .env file is configured correctly before running this."
echo ""

# 5. Final Instructions
echo "----------------------------------------------------"
echo "Setup Complete! Next Steps:"
echo "----------------------------------------------------"
echo "1. Activate the Python virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Configure your .env file with necessary API keys and settings."
echo ""
echo "3. Initialize the database (if you haven't already):"
echo "   python3 init_db.py"
echo ""
echo "4. To run the application or tests, please refer to the project documentation."
echo ""
echo "For the jules.google.com setup, the command to run this script is:"
echo "  bash setup.sh"
echo "----------------------------------------------------"

exit 0
