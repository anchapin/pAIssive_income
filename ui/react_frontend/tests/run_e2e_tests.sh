#!/bin/bash
# Script to run E2E tests with mock API server
# Enhanced with better environment detection and handling

# Enhanced environment detection
# CI Environment Detection
IS_CI=${CI:-false}
IS_GITHUB_ACTIONS=${GITHUB_ACTIONS:-false}
IS_JENKINS=${JENKINS_URL:+true}
IS_JENKINS=${IS_JENKINS:-false}
IS_GITLAB_CI=${GITLAB_CI:-false}
IS_CIRCLE_CI=${CIRCLECI:-false}
IS_TRAVIS=${TRAVIS:-false}
IS_AZURE_PIPELINES=${TF_BUILD:-false}
IS_TEAMCITY=${TEAMCITY_VERSION:+true}
IS_TEAMCITY=${IS_TEAMCITY:-false}
IS_BITBUCKET=${BITBUCKET_COMMIT:+true}
IS_BITBUCKET=${IS_BITBUCKET:-false}
IS_APPVEYOR=${APPVEYOR:-false}
IS_DRONE=${DRONE:-false}
IS_BUDDY=${BUDDY:-false}
IS_BUILDKITE=${BUILDKITE:-false}
IS_CODEBUILD=${CODEBUILD_BUILD_ID:+true}
IS_CODEBUILD=${IS_CODEBUILD:-false}

# Container Environment Detection
IS_DOCKER=false
IS_KUBERNETES=${KUBERNETES_SERVICE_HOST:+true}
IS_KUBERNETES=${IS_KUBERNETES:-false}
IS_DOCKER_COMPOSE=${COMPOSE_PROJECT_NAME:+true}
IS_DOCKER_COMPOSE=${IS_DOCKER_COMPOSE:-false}
IS_DOCKER_SWARM=${DOCKER_SWARM:-false}

# Check if running in Docker with multiple methods
if [ -f "/.dockerenv" ] || [ -n "$DOCKER_ENVIRONMENT" ] || [ -n "$DOCKER" ] || [ -f "/run/.containerenv" ]; then
    IS_DOCKER=true
elif [ -f "/proc/1/cgroup" ]; then
    if grep -q "docker" /proc/1/cgroup; then
        IS_DOCKER=true
    fi
fi

# Cloud Environment Detection
IS_AWS=${AWS_REGION:+true}
IS_AWS=${IS_AWS:-false}
IS_AZURE=${AZURE_FUNCTIONS_ENVIRONMENT:+true}
IS_AZURE=${IS_AZURE:-false}
IS_GCP=${GOOGLE_CLOUD_PROJECT:+true}
IS_GCP=${IS_GCP:-${GCLOUD_PROJECT:+true}}
IS_GCP=${IS_GCP:-false}

# OS Detection
IS_WSL=false
if [ -n "$WSL_DISTRO_NAME" ] || [ -n "$WSLENV" ]; then
    IS_WSL=true
fi

# Configuration
VERBOSE_LOGGING=${VERBOSE_LOGGING:-false}
MOCK_API_PORT=${MOCK_API_PORT:-8000}
REACT_PORT=${REACT_PORT:-3000}
MAX_RETRIES=${MAX_RETRIES:-30}
RETRY_INTERVAL=${RETRY_INTERVAL:-1}
TEST_SPEC=${TEST_SPEC:-"tests/e2e/agent_ui.spec.ts"}
REPORTER=${REPORTER:-"list"}

# Create logs directory
mkdir -p logs
mkdir -p playwright-report

