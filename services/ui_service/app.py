"""
UI Service for pAIssive income microservices architecture.

This module provides the UI Service implementation, which serves the web-based
user interface for the pAIssive income platform.
"""

import os
import logging
import argparse

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from services.service_discovery.registration import (
    register_service,
    get_service_metadata,
    get_default_tags,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="pAIssive Income UI Service",
    description="UI Service for pAIssive Income platform",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory for static files and templates
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

# Create static and templates directories if they don't exist
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Set up static files and templates
try:
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    templates = Jinja2Templates(directory=templates_dir)
except Exception as e:
    logger.error(f"Error setting up static files or templates: {str(e)}")
    # Continue without static files or templates

# Global variables
service_registration = None
service_discovery_client = None


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint for UI Service, serves the main UI page."""
    # For now, return a simple HTML page
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>pAIssive Income Platform</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                line-height: 1.6;
            }
            h1 { color: #333; }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .service-list {
                margin-top: 20px;
            }
            .service-item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            .service-item:last-child {
                border-bottom: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>pAIssive Income Platform</h1>
            <p>Welcome to the pAIssive Income microservices platform!</p>
            <p>This is a placeholder UI that will eventually be replaced with a React-based frontend.</p>
            
            <div class="service-list">
                <h2>Available Services</h2>
                <p>Loading services...</p>
                <div id="services"></div>
            </div>
        </div>
        
        <script>
            // Fetch services from the API Gateway
            fetch('/api/service-info')
                .then(response => response.json())
                .then(data => {
                    const servicesList = document.getElementById('services');
                    servicesList.innerHTML = '';
                    
                    if (data.services && Object.keys(data.services).length > 0) {
                        for (const [name, instances] of Object.entries(data.services)) {
                            const serviceDiv = document.createElement('div');
                            serviceDiv.className = 'service-item';
                            serviceDiv.innerHTML = `<strong>${name}</strong>: ${instances.length} instance(s)`;
                            servicesList.appendChild(serviceDiv);
                        }
                    } else {
                        servicesList.innerHTML = '<p>No services found.</p>';
                    }
                })
                .catch(error => {
                    console.error('Error fetching services:', error);
                    document.getElementById('services').innerHTML = '<p>Error loading services.</p>';
                });
        </script>
    </body>
    </html>
    """


@app.get("/api/status")
async def api_status():
    """API status endpoint."""
    return {"status": "ok", "version": "1.0.0", "service": "ui-service"}


@app.get("/api/service-info")
async def get_services():
    """Get information about available services."""
    if not service_discovery_client:
        return {"services": {}, "error": "Service discovery not available"}

    try:
        services = service_discovery_client.discover_all_services()
        # Convert ServiceInstance objects to simple dictionaries
        services_dict = {}
        for name, instances in services.items():
            services_dict[name] = [
                {
                    "id": instance.service_id,
                    "name": instance.service_name,
                    "host": instance.host,
                    "port": instance.port,
                    "version": instance.version,
                }
                for instance in instances
            ]
        return {"services": services_dict}
    except Exception as e:
        logger.error(f"Error discovering services: {str(e)}")
        return {"services": {}, "error": str(e)}


def check_service_health() -> bool:
    """
    Check if this service is healthy.

    Returns:
        bool: True if healthy, False otherwise
    """
    # For now, always return True
    # In a real implementation, check connections to backend services, etc.
    return True


def register_with_service_registry(port: int):
    """
    Register this service with the service registry.

    Args:
        port: Port this service is running on
    """
    global service_registration, service_discovery_client

    # Get metadata and tags
    metadata = get_service_metadata()
    tags = get_default_tags() + ["ui", "frontend", "web"]

    # Register service
    service_registration = register_service(
        app=app,
        service_name="ui-service",
        port=port,
        version="1.0.0",
        health_check_path="/health",
        check_functions=[check_service_health],
        tags=tags,
        metadata=metadata,
    )

    if service_registration:
        logger.info("Successfully registered UI Service with service registry")
        service_discovery_client = service_registration.client
    else:
        logger.warning(
            "Failed to register with service registry, continuing without service discovery"
        )


def start_ui_service(host: str = "0.0.0.0", port: int = 3000):
    """
    Start the UI Service.

    Args:
        host: Host to bind to
        port: Port to listen on
    """
    import uvicorn

    # Register with service registry
    register_with_service_registry(port)

    # Start the UI Service
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="UI Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=3000, help="Port to listen on")

    args = parser.parse_args()

    # Start the UI Service
    start_ui_service(host=args.host, port=args.port)
