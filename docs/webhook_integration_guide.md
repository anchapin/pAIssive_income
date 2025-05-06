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

**PHP**:
```php
function verifyWebhookSignature($payload, $signature, $secret) {
    $expectedSignature = base64_encode(
        hash_hmac('sha256', $payload, $secret, true)
    );

    return hash_equals($expectedSignature, $signature);
}

// In your webhook handler:
$payload = file_get_contents('php://input');
$signature = $_SERVER['HTTP_X_WEBHOOK_SIGNATURE'];

if (!verifyWebhookSignature($payload, $signature, 'your_webhook_secret')) {
    http_response_code(401);
    exit('Invalid signature');
}
```

**Ruby**:
```ruby
require 'openssl'
require 'base64'

def verify_webhook_signature(payload, signature, secret)
  expected_signature = Base64.strict_encode64(
    OpenSSL:HMAC.digest('SHA256', secret, payload)
  )

  ActiveSupport:SecurityUtils.secure_compare(
    expected_signature,
    signature
  )
end

# In your webhook handler:
signature = request.headers['X-Webhook-Signature']
payload = request.raw_post

unless verify_webhook_signature(payload, signature, 'your_webhook_secret')
  halt 401, 'Invalid signature'
end
```

**Go**:
```go
import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/base64"
    "crypto/subtle"
)

func verifyWebhookSignature(payload []byte, signature, secret string) bool {
    mac := hmac.New(sha256.New, []byte(secret))
    mac.Write(payload)
    expectedSignature := base64.StdEncoding.EncodeToString(mac.Sum(nil))

    return subtle.ConstantTimeCompare(
        []byte(expectedSignature),
        []byte(signature),
    ) == 1
}

// In your webhook handler:
func webhookHandler(w http.ResponseWriter, r *http.Request) {
    payload, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, "Error reading body", http.StatusBadRequest)
        return
    }

    signature := r.Header.Get("X-Webhook-Signature")
    if !verifyWebhookSignature(payload, signature, "your_webhook_secret") {
        http.Error(w, "Invalid signature", http.StatusUnauthorized)
        return
    }
    // Process the webhook...
}
```

**Java**:
```java
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;
import java.security.MessageDigest;

public class WebhookVerifier {
    public static boolean verifyWebhookSignature(
        String payload,
        String signature,
        String secret
    ) {
        try {
            Mac sha256Hmac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKey = new SecretKeySpec(
                secret.getBytes("UTF-8"),
                "HmacSHA256"
            );
            sha256Hmac.init(secretKey);

            String expectedSignature = Base64.getEncoder()
                .encodeToString(sha256Hmac.doFinal(
                    payload.getBytes("UTF-8")
                ));

            return MessageDigest.isEqual(
                expectedSignature.getBytes(),
                signature.getBytes()
            );
        } catch (Exception e) {
            return false;
        }
    }
}

// In your webhook handler:
@PostMapping("/webhook")
public ResponseEntity<?> handleWebhook(
    @RequestBody String payload,
    @RequestHeader("X-Webhook-Signature") String signature
) {
    if (!WebhookVerifier.verifyWebhookSignature(
        payload,
        signature,
        "your_webhook_secret"
    )) {
        return ResponseEntity.status(401).body("Invalid signature");
    }
    // Process the webhook...
    return ResponseEntity.ok().build();
}
```

**C#**:
```csharp
using System;
using System.Security.Cryptography;
using System.Text;

public class WebhookVerifier
{
    public static bool VerifyWebhookSignature(
        string payload,
        string signature,
        string secret)
    {
        using (var hmac = new HMACSHA256(
            Encoding.UTF8.GetBytes(secret)))
        {
            var expectedSignature = Convert.ToBase64String(
                hmac.ComputeHash(Encoding.UTF8.GetBytes(payload))
            );

            return CryptographicOperations.FixedTimeEquals(
                Convert.FromBase64String(expectedSignature),
                Convert.FromBase64String(signature)
            );
        }
    }
}

// In your webhook handler:
[HttpPost]
public IActionResult Webhook(
    [FromBody] string payload,
    [FromHeader(Name = "X-Webhook-Signature")] string signature)
{
    if (!WebhookVerifier.VerifyWebhookSignature(
        payload,
        signature,
        "your_webhook_secret"))
    {
        return Unauthorized("Invalid signature");
    }
    // Process the webhook...
    return Ok();
}
```

