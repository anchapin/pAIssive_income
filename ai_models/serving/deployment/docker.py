"""
Docker deployment utilities for AI models.

This module provides utilities for deploying AI models with Docker.
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List

# Set up logging
logging.basicConfig(
    level=logging.INFO, format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class DockerConfig:
    """
    Configuration for Docker deployment.
    """

    # Basic configuration
    image_name: str
    image_tag: str = "latest"
    base_image: str = "python:3.9 - slim"

    # Server configuration
    server_type: str = "rest"  # "rest" or "grpc"
    host: str = "127.0.0.1"
    port: int = 8000

    # Model configuration
    model_path: str = ""
    model_type: str = "text - generation"
    model_id: str = ""

    # Resource configuration
    cpu_limit: str = "1"
    memory_limit: str = "4Gi"
    gpu_count: int = 0

    # Environment variables
    env_vars: Dict[str, str] = field(default_factory=dict)

    # Volume configuration
    volumes: List[Dict[str, str]] = field(default_factory=list)

    # Additional configuration
    additional_packages: List[str] = field(default_factory=list)
    additional_commands: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "image_name": self.image_name,
            "image_tag": self.image_tag,
            "base_image": self.base_image,
            "server_type": self.server_type,
            "host": self.host,
            "port": self.port,
            "model_path": self.model_path,
            "model_type": self.model_type,
            "model_id": self.model_id,
            "cpu_limit": self.cpu_limit,
            "memory_limit": self.memory_limit,
            "gpu_count": self.gpu_count,
            "env_vars": self.env_vars,
            "volumes": self.volumes,
            "additional_packages": self.additional_packages,
            "additional_commands": self.additional_commands,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "DockerConfig":
        """
        Create a configuration from a dictionary.

        Args:
            config_dict: Dictionary with configuration parameters

        Returns:
            Docker configuration
        """
        return cls(**config_dict)


def generate_docker_config(config: DockerConfig, output_dir: str) -> str:
    """
    Generate Docker configuration files.

    Args:
        config: Docker configuration
        output_dir: Directory to save the configuration files

    Returns:
        Path to the generated Dockerfile
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Generate Dockerfile
    dockerfile_path = os.path.join(output_dir, "Dockerfile")
    _generate_dockerfile(config, dockerfile_path)

    # Generate docker - compose.yml
    compose_path = os.path.join(output_dir, "docker - compose.yml")
    _generate_docker_compose(config, compose_path)

    # Generate .dockerignore
    dockerignore_path = os.path.join(output_dir, ".dockerignore")
    _generate_dockerignore(dockerignore_path)

    # Generate entrypoint.sh
    entrypoint_path = os.path.join(output_dir, "entrypoint.sh")
    _generate_entrypoint(config, entrypoint_path)

    # Generate requirements.txt
    requirements_path = os.path.join(output_dir, "requirements.txt")
    _generate_requirements(config, requirements_path)

    logger.info(f"Docker configuration files generated in {output_dir}")

    return dockerfile_path


def _generate_dockerfile(config: DockerConfig, output_path: str) -> None:
    """
    Generate a Dockerfile.

    Args:
        config: Docker configuration
        output_path: Path to save the Dockerfile
    """
    # Create Dockerfile content
    content = f"""
FROM {config.base_image}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt - get update && apt - get install -y \\
    build - essential \\
    curl \\
    git \\
    && rm -rf /var / lib / apt / lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no - cache - dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV MODEL_PATH={config.model_path}
ENV MODEL_TYPE={config.model_type}
ENV MODEL_ID={config.model_id}
ENV SERVER_TYPE={config.server_type}
ENV HOST={config.host}
ENV PORT={config.port}
"""

    # Add environment variables
    for key, value in config.env_vars.items():
        content += f"ENV {key}={value}\n"

    # Add GPU support if needed
    if config.gpu_count > 0:
        content += """
# Install CUDA dependencies
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
"""

    # Add additional commands
    if config.additional_commands:
        content += "\n# Additional commands\n"
        for command in config.additional_commands:
            content += f"RUN {command}\n"

    # Add entrypoint
    content += """
# Make entrypoint executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE ${PORT}

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]
"""

    # Write Dockerfile
    with open(output_path, "w", encoding="utf - 8") as f:
        f.write(content.strip())


