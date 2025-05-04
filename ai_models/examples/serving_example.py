"""
"""
Example usage of the serving utilities.
Example usage of the serving utilities.


This script demonstrates how to use the serving utilities to deploy AI models.
This script demonstrates how to use the serving utilities to deploy AI models.
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




    import argparse
    import argparse
    import logging
    import logging
    import os
    import os
    import sys
    import sys


    # Add the parent directory to the path to import the ai_models module
    # Add the parent directory to the path to import the ai_models module
    sys.path.append(
    sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    )


    from ai_models.serving import (CloudConfig, CloudProvider, DockerConfig,
    from ai_models.serving import (CloudConfig, CloudProvider, DockerConfig,
    GRPCConfig, GRPCServer, KubernetesConfig,
    GRPCConfig, GRPCServer, KubernetesConfig,
    RESTConfig, RESTServer, generate_cloud_config,
    RESTConfig, RESTServer, generate_cloud_config,
    generate_docker_config,
    generate_docker_config,
    generate_kubernetes_config)
    generate_kubernetes_config)


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




    def test_rest_server(model_path: str, host: str = "0.0.0.0", port: int = 8000) -> None:
    def test_rest_server(model_path: str, host: str = "0.0.0.0", port: int = 8000) -> None:
    """
    """
    Test the REST API server.
    Test the REST API server.


    Args:
    Args:
    model_path: Path to the model
    model_path: Path to the model
    host: Host to bind the server to
    host: Host to bind the server to
    port: Port to bind the server to
    port: Port to bind the server to
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print("Testing REST API Server")
    print("Testing REST API Server")
    print("=" * 80)
    print("=" * 80)


    try:
    try:
    # Create server configuration
    # Create server configuration
    config = RESTConfig(
    config = RESTConfig(
    model_path=model_path,
    model_path=model_path,
    host=host,
    host=host,
    port=port,
    port=port,
    enable_text_generation=True,
    enable_text_generation=True,
    enable_text_classification=False,
    enable_text_classification=False,
    enable_embedding=False,
    enable_embedding=False,
    enable_health_check=True,
    enable_health_check=True,
    enable_metrics=True,
    enable_metrics=True,
    )
    )


    # Create server
    # Create server
    server = RESTServer(config)
    server = RESTServer(config)


    # Load model
    # Load model
    print(f"Loading model from {model_path}")
    print(f"Loading model from {model_path}")
    server.load_model()
    server.load_model()


    # Start server
    # Start server
    print(f"Starting server at http://{host}:{port}")
    print(f"Starting server at http://{host}:{port}")
    server.start()
    server.start()


    # Wait for user input
    # Wait for user input
    print("\nServer is running. Press Enter to stop...")
    print("\nServer is running. Press Enter to stop...")
    input()
    input()


    # Stop server
    # Stop server
    print("Stopping server...")
    print("Stopping server...")
    server.stop()
    server.stop()


    print("Server stopped")
    print("Server stopped")


