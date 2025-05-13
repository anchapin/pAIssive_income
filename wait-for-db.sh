#!/bin/bash
# wait-for-db.sh - Wait for PostgreSQL database to be ready

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

echo "Waiting for PostgreSQL at $host:$port..."

# Maximum number of attempts
max_attempts=60
attempt=1

# Wait for the database to be ready with timeout
while [ $attempt -le $max_attempts ]; do
  echo "Attempt $attempt of $max_attempts to connect to PostgreSQL..."

  if PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; then
    >&2 echo "PostgreSQL is up - connection successful"
    break
  else
    >&2 echo "PostgreSQL is unavailable - sleeping"

    # If this is the last attempt, try to get more diagnostic information
    if [ $attempt -eq $max_attempts ]; then
      echo "Final attempt failed. Checking PostgreSQL status..."
      # Try to get more information about the database
      echo "Checking if PostgreSQL port is reachable:"
      nc -zv "$host" "$port" || true
      echo "Checking PostgreSQL logs if available:"
      docker logs paissive-postgres 2>/dev/null || true
    fi

    sleep 2
    attempt=$((attempt + 1))
  fi
done

if [ $attempt -gt $max_attempts ]; then
  >&2 echo "Failed to connect to PostgreSQL after $max_attempts attempts"
  # Continue anyway - the Flask app will handle database connection errors gracefully
fi

# Initialize the database if needed
echo "Initializing database..."
python init_db.py || {
  echo "Database initialization failed, but continuing..."
  # We'll continue even if database initialization fails
  # The Flask app's health check will handle this gracefully
}

# Create logs directory if it doesn't exist
mkdir -p /app/logs

# Execute the command
echo "Starting Flask application..."
exec $cmd
