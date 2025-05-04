"""
"""
Deploy command for the command-line interface.
Deploy command for the command-line interface.


This module provides a command for deploying models.
This module provides a command for deploying models.
"""
"""


import argparse
import argparse
import json
import json
import logging
import logging
import os
import os
from typing import Any, Dict
from typing import Any, Dict


import boto3
import boto3


from ...serving.deployment import (DockerConfig, KubernetesConfig,
from ...serving.deployment import (DockerConfig, KubernetesConfig,
generate_docker_config,
generate_docker_config,
generate_kubernetes_config)
generate_kubernetes_config)
from ..base import BaseCommand
from ..base import BaseCommand


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




class DeployCommand(BaseCommand):
    class DeployCommand(BaseCommand):
    """
    """
    Command for deploying models.
    Command for deploying models.
    """
    """


    description = "Deploy a model"
    description = "Deploy a model"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.


    Args:
    Args:
    parser: Argument parser
    parser: Argument parser
    """
    """
    parser.add_argument(
    parser.add_argument(
    "--model-path", type=str, required=True, help="Path to the model"
    "--model-path", type=str, required=True, help="Path to the model"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--model-type",
    "--model-type",
    type=str,
    type=str,
    default="text-generation",
    default="text-generation",
    choices=[
    choices=[
    "text-generation",
    "text-generation",
    "text-classification",
    "text-classification",
    "embedding",
    "embedding",
    "image",
    "image",
    "audio",
    "audio",
    ],
    ],
    help="Type of the model",
    help="Type of the model",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--deployment-type",
    "--deployment-type",
    type=str,
    type=str,
    default="docker",
    default="docker",
    choices=["docker", "kubernetes", "aws", "gcp", "azure"],
    choices=["docker", "kubernetes", "aws", "gcp", "azure"],
    help="Type of deployment",
    help="Type of deployment",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--output-dir",
    "--output-dir",
    type=str,
    type=str,
    default="deployment",
    default="deployment",
    help="Directory to save deployment files",
    help="Directory to save deployment files",
    )
    )
    parser.add_argument("--name", type=str, help="Name of the deployment")
    parser.add_argument("--name", type=str, help="Name of the deployment")
    parser.add_argument(
    parser.add_argument(
    "--server-type",
    "--server-type",
    type=str,
    type=str,
    default="rest",
    default="rest",
    choices=["rest", "grpc"],
    choices=["rest", "grpc"],
    help="Type of server to deploy",
    help="Type of server to deploy",
    )
    )
    parser.add_argument("--port", type=int, default=8000, help="Port to expose")
    parser.add_argument("--port", type=int, default=8000, help="Port to expose")
    parser.add_argument(
    parser.add_argument(
    "--cpu-limit", type=str, default="1", help="CPU limit for the deployment"
    "--cpu-limit", type=str, default="1", help="CPU limit for the deployment"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--memory-limit",
    "--memory-limit",
    type=str,
    type=str,
    default="4Gi",
    default="4Gi",
    help="Memory limit for the deployment",
    help="Memory limit for the deployment",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--gpu-count", type=int, default=0, help="Number of GPUs to use"
    "--gpu-count", type=int, default=0, help="Number of GPUs to use"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--replicas",
    "--replicas",
    type=int,
    type=int,
    default=1,
    default=1,
    help="Number of replicas for Kubernetes deployment",
    help="Number of replicas for Kubernetes deployment",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--region",
    "--region",
    type=str,
    type=str,
    default="us-west-2",
    default="us-west-2",
    help="Region for cloud deployment",
    help="Region for cloud deployment",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--instance-type", type=str, help="Instance type for cloud deployment"
    "--instance-type", type=str, help="Instance type for cloud deployment"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--enable-auth", action="store_true", help="Enable authentication"
    "--enable-auth", action="store_true", help="Enable authentication"
    )
    )
    parser.add_argument("--enable-https", action="store_true", help="Enable HTTPS")
    parser.add_argument("--enable-https", action="store_true", help="Enable HTTPS")
    parser.add_argument(
    parser.add_argument(
    "--config-file", type=str, help="Path to configuration file"
    "--config-file", type=str, help="Path to configuration file"
    )
    )


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.


    Returns:
    Returns:
    Exit code
    Exit code
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_path"]):
    if not self._validate_args(["model_path"]):
    return 1
    return 1


    try:
    try:
    # Create output directory if it doesn't exist
    # Create output directory if it doesn't exist
    os.makedirs(self.args.output_dir, exist_ok=True)
    os.makedirs(self.args.output_dir, exist_ok=True)


    # Load configuration from file if provided
    # Load configuration from file if provided
    config_dict = {}
    config_dict = {}
    if self.args.config_file and os.path.exists(self.args.config_file):
    if self.args.config_file and os.path.exists(self.args.config_file):
    with open(self.args.config_file, "r", encoding="utf-8") as f:
    with open(self.args.config_file, "r", encoding="utf-8") as f:
    config_dict = json.load(f)
    config_dict = json.load(f)


    # Generate deployment configuration based on type
    # Generate deployment configuration based on type
    if self.args.deployment_type == "docker":
    if self.args.deployment_type == "docker":
    return self._generate_docker_config(config_dict)
    return self._generate_docker_config(config_dict)
    elif self.args.deployment_type == "kubernetes":
    elif self.args.deployment_type == "kubernetes":
    return self._generate_kubernetes_config(config_dict)
    return self._generate_kubernetes_config(config_dict)
    elif self.args.deployment_type in ["aws", "gcp", "azure"]:
    elif self.args.deployment_type in ["aws", "gcp", "azure"]:
    return self._generate_cloud_config(config_dict)
    return self._generate_cloud_config(config_dict)
    else:
    else:
    logger.error(
    logger.error(
    f"Unsupported deployment type: {self.args.deployment_type}"
    f"Unsupported deployment type: {self.args.deployment_type}"
    )
    )
    return 1
    return 1


