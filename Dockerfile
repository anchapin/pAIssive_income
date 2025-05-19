# --- Builder Stage ---
FROM --platform=$BUILDPLATFORM ghcr.io/astral-sh/uv:python3.10-bookworm-slim AS builder

WORKDIR /app

# Accept CI build argument
ARG CI=false

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    FLASK_APP=run_ui.py \
    FLASK_ENV=production \
    CI=$CI

# System dependencies (build only)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       git \
       curl \
       libpq-dev \
       postgresql-client \
       libffi-dev \
       python3-dev \
       net-tools \
       netcat-openbsd \
       procps \
       dnsutils \
       iputils-ping \
       wget \
    && apt-get clean \
    && rm -rf /lib/apt/lists/*

# Copy requirements files
COPY requirements-dev.txt .
COPY requirements-ci.txt .
COPY ai_models/requirements.txt ai_models_requirements.txt

# Select requirements file based on environment
RUN if [ "$CI" = "true" ]; then \
      cp requirements-ci.txt requirements.txt; \
    else \
      cat requirements-dev.txt ai_models_requirements.txt > requirements.txt; \
    fi

# Set up virtual environment and install dependencies
RUN uv venv /app/.venv \
    && . /app/.venv/bin/activate \
    && git clone --depth 1 https://github.com/modelcontextprotocol/python-sdk.git /tmp/mcp-sdk \
    && cd /tmp/mcp-sdk \
    && uv pip install -e . \
    && cd /app \
    && rm -rf /tmp/mcp-sdk \
    && uv pip install --no-cache -r requirements.txt --python /app/.venv/bin/python \
    && uv pip install psycopg2-binary gunicorn

# Copy application code (permissions are not preserved into distroless)
COPY . .

# Prepare runtime directories and log files
RUN mkdir -p /app/logs /app/data && \
    touch /app/logs/flask.log /app/logs/error.log /app/logs/audit.log /app/logs/app.log

# Install mem0 and its dependencies
RUN . /app/.venv/bin/activate && \
    uv pip install mem0ai qdrant-client openai pytz

# Ensure scripts are executable and have unix line endings
RUN chmod +x /app/docker-healthcheck.sh /app/wait-for-db.sh && \
    sed -i 's/\r$//' /app/docker-healthcheck.sh && \
    sed -i 's/\r$//' /app/wait-for-db.sh

# --- Runtime Stage: Distroless Python ---
FROM gcr.io/distroless/python3-debian11 AS runtime

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy only production application code and assets.
# DO NOT copy the entire /app to avoid including dev artefacts, .git, or test files.
# Adjust this list as needed for your project structure.
COPY --from=builder /app/api /app/api
COPY --from=builder /app/ai_models /app/ai_models
COPY --from=builder /app/niche_analysis /app/niche_analysis
COPY --from=builder /app/monetization /app/monetization
COPY --from=builder /app/marketing /app/marketing
COPY --from=builder /app/users /app/users
COPY --from=builder /app/common_utils /app/common_utils
COPY --from=builder /app/run_ui.py /app/run_ui.py
COPY --from=builder /app/init_db.py /app/init_db.py
COPY --from=builder /app/main.py /app/main.py
COPY --from=builder /app/docker-healthcheck.sh /app/docker-healthcheck.sh
COPY --from=builder /app/wait-for-db.sh /app/wait-for-db.sh

# If you need additional files (e.g., config, static assets), add them above.
# Ensure .dockerignore excludes dev/test files, .git, and other artefacts.

# Environment variables (runtime)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    FLASK_APP=run_ui.py \
    FLASK_ENV=production \
    PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv"

# Health check (distroless does not include shell, use python)
HEALTHCHECK --interval=30s --timeout=60s --start-period=240s --retries=12 \
  CMD ["python", "-c", "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/health').read().decode())"]

# Expose port (if needed, e.g., 5000 for Flask)
EXPOSE 5000

# Use a non-root user (distroless default is non-root user)
# If you want to specify UID/GID, add: USER 65532

# Entrypoint (ensure this uses the venv python)
CMD ["/app/.venv/bin/python", "/app/run_ui.py"]
