#!/bin/bash
# Health check script for Docker container

# Set variables
HEALTH_ENDPOINT="http://localhost:5000/health"
MAX_RETRIES=5
RETRY_INTERVAL=10

# Function to check health with retries
check_health() {
  for i in $(seq 1 $MAX_RETRIES); do
    echo "Health check attempt $i of $MAX_RETRIES..."

    # Check if the Flask process is running
    if ! pgrep -f "python run_ui.py" > /dev/null; then
      echo "Flask process is not running! Checking process list:"
      ps aux | grep python || true
    fi

    # Try to access the health endpoint with more robust error handling
    echo "Attempting to connect to $HEALTH_ENDPOINT..."
    response_output=$(curl -s -f -m 10 $HEALTH_ENDPOINT 2>&1)
    curl_exit_code=$?

    if [ $curl_exit_code -eq 0 ]; then
      echo "Health check successful!"
      return 0
    else
      echo "Health check failed with curl exit code: $curl_exit_code"

      # Try with verbose output for debugging
      echo "Detailed curl output:"
      curl -v -m 10 $HEALTH_ENDPOINT || true

      # Check if the port is actually listening
      echo "Checking if port 5000 is listening:"
      netstat -tulpn 2>/dev/null | grep 5000 || ss -tulpn 2>/dev/null | grep 5000 || true

      # Check database connectivity
      if command -v psql &> /dev/null; then
        echo "Checking database connectivity..."
        if PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c '\l' 2>/dev/null; then
          echo "Database connection successful"
        else
          echo "Database connection failed. Error:"
          PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c '\l' || true
        fi
      fi

      # Check Flask logs if available
      if [ -f "/app/logs/flask.log" ]; then
        echo "Last 10 lines of Flask logs:"
        tail -10 /app/logs/flask.log || true
      fi

      if [ $i -lt $MAX_RETRIES ]; then
        echo "Retrying in $RETRY_INTERVAL seconds..."
        sleep $RETRY_INTERVAL
      fi
    fi
  done

  echo "Health check failed after $MAX_RETRIES attempts"
  return 1
}

# Run the health check
check_health
exit $?