except Exception as e:
except Exception as e:
    print(f"Error running REST API server: {e}")
    print(f"Error running REST API server: {e}")




    def test_grpc_server(model_path: str, host: str = "0.0.0.0", port: int = 50051) -> None:
    def test_grpc_server(model_path: str, host: str = "0.0.0.0", port: int = 50051) -> None:
    """
    """
    Test the gRPC server.
    Test the gRPC server.


    Args:
    Args:
    model_path: Path to the model
    model_path: Path to the model
    host: Host to bind the server to
    host: Host to bind the server to
    port: Port to bind the server to
    port: Port to bind the server to
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print("Testing gRPC Server")
    print("Testing gRPC Server")
    print("=" * 80)
    print("=" * 80)


    try:
    try:
    # Create server configuration
    # Create server configuration
    config = GRPCConfig(
    config = GRPCConfig(
    model_path=model_path,
    model_path=model_path,
    host=host,
    host=host,
    port=port,
    port=port,
    enable_text_generation=True,
    enable_text_generation=True,
    enable_text_classification=False,
    enable_text_classification=False,
    enable_embedding=False,
    enable_embedding=False,
    enable_reflection=True,
    enable_reflection=True,
    enable_health_checking=True,
    enable_health_checking=True,
    )
    )


    # Create server
    # Create server
    server = GRPCServer(config)
    server = GRPCServer(config)


    # Load model
    # Load model
    print(f"Loading model from {model_path}")
    print(f"Loading model from {model_path}")
    server.load_model()
    server.load_model()


    # Start server
    # Start server
    print(f"Starting server at {host}:{port}")
    print(f"Starting server at {host}:{port}")
    server.start()
    server.start()


    # Wait for user input
    # Wait for user input
    print("\nServer is running. Press Enter to stop...")
    print("\nServer is running. Press Enter to stop...")
    input()
    input()


    # Stop server
    # Stop server
    print("Stopping server...")
    print("Stopping server...")
    server.stop()
    server.stop()


    print("Server stopped")
    print("Server stopped")


except Exception as e:
except Exception as e:
    print(f"Error running gRPC server: {e}")
    print(f"Error running gRPC server: {e}")




    def test_docker_deployment(
    def test_docker_deployment(
    model_path: str, output_dir: str, image_name: str = "ai-model-server"
    model_path: str, output_dir: str, image_name: str = "ai-model-server"
    ) -> None:
    ) -> None:
    """
    """
    Test Docker deployment.
    Test Docker deployment.


    Args:
    Args:
    model_path: Path to the model
    model_path: Path to the model
    output_dir: Directory to save the deployment files
    output_dir: Directory to save the deployment files
    image_name: Name of the Docker image
    image_name: Name of the Docker image
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print("Testing Docker Deployment")
    print("Testing Docker Deployment")
    print("=" * 80)
    print("=" * 80)


    try:
    try:
    # Create Docker configuration
    # Create Docker configuration
    config = DockerConfig(
    config = DockerConfig(
    image_name=image_name,
    image_name=image_name,
    image_tag="latest",
    image_tag="latest",
    base_image="python:3.9-slim",
    base_image="python:3.9-slim",
    server_type="rest",
    server_type="rest",
    model_path=model_path,
    model_path=model_path,
    model_type="text-generation",
    model_type="text-generation",
    port=8000,
    port=8000,
    cpu_limit="1",
    cpu_limit="1",
    memory_limit="4Gi",
    memory_limit="4Gi",
    gpu_count=0,
    gpu_count=0,
    env_vars={"LOG_LEVEL": "INFO", "MAX_BATCH_SIZE": "4"},
    env_vars={"LOG_LEVEL": "INFO", "MAX_BATCH_SIZE": "4"},
    volumes=[{"source": "./models", "target": "/app/models"}],
    volumes=[{"source": "./models", "target": "/app/models"}],
    additional_packages=[
    additional_packages=[
    "torch>=1.10.0",
    "torch>=1.10.0",
    "transformers>=4.20.0",
    "transformers>=4.20.0",
    "fastapi>=0.95.0",
    "fastapi>=0.95.0",
    "uvicorn>=0.22.0",
    "uvicorn>=0.22.0",
    ],
    ],
    )
    )


    # Generate Docker configuration
    # Generate Docker configuration
    print(f"Generating Docker configuration in {output_dir}")
    print(f"Generating Docker configuration in {output_dir}")
    dockerfile_path = generate_docker_config(config, output_dir)
    dockerfile_path = generate_docker_config(config, output_dir)


    print(f"Docker configuration generated at {dockerfile_path}")
    print(f"Docker configuration generated at {dockerfile_path}")
    print("\nTo build and run the Docker image:")
    print("\nTo build and run the Docker image:")
    print(f"cd {output_dir}")
    print(f"cd {output_dir}")
    print(f"docker build -t {image_name}:latest .")
    print(f"docker build -t {image_name}:latest .")
    print(f"docker run -p 8000:8000 {image_name}:latest")
    print(f"docker run -p 8000:8000 {image_name}:latest")


