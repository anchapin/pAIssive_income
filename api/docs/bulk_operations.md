# Bulk Operations API Guide

This guide explains how to use the bulk operation endpoints in the pAIssive Income API for improved performance when working with multiple resources.

## Overview

Bulk operations allow you to create, update, or delete multiple resources in a single API request, which can significantly improve performance compared to making individual requests for each resource.

The API provides the following bulk operation endpoints:

- `POST /api/v1/{resource}/bulk` - Create multiple resources
- `PUT /api/v1/{resource}/bulk` - Update multiple resources
- `DELETE /api/v1/{resource}/bulk` - Delete multiple resources

## Benefits of Bulk Operations

- **Reduced Network Overhead**: Fewer HTTP requests means less network overhead
- **Improved Performance**: Processing multiple items in a single request is more efficient
- **Atomic Operations**: All operations are processed together, making it easier to handle errors
- **Detailed Results**: Get detailed information about successful and failed operations

## Request Format

### Bulk Create

```json
{
  "items": [
    {
      "name": "Resource 1",
      "description": "Description for resource 1",
      "other_field": "value"
    },
    {
      "name": "Resource 2",
      "description": "Description for resource 2",
      "other_field": "value"
    }
  ],
  "options": {
    "validate_only": false
  }
}
```

### Bulk Update

```json
{
  "items": [
    {
      "id": "resource-id-1",
      "name": "Updated Resource 1",
      "description": "Updated description"
    },
    {
      "id": "resource-id-2",
      "name": "Updated Resource 2"
    }
  ],
  "options": {
    "partial_update": true
  }
}
```

### Bulk Delete

```json
{
  "ids": [
    "resource-id-1",
    "resource-id-2",
    "resource-id-3"
  ],
  "options": {
    "force": false
  }
}
```

## Response Format

All bulk operations return a consistent response format:

```json
{
  "items": [...],           // List of successfully processed items (for create/update)
  "deleted_ids": [...],     // List of successfully deleted IDs (for delete)
  "errors": [               // List of errors for failed operations
    {
      "index": 1,           // Index of the failed item in the request
      "error_code": "NOT_FOUND",
      "error_message": "Resource not found: resource-id-2",
      "item_id": "resource-id-2"
    }
  ],
  "stats": {                // Operation statistics
    "total_items": 3,
    "successful_items": 2,
    "failed_items": 1,
    "processing_time_ms": 156.78
  },
  "operation_id": "op-123456" // Unique ID for the bulk operation
}
```

## Example: Bulk Create Niches

### Request

```http
POST /api/v1/niche-analysis/niches/bulk
Content-Type: application/json

{
  "items": [
    {
      "name": "AI-powered content optimization",
      "description": "AI tools for content optimization",
      "market_segment": "Content Creation"
    },
    {
      "name": "Local AI code assistant",
      "description": "AI tools for code assistance",
      "market_segment": "Software Development"
    }
  ]
}
```

### Response

```json
{
  "items": [
    {
      "id": "niche-123",
      "name": "AI-powered content optimization",
      "description": "AI tools for content optimization",
      "market_segment": "Content Creation",
      "opportunity_score": 0.87,
      "problems": [],
      "opportunities": [],
      "created_at": "2023-06-15T10:30:45Z"
    },
    {
      "id": "niche-456",
      "name": "Local AI code assistant",
      "description": "AI tools for code assistance",
      "market_segment": "Software Development",
      "opportunity_score": 0.92,
      "problems": [],
      "opportunities": [],
      "created_at": "2023-06-15T10:30:45Z"
    }
  ],
  "errors": [],
  "stats": {
    "total_items": 2,
    "successful_items": 2,
    "failed_items": 0,
    "processing_time_ms": 125.45
  },
  "operation_id": "op-abc123"
}
```

## Error Handling

When errors occur during bulk operations, the API will still process as many items as possible and return detailed information about any failures. The response will include:

- Successfully processed items in the `items` or `deleted_ids` array
- Failed items in the `errors` array with details about each failure
- Statistics about the operation in the `stats` object

## Best Practices

1. **Batch Size**: Keep batch sizes reasonable (50-100 items per request)
2. **Error Handling**: Always check the `errors` array in the response
3. **Idempotency**: Use the `operation_id` for tracking and ensuring operations are not duplicated
4. **Partial Updates**: For update operations, only include the fields you want to change
5. **Validation**: Consider using the `validate_only` option to validate your request before making actual changes

## Rate Limiting

Bulk operations are subject to the same rate limits as individual operations, but count as multiple operations based on the number of items in the request. For example, a bulk create request with 10 items counts as 10 operations toward your rate limit.
