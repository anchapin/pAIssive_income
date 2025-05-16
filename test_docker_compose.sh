#!/bin/bash
# Script to test Docker Compose setup locally

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
  local color=$1
  local message=$2
  echo -e "${color}${message}${NC}"
}

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to check if Docker is running
check_docker_running() {
  if ! docker info >/dev/null 2>&1; then
    print_message "$RED" "ERROR: Docker daemon is not running. Please start Docker and try again."
    exit 1
  fi
  print_message "$GREEN" "✅ Docker daemon is running."
}

# Function to determine which Docker Compose command to use
get_compose_cmd() {
  if command_exists "docker compose"; then
    print_message "$GREEN" "✅ Using Docker Compose plugin"
    echo "docker compose"
  elif command_exists "docker-compose"; then
    print_message "$GREEN" "✅ Using standalone Docker Compose"
    echo "docker-compose"
  else
    print_message "$RED" "❌ Docker Compose not found. Please install Docker Compose and try again."
    exit 1
  fi
}

# Function to validate docker-compose.yml
validate_compose_file() {
  local compose_cmd=$1
  print_message "$YELLOW" "Validating docker-compose.yml..."
  
  if ! $compose_cmd config > /dev/null; then
    print_message "$RED" "❌ docker-compose.yml validation failed."
    return 1
  fi
  
  print_message "$GREEN" "✅ docker-compose.yml validation successful."
  return 0
}

# Function to create Docker network if it doesn't exist
create_network() {
  print_message "$YELLOW" "Creating Docker network 'paissive-network' if it doesn't exist..."
  docker network create paissive-network 2>/dev/null || true
  print_message "$GREEN" "✅ Network setup complete."
}

# Function to build and start services
start_services() {
  local compose_cmd=$1
  print_message "$YELLOW" "Building and starting services..."
  
  if ! $compose_cmd up --build -d; then
    print_message "$RED" "❌ Failed to start services."
    return 1
  fi
  
  print_message "$GREEN" "✅ Services started successfully."
  return 0
}

# Function to check service health
check_service_health() {
  local compose_cmd=$1
  local service=$2
  local max_attempts=$3
  local interval=$4
  
  print_message "$YELLOW" "Checking health of $service service (max $max_attempts attempts, $interval seconds interval)..."
  
  for i in $(seq 1 $max_attempts); do
    print_message "$YELLOW" "Attempt $i of $max_attempts..."
    
    if $compose_cmd ps $service | grep -q "Up"; then
      print_message "$GREEN" "✅ $service service is running."
      return 0
    fi
    
    if [ $i -lt $max_attempts ]; then
      print_message "$YELLOW" "Waiting $interval seconds before next attempt..."
      sleep $interval
    fi
  done
  
  print_message "$RED" "❌ $service service failed to start after $max_attempts attempts."
  return 1
}

# Function to check API health
check_api_health() {
  local max_attempts=$1
  local interval=$2
  
  print_message "$YELLOW" "Checking API health (max $max_attempts attempts, $interval seconds interval)..."
  
  for i in $(seq 1 $max_attempts); do
    print_message "$YELLOW" "Attempt $i of $max_attempts..."
    
    if curl -s -f http://localhost:5000/health > /dev/null; then
      print_message "$GREEN" "✅ API is healthy."
      return 0
    fi
    
    if [ $i -lt $max_attempts ]; then
      print_message "$YELLOW" "Waiting $interval seconds before next attempt..."
      sleep $interval
    fi
  done
  
  print_message "$RED" "❌ API health check failed after $max_attempts attempts."
  return 1
}

# Function to check frontend health
check_frontend_health() {
  local max_attempts=$1
  local interval=$2
  
  print_message "$YELLOW" "Checking frontend health (max $max_attempts attempts, $interval seconds interval)..."
  
  for i in $(seq 1 $max_attempts); do
    print_message "$YELLOW" "Attempt $i of $max_attempts..."
    
    if curl -s -f http://localhost:3000 > /dev/null; then
      print_message "$GREEN" "✅ Frontend is healthy."
      return 0
    fi
    
    if [ $i -lt $max_attempts ]; then
      print_message "$YELLOW" "Waiting $interval seconds before next attempt..."
      sleep $interval
    fi
  done
  
  print_message "$RED" "❌ Frontend health check failed after $max_attempts attempts."
  return 1
}

# Function to display service logs
show_logs() {
  local compose_cmd=$1
  local service=$2
  
  print_message "$YELLOW" "Showing logs for $service service..."
  $compose_cmd logs $service
}

# Function to clean up
cleanup() {
  local compose_cmd=$1
  
  print_message "$YELLOW" "Cleaning up..."
  $compose_cmd down -v
  print_message "$GREEN" "✅ Cleanup complete."
}

# Main function
main() {
  print_message "$YELLOW" "Starting Docker Compose test..."
  
  # Check if Docker is running
  check_docker_running
  
  # Get Docker Compose command
  compose_cmd=$(get_compose_cmd)
  
  # Validate docker-compose.yml
  if ! validate_compose_file "$compose_cmd"; then
    print_message "$RED" "❌ Test failed: docker-compose.yml validation failed."
    exit 1
  fi
  
  # Create network
  create_network
  
  # Build and start services
  if ! start_services "$compose_cmd"; then
    print_message "$RED" "❌ Test failed: Could not start services."
    cleanup "$compose_cmd"
    exit 1
  fi
  
  # Check service health
  if ! check_service_health "$compose_cmd" "db" 20 5; then
    print_message "$RED" "❌ Test failed: Database service is not healthy."
    show_logs "$compose_cmd" "db"
    cleanup "$compose_cmd"
    exit 1
  fi
  
  if ! check_service_health "$compose_cmd" "app" 30 10; then
    print_message "$RED" "❌ Test failed: App service is not healthy."
    show_logs "$compose_cmd" "app"
    cleanup "$compose_cmd"
    exit 1
  fi
  
  if ! check_service_health "$compose_cmd" "frontend" 20 5; then
    print_message "$RED" "❌ Test failed: Frontend service is not healthy."
    show_logs "$compose_cmd" "frontend"
    cleanup "$compose_cmd"
    exit 1
  fi
  
  # Check API health
  if ! check_api_health 20 10; then
    print_message "$RED" "❌ Test failed: API health check failed."
    show_logs "$compose_cmd" "app"
    cleanup "$compose_cmd"
    exit 1
  fi
  
  # Check frontend health
  if ! check_frontend_health 20 10; then
    print_message "$RED" "❌ Test failed: Frontend health check failed."
    show_logs "$compose_cmd" "frontend"
    cleanup "$compose_cmd"
    exit 1
  fi
  
  print_message "$GREEN" "✅ All tests passed! Docker Compose setup is working correctly."
  
  # Ask if user wants to keep services running
  read -p "Do you want to keep the services running? (y/n): " keep_running
  if [[ $keep_running != "y" && $keep_running != "Y" ]]; then
    cleanup "$compose_cmd"
  else
    print_message "$GREEN" "Services are still running. Use '$compose_cmd down' to stop them when you're done."
  fi
}

# Run the main function
main
