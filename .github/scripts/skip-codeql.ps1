# This script is used to skip CodeQL analysis in the consolidated-ci-cd.yml workflow
# as it's now handled by dedicated workflows for each OS

Write-Host "CodeQL analysis is now performed by dedicated workflows for each OS:"
Write-Host "- .github/workflows/codeql-ubuntu.yml for Ubuntu"
Write-Host "- .github/workflows/codeql-windows.yml for Windows"
Write-Host "- .github/workflows/codeql-macos.yml for macOS"
Write-Host ""
Write-Host "These workflows provide proper OS-specific configurations for security scanning."
Write-Host "The CodeQL section in consolidated-ci-cd.yml is kept for backward compatibility"
Write-Host "but will be removed in a future update."
