# Containerization Guide

This document provides instructions for containerizing and running the pAIssive Income application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system

## Files

- `Dockerfile`: Defines how to build the Docker image for the application
- `docker-compose.yml`: Defines the services, networks, and volumes for the application
- `.dockerignore`: Specifies files and directories to exclude from the Docker build context
- `docker-healthcheck.sh`: Script for checking the health of the Docker container

## Building and Running

### Build the Docker Image

```bash
docker build -t paissive-income .
```

### Run with Docker

```bash
docker run -p 5000:5000 paissive-income
```

### Run with Docker Compose

```bash
docker-compose up
```

To run in detached mode:

```bash
docker-compose up -d
```

## Environment Variables

The following environment variables can be set to configure the application:

- `FLASK_ENV`: Set to `production` for production environment
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `PASSWORD_RESET_SECRET_KEY`: Secret key for password reset token generation
- `REFRESH_TOKEN_SECRET_KEY`: Secret key for refresh token generation

## Volumes

The Docker Compose configuration includes a volume for persistent data:

- `./data:/app/data`: Maps the local `data` directory to `/app/data` in the container

## Health Checks

The Docker container includes a health check that verifies the application is running correctly. The health check:

- Makes an HTTP request to the application
- Runs every 30 seconds
- Has a timeout of 10 seconds
- Retries 3 times before marking the container as unhealthy
- Has a 5-second start period to allow the application to initialize

## Additional Services

The Docker Compose file includes commented sections for additional services:

- Redis: For caching and session storage
- PostgreSQL: For database storage

To enable these services, uncomment the relevant sections in the `docker-compose.yml` file.

## Troubleshooting

### Container Fails to Start

If the container fails to start, check the logs:

```bash
docker-compose logs
```

### Health Check Fails

If the health check fails, check if the application is running correctly:

```bash
docker exec -it paissive_income_app curl http://localhost:5000/
```

### Application Not Accessible

If the application is not accessible from the host, check if the port mapping is correct:

```bash
docker-compose ps
```

## Production Deployment

For production deployment, consider the following:

1. Use a proper secret management solution for environment variables
2. Enable and configure the database service
3. Set up a reverse proxy (e.g., Nginx) for SSL termination
4. Configure proper logging and monitoring
5. Set up container orchestration (e.g., Kubernetes) for scaling and high availability
