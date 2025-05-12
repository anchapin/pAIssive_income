#!/bin/bash
# Health check script for Docker container

# Set variables
HEALTH_ENDPOINT="http://localhost:5000/health"
MAX_RETRIES=3
RETRY_INTERVAL=5

# Function to check health with retries
check_health() {
  for i in $(seq 1 $MAX_RETRIES); do
    echo "Health check attempt $i of $MAX_RETRIES..."

    # Try to access the health endpoint
    response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_ENDPOINT)

    if [ "$response" = "200" ]; then
      echo "Health check successful!"
      return 0
    else
      echo "Health check failed with status code: $response"
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
