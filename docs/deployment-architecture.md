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

## CI/CD Pipeline Integration

The pAIssive Income framework can be integrated with Continuous Integration and Continuous Deployment (CI/CD) pipelines to automate testing, building, and deployment processes. Here are examples for common CI/CD platforms:

### GitHub Actions CI/CD Pipeline

```yaml
name: pAIssive Income CI/CD Pipeline

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest --cov=./ --cov-report=xml
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v1

  build:
    needs: test
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/dev')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1
      - name: Login to DockerHub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Build and push Docker image
        uses: docker/build-push-action@v2
        with:
          context: .
          push: true
          tags: paissiveincome/app:latest

  deploy-dev:
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/dev'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Development Environment
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DEV_HOST }}
          username: ${{ secrets.DEV_USER }}
          key: ${{ secrets.DEV_SSH_KEY }}
          script: |
            docker pull paissiveincome/app:latest
            docker-compose -f ~/paissive-income/docker-compose.yml down
            docker-compose -f ~/paissive-income/docker-compose.yml up -d

  deploy-prod:
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Production Environment
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            docker pull paissiveincome/app:latest
            docker-compose -f ~/paissive-income/docker-compose.yml down
            docker-compose -f ~/paissive-income/docker-compose.yml up -d
```

### GitLab CI/CD Pipeline

```yaml
stages:
  - test
  - build
  - deploy-dev
  - deploy-prod

variables:
  DOCKER_IMAGE: registry.gitlab.com/paissiveincome/app

test:
  stage: test
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
    - pytest --cov=./ --cov-report=term
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $DOCKER_IMAGE:$CI_COMMIT_SHORT_SHA .
    - docker push $DOCKER_IMAGE:$CI_COMMIT_SHORT_SHA
    - docker tag $DOCKER_IMAGE:$CI_COMMIT_SHORT_SHA $DOCKER_IMAGE:latest
    - docker push $DOCKER_IMAGE:latest
  only:
    - main
    - dev

deploy-dev:
  stage: deploy-dev
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh
    - eval $(ssh-agent -s)
    - echo "$DEV_SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - echo "$DEV_SSH_KNOWN_HOSTS" > ~/.ssh/known_hosts
  script:
    - ssh $DEV_USER@$DEV_HOST "docker pull $DOCKER_IMAGE:latest && docker-compose -f ~/paissive-income/docker-compose.yml down && docker-compose -f ~/paissive-income/docker-compose.yml up -d"
  only:
    - dev

deploy-prod:
  stage: deploy-prod
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh
    - eval $(ssh-agent -s)
    - echo "$PROD_SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - echo "$PROD_SSH_KNOWN_HOSTS" > ~/.ssh/known_hosts
  script:
    - ssh $PROD_USER@$PROD_HOST "docker pull $DOCKER_IMAGE:latest && docker-compose -f ~/paissive-income/docker-compose.yml down && docker-compose -f ~/paissive-income/docker-compose.yml up -d"
  only:
    - main
  when: manual
```

### Azure DevOps Pipeline

