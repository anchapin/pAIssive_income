# Docker Compose Integration

This document provides information about the Docker Compose integration for the pAIssive_income project.

## Overview

The Docker Compose setup allows you to run the entire application stack with a single command. It includes:

- Flask backend API
- React frontend with ag-ui integration
- PostgreSQL database
- (Optional) Redis for caching

## Prerequisites

- Docker installed and running
- Docker Compose installed (either as a plugin or standalone)
- Git repository cloned locally

## Configuration

The Docker Compose configuration is defined in the `docker-compose.yml` file in the root of the project. The main services are:

1. **app**: The Flask backend API
2. **frontend**: The React frontend with ag-ui integration
3. **db**: PostgreSQL database
4. **redis**: (Optional) Redis for caching

## Environment Variables

The Docker Compose setup uses environment variables defined in the `docker-compose.yml` file. You can override these by creating a `.env` file in the root of the project. See `.env.example` for a template.

Key environment variables:

- `FLASK_ENV`: Set to `development` or `production`
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Database credentials
- `REACT_APP_API_URL`: URL for the frontend to connect to the API
- `REACT_APP_AG_UI_ENABLED`: Set to `true` to enable ag-ui integration

## Usage

### Starting the Services

To start all services:

```bash
docker compose up -d
```

Or if you're using standalone Docker Compose:

```bash
docker-compose up -d
```

Add the `--build` flag to rebuild the images:

```bash
docker compose up -d --build
```

### Stopping the Services

To stop all services:

```bash
docker compose down
```

To stop and remove volumes (this will delete all data):

```bash
docker compose down -v
```

### Viewing Logs

To view logs for all services:

```bash
docker compose logs
```

To view logs for a specific service:

```bash
docker compose logs app
docker compose logs frontend
docker compose logs db
```

Add the `-f` flag to follow the logs:

```bash
docker compose logs -f app
```

### Testing the Setup

You can use the provided `test_docker_compose.sh` script to test the Docker Compose setup:

```bash
./test_docker_compose.sh
```

This script will:
1. Validate the docker-compose.yml file
2. Create the required Docker network
3. Build and start all services
4. Check the health of each service
5. Clean up (optional)

## Health Checks

Each service has a health check configured:

- **app**: Checks the `/health` endpoint
- **frontend**: Checks if the web server is responding
- **db**: Checks if PostgreSQL is accepting connections

## Volumes

The Docker Compose setup uses the following volumes:

- `postgres-data`: Persists PostgreSQL data
- `redis-data`: Persists Redis data (if enabled)
- Local volume mounts for development:
  - `./data:/app/data`: Application data
  - `./logs:/app/logs`: Application logs
  - `./ui/react_frontend:/app`: Frontend source code

## Networks

All services are connected to the `paissive-network` bridge network, allowing them to communicate with each other using service names as hostnames.

## GitHub Actions Integration

The Docker Compose setup is integrated with GitHub Actions for CI/CD. The workflow is defined in `.github/workflows/docker-compose-integration.yml`.

The workflow:
1. Sets up Docker and Docker Compose
2. Validates the docker-compose.yml file
3. Builds and starts all services
4. Checks the health of each service
5. Reports success or failure

## Troubleshooting

### Common Issues

1. **Services not starting**: Check the logs with `docker compose logs`
2. **Database connection issues**: Ensure the database is healthy with `docker compose ps db`
3. **Frontend not connecting to API**: Check the `REACT_APP_API_URL` environment variable

### Debugging

For detailed debugging:

```bash
# Check service status
docker compose ps

# Check container details
docker inspect <container_name>

# Check network connectivity
docker network inspect paissive-network

# Check disk space
df -h
```

## Extending the Setup

To add a new service:

1. Add the service configuration to `docker-compose.yml`
2. Add appropriate health checks
3. Update dependencies between services
4. Test the setup with `test_docker_compose.sh`

## Performance Tuning

The PostgreSQL service includes some basic performance tuning:

```yaml
command: ["postgres", "-c", "max_connections=200", "-c", "shared_buffers=256MB"]
```

Adjust these values based on your system resources and requirements.