except Exception as e:
except Exception as e:
    print(f"Error generating Docker configuration: {e}")
    print(f"Error generating Docker configuration: {e}")




    def test_kubernetes_deployment(
    def test_kubernetes_deployment(
    model_path: str,
    model_path: str,
    output_dir: str,
    output_dir: str,
    name: str = "ai-model-server",
    name: str = "ai-model-server",
    namespace: str = "default",
    namespace: str = "default",
    ) -> None:
    ) -> None:
    """
    """
    Test Kubernetes deployment.
    Test Kubernetes deployment.


    Args:
    Args:
    model_path: Path to the model
    model_path: Path to the model
    output_dir: Directory to save the deployment files
    output_dir: Directory to save the deployment files
    name: Name of the deployment
    name: Name of the deployment
    namespace: Kubernetes namespace
    namespace: Kubernetes namespace
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print("Testing Kubernetes Deployment")
    print("Testing Kubernetes Deployment")
    print("=" * 80)
    print("=" * 80)


    try:
    try:
    # Create Kubernetes configuration
    # Create Kubernetes configuration
    config = KubernetesConfig(
    config = KubernetesConfig(
    name=name,
    name=name,
    namespace=namespace,
    namespace=namespace,
    image="ai-model-server:latest",
    image="ai-model-server:latest",
    server_type="rest",
    server_type="rest",
    port=8000,
    port=8000,
    replicas=1,
    replicas=1,
    strategy="RollingUpdate",
    strategy="RollingUpdate",
    cpu_request="500m",
    cpu_request="500m",
    cpu_limit="1",
    cpu_limit="1",
    memory_request="1Gi",
    memory_request="1Gi",
    memory_limit="4Gi",
    memory_limit="4Gi",
    gpu_request=0,
    gpu_request=0,
    gpu_limit=0,
    gpu_limit=0,
    env_vars={
    env_vars={
    "MODEL_PATH": model_path,
    "MODEL_PATH": model_path,
    "MODEL_TYPE": "text-generation",
    "MODEL_TYPE": "text-generation",
    "SERVER_TYPE": "rest",
    "SERVER_TYPE": "rest",
    "PORT": "8000",
    "PORT": "8000",
    "LOG_LEVEL": "INFO",
    "LOG_LEVEL": "INFO",
    "MAX_BATCH_SIZE": "4",
    "MAX_BATCH_SIZE": "4",
    },
    },
    volumes=[
    volumes=[
    {
    {
    "type": "persistentVolumeClaim",
    "type": "persistentVolumeClaim",
    "source": "models-pvc",
    "source": "models-pvc",
    "target": "/app/models",
    "target": "/app/models",
    }
    }
    ],
    ],
    service_type="ClusterIP",
    service_type="ClusterIP",
    enable_ingress=True,
    enable_ingress=True,
    ingress_host="model-server.example.com",
    ingress_host="model-server.example.com",
    ingress_path="/",
    ingress_path="/",
    ingress_tls=False,
    ingress_tls=False,
    enable_hpa=True,
    enable_hpa=True,
    min_replicas=1,
    min_replicas=1,
    max_replicas=5,
    max_replicas=5,
    target_cpu_utilization=80,
    target_cpu_utilization=80,
    )
    )


    # Generate Kubernetes configuration
    # Generate Kubernetes configuration
    print(f"Generating Kubernetes configuration in {output_dir}")
    print(f"Generating Kubernetes configuration in {output_dir}")
    deployment_path = generate_kubernetes_config(config, output_dir)
    deployment_path = generate_kubernetes_config(config, output_dir)


    print(f"Kubernetes configuration generated at {deployment_path}")
    print(f"Kubernetes configuration generated at {deployment_path}")
    print("\nTo deploy to Kubernetes:")
    print("\nTo deploy to Kubernetes:")
    print(f"cd {output_dir}")
    print(f"cd {output_dir}")
    print("kubectl apply -k .")
    print("kubectl apply -k .")


