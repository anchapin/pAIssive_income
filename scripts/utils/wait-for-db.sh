#!/bin/bash
# Simplified wait-for-db.sh for CI environments

# Enable error handling but don't exit immediately on error
set +e

# Log with timestamp
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Parse arguments
host="$1"
port="$2"
shift 2
cmd="$@"

log "Starting wait-for-db script for PostgreSQL at $host:$port (CI-optimized)..."

# Configuration - reduced for CI environments
max_attempts=30
initial_retry_interval=1
max_retry_interval=5
connection_timeout=3

# Function to check if PostgreSQL port is reachable
check_port() {
  log "Checking if PostgreSQL port is reachable..."
  if nc -z -w $connection_timeout "$host" "$port" 2>/dev/null; then
    log "✅ PostgreSQL port $port is reachable"
    return 0
  else
    log "❌ PostgreSQL port $port is NOT reachable"
    return 1
  fi
}

# Function to check if PostgreSQL is accepting connections
check_postgres() {
  log "Checking if PostgreSQL is accepting connections..."
  if PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' -w -t $connection_timeout 2>/dev/null; then
    log "✅ PostgreSQL connection successful"
    return 0
  else
    log "❌ PostgreSQL connection failed"
    return 1
  fi
}

# Function to get simplified PostgreSQL diagnostics for CI
get_postgres_diagnostics() {
  log "=== POSTGRESQL DIAGNOSTICS (CI) ==="

  # Check if host is reachable via ping
  log "Checking if host is reachable via ping:"
  ping -c 1 "$host" 2>/dev/null && log "✅ Host is reachable via ping" || log "❌ Host is NOT reachable via ping"

  # Check if port is open
  check_port

  # Try a simple connection test
  log "Trying simple connection test:"
  PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" -w -t $connection_timeout 2>/dev/null || log "❌ Could not connect to PostgreSQL"
}

# Wait for the database to be ready with exponential backoff
attempt=1
while [ $attempt -le $max_attempts ]; do
  # Calculate retry interval with exponential backoff
  retry_interval=$((initial_retry_interval * (attempt / 10 + 1)))
  if [ "$retry_interval" -gt "$max_retry_interval" ]; then
    retry_interval=$max_retry_interval
  fi

  log "Attempt $attempt of $max_attempts to connect to PostgreSQL (retry interval: ${retry_interval}s)..."

  # First check if the port is reachable
  if check_port; then
    # Then check if PostgreSQL is accepting connections
    if check_postgres; then
      log "PostgreSQL is up and ready!"
      break
    else
      log "PostgreSQL port is reachable but not accepting connections yet"
    fi
  else
    log "PostgreSQL port is not reachable yet"
  fi

  # Get detailed diagnostics every 10 attempts or on the last attempt
  if [ $((attempt % 10)) -eq 0 ] || [ $attempt -eq $max_attempts ]; then
    get_postgres_diagnostics
  fi

  # Sleep with exponential backoff
  if [ $attempt -lt $max_attempts ]; then
    log "Retrying in $retry_interval seconds..."
    sleep $retry_interval
  fi

  attempt=$((attempt + 1))
done

# Check if we exceeded max attempts
if [ $attempt -gt $max_attempts ]; then
  log "⚠️ WARNING: Failed to connect to PostgreSQL after $max_attempts attempts"
  log "Will continue anyway for CI environment"
else
  log "✅ Successfully connected to PostgreSQL after $attempt attempts"
fi

# Initialize the database with simplified error handling for CI
log "Initializing database (CI mode)..."
python init_db.py || log "⚠️ Database initialization failed, continuing anyway for CI"

# Initialize the agent database
log "Initializing agent database (CI mode)..."
python init_agent_db.py || log "⚠️ Agent database initialization failed, continuing anyway for CI"

# Create necessary directories
log "Creating required directories..."
mkdir -p /app/logs
mkdir -p /app/data

# Set up logging
log "Setting up logging..."
touch /app/logs/flask.log
touch /app/logs/app.log

# Print minimal environment information for CI
log "=== CI ENVIRONMENT INFORMATION ==="
log "Python version: $(python --version 2>&1)"
log "CI: $CI"
log "GITHUB_ACTIONS: $GITHUB_ACTIONS"

# Execute the command
log "Starting Flask application with command: $cmd"
exec $cmd
