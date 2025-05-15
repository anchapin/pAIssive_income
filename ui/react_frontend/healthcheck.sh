#!/bin/sh
# Simple health check for React frontend

# Check if the server is responding
if wget -q --spider http://localhost:3000; then
  echo "Frontend is healthy"
  exit 0
else
  echo "Frontend is not healthy"
  exit 1
fi
