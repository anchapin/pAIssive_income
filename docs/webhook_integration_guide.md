# Webhook Integration Guide

This guide explains how to integrate with the pAIssive Income webhook system to receive real-time notifications about events in your account.

## Overview

Webhooks allow you to receive real-time notifications when specific events occur in your pAIssive Income account. Instead of polling our API for changes, webhooks push data to your server as events happen.

## Table of Contents

1. [Setting Up a Webhook](#setting-up-a-webhook)
2. [Event Types](#event-types)
3. [Webhook Payload](#webhook-payload)
4. [Security](#security)
5. [Handling Webhook Deliveries](#handling-webhook-deliveries)
6. [Retry Logic](#retry-logic)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Setting Up a Webhook

### Creating a Webhook

To create a webhook, make a POST request to the `/api/v1/webhooks` endpoint:

```json
POST /api/v1/webhooks
{
  "url": "https://your-server.com/webhook",
  "events": ["user.created", "payment.received"],
  "description": "My webhook for user and payment events",
  "headers": {
    "Authorization": "Bearer your-auth-token"
  }
}
```

### Required Parameters

- `url`: The URL where webhook events will be sent (HTTPS required)
- `events`: Array of event types to subscribe to

### Optional Parameters

- `description`: A description of the webhook
- `headers`: Custom headers to include with webhook requests
- `is_active`: Whether the webhook is active (default: `true`)

### Response

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

**Important**: Store the `secret` value securely. It will be used to verify webhook signatures and is only returned when creating a webhook.

## Event Types

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

## Webhook Payload

When an event occurs, we'll send an HTTP POST request to your webhook URL with a JSON payload:

```json
{
  "id": "evt_123456",
  "type": "payment.received",
  "created_at": "2025-04-30T21:35:00Z",
  "data": {
    "payment_id": "pay_123456",
    "amount": 19.99,
    "currency": "USD",
    "status": "succeeded",
    "customer_id": "cus_123456"
  }
}
```

### Payload Structure

- `id`: Unique identifier for the webhook event
- `type`: The type of event that occurred
- `created_at`: ISO 8601 timestamp when the event occurred
- `data`: Event-specific data

## Security

### HTTPS

All webhook URLs must use HTTPS to ensure secure transmission of data.

### Webhook Signatures

To verify that webhook requests are coming from pAIssive Income, we include a signature in the `X-Webhook-Signature` header. This signature is a base64-encoded HMAC-SHA256 hash of the request body, using your webhook secret as the key.

#### Verifying Signatures

Here's how to verify the signature in different languages:

**Python**:
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

**Node.js**:
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

## Handling Webhook Deliveries

### Response Requirements

Your webhook endpoint should:

1. Return a `2xx` status code (preferably `200 OK`) to acknowledge receipt
2. Respond within 10 seconds to avoid timeouts
3. Process the webhook asynchronously if the operation takes longer than 10 seconds

### Idempotency

Webhook events may be delivered more than once in rare circumstances. To handle this, implement idempotency by checking the event ID and ensuring you don't process the same event multiple times.

## Retry Logic

If your endpoint returns a non-2xx status code or times out, we'll retry the delivery with the following schedule:

1. 1 minute after the first failure
2. 5 minutes after the second failure
3. 10 minutes after the third failure
4. 30 minutes after the fourth failure
5. 1 hour after the fifth failure

After 5 failed attempts, we'll stop trying to deliver the webhook.

## Best Practices

1. **Verify signatures**: Always verify webhook signatures to ensure requests are legitimate.
2. **Implement idempotency**: Store event IDs to avoid processing duplicate events.
3. **Process asynchronously**: Acknowledge webhooks quickly and process them in the background.
4. **Monitor deliveries**: Use the webhook dashboard to monitor delivery status and troubleshoot issues.
5. **Set up redundancy**: Consider having multiple webhook endpoints for critical events.
6. **Test with our webhook tester**: Use our webhook tester to verify your endpoint works correctly.

## Troubleshooting

### Common Issues

1. **Webhook not being delivered**:
   - Check that your webhook URL is correct and accessible from the internet
   - Verify that your server is not blocking our IP addresses
   - Check your server logs for errors

2. **Signature verification failing**:
   - Ensure you're using the correct webhook secret
   - Check that you're verifying the raw request body without any modifications
   - Verify that you're using HMAC-SHA256 for signature verification

3. **Timeouts**:
   - Ensure your webhook handler responds within 10 seconds
   - Process webhooks asynchronously if needed

### Webhook Dashboard

You can view the status of your webhook deliveries in the [Webhook Dashboard](https://app.paissiveincome.com/dashboard/webhooks), which shows:

- Delivery attempts
- Response status codes
- Response bodies
- Error messages

### Testing Webhooks

You can test your webhook endpoint using our webhook tester:

```bash
curl -X POST https://api.paissiveincome.com/api/v1/webhooks/test \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook",
    "event_type": "payment.received"
  }'
```

This will send a test webhook event to your endpoint and return the delivery status.
