FROM python:3.13-slim

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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements-dev.txt .
COPY ai_models/requirements.txt ai_models_requirements.txt

# Create a consolidated requirements file
RUN cat requirements-dev.txt ai_models_requirements.txt > requirements.txt

# Install uv (modern Python packaging tool)
RUN pip install --no-cache-dir uv

# Install Python dependencies with uv (much faster and reproducible)
RUN uv pip install -r requirements.txt

# If you use requirements.lock for fully deterministic builds, replace the above with:
# COPY requirements.lock .
# RUN uv pip sync requirements.lock

# Copy project files
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "run_ui.py"]
