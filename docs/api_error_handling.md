# API Error Handling

This document describes the error handling system used in the pAIssive Income API.

## Error Response Format

All API errors are returned in a consistent format:

```json
{
  "error": {
    "message": "Human-readable error message",
    "code": "error_code",
    "details": [
      {
        "message": "Detailed error message",
        "code": "detail_code",
        "field": "field_name",
        "params": {
          "param1": "value1",
          "param2": "value2"
        }
      }
    ],
    "path": "/api/endpoint",
    "timestamp": "2023-01-01T00:00:00.000Z",
    "trace_id": "optional-trace-id"
  }
}
```

### Fields

- `message`: A human-readable error message describing what went wrong.
- `code`: A machine-readable error code for programmatic handling.
- `details`: An array of detailed error information, particularly useful for validation errors.
  - `message`: A human-readable message for this specific detail.
  - `code`: A machine-readable code for this specific detail.
  - `field`: The field that caused the error (for validation errors).
  - `params`: Additional parameters related to the error.
- `path`: The API endpoint that was accessed when the error occurred.
- `timestamp`: The time when the error occurred.
- `trace_id`: An optional trace ID for debugging purposes.

## HTTP Status Codes

The API uses standard HTTP status codes to indicate the success or failure of a request:

### Success Codes

- `200 OK`: The request was successful.
- `201 Created`: The request was successful and a resource was created.
- `202 Accepted`: The request has been accepted for processing but is not yet complete.
- `204 No Content`: The request was successful but there is no content to return.

### Client Error Codes

- `400 Bad Request`: The request was malformed or invalid.
- `401 Unauthorized`: Authentication is required or failed.
- `403 Forbidden`: The authenticated user does not have permission to access the resource.
- `404 Not Found`: The requested resource was not found.
- `405 Method Not Allowed`: The HTTP method is not supported for the requested resource.
- `409 Conflict`: The request conflicts with the current state of the resource.
- `422 Unprocessable Entity`: The request was well-formed but contains semantic errors.
- `429 Too Many Requests`: The user has sent too many requests in a given amount of time.

### Server Error Codes

- `500 Internal Server Error`: An unexpected error occurred on the server.
- `501 Not Implemented`: The requested functionality is not implemented.
- `502 Bad Gateway`: The server received an invalid response from an upstream server.
- `503 Service Unavailable`: The server is currently unavailable.
- `504 Gateway Timeout`: The server timed out waiting for a response from an upstream server.

## Common Error Codes

The API uses the following error codes for common error scenarios:

- `validation_error`: The request failed validation.
- `authentication_error`: Authentication failed.
- `authorization_error`: The user does not have permission to access the resource.
- `resource_not_found`: The requested resource was not found.
- `resource_already_exists`: The resource already exists.
- `rate_limit_exceeded`: The user has exceeded the rate limit.
- `internal_error`: An unexpected error occurred on the server.
- `service_unavailable`: The service is currently unavailable.
- `module_unavailable`: A required module is not available.

## Handling Errors in Client Applications

When handling errors in client applications, it's recommended to:

1. Check the HTTP status code first to determine the general category of the error.
2. Use the `code` field to handle specific error scenarios programmatically.
3. Display the `message` field to users for a human-readable explanation.
4. For validation errors, use the `details` array to show field-specific error messages.

## Example Error Responses

### Validation Error

```json
{
  "error": {
    "message": "Validation error",
    "code": "validation_error",
    "details": [
      {
        "message": "Field is required",
        "code": "missing_required_field",
        "field": "name"
      },
      {
        "message": "Must be a valid email",
        "code": "invalid_email",
        "field": "email"
      }
    ],
    "path": "/api/users",
    "timestamp": "2023-01-01T00:00:00.000Z"
  }
}
```

### Resource Not Found

```json
{
  "error": {
    "message": "Niche not found: 123",
    "code": "niche_not_found",
    "details": [
      {
        "message": "The specified niche ID does not exist",
        "code": "resource_not_found",
        "params": {
          "niche_id": "123"
        }
      }
    ],
    "path": "/api/niches/123",
    "timestamp": "2023-01-01T00:00:00.000Z"
  }
}
```

### Authentication Error

```json
{
  "error": {
    "message": "Invalid authentication credentials",
    "code": "authentication_error",
    "path": "/api/users/me",
    "timestamp": "2023-01-01T00:00:00.000Z"
  }
}
```

### Internal Server Error

```json
{
  "error": {
    "message": "An unexpected error occurred",
    "code": "internal_error",
    "path": "/api/niches",
    "timestamp": "2023-01-01T00:00:00.000Z",
    "trace_id": "abc123"
  }
}
```
