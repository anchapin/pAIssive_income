# API Rate Limiting

This document outlines the rate limiting system for the pAIssive Income API.

## Overview

The API uses a rate limiting system to prevent abuse and ensure fair usage of resources. The rate limiting system supports multiple strategies, scopes, and configurations to provide flexible control over API usage.

## Rate Limiting Strategies

The API supports the following rate limiting strategies:

1. **Fixed Window**: Limits the number of requests in a fixed time window (e.g., 100 requests per minute).
2. **Token Bucket**: Allows for bursts of traffic while maintaining a consistent average rate.
3. **Leaky Bucket**: Processes requests at a constant rate, queuing or rejecting excess requests.
4. **Sliding Window**: Tracks requests over a rolling time window for more accurate rate limiting.

The default strategy is **Token Bucket**, which provides a good balance between flexibility and protection.

## Rate Limiting Scopes

Rate limits can be applied at different scopes:

1. **Global**: A single rate limit for all API requests.
2. **IP**: Rate limits are applied per client IP address.
3. **API Key**: Rate limits are applied per API key.
4. **User**: Rate limits are applied per authenticated user.
5. **Endpoint**: Rate limits are applied per API endpoint.

The default scope is **IP**, which provides a good balance between security and usability.

## Rate Limit Tiers

The API supports different rate limit tiers for different types of users:

- **Default**: 100 requests per minute (for unauthenticated users)
- **Basic**: 300 requests per minute
- **Premium**: 1000 requests per minute
- **Unlimited**: No rate limit

## Endpoint-Specific Rate Limits

Some endpoints may have specific rate limits due to their resource requirements. For example:

- `/api/v1/ai-models/inference`: 20 requests per minute
- `/api/v2/ai-models/inference`: 30 requests per minute

## Rate Limit Headers

When rate limiting is enabled, the API includes the following headers in responses:

- `X-RateLimit-Limit`: The maximum number of requests allowed in the current time window.
- `X-RateLimit-Remaining`: The number of requests remaining in the current time window.
- `X-RateLimit-Reset`: The time (in Unix timestamp) when the rate limit window resets.
- `Retry-After`: The number of seconds to wait before retrying (only included when rate limited).

## Rate Limit Exemptions

Certain clients can be exempted from rate limiting:

- **Exempt IPs**: A list of IP addresses that are exempt from rate limiting.
- **Exempt API Keys**: A list of API keys that are exempt from rate limiting.

## Rate Limit Response

When a client exceeds the rate limit, the API returns a `429 Too Many Requests` response with the following body:

```json
{
  "detail": "Rate limit exceeded"
}
```

## Configuration

Rate limiting can be configured using the following options:

```bash
# Enable rate limiting
--enable-rate-limit

# Set rate limiting strategy
--rate-limit-strategy token_bucket

# Set rate limiting scope
--rate-limit-scope ip

# Set rate limit parameters
--rate-limit-requests 100
--rate-limit-period 60
--rate-limit-burst 50

# Disable rate limit headers
--disable-rate-limit-headers
```

## Best Practices for API Consumers

1. **Implement Backoff**: When you receive a 429 response, use the `Retry-After` header to determine how long to wait before retrying.
2. **Monitor Rate Limit Headers**: Keep track of the `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers to avoid hitting rate limits.
3. **Use API Keys**: Authenticate with an API key to get higher rate limits.
4. **Batch Requests**: When possible, batch multiple operations into a single request to reduce the number of API calls.
5. **Cache Responses**: Cache API responses when appropriate to reduce the number of requests.

## Example

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

### Rate Limit Exceeded Response

```
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1609459200
Retry-After: 30

{
  "detail": "Rate limit exceeded"
}
```
