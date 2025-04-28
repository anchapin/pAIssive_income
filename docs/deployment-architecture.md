# Deployment Architecture

This document outlines the deployment architecture for the pAIssive Income framework, providing guidance on how to deploy the framework and its components in various environments.

## Overview

The pAIssive Income framework can be deployed in several ways, depending on your requirements:

1. **Local Development**: For development and testing purposes
2. **Docker Containers**: For isolated and consistent deployments
3. **Kubernetes**: For orchestrated and scalable deployments
4. **Cloud Platforms**: For managed, scalable, and production-ready deployments

## Architecture Components

The deployment architecture consists of the following components:

### Core Components

- **Web Interface**: Flask-based web application for user interaction
- **Agent Team Service**: Coordinates AI agents for niche analysis, development, monetization, and marketing
- **AI Models Service**: Manages and serves AI models for inference
- **Database**: Stores project data, user information, and system state

### Supporting Services

- **Cache**: For performance optimization
- **Authentication Service**: For user authentication and authorization
- **Logging Service**: For centralized logging
- **Monitoring Service**: For system monitoring and alerting

## Deployment Options

### 1. Local Development Deployment

For local development and testing, the framework can be run directly on your machine:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the UI
python run_ui.py
```

This setup is suitable for:
- Individual developers
- Small-scale testing
- Prototype development

### 2. Docker Deployment

The framework can be containerized using Docker for consistent and isolated deployments:

```bash
# Build Docker image
docker build -t paissive-income .

# Run Docker container
docker run -d -p 5000:5000 --name paissive-income-app paissive-income
```

The AI Models module provides a `DockerConfig` class and `generate_docker_config` function to assist with Docker deployments:

```python
from ai_models.serving import DockerConfig, generate_docker_config

# Create a Docker configuration
docker_config = DockerConfig(
    image_name="paissive-income-model-server",
    base_image="python:3.9-slim",
    server_type="rest",
    port=8000,
    model_path="/models/my-model",
    model_type="text-generation",
    gpu_count=0  # Set to number of GPUs if available
)

# Generate Docker configuration files
generate_docker_config(docker_config, "docker")
```

This setup is suitable for:
- Development teams
- Staging environments
- Small-scale production deployments

### 3. Kubernetes Deployment

For larger-scale and more robust deployments, the framework can be deployed on Kubernetes:

The AI Models module provides a `KubernetesConfig` class and `generate_kubernetes_config` function to assist with Kubernetes deployments:

```python
from ai_models.serving import KubernetesConfig, generate_kubernetes_config

# Create a Kubernetes configuration
k8s_config = KubernetesConfig(
    name="paissive-income",
    namespace="ai-services",
    image="paissive-income:latest",
    replicas=2,
    server_type="rest",
    port=8000,
    cpu_request="500m",
    cpu_limit="1",
    memory_request="1Gi",
    memory_limit="4Gi",
    env_vars={
        "LOG_LEVEL": "INFO",
        "MAX_BATCH_SIZE": "4"
    },
    volumes=[
        {
            "type": "persistentVolumeClaim",
            "source": "models-pvc",
            "target": "/app/models"
        }
    ],
    enable_hpa=True,
    min_replicas=1,
    max_replicas=5,
    target_cpu_utilization=80
)

# Generate Kubernetes configuration files
generate_kubernetes_config(k8s_config, "kubernetes")
```

This setup is suitable for:
- Production deployments
- Large-scale applications
- High-availability requirements

### 4. Cloud Deployment

The framework can be deployed to various cloud platforms for managed and scalable deployments:

#### AWS Deployment

```python
from ai_models.serving import CloudConfig, CloudProvider, generate_cloud_config

# Create an AWS cloud configuration
aws_config = CloudConfig(
    provider=CloudProvider.AWS,
    name="paissive-income",
    region="us-west-2",
    server_type="rest",
    port=8000,
    model_path="/models/my-model",
    model_type="text-generation",
    instance_type="ml.m5.large",
    cpu_count=2,
    memory_gb=8,
    min_instances=1,
    max_instances=5,
    env_vars={
        "LOG_LEVEL": "INFO",
        "MAX_BATCH_SIZE": "4"
    }
)

# Generate AWS configuration files
generate_cloud_config(aws_config, "aws")
```

#### Google Cloud Platform (GCP) Deployment

```python
from ai_models.serving import CloudConfig, CloudProvider, generate_cloud_config

# Create a GCP cloud configuration
gcp_config = CloudConfig(
    provider=CloudProvider.GCP,
    name="paissive-income",
    region="us-central1",
    server_type="rest",
    port=8000,
    model_path="/models/my-model",
    model_type="text-generation",
    cpu_count=2,
    memory_gb=8,
    min_instances=1,
    max_instances=5,
    env_vars={
        "LOG_LEVEL": "INFO",
        "MAX_BATCH_SIZE": "4"
    }
)

# Generate GCP configuration files
generate_cloud_config(gcp_config, "gcp")
```

#### Microsoft Azure Deployment

```python
from ai_models.serving import CloudConfig, CloudProvider, generate_cloud_config