except Exception as e:
except Exception as e:
    logger.error(
    logger.error(
    f"Error generating deployment configuration: {e}", exc_info=True
    f"Error generating deployment configuration: {e}", exc_info=True
    )
    )
    return 1
    return 1


    def _generate_docker_config(self, config_dict: Dict[str, Any]) -> int:
    def _generate_docker_config(self, config_dict: Dict[str, Any]) -> int:
    """
    """
    Generate Docker deployment configuration.
    Generate Docker deployment configuration.


    Args:
    Args:
    config_dict: Configuration dictionary
    config_dict: Configuration dictionary


    Returns:
    Returns:
    Exit code
    Exit code
    """
    """
    # Import required modules
    # Import required modules
    # Get deployment name
    # Get deployment name
    name = self.args.name or os.path.basename(self.args.model_path)
    name = self.args.name or os.path.basename(self.args.model_path)


    # Create configuration
    # Create configuration
    config = DockerConfig(
    config = DockerConfig(
    image_name=name,
    image_name=name,
    image_tag="latest",
    image_tag="latest",
    server_type=self.args.server_type,
    server_type=self.args.server_type,
    port=self.args.port,
    port=self.args.port,
    model_path=self.args.model_path,
    model_path=self.args.model_path,
    model_type=self.args.model_type,
    model_type=self.args.model_type,
    model_id=name,
    model_id=name,
    cpu_limit=self.args.cpu_limit,
    cpu_limit=self.args.cpu_limit,
    memory_limit=self.args.memory_limit,
    memory_limit=self.args.memory_limit,
    gpu_count=self.args.gpu_count,
    gpu_count=self.args.gpu_count,
    )
    )


    # Update with configuration from file
    # Update with configuration from file
    for key, value in config_dict.items():
    for key, value in config_dict.items():
    if hasattr(config, key):
    if hasattr(config, key):
    setattr(config, key, value)
    setattr(config, key, value)


    # Generate Docker configuration
    # Generate Docker configuration
    output_dir = os.path.join(self.args.output_dir, "docker")
    output_dir = os.path.join(self.args.output_dir, "docker")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    logger.info(f"Generating Docker configuration in {output_dir}")
    logger.info(f"Generating Docker configuration in {output_dir}")
    dockerfile_path = generate_docker_config(config, output_dir)
    dockerfile_path = generate_docker_config(config, output_dir)


    logger.info(f"Docker configuration generated at {dockerfile_path}")
    logger.info(f"Docker configuration generated at {dockerfile_path}")
    logger.info("\nTo build and run the Docker image:")
    logger.info("\nTo build and run the Docker image:")
    logger.info(f"cd {output_dir}")
    logger.info(f"cd {output_dir}")
    logger.info(f"docker build -t {name}:latest .")
    logger.info(f"docker build -t {name}:latest .")
    logger.info(f"docker run -p {self.args.port}:{self.args.port} {name}:latest")
    logger.info(f"docker run -p {self.args.port}:{self.args.port} {name}:latest")


    return 0
    return 0


    def _generate_kubernetes_config(self, config_dict: Dict[str, Any]) -> int:
    def _generate_kubernetes_config(self, config_dict: Dict[str, Any]) -> int:
    """
    """
    Generate Kubernetes deployment configuration.
    Generate Kubernetes deployment configuration.


    Args:
    Args:
    config_dict: Configuration dictionary
    config_dict: Configuration dictionary


    Returns:
    Returns:
    Exit code
    Exit code
    """
    """
    # Import required modules
    # Import required modules
    # Get deployment name
    # Get deployment name
    name = self.args.name or os.path.basename(self.args.model_path)
    name = self.args.name or os.path.basename(self.args.model_path)


    # Create configuration
    # Create configuration
    config = KubernetesConfig(
    config = KubernetesConfig(
    name=name,
    name=name,
    namespace="default",
    namespace="default",
    image=f"{name}:latest",
    image=f"{name}:latest",
    server_type=self.args.server_type,
    server_type=self.args.server_type,
    port=self.args.port,
    port=self.args.port,
    replicas=self.args.replicas,
    replicas=self.args.replicas,
    cpu_request="500m",
    cpu_request="500m",
    cpu_limit=self.args.cpu_limit,
    cpu_limit=self.args.cpu_limit,
    memory_request="1Gi",
    memory_request="1Gi",
    memory_limit=self.args.memory_limit,
    memory_limit=self.args.memory_limit,
    gpu_request=self.args.gpu_count,
    gpu_request=self.args.gpu_count,
    gpu_limit=self.args.gpu_count,
    gpu_limit=self.args.gpu_count,
    env_vars={
    env_vars={
    "MODEL_PATH": self.args.model_path,
    "MODEL_PATH": self.args.model_path,
    "MODEL_TYPE": self.args.model_type,
    "MODEL_TYPE": self.args.model_type,
    "SERVER_TYPE": self.args.server_type,
    "SERVER_TYPE": self.args.server_type,
    "PORT": str(self.args.port),
    "PORT": str(self.args.port),
    },
    },
    service_type="ClusterIP",
    service_type="ClusterIP",
    enable_ingress=True,
    enable_ingress=True,
    ingress_host=f"{name}.example.com",
    ingress_host=f"{name}.example.com",
    enable_hpa=True,
    enable_hpa=True,
    min_replicas=1,
    min_replicas=1,
    max_replicas=self.args.replicas * 2,
    max_replicas=self.args.replicas * 2,
    )
    )


    # Update with configuration from file
    # Update with configuration from file
    for key, value in config_dict.items():
    for key, value in config_dict.items():
    if hasattr(config, key):
    if hasattr(config, key):
    setattr(config, key, value)
    setattr(config, key, value)


    # Generate Kubernetes configuration
    # Generate Kubernetes configuration
    output_dir = os.path.join(self.args.output_dir, "kubernetes")
    output_dir = os.path.join(self.args.output_dir, "kubernetes")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    logger.info(f"Generating Kubernetes configuration in {output_dir}")
    logger.info(f"Generating Kubernetes configuration in {output_dir}")
    deployment_path = generate_kubernetes_config(config, output_dir)
    deployment_path = generate_kubernetes_config(config, output_dir)


    logger.info(f"Kubernetes configuration generated at {deployment_path}")
    logger.info(f"Kubernetes configuration generated at {deployment_path}")
    logger.info("\nTo deploy to Kubernetes:")
    logger.info("\nTo deploy to Kubernetes:")
    logger.info(f"cd {output_dir}")
    logger.info(f"cd {output_dir}")
    logger.info("kubectl apply -k .")
    logger.info("kubectl apply -k .")


    return 0
    return 0


    def _generate_cloud_config(self, config_dict: Dict[str, Any]) -> int:
    def _generate_cloud_config(self, config_dict: Dict[str, Any]) -> int:
    """
    """
    Generate cloud deployment configuration.
    Generate cloud deployment configuration.


    Args:
    Args:
    config_dict: Configuration dictionary
    config_dict: Configuration dictionary


    Returns:
    Returns:
    Exit code
    Exit code
    """
    """
    # Import required modules
    # Import required modules
    from ...serving.deployment import (CloudConfig, CloudProvider,
    from ...serving.deployment import (CloudConfig, CloudProvider,
    generate_cloud_config)
    generate_cloud_config)


    # Get deployment name
    # Get deployment name
    name = self.args.name or os.path.basename(self.args.model_path)
    name = self.args.name or os.path.basename(self.args.model_path)


    # Convert provider string to enum
    # Convert provider string to enum
    provider_map = {
    provider_map = {
    "aws": CloudProvider.AWS,
    "aws": CloudProvider.AWS,
    "gcp": CloudProvider.GCP,
    "gcp": CloudProvider.GCP,
    "azure": CloudProvider.AZURE,
    "azure": CloudProvider.AZURE,
    }
    }
    provider = provider_map.get(self.args.deployment_type, CloudProvider.AWS)
    provider = provider_map.get(self.args.deployment_type, CloudProvider.AWS)


    # Create configuration
    # Create configuration
    config = CloudConfig(
    config = CloudConfig(
    provider=provider,
    provider=provider,
    name=name,
    name=name,
    region=self.args.region,
    region=self.args.region,
    server_type=self.args.server_type,
    server_type=self.args.server_type,
    port=self.args.port,
    port=self.args.port,
    model_path=self.args.model_path,
    model_path=self.args.model_path,
    model_type=self.args.model_type,
    model_type=self.args.model_type,
    model_id=name,
    model_id=name,
    instance_type=(
    instance_type=(
    self.args.instance_type or "ml.m5.large"
    self.args.instance_type or "ml.m5.large"
    if provider == CloudProvider.AWS
    if provider == CloudProvider.AWS
    else "n1-standard-2"
    else "n1-standard-2"
    ),
    ),
    cpu_count=(
    cpu_count=(
    int(self.args.cpu_limit.replace("m", "")) // 1000
    int(self.args.cpu_limit.replace("m", "")) // 1000
    if "m" in self.args.cpu_limit
    if "m" in self.args.cpu_limit
    else int(self.args.cpu_limit)
    else int(self.args.cpu_limit)
    ),
    ),
    memory_gb=(
    memory_gb=(
    int(self.args.memory_limit.replace("Gi", ""))
    int(self.args.memory_limit.replace("Gi", ""))
    if "Gi" in self.args.memory_limit
    if "Gi" in self.args.memory_limit
    else int(self.args.memory_limit)
    else int(self.args.memory_limit)
    ),
    ),
    gpu_count=self.args.gpu_count,
    gpu_count=self.args.gpu_count,
    min_instances=1,
    min_instances=1,
    max_instances=self.args.replicas,
    max_instances=self.args.replicas,
    auth_enabled=self.args.enable_auth,
    auth_enabled=self.args.enable_auth,
    )
    )


    # Update with configuration from file
    # Update with configuration from file
    for key, value in config_dict.items():
    for key, value in config_dict.items():
    if hasattr(config, key):
    if hasattr(config, key):
    setattr(config, key, value)
    setattr(config, key, value)


    # Generate cloud configuration
    # Generate cloud configuration
    output_dir = os.path.join(self.args.output_dir, self.args.deployment_type)
    output_dir = os.path.join(self.args.output_dir, self.args.deployment_type)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    logger.info(
    logger.info(
    f"Generating {self.args.deployment_type.upper()} configuration in {output_dir}"
    f"Generating {self.args.deployment_type.upper()} configuration in {output_dir}"
    )
    )
    config_path = generate_cloud_config(config, output_dir)
    config_path = generate_cloud_config(config, output_dir)


    logger.info(
    logger.info(
    f"{self.args.deployment_type.upper()} configuration generated at {config_path}"
    f"{self.args.deployment_type.upper()} configuration generated at {config_path}"
    )
    )
    logger.info("\nTo deploy to the cloud:")
    logger.info("\nTo deploy to the cloud:")
    logger.info(f"cd {output_dir}")
    logger.info(f"cd {output_dir}")
    logger.info("./deploy.sh")
    logger.info("./deploy.sh")


    return 0
    return 0