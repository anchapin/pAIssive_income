"""
Example usage of the serving utilities.

This module demonstrates how to use the serving utilities to deploy AI models.
"""

import argparse
import logging
import os
import sys

# Add the parent directory to the path to import the ai_models module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_models.serving import (
    CloudConfig,
    CloudProvider,
    DockerConfig,
    GRPCConfig,
    GRPCServer,
    KubernetesConfig,
    RESTConfig,
    RESTServer,
    generate_cloud_config,
    generate_docker_config,
    generate_kubernetes_config,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_rest_server(model_path: str, host: str = "0.0.0.0", port: int = 8000) -> None:
    """
    Test the REST API server.

    Args:
        model_path: Path to the model
        host: Host to bind the server to
        port: Port to bind the server to
    """
    print("\n" + "=" * 80)
    print("Testing REST API Server")
    print("=" * 80)

    try:
        # Create server configuration
        config = RESTConfig(
            model_path=model_path,
            host=host,
            port=port,
            enable_text_generation=True,
            enable_text_classification=False,
            enable_embedding=False,
            enable_health_check=True,
            enable_metrics=True,
        )

        # Create server
        server = RESTServer(config)

        # Load model
        print(f"Loading model from {model_path}")
        server.load_model()

        # Start server
        print(f"Starting server at http://{host}:{port}")
        server.start()

        # Wait for user input
        print("\nServer is running. Press Enter to stop...")
        input()

        # Stop server
        print("Stopping server...")
        server.stop()

        print("Server stopped")

    except Exception as e:
        print(f"Error running REST API server: {e}")


def test_grpc_server(model_path: str, host: str = "0.0.0.0", port: int = 50051) -> None:
    """
    Test the gRPC server.

    Args:
        model_path: Path to the model
        host: Host to bind the server to
        port: Port to bind the server to
    """
    print("\n" + "=" * 80)
    print("Testing gRPC Server")
    print("=" * 80)

    try:
        # Create server configuration
        config = GRPCConfig(
            model_path=model_path,
            host=host,
            port=port,
            enable_text_generation=True,
            enable_text_classification=False,
            enable_embedding=False,
            enable_reflection=True,
            enable_health_checking=True,
        )

        # Create server
        server = GRPCServer(config)

        # Load model
        print(f"Loading model from {model_path}")
        server.load_model()

        # Start server
        print(f"Starting server at {host}:{port}")
        server.start()

        # Wait for user input
        print("\nServer is running. Press Enter to stop...")
        input()

        # Stop server
        print("Stopping server...")
        server.stop()

        print("Server stopped")

    except Exception as e:
        print(f"Error running gRPC server: {e}")


def test_docker_deployment(
    model_path: str, output_dir: str, image_name: str = "ai-model-server"
) -> None:
    """
    Test Docker deployment.

    Args:
        model_path: Path to the model
        output_dir: Directory to save the deployment files
        image_name: Name of the Docker image
    """
    print("\n" + "=" * 80)
    print("Testing Docker Deployment")
    print("=" * 80)

    try:
        # Create Docker configuration
        config = DockerConfig(
            image_name=image_name,
            image_tag="latest",
            base_image="python:3.9-slim",
            server_type="rest",
            model_path=model_path,
            model_type="text-generation",
            port=8000,
            cpu_limit="1",
            memory_limit="4Gi",
            gpu_count=0,
            env_vars={"LOG_LEVEL": "INFO", "MAX_BATCH_SIZE": "4"},
            volumes=[{"source": "./models", "target": "/app/models"}],
            additional_packages=[
                "torch>=1.10.0",
                "transformers>=4.20.0",
                "fastapi>=0.95.0",
                "uvicorn>=0.22.0",
            ],
        )

        # Generate Docker configuration
        print(f"Generating Docker configuration in {output_dir}")
        dockerfile_path = generate_docker_config(config, output_dir)

        print(f"Docker configuration generated at {dockerfile_path}")
        print("\nTo build and run the Docker image:")
        print(f"cd {output_dir}")
        print(f"docker build -t {image_name}:latest .")
        print(f"docker run -p 8000:8000 {image_name}:latest")

    except Exception as e:
        print(f"Error generating Docker configuration: {e}")


