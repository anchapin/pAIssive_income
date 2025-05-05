# Webhook API Reference

This document provides a comprehensive reference for the pAIssive Income Webhook API, including all available endpoints, request/response formats, and security features.

## Table of Contents

- [Webhook API Reference](#webhook-api-reference)
  - [Table of Contents](#table-of-contents)
  - [Authentication](#authentication)
  - [Endpoints](#endpoints)
    - [Register Webhook](#register-webhook)
    - [List Webhooks](#list-webhooks)
    - [Get Webhook](#get-webhook)
    - [Update Webhook](#update-webhook)
    - [Delete Webhook](#delete-webhook)
    - [List Webhook Deliveries](#list-webhook-deliveries)
    - [Test Webhook](#test-webhook)
  - [Security Features](#security-features)
    - [Signature Verification](#signature-verification)
      - [Verifying Signatures](#verifying-signatures)
    - [IP Allowlisting](#ip-allowlisting)
    - [Rate Limiting](#rate-limiting)
    - [Security Endpoints](#security-endpoints)
      - [Configure IP Allowlist](#configure-ip-allowlist)
      - [Rotate Webhook Secret](#rotate-webhook-secret)
      - [Configure Rate Limits](#configure-rate-limits)
  - [Webhook Events](#webhook-events)
  - [Error Handling](#error-handling)
  - [Best Practices](#best-practices)

## Authentication

All API requests must include an API key in the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

API keys can be generated and managed in the [API Keys section](https://app.paissiveincome.com/dashboard/settings/api-keys) of your dashboard.

## Endpoints

All webhook endpoints are under the base path `/api/v1/webhooks`.

### Register Webhook

Creates a new webhook subscription.

**Endpoint:** `POST /api/v1/webhooks`

**Request Body:**

```json
{
  "url": "https://your-server.com/webhook",
  "events": ["user.created", "payment.received"],
  "description": "My webhook for user and payment events",
  "headers": {
    "Authorization": "Bearer your-auth-token"
  },
  "is_active": true
}
```

**Required Fields:**
- `url`: The URL where webhook events will be sent (HTTPS required)
- `events`: Array of event types to subscribe to

**Optional Fields:**
- `description`: A description of the webhook
- `headers`: Custom headers to include with webhook requests
- `is_active`: Whether the webhook is active (default: `true`)

**Response:**

```json
{
  "id": "webhook-123",
  "url": "https://your-server.com/webhook",
  "events": ["user.created", "payment.received"],
  "description": "My webhook for user and payment events",
  "headers": {
    "Authorization": "Bearer your-auth-token"
  },
  "is_active": true,
  "created_at": "2025-04-30T21:30:00Z",
  "last_called_at": null,
  "secret": "whsec_abcdefghijklmnopqrstuvwxyz"
}
```

**Status Codes:**
- `201 Created`: Webhook successfully registered
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid API key
- `500 Internal Server Error`: Server error

**Important:** The `secret` field is only returned when creating a webhook. Store this value securely as it's used for signature verification.

### List Webhooks

Returns a list of all webhooks for your account.

**Endpoint:** `GET /api/v1/webhooks`

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of webhooks per page (default: 10, max: 100)

**Response:**

```json
{
  "items": [
    {
      "id": "webhook-123",
      "url": "https://your-server.com/webhook",
      "events": ["user.created", "payment.received"],
      "description": "My webhook for user and payment events",
      "headers": {
        "Authorization": "Bearer your-auth-token"
      },
      "is_active": true,
      "created_at": "2025-04-30T21:30:00Z",
      "last_called_at": "2025-04-30T22:15:00Z",
      "secret": "whsec_abcdefghijklmnopqrstuvwxyz"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "pages": 1
}
```

**Status Codes:**
- `200 OK`: Success
- `401 Unauthorized`: Invalid API key
- `500 Internal Server Error`: Server error

### Get Webhook

Returns details for a specific webhook.

**Endpoint:** `GET /api/v1/webhooks/{webhook_id}`

**Path Parameters:**
- `webhook_id`: ID of the webhook to retrieve

**Response:**

```json
{
  "id": "webhook-123",
  "url": "https://your-server.com/webhook",
  "events": ["user.created", "payment.received"],
  "description": "My webhook for user and payment events",
  "headers": {
    "Authorization": "Bearer your-auth-token"
  },
  "is_active": true,
  "created_at": "2025-04-30T21:30:00Z",
  "last_called_at": "2025-04-30T22:15:00Z",
  "secret": "whsec_abcdefghijklmnopqrstuvwxyz"
}
```

**Status Codes:**
- `200 OK`: Success
- `401 Unauthorized`: Invalid API key
- `404 Not Found`: Webhook not found
- `500 Internal Server Error`: Server error

### Update Webhook

Updates an existing webhook.

**Endpoint:** `PUT /api/v1/webhooks/{webhook_id}`

**Path Parameters:**
- `webhook_id`: ID of the webhook to update

**Request Body:**

```json
{
  "url": "https://your-new-server.com/webhook",
  "events": ["user.created", "user.updated", "payment.received"],
  "description": "Updated webhook description",
  "headers": {
    "Authorization": "Bearer new-auth-token"
  },
  "is_active": true
}
```

**Optional Fields:**
All fields are optional. Only include the fields you want to update.

**Response:**

```json
{
  "id": "webhook-123",
  "url": "https://your-new-server.com/webhook",
  "events": ["user.created", "user.updated", "payment.received"],
  "description": "Updated webhook description",
  "headers": {
    "Authorization": "Bearer new-auth-token"
  },
  "is_active": true,
  "created_at": "2025-04-30T21:30:00Z",
  "last_called_at": "2025-04-30T22:15:00Z",
  "secret": "whsec_abcdefghijklmnopqrstuvwxyz"
}
```

**Status Codes:**
- `200 OK`: Webhook successfully updated
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid API key
- `404 Not Found`: Webhook not found
- `500 Internal Server Error`: Server error

### Delete Webhook

Deletes a webhook.

**Endpoint:** `DELETE /api/v1/webhooks/{webhook_id}`

**Path Parameters:**
- `webhook_id`: ID of the webhook to delete

**Response:**

```json
{
  "message": "Webhook deleted successfully"
}
```

**Status Codes:**
- `200 OK`: Webhook successfully deleted
- `401 Unauthorized`: Invalid API key
- `404 Not Found`: Webhook not found
- `500 Internal Server Error`: Server error

### List Webhook Deliveries

Returns a list of delivery attempts for a specific webhook.

**Endpoint:** `GET /api/v1/webhooks/{webhook_id}/deliveries`

**Path Parameters:**
- `webhook_id`: ID of the webhook

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of deliveries per page (default: 10, max: 100)
- `status`: Filter by delivery status (`pending`, `success`, `failed`, `retrying`, `max_retries_exceeded`)

**Response:**

```json
{
  "items": [
    {
      "id": "delivery-123",
      "webhook_id": "webhook-123",
      "status": "success",
      "timestamp": "2025-04-30T22:15:00Z",
      "attempts": [
        {
          "id": "attempt-123",
          "webhook_id": "webhook-123",
          "event_type": "user.created",
          "status": "success",
          "request_url": "https://your-server.com/webhook",
          "request_headers": {
            "Content-Type": "application/json",
            "X-Webhook-Signature": "base64-encoded-signature",
            "Authorization": "Bearer your-auth-token"
          },
          "request_body": {
            "id": "evt_123456",
            "type": "user.created",
            "created_at": "2025-04-30T22:15:00Z",
            "data": {
              "user_id": "user_123456",
              "email": "user@example.com",
              "name": "John Doe"
            }
          },
          "response_code": 200,
          "response_body": "OK",
          "error_message": null,
          "timestamp": "2025-04-30T22:15:00Z",
          "retries": 0,
          "next_retry": null
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "pages": 1
}
```

**Status Codes:**
- `200 OK`: Success
- `401 Unauthorized`: Invalid API key
- `404 Not Found`: Webhook not found
- `500 Internal Server Error`: Server error

### Test Webhook

Sends a test event to your webhook endpoint.

**Endpoint:** `POST /api/v1/webhooks/test`

**Request Body:**

```json
{
  "url": "https://your-server.com/webhook",
  "event_type": "payment.received"
}
```

**Required Fields:**
- `url`: The URL to send the test webhook to
- `event_type`: The type of event to simulate

**Response:**

```json
{
  "success": true,
  "delivery_id": "delivery-123",
  "status": "success",
  "response_code": 200,
  "response_body": "OK"
}
```

**Status Codes:**
- `200 OK`: Test webhook sent
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid API key
- `500 Internal Server Error`: Server error

## Security Features

The webhook system includes several security features to ensure that webhook deliveries are secure and reliable.

### Signature Verification

Each webhook request includes a signature in the `X-Webhook-Signature` header. This signature is a base64-encoded HMAC-SHA256 hash of the request body, using your webhook secret as the key.

#### Verifying Signatures

**Python:**
```python
import hmac
import hashlib
import base64

def verify_webhook_signature(payload, signature, secret):
    expected_signature = base64.b64encode(
        hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).digest()
    ).decode()
    
    return hmac.compare_digest(expected_signature, signature)

# In your webhook handler:
signature = request.headers.get('X-Webhook-Signature')
is_valid = verify_webhook_signature(request.body, signature, 'your_webhook_secret')
if not is_valid:
    return HttpResponse(status=401)
```

**Node.js:**
```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('base64');
  
  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature),
    Buffer.from(signature)
  );
}

// In your webhook handler:
const signature = req.headers['x-webhook-signature'];
const isValid = verifyWebhookSignature(
  JSON.stringify(req.body),
  signature,
  'your_webhook_secret'
);

if (!isValid) {
  return res.status(401).send('Invalid signature');
}
```

### IP Allowlisting

For additional security, we recommend configuring your firewall to only accept webhook requests from our IP addresses:

- `192.0.2.1`
- `192.0.2.2`
- `192.0.2.3`
- `192.0.2.4`

### Rate Limiting

To protect your systems from being overwhelmed, we implement rate limiting on webhook deliveries. The default rate limits are:

- Maximum of 100 webhook deliveries per minute per endpoint
- Maximum of 1000 webhook deliveries per hour per endpoint

If you need higher limits, please contact our support team.

### Security Endpoints

#### Configure IP Allowlist

**Endpoint:** `PUT /api/v1/webhooks/{webhook_id}/security/ip-allowlist`

**Path Parameters:**
- `webhook_id`: ID of the webhook to configure

**Request Body:**
```json
{
  "allowed_ips": [
    "203.0.113.1",
    "203.0.113.0/24",
    "2001:db8:/32"
  ],
  "enabled": true
}
```

**Response:**
```json
{
  "webhook_id": "webhook-123",
  "allowed_ips": [
    "203.0.113.1",
    "203.0.113.0/24",
    "2001:db8:/32"
  ],
  "enabled": true,
  "updated_at": "2025-04-30T22:15:00Z"
}
```

**Status Codes:**
- `200 OK`: IP allowlist updated successfully
- `400 Bad Request`: Invalid IP addresses
- `401 Unauthorized`: Invalid API key
- `404 Not Found`: Webhook not found

#### Rotate Webhook Secret

**Endpoint:** `POST /api/v1/webhooks/{webhook_id}/security/rotate-secret`

**Path Parameters:**
- `webhook_id`: ID of the webhook

**Response:**
```json
{
  "webhook_id": "webhook-123",
  "new_secret": "whsec_newSecretKey123",
  "old_secret_expiry": "2025-05-07T22:15:00Z"
}
```

The old secret will continue to work for 7 days after rotation to allow for a smooth transition.

**Status Codes:**
- `200 OK`: Secret rotated successfully
- `401 Unauthorized`: Invalid API key
- `404 Not Found`: Webhook not found

#### Configure Rate Limits

**Endpoint:** `PUT /api/v1/webhooks/{webhook_id}/security/rate-limits`

**Path Parameters:**
- `webhook_id`: ID of the webhook

**Request Body:**
```json
{
  "per_minute": 200,
  "per_hour": 2000
}
```

**Response:**
```json
{
  "webhook_id": "webhook-123",
  "rate_limits": {
    "per_minute": 200,
    "per_hour": 2000
  },
  "updated_at": "2025-04-30T22:15:00Z"
}
```

**Status Codes:**
- `200 OK`: Rate limits updated successfully
- `400 Bad Request`: Invalid rate limits
- `401 Unauthorized`: Invalid API key
- `404 Not Found`: Webhook not found
- `403 Forbidden`: Rate limit increase not allowed

## Webhook Events

The following event types are available for subscription:

| Event Type | Description |
|------------|-------------|
| `user.created` | A new user has been created |
| `user.updated` | A user's information has been updated |
| `user.deleted` | A user has been deleted |
| `strategy.created` | A new strategy has been created |
| `strategy.updated` | A strategy has been updated |
| `strategy.deleted` | A strategy has been deleted |
| `campaign.created` | A new marketing campaign has been created |
| `campaign.updated` | A campaign has been updated |
| `campaign.deleted` | A campaign has been deleted |
| `project.created` | A new project has been created |
| `project.updated` | A project has been updated |
| `project.deleted` | A project has been deleted |
| `niche_analysis.started` | A niche analysis has started |
| `niche_analysis.completed` | A niche analysis has completed |
| `niche_analysis.failed` | A niche analysis has failed |
| `subscription.created` | A new subscription has been created |
| `payment.received` | A payment has been received |

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests. Error responses include a JSON body with details about the error:

```json
{
  "error": {
    "code": "webhook_not_found",
    "message": "The specified webhook could not be found",
    "details": {
      "webhook_id": "webhook-123"
    }
  }
}
```

Common error codes:

| Error Code | Description |
|------------|-------------|
| `invalid_request` | The request was invalid |
| `webhook_not_found` | The specified webhook could not be found |
| `invalid_event_type` | The specified event type is not valid |
| `invalid_url` | The specified URL is not valid or not HTTPS |
| `rate_limit_exceeded` | You have exceeded the rate limit for this endpoint |
| `internal_error` | An internal server error occurred |

## Best Practices

1. **Verify signatures**: Always verify webhook signatures to ensure requests are legitimate.
2. **Implement idempotency**: Store event IDs to avoid processing duplicate events.
3. **Process asynchronously**: Acknowledge webhooks quickly and process them in the background.
4. **Monitor deliveries**: Use the webhook dashboard to monitor delivery status and troubleshoot issues.
5. **Set up redundancy**: Consider having multiple webhook endpoints for critical events.
6. **Test with our webhook tester**: Use our webhook tester to verify your endpoint works correctly.
7. **Use IP allowlisting**: Configure your firewall to only accept requests from our IP addresses.
8. **Implement proper error handling**: Handle webhook delivery failures gracefully.
9. **Set up alerts**: Configure alerts for webhook delivery failures to quickly identify issues.
10. **Keep your webhook secret secure**: Never expose your webhook secret in client-side code or public repositories.