```yaml
trigger:
  branches:
    include:
      - main
      - dev

pool:
  vmImage: 'ubuntu-latest'

variables:
  dockerRegistryServiceConnection: 'docker-registry-connection'
  imageRepository: 'paissiveincome/app'
  dockerfilePath: '$(Build.SourcesDirectory)/Dockerfile'
  tag: '$(Build.BuildId)'

stages:
- stage: Test
  jobs:
  - job: TestJob
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.9'
        addToPath: true
    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
      displayName: 'Install dependencies'
    - script: |
        pytest --cov=./ --cov-report=xml
      displayName: 'Run tests'
    - task: PublishCodeCoverageResults@1
      inputs:
        codeCoverageTool: Cobertura
        summaryFileLocation: '$(System.DefaultWorkingDirectory)/**/coverage.xml'

- stage: Build
  dependsOn: Test
  condition: succeeded()
  jobs:
  - job: BuildJob
    steps:
    - task: Docker@2
      displayName: Login to Docker Hub
      inputs:
        command: login
        containerRegistry: $(dockerRegistryServiceConnection)
    - task: Docker@2
      displayName: Build and Push
      inputs:
        command: buildAndPush
        repository: $(imageRepository)
        dockerfile: $(dockerfilePath)
        containerRegistry: $(dockerRegistryServiceConnection)
        tags: |
          $(tag)
          latest

- stage: DeployDev
  dependsOn: Build
  condition: and(succeeded(), eq(variables['Build.SourceBranchName'], 'dev'))
  jobs:
  - deployment: DeployDev
    environment: 'development'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: DownloadSecureFile@1
            name: sshKey
            displayName: 'Download SSH key'
            inputs:
              secureFile: 'id_rsa'
          - script: |
              mkdir -p ~/.ssh
              cp $(sshKey.secureFilePath) ~/.ssh/id_rsa
              chmod 700 ~/.ssh
              chmod 600 ~/.ssh/id_rsa
              ssh-keyscan -H $(DEV_HOST) >> ~/.ssh/known_hosts
              ssh $(DEV_USER)@$(DEV_HOST) "docker pull $(imageRepository):latest && docker-compose -f ~/paissive-income/docker-compose.yml down && docker-compose -f ~/paissive-income/docker-compose.yml up -d"
            displayName: 'Deploy to Dev Environment'

- stage: DeployProd
  dependsOn: Build
  condition: and(succeeded(), eq(variables['Build.SourceBranchName'], 'main'))
  jobs:
  - deployment: DeployProd
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: DownloadSecureFile@1
            name: sshKey
            displayName: 'Download SSH key'
            inputs:
              secureFile: 'id_rsa'
          - script: |
              mkdir -p ~/.ssh
              cp $(sshKey.secureFilePath) ~/.ssh/id_rsa
              chmod 700 ~/.ssh
              chmod 600 ~/.ssh/id_rsa
              ssh-keyscan -H $(PROD_HOST) >> ~/.ssh/known_hosts
              ssh $(PROD_USER)@$(PROD_HOST) "docker pull $(imageRepository):latest && docker-compose -f ~/paissive-income/docker-compose.yml down && docker-compose -f ~/paissive-income/docker-compose.yml up -d"
            displayName: 'Deploy to Production Environment'
```

### AWS CodePipeline Configuration

For AWS CodePipeline, you can create a `buildspec.yml` file:

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.9
    commands:
      - echo Installing dependencies...
      - pip install -r requirements.txt
      - pip install -r requirements-dev.txt
  
  pre_build:
    commands:
      - echo Running tests...
      - pytest
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
  
  build:
    commands:
      - echo Building the Docker image...
      - docker build -t $REPOSITORY_URI:latest .
      - docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION
  
  post_build:
    commands:
      - echo Pushing the Docker image...
      - docker push $REPOSITORY_URI:latest
      - docker push $REPOSITORY_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION
      - echo Writing image definitions file...
      - aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --force-new-deployment

artifacts:
  files:
    - appspec.yml
    - taskdef.json
    - imagedefinitions.json
```

These CI/CD pipeline configurations provide automation for:

1. Running tests on each push or pull request
2. Building and pushing Docker images upon successful tests
3. Deploying to development environments automatically
4. Deploying to production environments with various safety mechanisms (manual approval or main branch only)

## Scaling Considerations

When deploying pAIssive Income at scale, consider the following aspects:

### Horizontal Scaling

- **Web Interface**: Deploy behind a load balancer with multiple instances
- **Agent Team Services**: Scale based on request volume
- **AI Models**: Distribute inference loads across multiple servers
- **Database**: Use read replicas for scaling read operations

### Vertical Scaling

- **AI Models**: Provision instances with appropriate GPU/CPU resources based on model size
- **Database**: Upgrade instance types as data volume grows
- **Memory Optimization**: Configure memory limits based on workload characteristics

### Auto-Scaling Rules

- **CPU Utilization**: Scale when CPU utilization exceeds 70%
- **Memory Utilization**: Scale when memory utilization exceeds 80%
- **Request Rate**: Scale based on incoming request rates
- **Model Inference Time**: Scale when average inference time exceeds thresholds

## High-Availability Configuration

To ensure high availability of pAIssive Income deployments:

### Multi-AZ/Region Deployment

- Deploy application components across multiple availability zones
- Consider multi-region deployment for critical applications
- Set up proper database replication across zones/regions

### Backup and Disaster Recovery

- Regular database backups with tested restore procedures
- Automated snapshot creation for all persistent storage
- Documented disaster recovery procedures with recovery time objectives (RTO) and recovery point objectives (RPO)

### Health Monitoring

- Implement comprehensive health checks for all services
- Configure proper readiness and liveness probes for Kubernetes deployments
- Set up automated alerts based on service health status

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS Documentation](https://docs.aws.amazon.com/)
- [GCP Documentation](https://cloud.google.com/docs)
- [Azure Documentation](https://docs.microsoft.com/azure/)