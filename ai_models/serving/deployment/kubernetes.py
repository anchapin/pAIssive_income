"""
"""
Kubernetes deployment utilities for AI models.
Kubernetes deployment utilities for AI models.


This module provides utilities for deploying AI models with Kubernetes.
This module provides utilities for deploying AI models with Kubernetes.
"""
"""




import logging
import logging
import os
import os
from dataclasses import dataclass, field
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


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
class KubernetesConfig:
    class KubernetesConfig:
    """
    """
    Configuration for Kubernetes deployment.
    Configuration for Kubernetes deployment.
    """
    """


    # Basic configuration
    # Basic configuration
    name: str
    name: str
    namespace: str = "default"
    namespace: str = "default"
    image: str = ""
    image: str = ""


    # Server configuration
    # Server configuration
    server_type: str = "rest"  # "rest" or "grpc"
    server_type: str = "rest"  # "rest" or "grpc"
    port: int = 8000
    port: int = 8000


    # Deployment configuration
    # Deployment configuration
    replicas: int = 1
    replicas: int = 1
    strategy: str = "RollingUpdate"  # "RollingUpdate" or "Recreate"
    strategy: str = "RollingUpdate"  # "RollingUpdate" or "Recreate"


    # Resource configuration
    # Resource configuration
    cpu_request: str = "500m"
    cpu_request: str = "500m"
    cpu_limit: str = "1"
    cpu_limit: str = "1"
    memory_request: str = "1Gi"
    memory_request: str = "1Gi"
    memory_limit: str = "4Gi"
    memory_limit: str = "4Gi"
    gpu_request: int = 0
    gpu_request: int = 0
    gpu_limit: int = 0
    gpu_limit: int = 0


    # Environment variables
    # Environment variables
    env_vars: Dict[str, str] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)


    # Volume configuration
    # Volume configuration
    volumes: List[Dict[str, str]] = field(default_factory=list)
    volumes: List[Dict[str, str]] = field(default_factory=list)


    # Service configuration
    # Service configuration
    service_type: str = "ClusterIP"  # "ClusterIP", "NodePort", or "LoadBalancer"
    service_type: str = "ClusterIP"  # "ClusterIP", "NodePort", or "LoadBalancer"
    node_port: Optional[int] = None
    node_port: Optional[int] = None


    # Ingress configuration
    # Ingress configuration
    enable_ingress: bool = False
    enable_ingress: bool = False
    ingress_host: str = ""
    ingress_host: str = ""
    ingress_path: str = "/"
    ingress_path: str = "/"
    ingress_tls: bool = False
    ingress_tls: bool = False
    ingress_tls_secret: str = ""
    ingress_tls_secret: str = ""


    # Horizontal Pod Autoscaler configuration
    # Horizontal Pod Autoscaler configuration
    enable_hpa: bool = False
    enable_hpa: bool = False
    min_replicas: int = 1
    min_replicas: int = 1
    max_replicas: int = 10
    max_replicas: int = 10
    target_cpu_utilization: int = 80
    target_cpu_utilization: int = 80


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
    "name": self.name,
    "name": self.name,
    "namespace": self.namespace,
    "namespace": self.namespace,
    "image": self.image,
    "image": self.image,
    "server_type": self.server_type,
    "server_type": self.server_type,
    "port": self.port,
    "port": self.port,
    "replicas": self.replicas,
    "replicas": self.replicas,
    "strategy": self.strategy,
    "strategy": self.strategy,
    "cpu_request": self.cpu_request,
    "cpu_request": self.cpu_request,
    "cpu_limit": self.cpu_limit,
    "cpu_limit": self.cpu_limit,
    "memory_request": self.memory_request,
    "memory_request": self.memory_request,
    "memory_limit": self.memory_limit,
    "memory_limit": self.memory_limit,
    "gpu_request": self.gpu_request,
    "gpu_request": self.gpu_request,
    "gpu_limit": self.gpu_limit,
    "gpu_limit": self.gpu_limit,
    "env_vars": self.env_vars,
    "env_vars": self.env_vars,
    "volumes": self.volumes,
    "volumes": self.volumes,
    "service_type": self.service_type,
    "service_type": self.service_type,
    "node_port": self.node_port,
    "node_port": self.node_port,
    "enable_ingress": self.enable_ingress,
    "enable_ingress": self.enable_ingress,
    "ingress_host": self.ingress_host,
    "ingress_host": self.ingress_host,
    "ingress_path": self.ingress_path,
    "ingress_path": self.ingress_path,
    "ingress_tls": self.ingress_tls,
    "ingress_tls": self.ingress_tls,
    "ingress_tls_secret": self.ingress_tls_secret,
    "ingress_tls_secret": self.ingress_tls_secret,
    "enable_hpa": self.enable_hpa,
    "enable_hpa": self.enable_hpa,
    "min_replicas": self.min_replicas,
    "min_replicas": self.min_replicas,
    "max_replicas": self.max_replicas,
    "max_replicas": self.max_replicas,
    "target_cpu_utilization": self.target_cpu_utilization,
    "target_cpu_utilization": self.target_cpu_utilization,
    }
    }


    @classmethod
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "KubernetesConfig":
    def from_dict(cls, config_dict: Dict[str, Any]) -> "KubernetesConfig":
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
    Kubernetes configuration
    Kubernetes configuration
    """
    """
    return cls(**config_dict)
    return cls(**config_dict)




    def generate_kubernetes_config(config: KubernetesConfig, output_dir: str) -> str:
    def generate_kubernetes_config(config: KubernetesConfig, output_dir: str) -> str:
    """
    """
    Generate Kubernetes configuration files.
    Generate Kubernetes configuration files.


    Args:
    Args:
    config: Kubernetes configuration
    config: Kubernetes configuration
    output_dir: Directory to save the configuration files
    output_dir: Directory to save the configuration files


    Returns:
    Returns:
    Path to the generated deployment.yaml file
    Path to the generated deployment.yaml file
    """
    """
    # Create output directory
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


    # Generate deployment.yaml
    # Generate deployment.yaml
    deployment_path = os.path.join(output_dir, "deployment.yaml")
    deployment_path = os.path.join(output_dir, "deployment.yaml")
    _generate_deployment(config, deployment_path)
    _generate_deployment(config, deployment_path)


    # Generate service.yaml
    # Generate service.yaml
    service_path = os.path.join(output_dir, "service.yaml")
    service_path = os.path.join(output_dir, "service.yaml")
    _generate_service(config, service_path)
    _generate_service(config, service_path)


    # Generate ingress.yaml if enabled
    # Generate ingress.yaml if enabled
    if config.enable_ingress:
    if config.enable_ingress:
    ingress_path = os.path.join(output_dir, "ingress.yaml")
    ingress_path = os.path.join(output_dir, "ingress.yaml")
    _generate_ingress(config, ingress_path)
    _generate_ingress(config, ingress_path)


    # Generate hpa.yaml if enabled
    # Generate hpa.yaml if enabled
    if config.enable_hpa:
    if config.enable_hpa:
    hpa_path = os.path.join(output_dir, "hpa.yaml")
    hpa_path = os.path.join(output_dir, "hpa.yaml")
    _generate_hpa(config, hpa_path)
    _generate_hpa(config, hpa_path)


    # Generate kustomization.yaml
    # Generate kustomization.yaml
    kustomization_path = os.path.join(output_dir, "kustomization.yaml")
    kustomization_path = os.path.join(output_dir, "kustomization.yaml")
    _generate_kustomization(config, kustomization_path)
    _generate_kustomization(config, kustomization_path)


    logger.info(f"Kubernetes configuration files generated in {output_dir}")
    logger.info(f"Kubernetes configuration files generated in {output_dir}")


    return deployment_path
    return deployment_path




    def _generate_deployment(config: KubernetesConfig, output_path: str) -> None:
    def _generate_deployment(config: KubernetesConfig, output_path: str) -> None:
    """
    """
    Generate a Kubernetes deployment configuration.
    Generate a Kubernetes deployment configuration.


    Args:
    Args:
    config: Kubernetes configuration
    config: Kubernetes configuration
    output_path: Path to save the deployment.yaml file
    output_path: Path to save the deployment.yaml file
    """
    """
    # Create deployment.yaml content
    # Create deployment.yaml content
    content = """
    content = """
    apiVersion: apps/v1
    apiVersion: apps/v1
    kind: Deployment
    kind: Deployment
    metadata:
    metadata:
    name: {config.name}
    name: {config.name}
    namespace: {config.namespace}
    namespace: {config.namespace}
    labels:
    labels:
    app: {config.name}
    app: {config.name}
    spec:
    spec:
    replicas: {config.replicas}
    replicas: {config.replicas}
    selector:
    selector:
    matchLabels:
    matchLabels:
    app: {config.name}
    app: {config.name}
    strategy:
    strategy:
    type: {config.strategy}
    type: {config.strategy}
    template:
    template:
    metadata:
    metadata:
    labels:
    labels:
    app: {config.name}
    app: {config.name}
    spec:
    spec:
    containers:
    containers:
    - name: {config.name}
    - name: {config.name}
    image: {config.image}
    image: {config.image}
    ports:
    ports:
    - containerPort: {config.port}
    - containerPort: {config.port}
    resources:
    resources:
    requests:
    requests:
    cpu: {config.cpu_request}
    cpu: {config.cpu_request}
    memory: {config.memory_request}
    memory: {config.memory_request}
    limits:
    limits:
    cpu: {config.cpu_limit}
    cpu: {config.cpu_limit}
    memory: {config.memory_limit}
    memory: {config.memory_limit}
    """
    """


    # Add GPU resources if needed
    # Add GPU resources if needed
    if config.gpu_request > 0 or config.gpu_limit > 0:
    if config.gpu_request > 0 or config.gpu_limit > 0:
    content += "          requests:\n"
    content += "          requests:\n"
    if config.gpu_request > 0:
    if config.gpu_request > 0:
    content += f"            nvidia.com/gpu: {config.gpu_request}\n"
    content += f"            nvidia.com/gpu: {config.gpu_request}\n"
    content += "          limits:\n"
    content += "          limits:\n"
    if config.gpu_limit > 0:
    if config.gpu_limit > 0:
    content += f"            nvidia.com/gpu: {config.gpu_limit}\n"
    content += f"            nvidia.com/gpu: {config.gpu_limit}\n"


    # Add environment variables
    # Add environment variables
    if config.env_vars:
    if config.env_vars:
    content += "        env:\n"
    content += "        env:\n"
    for key, value in config.env_vars.items():
    for key, value in config.env_vars.items():
    content += """        - name: {key}
    content += """        - name: {key}
    value: "{value}"
    value: "{value}"
    """
    """


    # Add volumes
    # Add volumes
    if config.volumes:
    if config.volumes:
    content += "        volumeMounts:\n"
    content += "        volumeMounts:\n"
    for i, volume in enumerate(config.volumes):
    for i, volume in enumerate(config.volumes):
    content += """        - name: volume-{i}
    content += """        - name: volume-{i}
    mountPath: {volume['target']}
    mountPath: {volume['target']}
    """
    """


    content += "      volumes:\n"
    content += "      volumes:\n"
    for i, volume in enumerate(config.volumes):
    for i, volume in enumerate(config.volumes):
    volume_type = volume.get("type", "hostPath")
    volume_type = volume.get("type", "hostPath")


    if volume_type == "hostPath":
    if volume_type == "hostPath":
    content += """      - name: volume-{i}
    content += """      - name: volume-{i}
    hostPath:
    hostPath:
    path: {volume['source']}
    path: {volume['source']}
    """
    """
    elif volume_type == "persistentVolumeClaim":
    elif volume_type == "persistentVolumeClaim":
    content += """      - name: volume-{i}
    content += """      - name: volume-{i}
    persistentVolumeClaim:
    persistentVolumeClaim:
    claimName: {volume['source']}
    claimName: {volume['source']}
    """
    """


    # Write deployment.yaml
    # Write deployment.yaml
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())




    def _generate_service(config: KubernetesConfig, output_path: str) -> None:
    def _generate_service(config: KubernetesConfig, output_path: str) -> None:
    """
    """
    Generate a Kubernetes service configuration.
    Generate a Kubernetes service configuration.


    Args:
    Args:
    config: Kubernetes configuration
    config: Kubernetes configuration
    output_path: Path to save the service.yaml file
    output_path: Path to save the service.yaml file
    """
    """
    # Create service.yaml content
    # Create service.yaml content
    content = """
    content = """
    apiVersion: v1
    apiVersion: v1
    kind: Service
    kind: Service
    metadata:
    metadata:
    name: {config.name}
    name: {config.name}
    namespace: {config.namespace}
    namespace: {config.namespace}
    labels:
    labels:
    app: {config.name}
    app: {config.name}
    spec:
    spec:
    type: {config.service_type}
    type: {config.service_type}
    selector:
    selector:
    app: {config.name}
    app: {config.name}
    ports:
    ports:
    - port: {config.port}
    - port: {config.port}
    targetPort: {config.port}
    targetPort: {config.port}
    protocol: TCP
    protocol: TCP
    name: {config.server_type}
    name: {config.server_type}
    """
    """


    # Add node port if specified
    # Add node port if specified
    if config.service_type == "NodePort" and config.node_port:
    if config.service_type == "NodePort" and config.node_port:
    content += f"    nodePort: {config.node_port}\n"
    content += f"    nodePort: {config.node_port}\n"


    # Write service.yaml
    # Write service.yaml
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())




    def _generate_ingress(config: KubernetesConfig, output_path: str) -> None:
    def _generate_ingress(config: KubernetesConfig, output_path: str) -> None:
    """
    """
    Generate a Kubernetes ingress configuration.
    Generate a Kubernetes ingress configuration.


    Args:
    Args:
    config: Kubernetes configuration
    config: Kubernetes configuration
    output_path: Path to save the ingress.yaml file
    output_path: Path to save the ingress.yaml file
    """
    """
    # Create ingress.yaml content
    # Create ingress.yaml content
    content = """
    content = """
    apiVersion: networking.k8s.io/v1
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    kind: Ingress
    metadata:
    metadata:
    name: {config.name}
    name: {config.name}
    namespace: {config.namespace}
    namespace: {config.namespace}
    labels:
    labels:
    app: {config.name}
    app: {config.name}
    annotations:
    annotations:
    kubernetes.io/ingress.class: nginx
    kubernetes.io/ingress.class: nginx
    """
    """


    # Add TLS if enabled
    # Add TLS if enabled
    if config.ingress_tls:
    if config.ingress_tls:
    content += """spec:
    content += """spec:
    tls:
    tls:
    - hosts:
    - hosts:
    - {config.ingress_host}
    - {config.ingress_host}
    secretName: {config.ingress_tls_secret}
    secretName: {config.ingress_tls_secret}
    rules:
    rules:
    - host: {config.ingress_host}
    - host: {config.ingress_host}
    http:
    http:
    paths:
    paths:
    - path: {config.ingress_path}
    - path: {config.ingress_path}
    pathType: Prefix
    pathType: Prefix
    backend:
    backend:
    service:
    service:
    name: {config.name}
    name: {config.name}
    port:
    port:
    number: {config.port}
    number: {config.port}
    """
    """
    else:
    else:
    content += """spec:
    content += """spec:
    rules:
    rules:
    - host: {config.ingress_host}
    - host: {config.ingress_host}
    http:
    http:
    paths:
    paths:
    - path: {config.ingress_path}
    - path: {config.ingress_path}
    pathType: Prefix
    pathType: Prefix
    backend:
    backend:
    service:
    service:
    name: {config.name}
    name: {config.name}
    port:
    port:
    number: {config.port}
    number: {config.port}
    """
    """


    # Write ingress.yaml
    # Write ingress.yaml
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())




    def _generate_hpa(config: KubernetesConfig, output_path: str) -> None:
    def _generate_hpa(config: KubernetesConfig, output_path: str) -> None:
    """
    """
    Generate a Kubernetes Horizontal Pod Autoscaler configuration.
    Generate a Kubernetes Horizontal Pod Autoscaler configuration.


    Args:
    Args:
    config: Kubernetes configuration
    config: Kubernetes configuration
    output_path: Path to save the hpa.yaml file
    output_path: Path to save the hpa.yaml file
    """
    """
    # Create hpa.yaml content
    # Create hpa.yaml content
    content = """
    content = """
    apiVersion: autoscaling/v2
    apiVersion: autoscaling/v2
    kind: HorizontalPodAutoscaler
    kind: HorizontalPodAutoscaler
    metadata:
    metadata:
    name: {config.name}
    name: {config.name}
    namespace: {config.namespace}
    namespace: {config.namespace}
    labels:
    labels:
    app: {config.name}
    app: {config.name}
    spec:
    spec:
    scaleTargetRef:
    scaleTargetRef:
    apiVersion: apps/v1
    apiVersion: apps/v1
    kind: Deployment
    kind: Deployment
    name: {config.name}
    name: {config.name}
    minReplicas: {config.min_replicas}
    minReplicas: {config.min_replicas}
    maxReplicas: {config.max_replicas}
    maxReplicas: {config.max_replicas}
    metrics:
    metrics:
    - type: Resource
    - type: Resource
    resource:
    resource:
    name: cpu
    name: cpu
    target:
    target:
    type: Utilization
    type: Utilization
    averageUtilization: {config.target_cpu_utilization}
    averageUtilization: {config.target_cpu_utilization}
    """
    """


    # Write hpa.yaml
    # Write hpa.yaml
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())




    def _generate_kustomization(config: KubernetesConfig, output_path: str) -> None:
    def _generate_kustomization(config: KubernetesConfig, output_path: str) -> None:
    """
    """
    Generate a Kubernetes kustomization configuration.
    Generate a Kubernetes kustomization configuration.


    Args:
    Args:
    config: Kubernetes configuration
    config: Kubernetes configuration
    output_path: Path to save the kustomization.yaml file
    output_path: Path to save the kustomization.yaml file
    """
    """
    # Create kustomization.yaml content
    # Create kustomization.yaml content
    content = """
    content = """
    apiVersion: kustomize.config.k8s.io/v1beta1
    apiVersion: kustomize.config.k8s.io/v1beta1
    kind: Kustomization
    kind: Kustomization
    namespace: {config.namespace}
    namespace: {config.namespace}
    resources:
    resources:
    - deployment.yaml
    - deployment.yaml
    - service.yaml
    - service.yaml
    """
    """


    # Add ingress if enabled
    # Add ingress if enabled
    if config.enable_ingress:
    if config.enable_ingress:
    content += "- ingress.yaml\n"
    content += "- ingress.yaml\n"


    # Add HPA if enabled
    # Add HPA if enabled
    if config.enable_hpa:
    if config.enable_hpa:
    content += "- hpa.yaml\n"
    content += "- hpa.yaml\n"


    # Write kustomization.yaml
    # Write kustomization.yaml
    with open(output_path, "w", encoding="utf-8") as f:
    with open(output_path, "w", encoding="utf-8") as f:
    f.write(content.strip())
    f.write(content.strip())