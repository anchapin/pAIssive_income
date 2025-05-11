# pAIssive Income Python SDK

This package provides a Python client for the pAIssive Income API, allowing you to interact with all available API endpoints from your Python applications.

## Installation

You can install the package via pip:

```bash
pip install paissive_income_sdk
```

## Usage

### Authentication

The SDK supports two authentication methods:

#### API Key Authentication

```python
from paissive_income_sdk import Client
from paissive_income_sdk.auth import APIKeyAuth

# Create a client with API key authentication
client = Client(auth=APIKeyAuth(api_key="your-api-key"))
```

#### JWT Authentication

```python
from paissive_income_sdk import Client
from paissive_income_sdk.auth import JWTAuth

# Create a client with JWT authentication
client = Client(auth=JWTAuth(token="your-jwt-token"))
```

### Examples

#### Niche Analysis

```python
from paissive_income_sdk import Client
from paissive_income_sdk.auth import APIKeyAuth

# Create a client
client = Client(auth=APIKeyAuth(api_key="your-api-key"))

# Get market segments
segments = client.niche_analysis.get_market_segments()
print(segments)

# Analyze niches
analysis_results = client.niche_analysis.analyze_niches(["segment-id-1", "segment-id-2"])
print(analysis_results)
```

#### Monetization

```python
# Create a subscription model
subscription_model = client.monetization.create_subscription_model({
    "name": "Premium Plan",
    "description": "Premium access to all features",
    "tiers": [
        {
            "name": "Basic",
            "price": 9.99,
            "billing_period": "monthly"
        },
        {
            "name": "Pro",
            "price": 19.99,
            "billing_period": "monthly"
        }
    ],
    "features": [
        {
            "name": "Basic Access",
            "description": "Access to basic features",
            "tiers": ["Basic", "Pro"]
        },
        {
            "name": "Premium Support",
            "description": "24/7 support",
            "tiers": ["Pro"]
        }
    ]
})
```

#### AI Models

```python
# Run inference with an AI model
result = client.ai_models.run_inference({
    "model_id": "gpt2",
    "inputs": "What is artificial intelligence?",
    "parameters": {
        "max_tokens": 100,
        "temperature": 0.7
    }
})
print(result)
```

#### User Management

```python
# Register a new user
user = client.user.register({
    "username": "john_doe",
    "email": "john.doe@example.com",
    "password": "example_password_123"
})

# Log in
login_result = client.user.login({
    "email": "john.doe@example.com",
    "password": "example_password_123"
})

# Get JWT token from login result
token = login_result["token"]

# Create a new client with the JWT token
client = Client(auth=JWTAuth(token=token))

# Get user profile
profile = client.user.get_profile()
print(profile)
```

## API Reference

The SDK provides access to all pAIssive Income API endpoints through the following services:

- `client.niche_analysis` - Niche Analysis service
- `client.monetization` - Monetization service
- `client.marketing` - Marketing service
- `client.ai_models` - AI Models service
- `client.agent_team` - Agent Team service
- `client.user` - User service
- `client.dashboard` - Dashboard service
- `client.api_keys` - API Key service

For detailed documentation of all available methods, please refer to the [API Reference](https://paissiveincome.example.com/docs/api).

## License

[MIT License](https://opensource.org/licenses/MIT)