def test_kubernetes_deployment(
    model_path: str,
    output_dir: str,
    name: str = "ai-model-server",
    namespace: str = "default",
) -> None:
    """
    Test Kubernetes deployment.

    Args:
        model_path: Path to the model
        output_dir: Directory to save the deployment files
        name: Name of the deployment
        namespace: Kubernetes namespace
    """
    print("\n" + "=" * 80)
    print("Testing Kubernetes Deployment")
    print("=" * 80)

    try:
        # Create Kubernetes configuration
        config = KubernetesConfig(
            name=name,
            namespace=namespace,
            image="ai-model-server:latest",
            server_type="rest",
            port=8000,
            replicas=1,
            strategy="RollingUpdate",
            cpu_request="500m",
            cpu_limit="1",
            memory_request="1Gi",
            memory_limit="4Gi",
            gpu_request=0,
            gpu_limit=0,
            env_vars={
                "MODEL_PATH": model_path,
                "MODEL_TYPE": "text-generation",
                "SERVER_TYPE": "rest",
                "PORT": "8000",
                "LOG_LEVEL": "INFO",
                "MAX_BATCH_SIZE": "4",
            },
            volumes=[
                {
                    "type": "persistentVolumeClaim",
                    "source": "models-pvc",
                    "target": "/app/models",
                }
            ],
            service_type="ClusterIP",
            enable_ingress=True,
            ingress_host="model-server.example.com",
            ingress_path="/",
            ingress_tls=False,
            enable_hpa=True,
            min_replicas=1,
            max_replicas=5,
            target_cpu_utilization=80,
        )

        # Generate Kubernetes configuration
        print(f"Generating Kubernetes configuration in {output_dir}")
        deployment_path = generate_kubernetes_config(config, output_dir)

        print(f"Kubernetes configuration generated at {deployment_path}")
        print("\nTo deploy to Kubernetes:")
        print(f"cd {output_dir}")
        print(f"kubectl apply -k .")

    except Exception as e:
        print(f"Error generating Kubernetes configuration: {e}")


def test_cloud_deployment(
    model_path: str,
    output_dir: str,
    provider: str = "aws",
    name: str = "ai-model-server",
    region: str = "us-west-2",
) -> None:
    """
    Test cloud deployment.

    Args:
        model_path: Path to the model
        output_dir: Directory to save the deployment files
        provider: Cloud provider (aws, gcp, or azure)
        name: Name of the deployment
        region: Cloud region
    """
    print("\n" + "=" * 80)
    print("Testing {} Deployment".format(provider.upper()))
    print("=" * 80)

    try:
        # Convert provider string to enum
        if provider.lower() == "aws":
            cloud_provider = CloudProvider.AWS
        elif provider.lower() == "gcp":
            cloud_provider = CloudProvider.GCP
        elif provider.lower() == "azure":
            cloud_provider = CloudProvider.AZURE
        else:
            raise ValueError(f"Unsupported cloud provider: {provider}")

        # Create cloud configuration
        config = CloudConfig(
            provider=cloud_provider,
            name=name,
            region=region,
            server_type="rest",
            port=8000,
            model_path=model_path,
            model_type="text-generation",
            instance_type=(
                "ml.m5.large" if cloud_provider == CloudProvider.AWS else "n1-standard-2"
            ),
            cpu_count=2,
            memory_gb=8,
            gpu_type=None,
            gpu_count=0,
            min_instances=1,
            max_instances=5,
            storage_size_gb=20,
            storage_type="ssd",
            env_vars={"LOG_LEVEL": "INFO", "MAX_BATCH_SIZE": "4"},
            auth_enabled=True,
            auth_type="api_key",
        )

        # Generate cloud configuration
        print("Generating {} configuration in {}".format(provider.upper(), output_dir))
        config_path = generate_cloud_config(config, output_dir)

        print("{} configuration generated at {}".format(provider.upper(), config_path))
        print("\nTo deploy to the cloud:")
        print("cd {}".format(output_dir))
        print("./deploy.sh")

    except Exception as e:
        print(f"Error generating cloud configuration: {e}")


def main():
    """
    Main function to demonstrate the serving utilities.
    """
    parser = argparse.ArgumentParser(description="Test serving utilities")
    parser.add_argument("--model-path", type=str, required=True, help="Path to the model")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="deployment",
        help="Directory to save deployment files",
    )
    parser.add_argument(
        "--server",
        type=str,
        choices=["rest", "grpc", "none"],
        default="none",
        help="Server to run",
    )
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=None, help="Port to bind the server to")
    parser.add_argument(
        "--deployment",
        type=str,
        choices=["docker", "kubernetes", "aws", "gcp", "azure", "none"],
        default="none",
        help="Deployment to generate",
    )

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Run server if requested
    if args.server == "rest":
        test_rest_server(model_path=args.model_path, host=args.host, port=args.port or 8000)
    elif args.server == "grpc":
        test_grpc_server(model_path=args.model_path, host=args.host, port=args.port or 50051)

    # Generate deployment configuration if requested
    if args.deployment == "docker":
        test_docker_deployment(
            model_path=args.model_path,
            output_dir=os.path.join(args.output_dir, "docker"),
        )
    elif args.deployment == "kubernetes":
        test_kubernetes_deployment(
            model_path=args.model_path,
            output_dir=os.path.join(args.output_dir, "kubernetes"),
        )
    elif args.deployment in ["aws", "gcp", "azure"]:
        test_cloud_deployment(
            model_path=args.model_path,
            output_dir=os.path.join(args.output_dir, args.deployment),
            provider=args.deployment,
        )


if __name__ == "__main__":
    main()
