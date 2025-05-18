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

### Troubleshooting

- If you see errors like `sh: not found` or `/bin/sh: no such file or directory`, make sure:
  - Your entrypoint and healthcheck use Python (not shell scripts).
  - All scripts are executable and present in the final image.

### References

- [Distroless images](https://github.com/GoogleContainerTools/distroless)
- [Docker multi-stage builds](https://docs.docker.com/build/building/multi-stage/)

---

Setup, usage, common commands, and multi-container apps.