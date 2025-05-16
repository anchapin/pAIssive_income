FROM --platform=$BUILDPLATFORM ghcr.io/astral-sh/uv:python3.10-bookworm-slim AS builder

WORKDIR /app

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
    && apt-get clean \
    && rm -rf /lib/apt/lists/*

# Copy requirements files
COPY requirements-dev.txt .
COPY ai_models/requirements.txt ai_models_requirements.txt
RUN cat requirements-dev.txt ai_models_requirements.txt > requirements.txt

# Set up virtual environment and install dependencies
RUN uv venv /app/.venv \
    && . /app/.venv/bin/activate \
    # Clone and install MCP SDK first
    && git clone --depth 1 https://github.com/modelcontextprotocol/python-sdk.git /tmp/mcp-sdk \
    && cd /tmp/mcp-sdk \
    && uv pip install -e . \
    && cd /app \
    && rm -rf /tmp/mcp-sdk \
    # Then install other requirements
    && uv pip install --no-cache -r requirements.txt --python /app/.venv/bin/python

# Copy application code
COPY . .

# Set up PATH and PYTHONPATH
ENV PYTHONPATH="/app"
ENV PATH="/app/.venv/bin:$PATH"

# Set virtual environment activation
ENV VIRTUAL_ENV="/app/.venv"

# Health check script
COPY docker-healthcheck.sh /app/docker-healthcheck.sh
RUN chmod +x /app/docker-healthcheck.sh

# Set default platform values
ARG TARGETPLATFORM
ARG BUILDPLATFORM
RUN echo "Building on $BUILDPLATFORM for $TARGETPLATFORM"

# Run the application with wait-for-db script and initialize agent database
CMD ["/bin/bash", "-c", "/usr/local/bin/wait-for-db.sh db 5432 && python init_agent_db.py && python run_ui.py"]
