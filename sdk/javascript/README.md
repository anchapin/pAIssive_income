# pAIssive Income JavaScript SDK

This package provides a JavaScript client for the pAIssive Income API, allowing you to interact with all available API endpoints from your JavaScript applications.

## Installation

You can install the package via npm:

```bash
npm install paissive-income-sdk
```

Or using yarn:

```bash
yarn add paissive-income-sdk
```

## Usage

### Authentication

The SDK supports two authentication methods:

#### API Key Authentication

```javascript
const { Client, auth } = require('paissive-income-sdk');

// Create a client with API key authentication
const client = new Client({
  auth: new auth.APIKeyAuth('your-api-key')
});
```

#### JWT Authentication

```javascript
const { Client, auth } = require('paissive-income-sdk');

// Create a client with JWT authentication
const client = new Client({
  auth: new auth.JWTAuth('your-jwt-token')
});
```

### Examples

#### Niche Analysis

```javascript
const { Client, auth } = require('paissive-income-sdk');

// Create a client
const client = new Client({
  auth: new auth.APIKeyAuth('your-api-key')
});

// Get market segments
async function getMarketSegments() {
  try {
    const segments = await client.nicheAnalysis.getMarketSegments();
    console.log(segments);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Analyze niches
async function analyzeNiches() {
  try {
    const analysisResults = await client.nicheAnalysis.analyzeNiches(['segment-id-1', 'segment-id-2']);
    console.log(analysisResults);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Call the functions
getMarketSegments();
analyzeNiches();
```

#### Monetization

```javascript
// Create a subscription model
async function createSubscriptionModel() {
  try {
    const subscriptionModel = await client.monetization.createSubscriptionModel({
      name: "Premium Plan",
      description: "Premium access to all features",
      tiers: [
        {
          name: "Basic",
          price: 9.99,
          billing_period: "monthly"
        },
        {
          name: "Pro",
          price: 19.99,
          billing_period: "monthly"
        }
      ],
      features: [
        {
          name: "Basic Access",
          description: "Access to basic features",
          tiers: ["Basic", "Pro"]
        },
        {
          name: "Premium Support",
          description: "24/7 support",
          tiers: ["Pro"]
        }
      ]
    });
    
    console.log(subscriptionModel);
  } catch (error) {
    console.error('Error:', error.message);
  }
}
```

#### AI Models

```javascript
// Run inference with an AI model
async function runInference() {
  try {
    const result = await client.aiModels.runInference({
      model_id: "gpt2",
      inputs: "What is artificial intelligence?",
      parameters: {
        max_tokens: 100,
        temperature: 0.7
      }
    });
    
    console.log(result);
  } catch (error) {
    console.error('Error:', error.message);
  }
}
```

#### User Management

```javascript
// Register a new user
async function registerAndLogin() {
  try {
    // Register
    const user = await client.user.register({
      username: "john_doe",
      email: "john.doe@example.com",
      password: "secure_password123"
    });
    
    // Login
    const loginResult = await client.user.login({
      email: "john.doe@example.com",
      password: "secure_password123"
    });
    
    // Get JWT token from login result
    const token = loginResult.token;
    
    // Create a new client with the JWT token
    const authenticatedClient = new Client({
      auth: new auth.JWTAuth(token)
    });
    
    // Get user profile
    const profile = await authenticatedClient.user.getProfile();
    console.log(profile);
  } catch (error) {
    console.error('Error:', error.message);
  }
}
```

## Usage in a Browser Environment

To use the SDK in a browser environment, you'll need to use a bundler like Webpack or Rollup:

```javascript
import { Client, auth } from 'paissive-income-sdk';

const client = new Client({
  auth: new auth.APIKeyAuth('your-api-key')
});

// Use the client as shown in the examples above
```

## API Reference

The SDK provides access to all pAIssive Income API endpoints through the following services:

- `client.nicheAnalysis` - Niche Analysis service
- `client.monetization` - Monetization service
- `client.marketing` - Marketing service
- `client.aiModels` - AI Models service
- `client.agentTeam` - Agent Team service
- `client.user` - User service
- `client.dashboard` - Dashboard service
- `client.apiKeys` - API Key service

For detailed documentation of all available methods, please refer to the [API Reference](https://paissiveincome.example.com/docs/api).

## License

[MIT License](https://opensource.org/licenses/MIT)