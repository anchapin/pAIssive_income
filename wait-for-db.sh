#!/bin/bash
# wait-for-db.sh - Wait for PostgreSQL database to be ready

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

echo "Waiting for PostgreSQL at $host:$port..."

# Wait for the database to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"

# Initialize the database if needed
echo "Initializing database..."
python init_db.py

# Execute the command
exec $cmd
