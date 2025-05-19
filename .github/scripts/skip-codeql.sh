#!/bin/bash

# This script is used to skip CodeQL analysis in the consolidated-ci-cd.yml workflow
# as it's now handled by dedicated workflows for each OS

echo "CodeQL analysis is now performed by dedicated workflows for each OS:"
echo "- .github/workflows/codeql-ubuntu.yml for Ubuntu"
echo "- .github/workflows/codeql-windows.yml for Windows"
echo "- .github/workflows/codeql-macos.yml for macOS"
echo ""
echo "These workflows provide proper OS-specific configurations for security scanning."
echo "The CodeQL section in consolidated-ci-cd.yml is kept for backward compatibility"
echo "but will be removed in a future update."
