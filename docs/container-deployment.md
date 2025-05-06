# Container Deployment Guide

This document provides instructions for deploying the pAIssive Income application using containers with both Docker Compose and Kubernetes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Compose Deployment](#docker-compose-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Health Monitoring](#health-monitoring)
5. [Scaling the Application](#scaling-the-application)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying the application, ensure you have the following installed:

- Docker and Docker Compose (for local deployment)
- Kubernetes CLI (kubectl) and access to a Kubernetes cluster (for Kubernetes deployment)
- Git (for obtaining the source code)

## Docker Compose Deployment

### Building and Running with Docker Compose

1. Clone the repository and navigate to the project root:

```bash
git clone https://github.com/yourusername/paissive-income.git
cd paissive-income
```

2. Build and start the containers:

```bash
docker-compose up --build
```

3. To run in detached mode (in the background):

```bash
docker-compose up -d --build
```

4. Access the application at http://localhost:5000

### Stopping the Application

To stop the application and remove containers:

```bash
docker-compose down
```

To stop the application while preserving the containers:

```bash
docker-compose stop
```

### Managing Volumes

The Docker Compose configuration defines volumes for persistent data:

- `./data:/app/data` - Stores application data
- `./logs:/app/logs` - Stores application logs

These volumes persist data between container restarts.

## Kubernetes Deployment

### Deploying to Kubernetes

1. Apply the ConfigMap:

```bash
kubectl apply -f kubernetes/configmap.yaml
```

2. Create the persistent volume claims:

```bash
kubectl apply -f kubernetes/persistent-volume-claims.yaml
```

3. Deploy the application:

```bash
kubectl apply -f kubernetes/deployment.yaml
```

4. Deploy the service to expose the application:

```bash
kubectl apply -f kubernetes/service.yaml
```

### Accessing the Deployed Application

Once deployed, you can access the application by:

```bash
kubectl get services paissive-income-service
```

This will display the external IP address where the application is available.

### Updating the Deployment

To update the deployment with a new version:

1. Build and push a new image:

```bash
docker build -t paissive-income:latest .
docker tag paissive-income:latest your-registry/paissive-income:version
docker push your-registry/paissive-income:version
```

2. Update the image in the deployment:

```bash
kubectl set image deployment/paissive-income-app paissive-income-app=your-registry/paissive-income:version
```

## Health Monitoring

Both deployment methods include health checks:

- Docker Compose: Health check defined in the Dockerfile runs every 30 seconds
- Kubernetes: Both liveness and readiness probes are configured

You can manually check application health by calling the health endpoint:

```bash
curl http://localhost:5000/health
```

The response should look like:

```json
{
  "status": "healthy",
  "timestamp": "2025-04-28T12:00:00",
  "version": "1.0.0"
}
```

## Scaling the Application

### Scaling with Docker Compose

```bash
docker-compose up -d --scale app=3
```

This scales the service to 3 instances (only works if you remove the container_name and manually configure ports).

### Scaling with Kubernetes

```bash
kubectl scale deployment paissive-income-app --replicas=5
```

This scales the deployment to 5 replicas.

## Troubleshooting

### Common Issues

1. **Container fails to start**:
   - Check logs: `docker-compose logs` or `kubectl logs deployment/paissive-income-app`
   - Verify environment configuration

2. **Health check fails**:
   - Check if the /health endpoint is responding correctly
   - Review service connectivity

3. **Performance issues**:
   - Review resource allocation in deployment configuration
   - Check memory and CPU usage with monitoring tools

4. **Persistence issues**:
   - Verify volume mounts are correctly configured
   - Check permissions on mounted directories

For additional assistance, consult the project's troubleshooting guide or open an issue in the repository.
