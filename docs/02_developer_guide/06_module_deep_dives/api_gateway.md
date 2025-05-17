# API Gateway Deep Dive

This document provides a comprehensive guide to the pAIssive Income API module, including server architecture, authentication, endpoints, and usage.

---

<!--
The content below was migrated from api/README.md. For a summary, see the module directory.
-->

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

See the module README for prerequisites and quick start.

## Running the API Server

```bash
python -m api.main
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Authentication

- Supports API Key and JWT authentication.
- See details and usage examples in the "Authentication" section of this document.

## API Key Management

Describes endpoints for creating, listing, updating, and revoking API keys.

## API Endpoints

- Niche Analysis
- Monetization
- Marketing
- AI Models
- Agent Team
- User
- Dashboard

(See the full endpoint listing and usage examples as migrated from the original api/README.md.)