#!/bin/bash
# Script to run E2E tests with mock API server

echo "Starting mock API server..."

# Start the mock API server in the background
node tests/mock_api_server.js &
MOCK_API_PID=$!

# Wait for the mock API server to start
echo "Waiting for mock API server to start..."
MAX_RETRIES=30
RETRY_COUNT=0
SERVER_READY=false

while [ "$SERVER_READY" = false ] && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl --silent --fail http://localhost:8000/health > /dev/null; then
        echo "Mock API server is ready."
        SERVER_READY=true
    else
        echo "Waiting for mock API server to be ready... (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
        sleep 1
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ "$SERVER_READY" = false ]; then
    echo "Mock API server failed to start within 30 seconds. Exiting..."
    kill $MOCK_API_PID
    exit 1
fi

# Start the React app in the background
echo "Starting React app..."
REACT_APP_API_BASE_URL=http://localhost:8000/api pnpm start -- --port=3000 &
REACT_PID=$!

# Wait for the React app to start
echo "Waiting for React app to start..."
MAX_RETRIES=30
RETRY_COUNT=0
APP_READY=false

while [ "$APP_READY" = false ] && [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl --silent --fail http://localhost:3000 > /dev/null; then
        echo "React app is ready."
        APP_READY=true
    else
        echo "Waiting for React app to be ready... (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
        sleep 1
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ "$APP_READY" = false ]; then
    echo "React app failed to start within 30 seconds. Exiting..."
    kill $MOCK_API_PID
    kill $REACT_PID
    exit 1
fi

# Run the Playwright tests
echo "Running Playwright tests..."
npx playwright test tests/e2e/agent_ui.spec.ts --reporter=list

# Capture the exit code
TEST_EXIT_CODE=$?

# Clean up processes
echo "Cleaning up processes..."
kill $MOCK_API_PID
kill $REACT_PID

# Exit with the test exit code
exit $TEST_EXIT_CODE
