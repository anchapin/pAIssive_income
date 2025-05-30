#!/bin/bash

# Create required directories
mkdir -p tests/unit
mkdir -p tests/e2e
mkdir -p tests/mock-api
mkdir -p tests/__mocks__
mkdir -p ci-reports
mkdir -p ci-artifacts
mkdir -p ci-logs
mkdir -p ci-temp
mkdir -p ci-cache
mkdir -p test-results/github
mkdir -p logs

# Set CI environment variables
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
echo "REACT_APP_API_BASE_URL=http://localhost:3001" >> $GITHUB_ENV
echo "MOCK_API_PORT=3001" >> $GITHUB_ENV
echo "MOCK_API_TIMEOUT=5000" >> $GITHUB_ENV
echo "VITEST_TIMEOUT=10000" >> $GITHUB_ENV
echo "E2E_TIMEOUT=30000" >> $GITHUB_ENV

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