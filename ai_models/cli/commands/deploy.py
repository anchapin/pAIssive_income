"""
Deploy command for the command-line interface.

This module provides a command for deploying models.
"""

import argparse
import json
import logging
import os
from typing import Any, Dict

import boto3

from ...serving.deployment import (DockerConfig, KubernetesConfig,
generate_docker_config,
generate_kubernetes_config)
from ..base import BaseCommand

# Set up logging
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeployCommand(BaseCommand):
    """
    Command for deploying models.
    """

    description = "Deploy a model"

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    Add command-specific arguments to the parser.

    Args:
    parser: Argument parser
    """
    parser.add_argument(
    "--model-path", type=str, required=True, help="Path to the model"
    )
    parser.add_argument(
    "--model-type",
    type=str,
    default="text-generation",
    choices=[
    "text-generation",
    "text-classification",
    "embedding",
    "image",
    "audio",
    ],
    help="Type of the model",
    )
    parser.add_argument(
    "--deployment-type",
    type=str,
    default="docker",
    choices=["docker", "kubernetes", "aws", "gcp", "azure"],
    help="Type of deployment",
    )
    parser.add_argument(
    "--output-dir",
    type=str,
    default="deployment",
    help="Directory to save deployment files",
    )
    parser.add_argument("--name", type=str, help="Name of the deployment")
    parser.add_argument(
    "--server-type",
    type=str,
    default="rest",
    choices=["rest", "grpc"],
    help="Type of server to deploy",
    )
    parser.add_argument("--port", type=int, default=8000, help="Port to expose")
    parser.add_argument(
    "--cpu-limit", type=str, default="1", help="CPU limit for the deployment"
    )
    parser.add_argument(
    "--memory-limit",
    type=str,
    default="4Gi",
    help="Memory limit for the deployment",
    )
    parser.add_argument(
    "--gpu-count", type=int, default=0, help="Number of GPUs to use"
    )
    parser.add_argument(
    "--replicas",
    type=int,
    default=1,
    help="Number of replicas for Kubernetes deployment",
    )
    parser.add_argument(
    "--region",
    type=str,
    default="us-west-2",
    help="Region for cloud deployment",
    )
    parser.add_argument(
    "--instance-type", type=str, help="Instance type for cloud deployment"
    )
    parser.add_argument(
    "--enable-auth", action="store_true", help="Enable authentication"
    )
    parser.add_argument("--enable-https", action="store_true", help="Enable HTTPS")
    parser.add_argument(
    "--config-file", type=str, help="Path to configuration file"
    )

    def run(self) -> int:
    """
    Run the command.

    Returns:
    Exit code
    """
    # Validate arguments
    if not self._validate_args(["model_path"]):
    return 1

    try:
    # Create output directory if it doesn't exist
    os.makedirs(self.args.output_dir, exist_ok=True)

    # Load configuration from file if provided
    config_dict = {}
    if self.args.config_file and os.path.exists(self.args.config_file):
    with open(self.args.config_file, "r", encoding="utf-8") as f:
    config_dict = json.load(f)

    # Generate deployment configuration based on type
    if self.args.deployment_type == "docker":
    return self._generate_docker_config(config_dict)
    elif self.args.deployment_type == "kubernetes":
    return self._generate_kubernetes_config(config_dict)
    elif self.args.deployment_type in ["aws", "gcp", "azure"]:
    return self._generate_cloud_config(config_dict)
    else:
    logger.error(
    f"Unsupported deployment type: {self.args.deployment_type}"
    )
    return 1

except Exception as e:
    logger.error(
    f"Error generating deployment configuration: {e}", exc_info=True
    )
    return 1

    def _generate_docker_config(self, config_dict: Dict[str, Any]) -> int:
    """
    Generate Docker deployment configuration.

    Args:
    config_dict: Configuration dictionary

    Returns:
    Exit code
    """
    # Import required modules
    # Get deployment name
    name = self.args.name or os.path.basename(self.args.model_path)

    # Create configuration
    config = DockerConfig(
    image_name=name,
    image_tag="latest",
    server_type=self.args.server_type,
    port=self.args.port,
    model_path=self.args.model_path,
    model_type=self.args.model_type,
    model_id=name,
    cpu_limit=self.args.cpu_limit,
    memory_limit=self.args.memory_limit,
    gpu_count=self.args.gpu_count,
    )

    # Update with configuration from file
    for key, value in config_dict.items():
    if hasattr(config, key):
    setattr(config, key, value)

    # Generate Docker configuration
    output_dir = os.path.join(self.args.output_dir, "docker")
    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"Generating Docker configuration in {output_dir}")
    dockerfile_path = generate_docker_config(config, output_dir)

    logger.info(f"Docker configuration generated at {dockerfile_path}")
    logger.info("\nTo build and run the Docker image:")
    logger.info(f"cd {output_dir}")
    logger.info(f"docker build -t {name}:latest .")
    logger.info(f"docker run -p {self.args.port}:{self.args.port} {name}:latest")

    return 0

    def _generate_kubernetes_config(self, config_dict: Dict[str, Any]) -> int:
    """
    Generate Kubernetes deployment configuration.

    Args:
    config_dict: Configuration dictionary

    Returns:
    Exit code
    """
    # Import required modules
    # Get deployment name
    name = self.args.name or os.path.basename(self.args.model_path)

    # Create configuration
    config = KubernetesConfig(
    name=name,
    namespace="default",
    image=f"{name}:latest",
    server_type=self.args.server_type,
    port=self.args.port,
    replicas=self.args.replicas,
    cpu_request="500m",
    cpu_limit=self.args.cpu_limit,
    memory_request="1Gi",
    memory_limit=self.args.memory_limit,
    gpu_request=self.args.gpu_count,
    gpu_limit=self.args.gpu_count,
    env_vars={
    "MODEL_PATH": self.args.model_path,
    "MODEL_TYPE": self.args.model_type,
    "SERVER_TYPE": self.args.server_type,
    "PORT": str(self.args.port),
    },
    service_type="ClusterIP",
    enable_ingress=True,
    ingress_host=f"{name}.example.com",
    enable_hpa=True,
    min_replicas=1,
    max_replicas=self.args.replicas * 2,
    )

    # Update with configuration from file
    for key, value in config_dict.items():
    if hasattr(config, key):
    setattr(config, key, value)

    # Generate Kubernetes configuration
    output_dir = os.path.join(self.args.output_dir, "kubernetes")
    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"Generating Kubernetes configuration in {output_dir}")
    deployment_path = generate_kubernetes_config(config, output_dir)

    logger.info(f"Kubernetes configuration generated at {deployment_path}")
    logger.info("\nTo deploy to Kubernetes:")
    logger.info(f"cd {output_dir}")
    logger.info("kubectl apply -k .")

    return 0

    def _generate_cloud_config(self, config_dict: Dict[str, Any]) -> int:
    """
    Generate cloud deployment configuration.

    Args:
    config_dict: Configuration dictionary

    Returns:
    Exit code
    """
    # Import required modules
    from ...serving.deployment import (CloudConfig, CloudProvider,
    generate_cloud_config)

    # Get deployment name
    name = self.args.name or os.path.basename(self.args.model_path)

    # Convert provider string to enum
    provider_map = {
    "aws": CloudProvider.AWS,
    "gcp": CloudProvider.GCP,
    "azure": CloudProvider.AZURE,
    }
    provider = provider_map.get(self.args.deployment_type, CloudProvider.AWS)

    # Create configuration
    config = CloudConfig(
    provider=provider,
    name=name,
    region=self.args.region,
    server_type=self.args.server_type,
    port=self.args.port,
    model_path=self.args.model_path,
    model_type=self.args.model_type,
    model_id=name,
    instance_type=(
    self.args.instance_type or "ml.m5.large"
    if provider == CloudProvider.AWS
    else "n1-standard-2"
    ),
    cpu_count=(
    int(self.args.cpu_limit.replace("m", "")) // 1000
    if "m" in self.args.cpu_limit
    else int(self.args.cpu_limit)
    ),
    memory_gb=(
    int(self.args.memory_limit.replace("Gi", ""))
    if "Gi" in self.args.memory_limit
    else int(self.args.memory_limit)
    ),
    gpu_count=self.args.gpu_count,
    min_instances=1,
    max_instances=self.args.replicas,
    auth_enabled=self.args.enable_auth,
    )

    # Update with configuration from file
    for key, value in config_dict.items():
    if hasattr(config, key):
    setattr(config, key, value)

    # Generate cloud configuration
    output_dir = os.path.join(self.args.output_dir, self.args.deployment_type)
    os.makedirs(output_dir, exist_ok=True)

    logger.info(
    f"Generating {self.args.deployment_type.upper()} configuration in {output_dir}"
    )
    config_path = generate_cloud_config(config, output_dir)

    logger.info(
    f"{self.args.deployment_type.upper()} configuration generated at {config_path}"
    )
    logger.info("\nTo deploy to the cloud:")
    logger.info(f"cd {output_dir}")
    logger.info("./deploy.sh")

    return 0