# pAIssive Income API

This module provides RESTful API endpoints for all core services in the pAIssive Income project.

## Overview

The API module is organized into the following components:

1. **Server**: The main API server that handles requests and responses
2. **Routes**: Route handlers for each core service
3. **Schemas**: Pydantic models for request and response validation
4. **Middleware**: Middleware components for authentication, rate limiting, etc.
5. **Models**: Data models for the API
6. **Repositories**: Data storage and retrieval
7. **Services**: Business logic

## Getting Started

### Prerequisites

- Python 3.8 or higher
- FastAPI
- Uvicorn

Install the required dependencies:

```bash
pip install fastapi uvicorn pydantic
```

### Running the API Server

To run the API server:

```bash
python -m api.main
```

This will start the API server on the default host (0.0.0.0) and port (8000).

### Command-Line Options

The API server supports the following command-line options:

- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 8000)
- `--debug`: Enable debug mode
- `--prefix`: API prefix (default: /api)
- `--version`: API version (default: v1)
- `--enable-auth`: Enable authentication
- `--enable-https`: Enable HTTPS
- `--ssl-keyfile`: SSL key file
- `--ssl-certfile`: SSL certificate file
- `--disable-niche-analysis`: Disable niche analysis module
- `--disable-monetization`: Disable monetization module
- `--disable-marketing`: Disable marketing module
- `--disable-ai-models`: Disable AI models module
- `--disable-agent-team`: Disable agent team module
- `--disable-user`: Disable user module
- `--disable-dashboard`: Disable dashboard module

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Authentication

The API supports two authentication methods:

### API Key Authentication

API keys provide a simple way to authenticate with the API. To use API key authentication:

1. Create an API key through the API key management endpoints
2. Include the API key in the `X-API-Key` header in your requests

Example:

```bash
curl -X GET "http://localhost:8000/api/v1/user/profile" -H "X-API-Key: your-api-key"
```

### JWT Authentication

JWT (JSON Web Token) authentication provides a more secure way to authenticate with the API. To use JWT authentication:

1. Log in using the `/api/v1/user/login` endpoint to get a JWT token
2. Include the JWT token in the `Authorization` header in your requests

Example:

```bash
curl -X GET "http://localhost:8000/api/v1/user/profile" -H "Authorization: Bearer your-jwt-token"
```

## API Key Management

The API provides endpoints for managing API keys:

- `POST /api/v1/api-keys`: Create a new API key
- `GET /api/v1/api-keys`: Get all API keys for the current user
- `GET /api/v1/api-keys/{api_key_id}`: Get an API key by ID
- `PUT /api/v1/api-keys/{api_key_id}`: Update an API key
- `DELETE /api/v1/api-keys/{api_key_id}`: Delete an API key
- `POST /api/v1/api-keys/{api_key_id}/revoke`: Revoke an API key

## API Endpoints

The API provides the following endpoints:

### Niche Analysis

- `POST /api/v1/niche-analysis/analyze`: Start a niche analysis
- `GET /api/v1/niche-analysis/analyses`: Get all niche analyses
- `GET /api/v1/niche-analysis/analyses/{analysis_id}`: Get niche analysis details
- `GET /api/v1/niche-analysis/niches`: Get all niches
- `GET /api/v1/niche-analysis/niches/{niche_id}`: Get niche details
- `GET /api/v1/niche-analysis/segments`: Get all market segments

### Monetization

- `POST /api/v1/monetization/subscription-models`: Create a subscription model
- `GET /api/v1/monetization/subscription-models`: Get all subscription models
- `GET /api/v1/monetization/subscription-models/{model_id}`: Get subscription model details
- `POST /api/v1/monetization/revenue-projections`: Create a revenue projection

### Marketing

- `POST /api/v1/marketing/strategies`: Create a marketing strategy
- `GET /api/v1/marketing/strategies`: Get all marketing strategies
- `GET /api/v1/marketing/strategies/{strategy_id}`: Get marketing strategy details
- `GET /api/v1/marketing/personas`: Get all user personas
- `GET /api/v1/marketing/channels`: Get all marketing channels

### AI Models

- `GET /api/v1/ai-models/models`: Get all AI models
- `GET /api/v1/ai-models/models/{model_id}`: Get AI model details
- `POST /api/v1/ai-models/inference`: Run inference on an AI model

### Agent Team

- `POST /api/v1/agent-team/teams`: Create an agent team
- `GET /api/v1/agent-team/teams`: Get all agent teams
- `GET /api/v1/agent-team/teams/{team_id}`: Get agent team details
- `GET /api/v1/agent-team/agents`: Get all agents
- `GET /api/v1/agent-team/workflows`: Get all workflows

### User

- `POST /api/v1/user/register`: Register a new user
- `POST /api/v1/user/login`: Log in a user
- `GET /api/v1/user/profile`: Get user profile
- `PUT /api/v1/user/profile`: Update user profile

### Dashboard

- `GET /api/v1/dashboard/overview`: Get dashboard overview
- `GET /api/v1/dashboard/revenue`: Get revenue statistics
- `GET /api/v1/dashboard/subscribers`: Get subscriber statistics
