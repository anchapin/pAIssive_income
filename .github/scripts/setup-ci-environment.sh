#!/bin/bash

# Create necessary directories
mkdir -p ci-reports ci-artifacts ci-logs ci-temp ci-cache
mkdir -p test-results/github
mkdir -p logs
mkdir -p coverage

# Set environment variables
echo "CI=true" >> $GITHUB_ENV
echo "CI_ENVIRONMENT=true" >> $GITHUB_ENV
echo "CI_TYPE=github" >> $GITHUB_ENV
echo "GITHUB_ACTIONS=true" >> $GITHUB_ENV
echo "CI_PLATFORM=github" >> $GITHUB_ENV
echo "CI_OS=$(uname -s)" >> $GITHUB_ENV
echo "CI_ARCH=$(uname -m)" >> $GITHUB_ENV
echo "CI_PYTHON_VERSION=$(python --version | cut -d' ' -f2)" >> $GITHUB_ENV
echo "CI_NODE_VERSION=$(node --version)" >> $GITHUB_ENV
echo "CI_RUNNER_OS=${{ runner.os }}" >> $GITHUB_ENV
echo "CI_WORKSPACE=${{ github.workspace }}" >> $GITHUB_ENV
echo "FLASK_ENV=development" >> $GITHUB_ENV
echo "DATABASE_URL=sqlite:///:memory:" >> $GITHUB_ENV
echo "TESTING=true" >> $GITHUB_ENV

# Create dummy test files if they don't exist
touch test-results/junit.xml
touch coverage/coverage.xml
touch ci-reports/test-report.json
touch ci-logs/test.log

# Set permissions
chmod -R 755 ci-reports ci-artifacts ci-logs ci-temp ci-cache
chmod -R 755 test-results coverage logs

# Generate environment report
{
  echo "=== CI Environment Report ==="
  echo "Date: $(date)"
  echo "OS: $(uname -a)"
  echo "Python: $(python --version)"
  echo "Node: $(node --version)"
  echo "npm: $(npm --version)"
  echo "pnpm: $(pnpm --version)"
  echo "Runner OS: ${{ runner.os }}"
  echo "Workspace: ${{ github.workspace }}"
  echo "Event: ${{ github.event_name }}"
  echo "Repository: ${{ github.repository }}"
  echo "Ref: ${{ github.ref }}"
  echo "SHA: ${{ github.sha }}"
  echo "=========================="
} > ci-reports/environment-report.txt

# Display environment report
cat ci-reports/environment-report.txt