FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements-dev.txt .
COPY ai_models/requirements.txt ai_models_requirements.txt

# Create a consolidated requirements file
RUN cat requirements-dev.txt ai_models_requirements.txt > requirements.txt

# Install Python dependencies using uv and create a virtual environment
RUN uv venv .venv && \
    # Use the system-wide uv to install packages into the virtual environment
    uv pip install --no-cache -r requirements.txt --python .venv/bin/python

# Update PATH to include virtual environment for subsequent commands and runtime
# This is good for making `python` and other tools resolve to the venv versions.
ENV PATH="/app/.venv/bin:$PATH"

# Copy project files
COPY . .

# Copy health check script and wait-for-db script (and fix permissions)
# Consolidate these RUN commands to reduce layers
COPY docker-healthcheck.sh /usr/local/bin/
COPY wait-for-db.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-healthcheck.sh /usr/local/bin/wait-for-db.sh && \
    sed -i 's/\r$//' /usr/local/bin/docker-healthcheck.sh && \
    sed -i 's/\r$//' /usr/local/bin/wait-for-db.sh && \
    # Install additional diagnostic tools
    # It's better to group apt-get installs if possible
    apt-get update && \
    apt-get install -y --no-install-recommends \
       net-tools \
       netcat-openbsd \
       procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Health check
HEALTHCHECK --interval=30s --timeout=60s --start-period=180s --retries=10 \
  CMD ["/usr/local/bin/docker-healthcheck.sh"]

# Expose port
EXPOSE 5000

# Add a non-root user (using Debian commands)
RUN groupadd --system appgroup && useradd --system --no-create-home --gid appgroup appuser
USER appuser

# Run the application with wait-for-db script
CMD ["/bin/bash", "-c", "/usr/local/bin/wait-for-db.sh db 5432 python run_ui.py"]