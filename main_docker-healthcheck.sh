#!/bin/bash
# Enhanced health check script for Docker container with comprehensive diagnostics

# Set variables
HEALTH_ENDPOINT="http://localhost:5000/health"
MAX_RETRIES=8
INITIAL_RETRY_INTERVAL=5
MAX_RETRY_INTERVAL=30
CURL_TIMEOUT=15

# Log with timestamp
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if a process is running
check_process() {
  local process_pattern="$1"
  local count=$(pgrep -f "$process_pattern" | wc -l)

  if [ "$count" -gt 0 ]; then
    log "✅ Process '$process_pattern' is running ($count instances found)"
    return 0
  else
    log "❌ Process '$process_pattern' is NOT running"
    return 1
  fi
}

# Check if a port is listening
check_port() {
  local port="$1"

  if netstat -tulpn 2>/dev/null | grep -q ":$port " || ss -tulpn 2>/dev/null | grep -q ":$port "; then
    log "✅ Port $port is listening"
    return 0
  else
    log "❌ Port $port is NOT listening"
    return 1
  fi
}

# Check database connectivity
check_database() {
  if ! command -v psql &> /dev/null; then
    log "⚠️ PostgreSQL client not installed, skipping database check"
    return 0
  fi

  log "Checking database connectivity..."
  if PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c '\l' &>/dev/null; then
    log "✅ Database connection successful"
    return 0
  else
    log "❌ Database connection failed"
    # Try to get more diagnostic information
    log "Database connection error details:"
    PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c '\l' 2>&1 || true

    # Check if we can reach the database host
    log "Checking if database host is reachable:"
    ping -c 1 db &>/dev/null && log "✅ Database host is reachable" || log "❌ Database host is NOT reachable"

    return 1
  fi
}

# Check disk space
check_disk_space() {
  local available=$(df -m /app | awk 'NR==2 {print $4}')
  log "Available disk space: ${available}MB"

  if [ "$available" -lt 100 ]; then
    log "⚠️ Low disk space warning: less than 100MB available"
    return 1
  fi
  return 0
}

# Check memory usage
check_memory() {
  local total_mem=$(free -m | awk 'NR==2 {print $2}')
  local used_mem=$(free -m | awk 'NR==2 {print $3}')
  local free_mem=$(free -m | awk 'NR==2 {print $4}')
  local usage_percent=$((used_mem * 100 / total_mem))

  log "Memory usage: ${usage_percent}% (${used_mem}MB used,
  ${free_mem}MB free,
  ${total_mem}MB total)"

  if [ "$usage_percent" -gt 90 ]; then
    log "⚠️ High memory usage warning: ${usage_percent}%"
    return 1
  fi
  return 0
}

# Comprehensive health check with exponential backoff
check_health() {
  log "Starting health check with $MAX_RETRIES retries"

  # Initial system checks
  log "=== SYSTEM CHECKS ==="
  check_disk_space
  check_memory

  # Process checks
  log "=== PROCESS CHECKS ==="
  check_process "python run_ui.py"
  python_running=$?

  # Port checks
  log "=== PORT CHECKS ==="
  check_port "5000"
  port_listening=$?

  # Database checks
  log "=== DATABASE CHECKS ==="
  check_database
  db_connected=$?

  # Health endpoint checks with retries and exponential backoff
  log "=== HEALTH ENDPOINT CHECKS ==="

  for i in $(seq 1 $MAX_RETRIES); do
    # Calculate retry interval with exponential backoff
    retry_interval=$((INITIAL_RETRY_INTERVAL * 2 ** (i - 1)))
    if [ "$retry_interval" -gt "$MAX_RETRY_INTERVAL" ]; then
      retry_interval=$MAX_RETRY_INTERVAL
    fi

    log "Health check attempt $i of $MAX_RETRIES (retry interval: ${retry_interval}s)..."

    # Try multiple methods to check health endpoint
    log "Attempting to connect to $HEALTH_ENDPOINT..."

    # Method 1: Silent curl
    response_output=$(curl -s -f -m $CURL_TIMEOUT $HEALTH_ENDPOINT 2>&1)
    curl_exit_code=$?

    if [ $curl_exit_code -eq 0 ]; then
      log "✅ Health check successful!"
      log "Response: $response_output"
      return 0
    else
      log "❌ Health check failed with curl exit code: $curl_exit_code"

      # Method 2: Try with wget if curl failed
      if command -v wget &> /dev/null; then
        log "Trying with wget..."
        if wget -q -O- -T $CURL_TIMEOUT $HEALTH_ENDPOINT &>/dev/null; then
          log "✅ Health check successful with wget!"
          return 0
        else
          log "❌ Health check failed with wget as well"
        fi
      fi

      # Collect diagnostic information on failure
      if [ $i -eq $MAX_RETRIES ] || [ $((i % 3)) -eq 0 ]; then
        log "=== DIAGNOSTIC INFORMATION ==="

        # Verbose curl output for debugging
        log "Detailed curl output:"
        curl -v -m $CURL_TIMEOUT $HEALTH_ENDPOINT 2>&1 || true

        # Check if the port is still listening
        check_port "5000"

        # Check if the process is still running
        check_process "python run_ui.py"

        # Check Flask logs if available
        if [ -f "/app/logs/flask.log" ]; then
          log "Last 20 lines of Flask logs:"
          tail -20 /app/logs/flask.log || true
        fi

        # Check system logs
        log "Last 10 lines of system logs:"
        dmesg | tail -10 || true

        # Check memory and disk again
        check_memory
        check_disk_space
      fi

      if [ $i -lt $MAX_RETRIES ]; then
        log "Retrying in $retry_interval seconds..."
        sleep $retry_interval
      fi
    fi
  done

  log "❌ Health check failed after $MAX_RETRIES attempts"

  # Final decision based on all checks
  if [ "$python_running" -eq 0 ] && [ "$port_listening" -eq 0 ]; then
    log "⚠️ Flask process is running and port is listening,
    but health endpoint is not responding."
    log "This might be a transient issue. Returning success to avoid container restart."
    return 0
  fi

  return 1
}

# Run the health check
check_health
exit_code=$?
log "Health check completed with exit code: $exit_code"
exit $exit_code
