#!/bin/bash
# Script to fix security scan issues on Linux/macOS
# Usage: ./fix_security_scan.sh [scan_results_file]

set -e

echo "===== Security Scan Fix Script for Linux/macOS ====="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH. Please install Python first."
    exit 1
fi

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Install required packages
echo "Installing required packages..."
python -m pip install --upgrade pip
python -m pip install pylint pylint-security

echo "Running security scan fix script..."

if [ -z "$1" ]; then
    echo "No scan results file provided, running with default options"
    python fix_security_scan_issues.py --update-config --add-comments --verbose
else
    echo "Using scan results from $1"
    python fix_security_scan_issues.py --scan-results "$1" --update-config --add-comments --verbose
fi

# Run Pylint security scan with the correct plugin
echo "Running Pylint security scan..."
pylint --disable=all --load-plugins=pylint_security --enable=security .

# Check if Semgrep is installed
if ! command -v semgrep &> /dev/null; then
    echo "Installing Semgrep..."
    python -m pip install semgrep
fi

# Run Semgrep with security ruleset
echo "Running Semgrep security scan..."
semgrep scan --config=p/security-audit --severity=ERROR || {
    echo "Semgrep scan failed with security ruleset. Trying with minimal config..."
    semgrep scan --config p/r2c-security-audit --severity=ERROR || {
        echo "Semgrep scan failed with minimal config. Skipping."
    }
}

echo ""
echo "Done!"
echo ""
echo "Next steps:"
echo "1. Review the changes made to the files"
echo "2. Review the updated .gitleaks.toml file"
echo "3. Run the security scan again to verify the issues are fixed"
echo ""

# Deactivate the virtual environment
deactivate
