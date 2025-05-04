"""
"""
Docker deployment utilities for AI models.
Docker deployment utilities for AI models.


This module provides utilities for deploying AI models with Docker.
This module provides utilities for deploying AI models with Docker.
"""
"""


try:
    try:
    import torch
    import torch
except ImportError:
except ImportError:
    pass
    pass




    import logging
    import logging
    import os
    import os
    from dataclasses import dataclass, field
    from dataclasses import dataclass, field
    from typing import Any, Dict, List
    from typing import Any, Dict, List


    # Set up logging
    # Set up logging
    logging.basicConfig(
    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    )
    logger = logging.getLogger(__name__)
    logger = logging.getLogger(__name__)




    @dataclass
    @dataclass
    class DockerConfig:
    class DockerConfig:
    """
    """
    Configuration for Docker deployment.
    Configuration for Docker deployment.
    """
    """


    # Basic configuration
    # Basic configuration
    image_name: str
    image_name: str
    image_tag: str = "latest"
    image_tag: str = "latest"
    base_image: str = "python:3.9-slim"
    base_image: str = "python:3.9-slim"


    # Server configuration
    # Server configuration
    server_type: str = "rest"  # "rest" or "grpc"
    server_type: str = "rest"  # "rest" or "grpc"
    host: str = "0.0.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    port: int = 8000


    # Model configuration
    # Model configuration
    model_path: str = ""
    model_path: str = ""
    model_type: str = "text-generation"
    model_type: str = "text-generation"
    model_id: str = ""
    model_id: str = ""


    # Resource configuration
    # Resource configuration
    cpu_limit: str = "1"
    cpu_limit: str = "1"
    memory_limit: str = "4Gi"
    memory_limit: str = "4Gi"
    gpu_count: int = 0
    gpu_count: int = 0


    # Environment variables
    # Environment variables
    env_vars: Dict[str, str] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)


    # Volume configuration
    # Volume configuration
    volumes: List[Dict[str, str]] = field(default_factory=list)
    volumes: List[Dict[str, str]] = field(default_factory=list)


    # Additional configuration
    # Additional configuration
    additional_packages: List[str] = field(default_factory=list)
    additional_packages: List[str] = field(default_factory=list)
    additional_commands: List[str] = field(default_factory=list)
    additional_commands: List[str] = field(default_factory=list)


    def to_dict(self) -> Dict[str, Any]:
    def to_dict(self) -> Dict[str, Any]:
    """
    """
    Convert the configuration to a dictionary.
    Convert the configuration to a dictionary.


    Returns:
    Returns:
    Dictionary representation of the configuration
    Dictionary representation of the configuration
    """
    """
    return {
    return {
    "image_name": self.image_name,
    "image_name": self.image_name,
    "image_tag": self.image_tag,
    "image_tag": self.image_tag,
    "base_image": self.base_image,
    "base_image": self.base_image,
    "server_type": self.server_type,
    "server_type": self.server_type,
    "host": self.host,
    "host": self.host,
    "port": self.port,
    "port": self.port,
    "model_path": self.model_path,
    "model_path": self.model_path,
    "model_type": self.model_type,
    "model_type": self.model_type,
    "model_id": self.model_id,
    "model_id": self.model_id,
    "cpu_limit": self.cpu_limit,
    "cpu_limit": self.cpu_limit,
    "memory_limit": self.memory_limit,
    "memory_limit": self.memory_limit,
    "gpu_count": self.gpu_count,
    "gpu_count": self.gpu_count,
    "env_vars": self.env_vars,
    "env_vars": self.env_vars,
    "volumes": self.volumes,
    "volumes": self.volumes,
    "additional_packages": self.additional_packages,
    "additional_packages": self.additional_packages,
    "additional_commands": self.additional_commands,
    "additional_commands": self.additional_commands,
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "DockerConfig":
    def from_dict(cls, config_dict: Dict[str, Any]) -> "DockerConfig":
    """
    """
    Create a configuration from a dictionary.
    Create a configuration from a dictionary.


    Args:
    Args:
    config_dict: Dictionary with configuration parameters
    config_dict: Dictionary with configuration parameters


    Returns:
    Returns:
    Docker configuration
    Docker configuration
    """
    """
    return cls(**config_dict)
    return cls(**config_dict)




    def generate_docker_config(config: DockerConfig, output_dir: str) -> str:
    def generate_docker_config(config: DockerConfig, output_dir: str) -> str:
    """
    """
    Generate Docker configuration files.
    Generate Docker configuration files.


    Args:
    Args:
    config: Docker configuration
    config: Docker configuration
    output_dir: Directory to save the configuration files
    output_dir: Directory to save the configuration files


    Returns:
    Returns:
    Path to the generated Dockerfile
    Path to the generated Dockerfile
    """
    """
    # Create output directory
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    # Generate Dockerfile
    # Generate Dockerfile
    dockerfile_path = os.path.join(output_dir, "Dockerfile")
    dockerfile_path = os.path.join(output_dir, "Dockerfile")
    _generate_dockerfile(config, dockerfile_path)
    _generate_dockerfile(config, dockerfile_path)


    # Generate docker-compose.yml
    # Generate docker-compose.yml
    compose_path = os.path.join(output_dir, "docker-compose.yml")
    compose_path = os.path.join(output_dir, "docker-compose.yml")
    _generate_docker_compose(config, compose_path)
    _generate_docker_compose(config, compose_path)


    # Generate .dockerignore
    # Generate .dockerignore
    dockerignore_path = os.path.join(output_dir, ".dockerignore")
    dockerignore_path = os.path.join(output_dir, ".dockerignore")
    _generate_dockerignore(dockerignore_path)
    _generate_dockerignore(dockerignore_path)


    # Generate entrypoint.sh
    # Generate entrypoint.sh
    entrypoint_path = os.path.join(output_dir, "entrypoint.sh")
    entrypoint_path = os.path.join(output_dir, "entrypoint.sh")
    _generate_entrypoint(config, entrypoint_path)
    _generate_entrypoint(config, entrypoint_path)


    # Generate requirements.txt
    # Generate requirements.txt
    requirements_path = os.path.join(output_dir, "requirements.txt")
    requirements_path = os.path.join(output_dir, "requirements.txt")
    _generate_requirements(config, requirements_path)
    _generate_requirements(config, requirements_path)


    logger.info(f"Docker configuration files generated in {output_dir}")
    logger.info(f"Docker configuration files generated in {output_dir}")


    return dockerfile_path
    return dockerfile_path




    def _generate_dockerfile(config: DockerConfig, output_path: str) -> None:
    def _generate_dockerfile(config: DockerConfig, output_path: str) -> None:
    """
    """
    Generate a Dockerfile.
    Generate a Dockerfile.


    Args:
    Args:
    config: Docker configuration
    config: Docker configuration
    output_path: Path to save the Dockerfile
    output_path: Path to save the Dockerfile
    """
    """
    # Create Dockerfile content
    # Create Dockerfile content
    content = """
    content = """
    FROM {config.base_image}
    FROM {config.base_image}


    # Set working directory
    # Set working directory
    WORKDIR /app
    WORKDIR /app


    # Install system dependencies
    # Install system dependencies
    RUN apt-get update && apt-get install -y \\
    RUN apt-get update && apt-get install -y \\
    build-essential \\
    build-essential \\
    curl \\
    curl \\
    git \\
    git \\
    && rm -rf /var/lib/apt/lists/*
    && rm -rf /var/lib/apt/lists/*


    # Copy requirements
    # Copy requirements
    COPY requirements.txt .
    COPY requirements.txt .


    # Install Python dependencies
    # Install Python dependencies
    RUN pip install --no-cache-dir -r requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt


    # Copy application code
    # Copy application code
    COPY . .
    COPY . .


    # Set environment variables
    # Set environment variables
    ENV MODEL_PATH={config.model_path}
    ENV MODEL_PATH={config.model_path}
    ENV MODEL_TYPE={config.model_type}
    ENV MODEL_TYPE={config.model_type}
    ENV MODEL_ID={config.model_id}
    ENV MODEL_ID={config.model_id}
    ENV SERVER_TYPE={config.server_type}
    ENV SERVER_TYPE={config.server_type}
    ENV HOST={config.host}
    ENV HOST={config.host}
    ENV PORT={config.port}
    ENV PORT={config.port}
    """
    """


    # Add environment variables
    # Add environment variables
    for key, value in config.env_vars.items():
    for key, value in config.env_vars.items():
    content += f"ENV {key}={value}\n"
    content += f"ENV {key}={value}\n"


    # Add GPU support if needed
    # Add GPU support if needed
    if config.gpu_count > 0:
    if config.gpu_count > 0:
    content += """
    content += """
    # Install CUDA dependencies
    # Install CUDA dependencies
    ENV NVIDIA_VISIBLE_DEVICES=all
    ENV NVIDIA_VISIBLE_DEVICES=all
    ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
    ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
    """
    """


    # Add additional commands
    # Add additional commands
    if config.additional_commands:
    if config.additional_commands:
    content += "\n# Additional commands\n"
    content += "\n# Additional commands\n"
    for command in config.additional_commands:
    for command in config.additional_commands:
    content += f"RUN {command}\n"
    content += f"RUN {command}\n"


    # Add entrypoint
    # Add entrypoint
    content += """
    content += """
    # Make entrypoint executable
    # Make entrypoint executable
    COPY entrypoint.sh .
    COPY entrypoint.sh .
    RUN chmod +x entrypoint.sh
    RUN chmod +x entrypoint.sh


    # Expose port
    # Expose port
    EXPOSE ${PORT}
    EXPOSE ${PORT}


    # Set entrypoint
    # Set entrypoint
    ENTRYPOINT ["./entrypoint.sh"]
    ENTRYPOINT ["./entrypoint.sh"]
    """
    """


    # Write Dockerfile
    # Write Dockerfile
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())




    def _generate_docker_compose(config: DockerConfig, output_path: str) -> None:
    def _generate_docker_compose(config: DockerConfig, output_path: str) -> None:
    """
    """
    Generate a docker-compose.yml file.
    Generate a docker-compose.yml file.


    Args:
    Args:
    config: Docker configuration
    config: Docker configuration
    output_path: Path to save the docker-compose.yml file
    output_path: Path to save the docker-compose.yml file
    """
    """
    # Create docker-compose.yml content
    # Create docker-compose.yml content
    content = """
    content = """
    version: '3'
    version: '3'


    services:
    services:
    model-server:
    model-server:
    build:
    build:
    context: .
    context: .
    dockerfile: Dockerfile
    dockerfile: Dockerfile
    image: {config.image_name}:{config.image_tag}
    image: {config.image_name}:{config.image_tag}
    container_name: model-server
    container_name: model-server
    ports:
    ports:
    - "{config.port}:{config.port}"
    - "{config.port}:{config.port}"
    environment:
    environment:
    - MODEL_PATH={config.model_path}
    - MODEL_PATH={config.model_path}
    - MODEL_TYPE={config.model_type}
    - MODEL_TYPE={config.model_type}
    - MODEL_ID={config.model_id}
    - MODEL_ID={config.model_id}
    - SERVER_TYPE={config.server_type}
    - SERVER_TYPE={config.server_type}
    - HOST={config.host}
    - HOST={config.host}
    - PORT={config.port}
    - PORT={config.port}
    """
    """


    # Add environment variables
    # Add environment variables
    for key, value in config.env_vars.items():
    for key, value in config.env_vars.items():
    content += f"      - {key}={value}\n"
    content += f"      - {key}={value}\n"


    # Add volumes
    # Add volumes
    if config.volumes:
    if config.volumes:
    content += "    volumes:\n"
    content += "    volumes:\n"
    for volume in config.volumes:
    for volume in config.volumes:
    content += f"      - {volume['source']}:{volume['target']}\n"
    content += f"      - {volume['source']}:{volume['target']}\n"


    # Add resource limits
    # Add resource limits
    content += """
    content += """
    deploy:
    deploy:
    resources:
    resources:
    limits:
    limits:
    cpus: '{config.cpu_limit}'
    cpus: '{config.cpu_limit}'
    memory: {config.memory_limit}
    memory: {config.memory_limit}
    """
    """


    # Add GPU support if needed
    # Add GPU support if needed
    if config.gpu_count > 0:
    if config.gpu_count > 0:
    content += """
    content += """
    runtime: nvidia
    runtime: nvidia
    environment:
    environment:
    - NVIDIA_VISIBLE_DEVICES=all
    - NVIDIA_VISIBLE_DEVICES=all
    """
    """


    # Write docker-compose.yml
    # Write docker-compose.yml
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())




    def _generate_dockerignore(output_path: str) -> None:
    def _generate_dockerignore(output_path: str) -> None:
    """
    """
    Generate a .dockerignore file.
    Generate a .dockerignore file.


    Args:
    Args:
    output_path: Path to save the .dockerignore file
    output_path: Path to save the .dockerignore file
    """
    """
    # Create .dockerignore content
    # Create .dockerignore content
    content = """
    content = """
    # Git
    # Git
    .git
    .git
    .gitignore
    .gitignore


    # Python
    # Python
    __pycache__/
    __pycache__/
    *.py[cod]
    *.py[cod]
    *$py.class
    *$py.class
    *.so
    *.so
    .Python
    .Python
    env/
    env/
    build/
    build/
    develop-eggs/
    develop-eggs/
    dist/
    dist/
    downloads/
    downloads/
    eggs/
    eggs/
    .eggs/
    .eggs/
    lib/
    lib/
    lib64/
    lib64/
    parts/
    parts/
    sdist/
    sdist/
    var/
    var/
    *.egg-info/
    *.egg-info/
    .installed.cfg
    .installed.cfg
    *.egg
    *.egg


    # Virtual environment
    # Virtual environment
    venv/
    venv/
    ENV/
    ENV/


    # IDE
    # IDE
    .idea/
    .idea/
    .vscode/
    .vscode/
    *.swp
    *.swp
    *.swo
    *.swo


    # Docker
    # Docker
    Dockerfile
    Dockerfile
    docker-compose.yml
    docker-compose.yml
    .dockerignore
    .dockerignore


    # Logs
    # Logs
    logs/
    logs/
    *.log
    *.log


    # Data
    # Data
    data/
    data/
    models/
    models/
    """
    """


    # Write .dockerignore
    # Write .dockerignore
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())




    def _generate_entrypoint(config: DockerConfig, output_path: str) -> None:
    def _generate_entrypoint(config: DockerConfig, output_path: str) -> None:
    """
    """
    Generate an entrypoint.sh file.
    Generate an entrypoint.sh file.


    Args:
    Args:
    config: Docker configuration
    config: Docker configuration
    output_path: Path to save the entrypoint.sh file
    output_path: Path to save the entrypoint.sh file
    """
    """
    # Create entrypoint.sh content
    # Create entrypoint.sh content
    content = """#!/bin/bash
    content = """#!/bin/bash
    set -e
    set -e


    # Download model if needed
    # Download model if needed
    if [ ! -d "$MODEL_PATH" ]; then
    if [ ! -d "$MODEL_PATH" ]; then
    echo "Downloading model..."
    echo "Downloading model..."
    python -m ai_models.cli download --model-id $MODEL_ID --output-dir $MODEL_PATH
    python -m ai_models.cli download --model-id $MODEL_ID --output-dir $MODEL_PATH
    fi
    fi


    # Start server
    # Start server
    if [ "$SERVER_TYPE" = "rest" ]; then
    if [ "$SERVER_TYPE" = "rest" ]; then
    echo "Starting REST API server..."
    echo "Starting REST API server..."
    python -m ai_models.cli serve-rest --model-path $MODEL_PATH --model-type $MODEL_TYPE --host $HOST --port $PORT
    python -m ai_models.cli serve-rest --model-path $MODEL_PATH --model-type $MODEL_TYPE --host $HOST --port $PORT
    elif [ "$SERVER_TYPE" = "grpc" ]; then
    elif [ "$SERVER_TYPE" = "grpc" ]; then
    echo "Starting gRPC server..."
    echo "Starting gRPC server..."
    python -m ai_models.cli serve-grpc --model-path $MODEL_PATH --model-type $MODEL_TYPE --host $HOST --port $PORT
    python -m ai_models.cli serve-grpc --model-path $MODEL_PATH --model-type $MODEL_TYPE --host $HOST --port $PORT
    else
    else
    echo "Unknown server type: $SERVER_TYPE"
    echo "Unknown server type: $SERVER_TYPE"
    exit 1
    exit 1
    fi
    fi
    """
    """


    # Write entrypoint.sh
    # Write entrypoint.sh
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())




    def _generate_requirements(config: DockerConfig, output_path: str) -> None:
    def _generate_requirements(config: DockerConfig, output_path: str) -> None:
    """
    """
    Generate a requirements.txt file.
    Generate a requirements.txt file.


    Args:
    Args:
    config: Docker configuration
    config: Docker configuration
    output_path: Path to save the requirements.txt file
    output_path: Path to save the requirements.txt file
    """
    """
    # Create requirements.txt content
    # Create requirements.txt content
    content = """
    content = """
    # Core dependencies
    # Core dependencies
    torch>=1.10.0
    torch>=1.10.0
    transformers>=4.20.0
    transformers>=4.20.0
    sentence-transformers>=2.2.0
    sentence-transformers>=2.2.0


    # Server dependencies
    # Server dependencies
    fastapi>=0.95.0
    fastapi>=0.95.0
    uvicorn>=0.22.0
    uvicorn>=0.22.0
    grpcio>=1.54.0
    grpcio>=1.54.0
    grpcio-reflection>=1.54.0
    grpcio-reflection>=1.54.0
    grpcio-health-checking>=1.54.0
    grpcio-health-checking>=1.54.0
    protobuf>=4.22.3
    protobuf>=4.22.3


    # Utility dependencies
    # Utility dependencies
    numpy>=1.24.3
    numpy>=1.24.3
    tqdm>=4.65.0
    tqdm>=4.65.0
    psutil>=5.9.5
    psutil>=5.9.5
    """
    """


    # Add additional packages
    # Add additional packages
    if config.additional_packages:
    if config.additional_packages:
    content += "\n# Additional packages\n"
    content += "\n# Additional packages\n"
    for package in config.additional_packages:
    for package in config.additional_packages:
    content += f"{package}\n"
    content += f"{package}\n"


    # Write requirements.txt
    # Write requirements.txt
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())