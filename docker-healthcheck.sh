#!/bin/bash
# Health check script for Docker container

# Check if the application is running
curl -f http://localhost:5000/ || exit 1
