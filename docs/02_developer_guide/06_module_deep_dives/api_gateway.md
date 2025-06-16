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
- **Math Tool APIs** (see below)

(See the full endpoint listing and usage examples as migrated from the original api/README.md.)

---

## Math Tool APIs

The Math Tool APIs allow agents and services to access core mathematical operations programmatically. All endpoints require authentication using an API key.

### Authentication

Each request must include a valid API key in the `x-api-key` HTTP header. The default development key is:

```
x-api-key: supersecretkey
```

Requests missing a valid key will receive a `401 Unauthorized` error.

### Available Endpoints

All endpoints are available under the `/tools/` prefix and use the POST method.

#### `/tools/add`

**Description:** Add two numbers.

**Request:**

```json
POST /tools/add
Content-Type: application/json
x-api-key: supersecretkey

{
  "a": 3.0,
  "b": 4.5
}
```

**Response:**

```json
{
  "result": 7.5
}
```

#### `/tools/subtract`

**Description:** Subtract two numbers.

```json
POST /tools/subtract
Content-Type: application/json
x-api-key: supersecretkey

{
  "a": 10.0,
  "b": 6.0
}
```

**Response:**

```json
{
  "result": 4.0
}
```

#### `/tools/multiply`

**Description:** Multiply two numbers.

```json
POST /tools/multiply
Content-Type: application/json
x-api-key: supersecretkey

{
  "a": 2.0,
  "b": 3.5
}
```

**Response:**

```json
{
  "result": 7.0
}
```

#### `/tools/divide`

**Description:** Divide two numbers.

```json
POST /tools/divide
Content-Type: application/json
x-api-key: supersecretkey

{
  "a": 8.0,
  "b": 2.0
}
```

**Response:**

```json
{
  "result": 4.0
}
```

If division by zero is attempted, the response will be:

```json
{
  "detail": "Cannot divide by zero"
}
```
(Status: 400)

#### `/tools/average`

**Description:** Average a list of numbers.

```json
POST /tools/average
Content-Type: application/json
x-api-key: supersecretkey

{
  "numbers": [2.0, 4.0, 6.0]
}
```

**Response:**

```json
{
  "result": 4.0
}
```

If the list is empty, the response will be:

```json
{
  "detail": "Cannot calculate average of empty list"
}
```
(Status: 400)

---

### Permission Checks

All endpoints require a valid API key. Permission is binary (allowed/denied) based solely on the key. More granular permissions can be implemented in the future.

### Audit Logging

For every request, the following fields are logged for auditability:

- Tool name (`add`, `subtract`, etc.)
- Input parameters
- API key (obfuscated if required for production)
- Authentication failures
- Error details (e.g., division by zero)

Logs are written to the server log (stdout by default).

### How to Add New Tools

To expose a new Python utility as an API tool:

1. Implement the function in `utils/math_utils.py` or a similar module.
2. Add a Pydantic request model if needed.
3. Add a new endpoint to `api/routes/tool_router.py`, following the existing pattern.
4. Register the endpoint in the router. Ensure it:
    - Uses `POST`
    - Requires `x-api-key` authentication
    - Logs invocations and errors
    - Has OpenAPI docstrings
5. Add or update tests in `tests/api/test_tool_router.py`.
6. Update this documentation section with usage examples.