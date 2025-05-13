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
      echo "Flask process is not running!"
    fi

    # Try to access the health endpoint with more verbose output
    echo "Attempting to connect to $HEALTH_ENDPOINT..."
    response_output=$(curl -v $HEALTH_ENDPOINT 2>&1)
    response=$(echo "$response_output" | grep -o "HTTP/[0-9.]* [0-9]*" | awk '{print $2}')

    if [ "$response" = "200" ]; then
      echo "Health check successful!"
      return 0
    else
      echo "Health check failed with status code: $response"
      echo "Curl output: $response_output"

      # Check database connectivity
      if command -v psql &> /dev/null; then
        echo "Checking database connectivity..."
        if PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c '\l' &> /dev/null; then
          echo "Database connection successful"
        else
          echo "Database connection failed"
        fi
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
