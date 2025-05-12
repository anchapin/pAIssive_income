FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       git \
       curl \
       libpq-dev \
       postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements-dev.txt .
COPY ai_models/requirements.txt ai_models_requirements.txt

# Create a consolidated requirements file
RUN cat requirements-dev.txt ai_models_requirements.txt > requirements.txt

# Create a virtual environment and install dependencies
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir uv && \
    /app/.venv/bin/uv pip install -r requirements.txt

# Copy project files
COPY . .

# Copy health check script
COPY docker-healthcheck.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-healthcheck.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=5 \
  CMD ["docker-healthcheck.sh"]

# Expose port
EXPOSE 5000

# Add a non-root user
RUN addgroup --system appgroup && adduser --system --no-create-home appuser --ingroup appgroup
USER appuser

# Run the application
CMD ["python", "run_ui.py"]