except Exception as e:
except Exception as e:
    print(f"Error generating Kubernetes configuration: {e}")
    print(f"Error generating Kubernetes configuration: {e}")




    def test_cloud_deployment(
    def test_cloud_deployment(
    model_path: str,
    model_path: str,
    output_dir: str,
    output_dir: str,
    provider: str = "aws",
    provider: str = "aws",
    name: str = "ai-model-server",
    name: str = "ai-model-server",
    region: str = "us-west-2",
    region: str = "us-west-2",
    ) -> None:
    ) -> None:
    """
    """
    Test cloud deployment.
    Test cloud deployment.


    Args:
    Args:
    model_path: Path to the model
    model_path: Path to the model
    output_dir: Directory to save the deployment files
    output_dir: Directory to save the deployment files
    provider: Cloud provider (aws, gcp, or azure)
    provider: Cloud provider (aws, gcp, or azure)
    name: Name of the deployment
    name: Name of the deployment
    region: Cloud region
    region: Cloud region
    """
    """
    print("\n" + "=" * 80)
    print("\n" + "=" * 80)
    print(f"Testing {provider.upper()} Deployment")
    print(f"Testing {provider.upper()} Deployment")
    print("=" * 80)
    print("=" * 80)


    try:
    try:
    # Convert provider string to enum
    # Convert provider string to enum
    if provider.lower() == "aws":
    if provider.lower() == "aws":
    cloud_provider = CloudProvider.AWS
    cloud_provider = CloudProvider.AWS
    elif provider.lower() == "gcp":
    elif provider.lower() == "gcp":
    cloud_provider = CloudProvider.GCP
    cloud_provider = CloudProvider.GCP
    elif provider.lower() == "azure":
    elif provider.lower() == "azure":
    cloud_provider = CloudProvider.AZURE
    cloud_provider = CloudProvider.AZURE
    else:
    else:
    raise ValueError(f"Unsupported cloud provider: {provider}")
    raise ValueError(f"Unsupported cloud provider: {provider}")


    # Create cloud configuration
    # Create cloud configuration
    config = CloudConfig(
    config = CloudConfig(
    provider=cloud_provider,
    provider=cloud_provider,
    name=name,
    name=name,
    region=region,
    region=region,
    server_type="rest",
    server_type="rest",
    port=8000,
    port=8000,
    model_path=model_path,
    model_path=model_path,
    model_type="text-generation",
    model_type="text-generation",
    instance_type=(
    instance_type=(
    "ml.m5.large"
    "ml.m5.large"
    if cloud_provider == CloudProvider.AWS
    if cloud_provider == CloudProvider.AWS
    else "n1-standard-2"
    else "n1-standard-2"
    ),
    ),
    cpu_count=2,
    cpu_count=2,
    memory_gb=8,
    memory_gb=8,
    gpu_type=None,
    gpu_type=None,
    gpu_count=0,
    gpu_count=0,
    min_instances=1,
    min_instances=1,
    max_instances=5,
    max_instances=5,
    storage_size_gb=20,
    storage_size_gb=20,
    storage_type="ssd",
    storage_type="ssd",
    env_vars={"LOG_LEVEL": "INFO", "MAX_BATCH_SIZE": "4"},
    env_vars={"LOG_LEVEL": "INFO", "MAX_BATCH_SIZE": "4"},
    auth_enabled=True,
    auth_enabled=True,
    auth_type="api_key",
    auth_type="api_key",
    )
    )


    # Generate cloud configuration
    # Generate cloud configuration
    print(f"Generating {provider.upper()} configuration in {output_dir}")
    print(f"Generating {provider.upper()} configuration in {output_dir}")
    config_path = generate_cloud_config(config, output_dir)
    config_path = generate_cloud_config(config, output_dir)


    print(f"{provider.upper()} configuration generated at {config_path}")
    print(f"{provider.upper()} configuration generated at {config_path}")
    print("\nTo deploy to the cloud:")
    print("\nTo deploy to the cloud:")
    print(f"cd {output_dir}")
    print(f"cd {output_dir}")
    print("./deploy.sh")
    print("./deploy.sh")