def _generate_docker_compose(config: DockerConfig, output_path: str) -> None:
    """
    Generate a docker - compose.yml file.

    Args:
        config: Docker configuration
        output_path: Path to save the docker - compose.yml file
    """
    # Create docker - compose.yml content
    content = f"""
version: '3'

services:
  model - server:
    build:
      context: .
      dockerfile: Dockerfile
    image: {config.image_name}:{config.image_tag}
    container_name: model - server
    ports:
      - "{config.port}:{config.port}"
    environment:
      - MODEL_PATH={config.model_path}
      - MODEL_TYPE={config.model_type}
      - MODEL_ID={config.model_id}
      - SERVER_TYPE={config.server_type}
      - HOST={config.host}
      - PORT={config.port}
"""

    # Add environment variables
    for key, value in config.env_vars.items():
        content += f"      - {key}={value}\n"

    # Add volumes
    if config.volumes:
        content += "    volumes:\n"
        for volume in config.volumes:
            content += f"      - {volume['source']}:{volume['target']}\n"

    # Add resource limits
    content += f"""
    deploy:
      resources:
        limits:
          cpus: '{config.cpu_limit}'
          memory: {config.memory_limit}
"""

    # Add GPU support if needed
    if config.gpu_count > 0:
        content += """
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
"""

    # Write docker - compose.yml
    with open(output_path, "w", encoding="utf - 8") as f:
        f.write(content.strip())


def _generate_dockerignore(output_path: str) -> None:
    """
    Generate a .dockerignore file.

    Args:
        output_path: Path to save the .dockerignore file
    """
    # Create .dockerignore content
    content = """
# Git
.git
.gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop - eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg - info/
.installed.cfg
*.egg

# Virtual environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Docker
Dockerfile
docker - compose.yml
.dockerignore

# Logs
logs/
*.log

# Data
data/
models/
"""

    # Write .dockerignore
    with open(output_path, "w", encoding="utf - 8") as f:
        f.write(content.strip())


def _generate_entrypoint(config: DockerConfig, output_path: str) -> None:
    """
    Generate an entrypoint.sh file.

    Args:
        config: Docker configuration
        output_path: Path to save the entrypoint.sh file
    """
    # Create entrypoint.sh content
    content = """#!/bin / bash
set -e

# Download model if needed
if [ ! -d "$MODEL_PATH" ]; then
    echo "Downloading model..."
    python -m ai_models.cli download --model - id $MODEL_ID --output - dir $MODEL_PATH
fi

# Start server
if [ "$SERVER_TYPE" = "rest" ]; then
    echo "Starting REST API server..."
    python -m ai_models.cli serve - rest --model - path $MODEL_PATH --model - type $MODEL_TYPE --host $HOST --port $PORT
elif [ "$SERVER_TYPE" = "grpc" ]; then
    echo "Starting gRPC server..."
    python -m ai_models.cli serve - grpc --model - path $MODEL_PATH --model - type $MODEL_TYPE --host $HOST --port $PORT
else
    echo "Unknown server type: $SERVER_TYPE"
    exit 1
fi
"""

    # Write entrypoint.sh
    with open(output_path, "w", encoding="utf - 8") as f:
        f.write(content.strip())


def _generate_requirements(config: DockerConfig, output_path: str) -> None:
    """
    Generate a requirements.txt file.

    Args:
        config: Docker configuration
        output_path: Path to save the requirements.txt file
    """
    # Create requirements.txt content
    content = """
# Core dependencies
torch>=1.10.0
transformers>=4.20.0
sentence - transformers>=2.2.0

# Server dependencies
fastapi>=0.95.0
uvicorn>=0.22.0
grpcio>=1.54.0
grpcio - reflection>=1.54.0
grpcio - health - checking>=1.54.0
protobuf>=4.22.3

# Utility dependencies
numpy>=1.24.3
tqdm>=4.65.0
psutil>=5.9.5
"""

    # Add additional packages
    if config.additional_packages:
        content += "\n# Additional packages\n"
        for package in config.additional_packages:
            content += f"{package}\n"

    # Write requirements.txt
    with open(output_path, "w", encoding="utf - 8") as f:
        f.write(content.strip())
