# Docker and Docker Compose

## Multi-Stage & Distroless Docker Builds

The Dockerfile for this project uses a **multi-stage build** and a **distroless** runtime image for optimal security and efficiency.

### How it works

- **Builder stage:** Installs build tools, system dependencies, Python packages, and clones required repositories.
- **Runtime stage:** Uses [`gcr.io/distroless/python3-debian11`](https://github.com/GoogleContainerTools/distroless) as the base. Only the minimal Python runtime and your app + virtualenv are included.
- **Benefits:**  
  - Image size is much smaller (no build tools in runtime).
  - Attack surface is greatly reduced (no shell, package manager, or compilers).
  - No root user—uses the non-root user provided by distroless by default.

### Important Notes

- **No /bin/sh or shell!**  
  All healthchecks, entrypoints, and scripts must use the Python interpreter (`/app/.venv/bin/python` or your venv’s Python). Bash scripts will not work unless explicitly supported.
- **Scripts:**  
  - Make sure any scripts (like `docker-healthcheck.sh`, `wait-for-db.sh`) are executable and use UNIX line endings.
  - Prefer Python scripts for container healthchecks and orchestration.
- **Entrypoint:**  
  Set the entrypoint to use the virtual environment’s Python interpreter or a direct binary.

### Building and Running

```bash
# Build the image (from the project root)
docker build -t paissive_income:latest .

# Or use Docker Compose
docker compose build
docker compose up
```

#### ⚠️ Best Practice: Keep the Runtime Image Slim

- **Do NOT copy the entire build context into the runtime image.**  
  Instead, copy only application code, dependencies, and config needed to run the app.
- Use a strict `.dockerignore` to exclude:
  - `.git`, test directories, docs, dev scripts, local configs, and any secrets.
  - Dev requirements files (`requirements-dev.txt`, etc.)
- The sample Dockerfile may use `COPY --from=builder /app /app` for clarity, but you should refine this to include only what is strictly necessary (e.g., `/app/api`, `/app/ai_models`, `/app/.venv`, etc.), and update `.dockerignore` accordingly.

### Troubleshooting

- If you see errors like `sh: not found` or `/bin/sh: no such file or directory`, make sure:
  - Your entrypoint and healthcheck use Python (not shell scripts).
  - All scripts are executable and present in the final image.

### References

- [Distroless images](https://github.com/GoogleContainerTools/distroless)
- [Docker multi-stage builds](https://docs.docker.com/build/building/multi-stage/)

---

## Docker Compose Integration

This section covers Docker Compose integration for the project, combining local development, multi-service orchestration, and CI/CD use.

### Overview

The Docker Compose setup allows you to run the entire application stack with one command. It includes:

- Flask backend API
- React frontend with ag-ui integration
- PostgreSQL database
- (Optional) Redis for caching

### Prerequisites

- Docker and Docker Compose installed
- Repository cloned locally

### Configuration

The main configuration is in `docker-compose.yml` at the project root, with services:
- **app**: Flask backend
- **frontend**: React frontend
- **db**: PostgreSQL
- **redis**: (optional) Redis

### Environment Variables

Set variables in `.env` (see `.env.example`), e.g.:
- `FLASK_ENV`
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `REACT_APP_API_URL`
- `REACT_APP_AG_UI_ENABLED`

### Usage

#### Docker Compose Bake (Build Acceleration)

Set `COMPOSE_BAKE=true` to enable advanced parallel builds:

```bash
export COMPOSE_BAKE=true
docker compose up -d --build
```

Unset to revert to standard Compose behavior.

#### Start/Stop/Logs

```bash
docker compose up -d        # Start all services
docker compose up -d --build  # Build and start
docker compose down         # Stop all
docker compose down -v      # Stop/remove volumes
docker compose logs         # Logs for all
docker compose logs app     # Logs for app only
docker compose logs -f app  # Follow logs
```

#### Testing Compose Setup

Use the script:

```bash
./test_docker_compose.sh
```

### Health Checks

- **app**: `/health`
- **frontend**: web server response
- **db**: PostgreSQL connection

### Volumes

- `postgres-data` (PostgreSQL)
- `redis-data` (Redis, if enabled)
- `./data`, `./logs`, `./ui/react_frontend` (for dev)

### Networks

All services use the `paissive-network` bridge.

### CI/CD Integration

The setup is integrated into GitHub Actions via `.github/workflows/docker-compose-integration.yml`:
- Sets up Docker, validates Compose config, builds/starts services, checks health, reports status

### Troubleshooting

- Use `docker compose logs` for issues
- Check PostgreSQL health with `docker compose ps db`
- Verify `REACT_APP_API_URL` for frontend API
- For Bake issues, unset `COMPOSE_BAKE` and retry

### Debugging

- `docker compose ps`
- `docker inspect <container>`
- `docker network inspect paissive-network`
- `df -h` for disk space

### Extending Setup

- Add new services in `docker-compose.yml`
- Add/update health checks
- Update dependencies
- Test with `test_docker_compose.sh`

### Performance Tuning

- Compose Bake (`COMPOSE_BAKE=true`) improves build times with parallelism
- PostgreSQL tuning via service command (see `docker-compose.yml`)

---