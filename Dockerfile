FROM python:3.10-slim-bookworm

# Set working directory
WORKDIR /app

# Accept CI build argument
ARG CI=false

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    FLASK_APP=run_ui.py \
    FLASK_ENV=production \
    PATH="/root/.cargo/bin:$PATH" \
    CI=$CI

# Install system dependencies
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
       docker-compose \
       net-tools \
       netcat-openbsd \
       procps \
       dnsutils \
       iputils-ping \
       wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements-dev.txt .
COPY requirements-ci.txt .
COPY ai_models/requirements.txt ai_models_requirements.txt

# Choose requirements file based on environment
RUN if [ "$CI" = "true" ]; then \
      echo "Using minimal requirements for CI environment" && \
      cp requirements-ci.txt requirements.txt; \
    else \
      echo "Using full requirements for non-CI environment" && \
      cat requirements-dev.txt ai_models_requirements.txt > requirements.txt; \
    fi

# Install Python dependencies using pip (more reliable in CI)
RUN python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install -r requirements.txt && \
    # Verify Flask installation
    .venv/bin/python -c "import flask; print(f'Flask version: {flask.__version__}')" && \
    # Install additional packages that might be needed
    .venv/bin/pip install psycopg2-binary gunicorn

# Update PATH to include virtual environment for subsequent commands and runtime
ENV PATH="/app/.venv/bin:$PATH"

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs && \
    mkdir -p /app/data && \
    # Add a non-root user (using Debian commands)
    groupadd --system appgroup && \
    useradd --system --no-create-home --gid appgroup appuser && \
    # Set ownership and permissions for logs directory to allow writing
    chown -R root:appgroup /app/logs && \
    chmod 2777 /app/logs && \
    # Set ownership and permissions for data directory
    chown -R root:appgroup /app/data && \
    chmod 2777 /app/data && \
    # Create log files with correct permissions
    touch /app/logs/flask.log /app/logs/error.log /app/logs/audit.log /app/logs/app.log && \
    chmod 666 /app/logs/*.log

# Copy project files
COPY --chown=root:appgroup . .

# Copy health check script and wait-for-db script (and fix permissions)
COPY docker-healthcheck.sh /usr/local/bin/
COPY wait-for-db.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-healthcheck.sh /usr/local/bin/wait-for-db.sh && \
    sed -i 's/\r$//' /usr/local/bin/docker-healthcheck.sh && \
    sed -i 's/\r$//' /usr/local/bin/wait-for-db.sh

# Verify scripts are executable
RUN ls -la /usr/local/bin/docker-healthcheck.sh /usr/local/bin/wait-for-db.sh && \
    # Verify Python can import Flask (using the virtual environment)
    .venv/bin/python -c "import flask; print(f'Flask version: {flask.__version__}')" && \
    # Verify the run_ui.py file exists and is readable
    ls -la /app/run_ui.py && \
    # Verify the init_db.py file exists and is readable
    ls -la /app/init_db.py

# Health check with increased start period and retries
HEALTHCHECK --interval=30s --timeout=60s --start-period=240s --retries=12 \
  CMD ["/usr/local/bin/docker-healthcheck.sh"]

# Expose port
EXPOSE 5000

# Switch to non-root user for security
USER appuser

# Run the application with wait-for-db script
CMD ["/bin/bash", "-c", "/usr/local/bin/wait-for-db.sh db 5432 python run_ui.py"]