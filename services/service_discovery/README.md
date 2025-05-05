# Service Discovery for pAIssive Income Microservices

This module provides service discovery capabilities for the pAIssive Income microservices architecture, allowing services to register themselves and discover other services dynamically.

## Overview

Service discovery is a crucial part of any microservices architecture, as it enables:

1. Dynamic service registration and discovery
2. Load balancing across multiple instances of a service
3. Health checking to detect and route around failures
4. Metadata and versioning information for services

This implementation uses Consul as the service registry, providing a robust and battle-tested solution for service discovery.

## Key Components

- **ServiceRegistry**: Interface for registry implementations
- **ConsulServiceRegistry**: Implementation using Consul
- **ServiceDiscoveryClient**: High-level client for service discovery operations
- **LoadBalancer**: Strategies for selecting service instances
- **ServiceRegistration**: Utility for registering services with the registry
- **Setup Tools**: Utilities for setting up and configuring the service registry

## Quick Start

### 1. Install Dependencies

Make sure you have Consul installed on your system:

```bash
# For Ubuntu/Debian
apt-get update && apt-get install -y consul

# For macOS
brew install consul

# For Windows
# Download from https://developer.hashicorp.com/consul/downloads and add to PATH
```

Also install the Python dependencies:

```bash
pip install python-consul fastapi uvicorn requests
```

### 2. Start the Services

The easiest way to start the microservices with service discovery is to use the `run_microservices.py` script:

```bash
python run_microservices.py
```

This script will:
1. Start Consul in development mode
2. Start the API Gateway service
3. Start the UI service
4. Start the AI Models service

You can access:
- Consul UI: http://localhost:8500/ui/
- API Gateway: http://localhost:8000/
- UI Service: http://localhost:3000/
- AI Models API: http://localhost:8002/docs

### 3. Manual Setup

If you want to start services manually, first start Consul:

```bash
consul agent -dev -ui
```

Then start each service individually, making sure to set the environment variables:

```bash
export SERVICE_REGISTRY_HOST=localhost
export SERVICE_REGISTRY_PORT=8500
export ENVIRONMENT=development

# Start API Gateway
python -m services.api_gateway.app --port 8000

# Start UI Service
python -m services.ui_service.app --port 3000

# Start AI Models Service
python -m services.ai_models_service.app --port 8002
```

## Using Service Discovery in a Microservice

### 1. Register Your Service

The simplest way to register a service is to use the `register_service` function:

```python
from fastapi import FastAPI
from services.service_discovery.registration import register_service, get_service_metadata

app = FastAPI()
service_registration = register_service(
    app=app,
    service_name="my-service",
    port=8080,
    version="1.0.0",
    health_check_path="/health"
)
```

### 2. Discover Other Services

To discover other services, use the ServiceDiscoveryClient:

```python
from services.service_discovery.discovery_client import ServiceDiscoveryClient

client = ServiceDiscoveryClient(
    service_name="my-client",
    port=0,  # No need to register this client
    auto_register=False,
    registry_host="localhost",
    registry_port=8500
)

# Get all instances of a service
instances = client.discover_service("target-service")

# Get URL for a service (with automatic load balancing)
url = client.get_service_url("target-service", "/api/resource")
```

### 3. Add Health Check Endpoints

Health check endpoints are required for proper service discovery:

```python
from services.service_discovery.helpers import register_health_check_endpoint

def check_database():
    # Check database connectivity
    return True

def check_cache():
    # Check cache connectivity
    return True

# Register health check endpoint
register_health_check_endpoint(
    app=app,
    service_name="my-service",
    check_functions=[check_database, check_cache]
)
```

## Advanced Features

### Load Balancing

The service discovery client supports multiple load balancing strategies:

- **Round Robin**: Selects instances in a circular order
- **Random**: Randomly selects an instance
- **Weighted Random**: Selects instances with higher weights more frequently
- **Least Connections**: Selects the instance with the fewest connections

Example:

```python
from services.service_discovery.load_balancer import WeightedRandomStrategy

def weight_function(instance):
    # Give higher weight to newer versions
    if instance.version == "2.0.0":
        return 10
    return 5

client = ServiceDiscoveryClient(
    service_name="my-service",
    load_balancer_strategy="custom"
)
client.load_balancer.strategy = WeightedRandomStrategy(weight_function)
```

### Service Metadata

You can add custom metadata to your services:

```python
service_registration = register_service(
    app=app,
    service_name="my-service",
    port=8080,
    version="1.0.0",
    metadata={
        "api_version": "v2",
        "features": "authentication,billing,reporting",
        "region": "us-east"
    }
)
```

### Local Development

For local development without a running Consul instance, you can create a fallback mechanism:

```python
try:
    # Try to get service URL from service discovery
    service_url = client.get_service_url("target-service")
    if not service_url:
        # Fallback to localhost
        service_url = "http://localhost:8000"
except Exception:
    # Fallback to localhost
    service_url = "http://localhost:8000"
```

## Configuration

The service discovery module can be configured through environment variables:

- `SERVICE_REGISTRY_HOST`: Hostname of the service registry (default: localhost)
- `SERVICE_REGISTRY_PORT`: Port of the service registry (default: 8500)
- `ENVIRONMENT`: Environment name (development, testing, production)

## Troubleshooting

### Service Registration Fails

1. Check if Consul is running: `consul members`
2. Check if the service is reachable (firewall, network issues)
3. Check the logs for error messages

### Service Discovery Fails

1. Check if the service is registered: `consul catalog services`
2. Check if the service has passing health checks: `consul health service <service-name>`
3. Check for connectivity issues between services

## Further Reading

- [Service Discovery Options Document](../../docs/architecture/service-discovery-options.md)
- [Consul Documentation](https://developer.hashicorp.com/consul/docs)
- [Microservices Architecture Overview](../../docs/architecture/microservices-architecture-overview.md)