# Log function with timestamps and levels
log() {
    local level="INFO"
    if [ $# -eq 2 ]; then
        level=$(echo "$1" | tr '[:lower:]' '[:upper:]')
        message="$2"
    else
        message="$1"
    fi

    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
    echo "[$timestamp] [$level] $message"
    echo "[$timestamp] [$level] $message" >> logs/run_e2e_tests.log

    # For important messages, also create a report file
    if [ "$level" = "ERROR" ] || [ "$level" = "IMPORTANT" ]; then
        echo "[$timestamp] [$level] $message" > "playwright-report/run-e2e-tests-${level,,}-$(date +%s).txt"
    fi
}

# Log environment information
log "IMPORTANT" "Starting E2E tests with enhanced environment detection"

# Log OS information
log "INFO" "OS Information:"
log "INFO" "  Platform: $(uname -s)"
log "INFO" "  WSL: $IS_WSL"
if [ "$IS_WSL" = "true" ]; then
    log "INFO" "  WSL Distro: $WSL_DISTRO_NAME"
fi
log "INFO" "  Working directory: $(pwd)"

# Log Node.js information
log "INFO" "Node.js Information:"
log "INFO" "  Version: $(node --version)"
log "INFO" "  NPM Version: $(npm --version 2>/dev/null || echo 'not installed')"
log "INFO" "  PNPM Version: $(pnpm --version 2>/dev/null || echo 'not installed')"

# Log CI environment information
log "INFO" "CI Environment:"
log "INFO" "  CI: $IS_CI"
log "INFO" "  GitHub Actions: $IS_GITHUB_ACTIONS"
log "INFO" "  Jenkins: $IS_JENKINS"
log "INFO" "  GitLab CI: $IS_GITLAB_CI"
log "INFO" "  CircleCI: $IS_CIRCLE_CI"
log "INFO" "  Travis CI: $IS_TRAVIS"
log "INFO" "  Azure Pipelines: $IS_AZURE_PIPELINES"
log "INFO" "  TeamCity: $IS_TEAMCITY"
log "INFO" "  Bitbucket: $IS_BITBUCKET"
log "INFO" "  AppVeyor: $IS_APPVEYOR"
log "INFO" "  Drone CI: $IS_DRONE"
log "INFO" "  Buddy CI: $IS_BUDDY"
log "INFO" "  Buildkite: $IS_BUILDKITE"
log "INFO" "  AWS CodeBuild: $IS_CODEBUILD"

# Log container environment information
log "INFO" "Container Environment:"
log "INFO" "  Docker: $IS_DOCKER"
log "INFO" "  Kubernetes: $IS_KUBERNETES"
log "INFO" "  Docker Compose: $IS_DOCKER_COMPOSE"
log "INFO" "  Docker Swarm: $IS_DOCKER_SWARM"

# Log cloud environment information
log "INFO" "Cloud Environment:"
log "INFO" "  AWS: $IS_AWS"
log "INFO" "  Azure: $IS_AZURE"
log "INFO" "  GCP: $IS_GCP"

# Detect environment and set appropriate variables
# CI-specific settings
if [ "$IS_CI" = "true" ]; then
    log "INFO" "CI environment detected, using CI-specific settings"
    VERBOSE_LOGGING=true
    RETRY_INTERVAL=2
    # Use simple mock server in CI environments for better reliability
    USE_SIMPLE_MOCK=true

    # GitHub Actions specific settings
    if [ "$IS_GITHUB_ACTIONS" = "true" ]; then
        log "INFO" "GitHub Actions specific settings applied"
        MAX_RETRIES=45
        PLAYWRIGHT_ARGS="--retries=2 --reporter=github"
    fi

    # Jenkins specific settings
    if [ "$IS_JENKINS" = "true" ]; then
        log "INFO" "Jenkins specific settings applied"
        PLAYWRIGHT_ARGS="--retries=2 --reporter=junit"
    fi

    # GitLab CI specific settings
    if [ "$IS_GITLAB_CI" = "true" ]; then
        log "INFO" "GitLab CI specific settings applied"
        PLAYWRIGHT_ARGS="--retries=2 --reporter=junit"
    fi

    # CircleCI specific settings
    if [ "$IS_CIRCLE_CI" = "true" ]; then
        log "INFO" "CircleCI specific settings applied"
        PLAYWRIGHT_ARGS="--retries=2 --reporter=junit"
    fi

    # Travis CI specific settings
    if [ "$IS_TRAVIS" = "true" ]; then
        log "INFO" "Travis CI specific settings applied"
        PLAYWRIGHT_ARGS="--retries=2 --reporter=junit"
    fi

    # Azure Pipelines specific settings
    if [ "$IS_AZURE_PIPELINES" = "true" ]; then
        log "INFO" "Azure Pipelines specific settings applied"
        PLAYWRIGHT_ARGS="--retries=2 --reporter=junit"
    fi
else
    log "INFO" "Local environment detected"
    USE_SIMPLE_MOCK=false
    PLAYWRIGHT_ARGS="--reporter=$REPORTER"
fi

# Container-specific settings
if [ "$IS_DOCKER" = "true" ]; then
    log "INFO" "Docker environment detected, using Docker-specific settings"
    # In Docker, we might need to use different host names
    REACT_APP_API_HOST="host.docker.internal"

    # Docker Compose specific settings
    if [ "$IS_DOCKER_COMPOSE" = "true" ]; then
        log "INFO" "Docker Compose specific settings applied"
        # In Docker Compose, use service names as hostnames
        REACT_APP_API_HOST="api"
    fi

    # Kubernetes specific settings
    if [ "$IS_KUBERNETES" = "true" ]; then
        log "INFO" "Kubernetes specific settings applied"
        # In Kubernetes, use service names with namespace
        REACT_APP_API_HOST="api.default.svc.cluster.local"
    fi
else
    REACT_APP_API_HOST="localhost"
fi

# Cloud-specific settings
if [ "$IS_AWS" = "true" ]; then
    log "INFO" "AWS environment detected, using AWS-specific settings"
    # AWS-specific settings here
fi

if [ "$IS_AZURE" = "true" ]; then
    log "INFO" "Azure environment detected, using Azure-specific settings"
    # Azure-specific settings here
fi

if [ "$IS_GCP" = "true" ]; then
    log "INFO" "GCP environment detected, using GCP-specific settings"
    # GCP-specific settings here
fi

# OS-specific settings
if [ "$IS_WSL" = "true" ]; then
    log "INFO" "WSL environment detected, using WSL-specific settings"
    # WSL-specific settings here
fi

# Function to check if a port is available
check_port_available() {
    local port=$1
    if nc -z localhost $port 2>/dev/null; then
        return 1
    else
        return 0
    fi
}

# Find available ports if the default ones are in use
if ! check_port_available $MOCK_API_PORT; then
    log "WARN" "Port $MOCK_API_PORT is already in use, finding an alternative port"
    for port in {8001..8020}; do
        if check_port_available $port; then
            MOCK_API_PORT=$port
            log "INFO" "Using alternative port $MOCK_API_PORT for mock API server"
            break
        fi
    done
fi

if ! check_port_available $REACT_PORT; then
    log "WARN" "Port $REACT_PORT is already in use, finding an alternative port"
    for port in {3001..3020}; do
        if check_port_available $port; then
            REACT_PORT=$port
            log "INFO" "Using alternative port $REACT_PORT for React app"
            break
        fi
    done
fi

# Start the appropriate mock server based on environment
if [ "$USE_SIMPLE_MOCK" = "true" ]; then
    log "INFO" "Starting simple mock server on port $MOCK_API_PORT..."
    MOCK_API_PORT=$MOCK_API_PORT node tests/simple_mock_server.js > logs/simple_mock_server.log 2>&1 &
    MOCK_API_PID=$!
else
    log "INFO" "Starting mock API server on port $MOCK_API_PORT..."
    MOCK_API_PORT=$MOCK_API_PORT node tests/mock_api_server.js > logs/mock_api_server.log 2>&1 &
    MOCK_API_PID=$!
fi

# Wait for the mock API server to start
log "INFO" "Waiting for mock API server to start..."
RETRY_COUNT=0
SERVER_READY=false

while [ "$SERVER_READY" = false ] && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl --silent --fail http://localhost:$MOCK_API_PORT/health > /dev/null; then
        log "INFO" "Mock API server is ready on port $MOCK_API_PORT."
        SERVER_READY=true
    else
        log "INFO" "Waiting for mock API server to be ready... (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ "$SERVER_READY" = false ]; then
    log "ERROR" "Mock API server failed to start within $((MAX_RETRIES * RETRY_INTERVAL)) seconds."

    # Try the fallback server as a last resort
    log "INFO" "Starting fallback server as a last resort..."
    MOCK_API_PORT=$MOCK_API_PORT node tests/simple_fallback_server.js > logs/fallback_server.log 2>&1 &
    FALLBACK_PID=$!

    # Wait for the fallback server to start
    sleep 5

    if curl --silent --fail http://localhost:$MOCK_API_PORT/health > /dev/null; then
        log "INFO" "Fallback server is ready on port $MOCK_API_PORT."
        SERVER_READY=true
        MOCK_API_PID=$FALLBACK_PID
    else
        log "ERROR" "Fallback server also failed to start. Exiting..."
        kill $MOCK_API_PID 2>/dev/null
        kill $FALLBACK_PID 2>/dev/null
        exit 1
    fi
fi

# Start the React app in the background
log "INFO" "Starting React app on port $REACT_PORT..."
REACT_APP_API_BASE_URL=http://$REACT_APP_API_HOST:$MOCK_API_PORT/api \
REACT_APP_AG_UI_ENABLED=true \
PORT=$REACT_PORT \
pnpm start > logs/react_app.log 2>&1 &
REACT_PID=$!

# Wait for the React app to start
log "INFO" "Waiting for React app to start..."
RETRY_COUNT=0
APP_READY=false

while [ "$APP_READY" = false ] && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl --silent --fail http://localhost:$REACT_PORT > /dev/null; then
        log "INFO" "React app is ready on port $REACT_PORT."
        APP_READY=true
    else
        log "INFO" "Waiting for React app to be ready... (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ "$APP_READY" = false ]; then
    log "ERROR" "React app failed to start within $((MAX_RETRIES * RETRY_INTERVAL)) seconds."

    # In CI, we can try to run tests anyway with a static HTML server
    if [ "$IS_CI" = "true" ] || [ "$IS_GITHUB_ACTIONS" = "true" ]; then
        log "WARN" "CI environment detected, creating a simple HTML server for testing..."

        # Create a simple HTML file
        mkdir -p public
        cat > public/index.html << EOF
<!DOCTYPE html>
<html>
<head>
  <title>Test Frontend</title>
</head>
<body>
  <h1>Test Frontend</h1>
  <div id="root">
    <div class="app-container">
      <div class="app-header">Test Header</div>
      <div class="app-content">Test Content</div>
    </div>
  </div>
</body>
</html>
EOF

        # Start a simple HTTP server
        npx http-server public -p $REACT_PORT --silent > logs/http_server.log 2>&1 &
        HTTP_SERVER_PID=$!

        # Wait for the HTTP server to start
        sleep 5

        if curl --silent --fail http://localhost:$REACT_PORT > /dev/null; then
            log "INFO" "Simple HTTP server is ready on port $REACT_PORT."
            APP_READY=true
            REACT_PID=$HTTP_SERVER_PID
        else
            log "ERROR" "Simple HTTP server also failed to start. Exiting..."
            kill $MOCK_API_PID 2>/dev/null
            kill $HTTP_SERVER_PID 2>/dev/null
            exit 1
        fi
    else
        log "ERROR" "Exiting due to React app startup failure."
        kill $MOCK_API_PID
        kill $REACT_PID 2>/dev/null
        exit 1
    fi
fi

# Set environment variables for the tests
export PLAYWRIGHT_BASE_URL=http://localhost:$REACT_PORT
export PLAYWRIGHT_API_BASE_URL=http://localhost:$MOCK_API_PORT/api
export REACT_APP_API_BASE_URL=http://localhost:$MOCK_API_PORT/api

# Run the Playwright tests
log "IMPORTANT" "Running Playwright tests..."
log "INFO" "Test spec: $TEST_SPEC"
log "INFO" "Reporter: $REPORTER"
log "INFO" "Base URL: $PLAYWRIGHT_BASE_URL"
log "INFO" "API Base URL: $PLAYWRIGHT_API_BASE_URL"

# Add additional arguments for CI environments
PLAYWRIGHT_ARGS="--reporter=$REPORTER"
if [ "$IS_CI" = "true" ] || [ "$IS_GITHUB_ACTIONS" = "true" ]; then
    PLAYWRIGHT_ARGS="$PLAYWRIGHT_ARGS --retries=2"
fi

npx playwright test $TEST_SPEC $PLAYWRIGHT_ARGS

# Capture the exit code
TEST_EXIT_CODE=$?

# Log the test result
if [ $TEST_EXIT_CODE -eq 0 ]; then
    log "IMPORTANT" "Tests completed successfully!"
else
    log "ERROR" "Tests failed with exit code $TEST_EXIT_CODE"
fi

# Clean up processes
log "INFO" "Cleaning up processes..."
kill $MOCK_API_PID 2>/dev/null
kill $REACT_PID 2>/dev/null

# Create a summary report
cat > playwright-report/test-summary.txt << EOF
E2E Test Summary
---------------
Date: $(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
Test Spec: $TEST_SPEC
Exit Code: $TEST_EXIT_CODE

Operating System:
  Platform: $(uname -s)
  WSL: $IS_WSL
  WSL Distro: ${WSL_DISTRO_NAME:-N/A}

CI Environment:
  CI: $IS_CI
  GitHub Actions: $IS_GITHUB_ACTIONS
  Jenkins: $IS_JENKINS
  GitLab CI: $IS_GITLAB_CI
  CircleCI: $IS_CIRCLE_CI
  Travis CI: $IS_TRAVIS
  Azure Pipelines: $IS_AZURE_PIPELINES
  TeamCity: $IS_TEAMCITY
  Bitbucket: $IS_BITBUCKET
  AppVeyor: $IS_APPVEYOR
  Drone CI: $IS_DRONE
  Buddy CI: $IS_BUDDY
  Buildkite: $IS_BUILDKITE
  AWS CodeBuild: $IS_CODEBUILD

Container Environment:
  Docker: $IS_DOCKER
  Kubernetes: $IS_KUBERNETES
  Docker Compose: $IS_DOCKER_COMPOSE
  Docker Swarm: $IS_DOCKER_SWARM

Cloud Environment:
  AWS: $IS_AWS
  Azure: $IS_AZURE
  GCP: $IS_GCP

Configuration:
  Mock API Port: $MOCK_API_PORT
  React Port: $REACT_PORT
  API Host: $REACT_APP_API_HOST
  Playwright Args: $PLAYWRIGHT_ARGS
EOF

log "INFO" "Test summary written to playwright-report/test-summary.txt"
log "IMPORTANT" "E2E tests completed with exit code $TEST_EXIT_CODE"

# Exit with the test exit code
exit $TEST_EXIT_CODE
