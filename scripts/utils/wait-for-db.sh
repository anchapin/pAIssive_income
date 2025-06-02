#!/bin/bash
# Script to wait for PostgreSQL database to be ready

# Set default values
DB_HOST=${POSTGRES_HOST:-db}
DB_PORT=${POSTGRES_PORT:-5432}
DB_USER=${POSTGRES_USER:-myuser}
DB_PASSWORD=${POSTGRES_PASSWORD:-mypassword}
DB_NAME=${POSTGRES_DB:-mydb}
MAX_RETRIES=${MAX_RETRIES:-30}
RETRY_INTERVAL=${RETRY_INTERVAL:-2}

# Log with timestamp
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if PostgreSQL client is installed
if ! command -v pg_isready &> /dev/null; then
  log "PostgreSQL client not installed. Cannot check database readiness."
  exit 1
fi

log "Waiting for PostgreSQL database to be ready..."
log "Host: $DB_HOST, Port: $DB_PORT, User: $DB_USER, Database: $DB_NAME"

# Try to connect to the database
for i in $(seq 1 $MAX_RETRIES); do
  log "Attempt $i of $MAX_RETRIES..."
  
  if pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > /dev/null 2>&1; then
    log "✅ Database is ready!"
    exit 0
  fi
  
  log "Database not ready yet. Waiting $RETRY_INTERVAL seconds..."
  sleep $RETRY_INTERVAL
done

log "❌ Database not ready after $MAX_RETRIES attempts."
exit 1