# Create an Azure cloud configuration
azure_config = CloudConfig(
    provider=CloudProvider.AZURE,
    name="paissive-income",
    region="eastus",
    server_type="rest",
    port=8000,
    model_path="/models/my-model",
    model_type="text-generation",
    cpu_count=2,
    memory_gb=8,
    min_instances=1,
    max_instances=5,
    env_vars={
        "LOG_LEVEL": "INFO",
        "MAX_BATCH_SIZE": "4"
    }
)

# Generate Azure configuration files
generate_cloud_config(azure_config, "azure")
```

This setup is suitable for:
- Production deployments
- Managed infrastructure
- Pay-as-you-go scaling
- Global availability

## Deployment Architecture Diagrams

### Local Deployment Architecture

```
+-------------------+       +-------------------+
|                   |       |                   |
|   Web Interface   |<----->|   Agent Team      |
|   (Flask)         |       |   Services        |
|                   |       |                   |
+-------------------+       +-------------------+
         ^                           ^
         |                           |
         v                           v
+-------------------+       +-------------------+
|                   |       |                   |
|   Local File      |<----->|   AI Models       |
|   Storage         |       |   (Local)         |
|                   |       |                   |
+-------------------+       +-------------------+
```

### Container Deployment Architecture

```
+-------------------+       +-------------------+
|                   |       |                   |
|   Web Interface   |<----->|   Agent Team      |
|   Container       |       |   Container       |
|                   |       |                   |
+-------------------+       +-------------------+
         ^                           ^
         |                           |
         v                           v
+-------------------+       +-------------------+
|                   |       |                   |
|   Database        |<----->|   AI Models       |
|   Container       |       |   Container       |
|                   |       |                   |
+-------------------+       +-------------------+
```

### Kubernetes Deployment Architecture

```
+-------------------+       +-------------------+
|                   |       |                   |
|   Web Interface   |<----->|   Agent Team      |
|   Pod (replicated)|       |   Pod (replicated)|
|                   |       |                   |
+-------------------+       +-------------------+
         ^                           ^
         |                           |
         v                           v
+-------------------+       +-------------------+
|                   |       |                   |
|   Database        |<----->|   AI Models       |
|   StatefulSet     |       |   Deployment      |
|                   |       |   (auto-scaling)  |
+-------------------+       +-------------------+
         ^                           ^
         |                           |
         v                           v
+-------------------+       +-------------------+
|                   |       |                   |
|   Persistent      |       |   Model           |
|   Volume Claims   |       |   Volume Claims   |
|                   |       |                   |
+-------------------+       +-------------------+
```

### Cloud Deployment Architecture

```
+-------------------+       +-------------------+
|                   |       |                   |
|   Web Interface   |<----->|   Agent Team      |
|   (App Service)   |       |   (Container App) |
|                   |       |                   |
+-------------------+       +-------------------+
         ^                           ^
         |                           |
         v                           v
+-------------------+       +-------------------+
|                   |       |                   |
|   Database        |<----->|   AI Models       |
|   (Managed DB)    |       |   (ML Service)    |
|                   |       |   (auto-scaling)  |
+-------------------+       +-------------------+
         ^                           ^
         |                           |
         v                           v
+-------------------+       +-------------------+
|                   |       |                   |
|   Blob/Object     |       |   Model           |
|   Storage         |       |   Registry        |
|                   |       |                   |
+-------------------+       +-------------------+
```

## Configuration and Secrets Management

For secure deployment, sensitive information such as API keys, database credentials, and other secrets should be managed using environment variables or a dedicated secrets management service.

### Environment Variables

Essential environment variables for deployment:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for session encryption
- `AI_MODEL_API_KEY`: API key for external AI model providers
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

### Secrets Management Services

For production deployments, consider using:

- AWS Secrets Manager for AWS deployments
- Google Secret Manager for GCP deployments
- Azure Key Vault for Azure deployments
- HashiCorp Vault for self-hosted deployments

## Deployment Checklist

- [ ] Configure environment variables and secrets
- [ ] Set up database and migrations
- [ ] Configure AI model paths and providers
- [ ] Set up authentication and authorization
- [ ] Configure logging and monitoring
- [ ] Set up backups for database and files
- [ ] Configure SSL/TLS certificates
- [ ] Set up auto-scaling policies
- [ ] Configure health checks and readiness probes
- [ ] Set up CI/CD pipelines for automated deployment

## Common Deployment Issues

1. **Model Loading Failures**: Ensure model paths are correctly configured and models are accessible
2. **Memory Issues**: Monitor memory usage, especially for larger models
3. **Database Connection Issues**: Verify database connection strings and credentials
4. **Authentication Failures**: Check authentication configuration and credentials
5. **Network Issues**: Verify network connectivity between components

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS Documentation](https://docs.aws.amazon.com/)
- [GCP Documentation](https://cloud.google.com/docs)
- [Azure Documentation](https://docs.microsoft.com/azure/)