"""
Fix Dockerfile to use the uv-based image.

This script creates a Dockerfile that uses the ghcr.io/astral-sh/uv image
as the base, which includes uv pre-installed.
"""

from pathlib import Path


def fix_dockerfile() -> None:
    """
    Create a Dockerfile using the uv-based image.

    The Dockerfile will use ghcr.io/astral-sh/uv:python3.10-bookworm-slim
    as the base image and set up the project dependencies.
    """
    dockerfile_content = """FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

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

# Combine requirements
RUN cat requirements-dev.txt ai_models_requirements.txt > requirements.txt

# Create venv and install dependencies
RUN uv venv .venv

# Clone and install MCP SDK first
RUN git clone https://github.com/modelcontextprotocol/python-sdk.git /tmp/mcp-sdk && \
    cd /tmp/mcp-sdk && \
    uv pip install -e . --python .venv/bin/python && \
    cd /app && \
    rm -rf /tmp/mcp-sdk

# Install project dependencies
RUN uv pip install --no-cache -r requirements.txt --python .venv/bin/python

# Copy entire project
COPY . .

# Set the working directory
WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set Python path
ENV PYTHONPATH=/app

CMD ["python", "-m", "tests"]
"""

    dockerfile_path = Path("Dockerfile")
    with dockerfile_path.open("w") as f:
        f.write(dockerfile_content)


if __name__ == "__main__":
    fix_dockerfile()
