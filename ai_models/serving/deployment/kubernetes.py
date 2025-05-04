"""
Kubernetes deployment utilities for AI models.

This module provides utilities for deploying AI models with Kubernetes.
"""


import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Set up logging
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class KubernetesConfig:
    """
    Configuration for Kubernetes deployment.
    """

    # Basic configuration
    name: str
    namespace: str = "default"
    image: str = ""

    # Server configuration
    server_type: str = "rest"  # "rest" or "grpc"
    port: int = 8000

    # Deployment configuration
    replicas: int = 1
    strategy: str = "RollingUpdate"  # "RollingUpdate" or "Recreate"

    # Resource configuration
    cpu_request: str = "500m"
    cpu_limit: str = "1"
    memory_request: str = "1Gi"
    memory_limit: str = "4Gi"
    gpu_request: int = 0
    gpu_limit: int = 0

    # Environment variables
    env_vars: Dict[str, str] = field(default_factory=dict)

    # Volume configuration
    volumes: List[Dict[str, str]] = field(default_factory=list)

    # Service configuration
    service_type: str = "ClusterIP"  # "ClusterIP", "NodePort", or "LoadBalancer"
    node_port: Optional[int] = None

    # Ingress configuration
    enable_ingress: bool = False
    ingress_host: str = ""
    ingress_path: str = "/"
    ingress_tls: bool = False
    ingress_tls_secret: str = ""

    # Horizontal Pod Autoscaler configuration
    enable_hpa: bool = False
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_utilization: int = 80

    def to_dict(self) -> Dict[str, Any]:
    """
    Convert the configuration to a dictionary.

    Returns:
    Dictionary representation of the configuration
    """
    return {
    "name": self.name,
    "namespace": self.namespace,
    "image": self.image,
    "server_type": self.server_type,
    "port": self.port,
    "replicas": self.replicas,
    "strategy": self.strategy,
    "cpu_request": self.cpu_request,
    "cpu_limit": self.cpu_limit,
    "memory_request": self.memory_request,
    "memory_limit": self.memory_limit,
    "gpu_request": self.gpu_request,
    "gpu_limit": self.gpu_limit,
    "env_vars": self.env_vars,
    "volumes": self.volumes,
    "service_type": self.service_type,
    "node_port": self.node_port,
    "enable_ingress": self.enable_ingress,
    "ingress_host": self.ingress_host,
    "ingress_path": self.ingress_path,
    "ingress_tls": self.ingress_tls,
    "ingress_tls_secret": self.ingress_tls_secret,
    "enable_hpa": self.enable_hpa,
    "min_replicas": self.min_replicas,
    "max_replicas": self.max_replicas,
    "target_cpu_utilization": self.target_cpu_utilization,
    }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "KubernetesConfig":
    """
    Create a configuration from a dictionary.

    Args:
    config_dict: Dictionary with configuration parameters

    Returns:
    Kubernetes configuration
    """
    return cls(**config_dict)


    def generate_kubernetes_config(config: KubernetesConfig, output_dir: str) -> str:
    """
    Generate Kubernetes configuration files.

    Args:
    config: Kubernetes configuration
    output_dir: Directory to save the configuration files

    Returns:
    Path to the generated deployment.yaml file
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Generate deployment.yaml
    deployment_path = os.path.join(output_dir, "deployment.yaml")
    _generate_deployment(config, deployment_path)

    # Generate service.yaml
    service_path = os.path.join(output_dir, "service.yaml")
    _generate_service(config, service_path)

    # Generate ingress.yaml if enabled
    if config.enable_ingress:
    ingress_path = os.path.join(output_dir, "ingress.yaml")
    _generate_ingress(config, ingress_path)

    # Generate hpa.yaml if enabled
    if config.enable_hpa:
    hpa_path = os.path.join(output_dir, "hpa.yaml")
    _generate_hpa(config, hpa_path)

    # Generate kustomization.yaml
    kustomization_path = os.path.join(output_dir, "kustomization.yaml")
    _generate_kustomization(config, kustomization_path)

    logger.info(f"Kubernetes configuration files generated in {output_dir}")

    return deployment_path


    def _generate_deployment(config: KubernetesConfig, output_path: str) -> None:
    """
    Generate a Kubernetes deployment configuration.

    Args:
    config: Kubernetes configuration
    output_path: Path to save the deployment.yaml file
    """
    # Create deployment.yaml content
    content = """
    apiVersion: apps/v1
    kind: Deployment
    metadata:
    name: {config.name}
    namespace: {config.namespace}
    labels:
    app: {config.name}
    spec:
    replicas: {config.replicas}
    selector:
    matchLabels:
    app: {config.name}
    strategy:
    type: {config.strategy}
    template:
    metadata:
    labels:
    app: {config.name}
    spec:
    containers:
    - name: {config.name}
    image: {config.image}
    ports:
    - containerPort: {config.port}
    resources:
    requests:
    cpu: {config.cpu_request}
    memory: {config.memory_request}
    limits:
    cpu: {config.cpu_limit}
    memory: {config.memory_limit}
    """

    # Add GPU resources if needed
    if config.gpu_request > 0 or config.gpu_limit > 0:
    content += "          requests:\n"
    if config.gpu_request > 0:
    content += f"            nvidia.com/gpu: {config.gpu_request}\n"
    content += "          limits:\n"
    if config.gpu_limit > 0:
    content += f"            nvidia.com/gpu: {config.gpu_limit}\n"

    # Add environment variables
    if config.env_vars:
    content += "        env:\n"
    for key, value in config.env_vars.items():
    content += """        - name: {key}
    value: "{value}"
    """

    # Add volumes
    if config.volumes:
    content += "        volumeMounts:\n"
    for i, volume in enumerate(config.volumes):
    content += """        - name: volume-{i}
    mountPath: {volume['target']}
    """

    content += "      volumes:\n"
    for i, volume in enumerate(config.volumes):
    volume_type = volume.get("type", "hostPath")

    if volume_type == "hostPath":
    content += """      - name: volume-{i}
    hostPath:
    path: {volume['source']}
    """
    elif volume_type == "persistentVolumeClaim":
    content += """      - name: volume-{i}
    persistentVolumeClaim:
    claimName: {volume['source']}
    """

    # Write deployment.yaml
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())


    def _generate_service(config: KubernetesConfig, output_path: str) -> None:
    """
    Generate a Kubernetes service configuration.

    Args:
    config: Kubernetes configuration
    output_path: Path to save the service.yaml file
    """
    # Create service.yaml content
    content = """
    apiVersion: v1
    kind: Service
    metadata:
    name: {config.name}
    namespace: {config.namespace}
    labels:
    app: {config.name}
    spec:
    type: {config.service_type}
    selector:
    app: {config.name}
    ports:
    - port: {config.port}
    targetPort: {config.port}
    protocol: TCP
    name: {config.server_type}
    """

    # Add node port if specified
    if config.service_type == "NodePort" and config.node_port:
    content += f"    nodePort: {config.node_port}\n"

    # Write service.yaml
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())


    def _generate_ingress(config: KubernetesConfig, output_path: str) -> None:
    """
    Generate a Kubernetes ingress configuration.

    Args:
    config: Kubernetes configuration
    output_path: Path to save the ingress.yaml file
    """
    # Create ingress.yaml content
    content = """
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
    name: {config.name}
    namespace: {config.namespace}
    labels:
    app: {config.name}
    annotations:
    kubernetes.io/ingress.class: nginx
    """

    # Add TLS if enabled
    if config.ingress_tls:
    content += """spec:
    tls:
    - hosts:
    - {config.ingress_host}
    secretName: {config.ingress_tls_secret}
    rules:
    - host: {config.ingress_host}
    http:
    paths:
    - path: {config.ingress_path}
    pathType: Prefix
    backend:
    service:
    name: {config.name}
    port:
    number: {config.port}
    """
    else:
    content += """spec:
    rules:
    - host: {config.ingress_host}
    http:
    paths:
    - path: {config.ingress_path}
    pathType: Prefix
    backend:
    service:
    name: {config.name}
    port:
    number: {config.port}
    """

    # Write ingress.yaml
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())


    def _generate_hpa(config: KubernetesConfig, output_path: str) -> None:
    """
    Generate a Kubernetes Horizontal Pod Autoscaler configuration.

    Args:
    config: Kubernetes configuration
    output_path: Path to save the hpa.yaml file
    """
    # Create hpa.yaml content
    content = """
    apiVersion: autoscaling/v2
    kind: HorizontalPodAutoscaler
    metadata:
    name: {config.name}
    namespace: {config.namespace}
    labels:
    app: {config.name}
    spec:
    scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {config.name}
    minReplicas: {config.min_replicas}
    maxReplicas: {config.max_replicas}
    metrics:
    - type: Resource
    resource:
    name: cpu
    target:
    type: Utilization
    averageUtilization: {config.target_cpu_utilization}
    """

    # Write hpa.yaml
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())


    def _generate_kustomization(config: KubernetesConfig, output_path: str) -> None:
    """
    Generate a Kubernetes kustomization configuration.

    Args:
    config: Kubernetes configuration
    output_path: Path to save the kustomization.yaml file
    """
    # Create kustomization.yaml content
    content = """
    apiVersion: kustomize.config.k8s.io/v1beta1
    kind: Kustomization
    namespace: {config.namespace}
    resources:
    - deployment.yaml
    - service.yaml
    """

    # Add ingress if enabled
    if config.enable_ingress:
    content += "- ingress.yaml\n"

    # Add HPA if enabled
    if config.enable_hpa:
    content += "- hpa.yaml\n"

    # Write kustomization.yaml
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())