except Exception as e:
except Exception as e:
    print(f"Error generating cloud configuration: {e}")
    print(f"Error generating cloud configuration: {e}")




    def main():
    def main():
    """
    """
    Main function to demonstrate the serving utilities.
    Main function to demonstrate the serving utilities.
    """
    """
    parser = argparse.ArgumentParser(description="Test serving utilities")
    parser = argparse.ArgumentParser(description="Test serving utilities")
    parser.add_argument(
    parser.add_argument(
    "--model-path", type=str, required=True, help="Path to the model"
    "--model-path", type=str, required=True, help="Path to the model"
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
    parser.add_argument(
    parser.add_argument(
    "--server",
    "--server",
    type=str,
    type=str,
    choices=["rest", "grpc", "none"],
    choices=["rest", "grpc", "none"],
    default="none",
    default="none",
    help="Server to run",
    help="Server to run",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--host", type=str, default="0.0.0.0", help="Host to bind the server to"
    "--host", type=str, default="0.0.0.0", help="Host to bind the server to"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--port", type=int, default=None, help="Port to bind the server to"
    "--port", type=int, default=None, help="Port to bind the server to"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--deployment",
    "--deployment",
    type=str,
    type=str,
    choices=["docker", "kubernetes", "aws", "gcp", "azure", "none"],
    choices=["docker", "kubernetes", "aws", "gcp", "azure", "none"],
    default="none",
    default="none",
    help="Deployment to generate",
    help="Deployment to generate",
    )
    )


    args = parser.parse_args()
    args = parser.parse_args()


    # Create output directory
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)


    # Run server if requested
    # Run server if requested
    if args.server == "rest":
    if args.server == "rest":
    test_rest_server(
    test_rest_server(
    model_path=args.model_path, host=args.host, port=args.port or 8000
    model_path=args.model_path, host=args.host, port=args.port or 8000
    )
    )
    elif args.server == "grpc":
    elif args.server == "grpc":
    test_grpc_server(
    test_grpc_server(
    model_path=args.model_path, host=args.host, port=args.port or 50051
    model_path=args.model_path, host=args.host, port=args.port or 50051
    )
    )


    # Generate deployment configuration if requested
    # Generate deployment configuration if requested
    if args.deployment == "docker":
    if args.deployment == "docker":
    test_docker_deployment(
    test_docker_deployment(
    model_path=args.model_path,
    model_path=args.model_path,
    output_dir=os.path.join(args.output_dir, "docker"),
    output_dir=os.path.join(args.output_dir, "docker"),
    )
    )
    elif args.deployment == "kubernetes":
    elif args.deployment == "kubernetes":
    test_kubernetes_deployment(
    test_kubernetes_deployment(
    model_path=args.model_path,
    model_path=args.model_path,
    output_dir=os.path.join(args.output_dir, "kubernetes"),
    output_dir=os.path.join(args.output_dir, "kubernetes"),
    )
    )
    elif args.deployment in ["aws", "gcp", "azure"]:
    elif args.deployment in ["aws", "gcp", "azure"]:
    test_cloud_deployment(
    test_cloud_deployment(
    model_path=args.model_path,
    model_path=args.model_path,
    output_dir=os.path.join(args.output_dir, args.deployment),
    output_dir=os.path.join(args.output_dir, args.deployment),
    provider=args.deployment,
    provider=args.deployment,
    )
    )




    if __name__ == "__main__":
    if __name__ == "__main__":
    main()
    main()