### IP Allowlisting

For additional security, we recommend configuring your firewall to only accept webhook requests from our IP addresses:

- `192.0.2.1`
- `192.0.2.2`
- `192.0.2.3`
- `192.0.2.4`

### Managing Security Settings

Here are examples of how to manage webhook security settings in different languages:

**Python (using requests)**:
```python
import requests

def configure_ip_allowlist(webhook_id, allowed_ips, api_key):
    response = requests.put(
        f"https://api.paissiveincome.com/api/v1/webhooks/{webhook_id}/security/ip-allowlist",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "allowed_ips": allowed_ips,
            "enabled": True
        }
    )
    return response.json()

def rotate_webhook_secret(webhook_id, api_key):
    response = requests.post(
        f"https://api.paissiveincome.com/api/v1/webhooks/{webhook_id}/security/rotate-secret",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    return response.json()

def configure_rate_limits(webhook_id, per_minute, per_hour, api_key):
    response = requests.put(
        f"https://api.paissiveincome.com/api/v1/webhooks/{webhook_id}/security/rate-limits",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "per_minute": per_minute,
            "per_hour": per_hour
        }
    )
    return response.json()

# Example usage:
api_key = "your_api_key"
webhook_id = "webhook-123"

# Configure IP allowlist
allowlist_response = configure_ip_allowlist(
    webhook_id,
    ["203.0.113.1", "203.0.113.0/24"],
    api_key
)

# Rotate webhook secret
rotation_response = rotate_webhook_secret(webhook_id, api_key)
new_secret = rotation_response["new_secret"]
old_secret_expiry = rotation_response["old_secret_expiry"]

# Configure rate limits
rate_limit_response = configure_rate_limits(
    webhook_id,
    per_minute=200,
    per_hour=2000,
    api_key
)
```

**Node.js (using axios)**:
```javascript
const axios = require('axios');

class WebhookSecurityManager {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.client = axios.create({
      baseURL: 'https://api.paissiveincome.com/api/v1',
      headers: { Authorization: `Bearer ${apiKey}` }
    });
  }

  async configureIpAllowlist(webhookId, allowedIps) {
    const response = await this.client.put(
      `/webhooks/${webhookId}/security/ip-allowlist`,
      {
        allowed_ips: allowedIps,
        enabled: true
      }
    );
    return response.data;
  }

  async rotateWebhookSecret(webhookId) {
    const response = await this.client.post(
      `/webhooks/${webhookId}/security/rotate-secret`
    );
    return response.data;
  }

  async configureRateLimits(webhookId, perMinute, perHour) {
    const response = await this.client.put(
      `/webhooks/${webhookId}/security/rate-limits`,
      {
        per_minute: perMinute,
        per_hour: perHour
      }
    );
    return response.data;
  }
}

// Example usage:
async function manageWebhookSecurity() {
  const manager = new WebhookSecurityManager('your_api_key');
  const webhookId = 'webhook-123';

  try {
    // Configure IP allowlist
    const allowlistResponse = await manager.configureIpAllowlist(
      webhookId,
      ['203.0.113.1', '203.0.113.0/24']
    );
    console.log('IP allowlist configured:', allowlistResponse);

    // Rotate webhook secret
    const rotationResponse = await manager.rotateWebhookSecret(webhookId);
    console.log(
      'New secret:', rotationResponse.new_secret,
      'Old secret expires:', rotationResponse.old_secret_expiry
    );

    // Configure rate limits
    const rateLimitResponse = await manager.configureRateLimits(
      webhookId,
      200, // per minute
      2000 // per hour
    );
    console.log('Rate limits configured:', rateLimitResponse);
  } catch (error) {
    console.error('Error managing webhook security:', error);
  }
}
```

These examples show how to:
1. Configure IP allowlisting to restrict which IP addresses can send webhooks
2. Rotate webhook secrets for security maintenance
3. Configure custom rate limits for high-volume webhook endpoints

Remember to:
- Update your webhook handlers when rotating secrets (the old secret remains valid for 7 days)
- Set appropriate rate limits based on your expected webhook volume
- Keep your API keys secure and never expose them in client-side code

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
