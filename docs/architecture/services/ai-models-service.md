# AI Models Service Design

## Overview

The AI Models Service manages all interactions with AI models in the pAIssive income platform. It handles model inference, versioning, fallbacks, performance monitoring, and batch processing. This service abstracts the complexity of working with different AI models and providers, offering a unified API for other services.

## Responsibilities

- Provide AI model inference capabilities
- Manage model versions and compatibility
- Implement fallback strategies for model availability
- Monitor model performance and usage metrics
- Support batch inference for efficiency
- Manage model downloads and caching
- Optimize model usage and cost

## API Design

### External API (Service-to-Service)

#### Model Management
- `GET /api/models` - List available models
- `GET /api/models/{model_id}` - Get model details
- `GET /api/models/{model_id}/versions` - List versions of a model
- `GET /api/models/{model_id}/metrics` - Get model performance metrics
- `POST /api/models/download` - Trigger model download

#### Inference
- `POST /api/inference/text` - Generate text using specified model
- `POST /api/inference/analyze` - Analyze provided text
- `POST /api/inference/batch` - Process batch inference requests
- `GET /api/inference/jobs/{job_id}` - Get status of async inference job

#### Performance Monitoring
- `GET /api/metrics` - Get service metrics
- `GET /api/metrics/models/{model_id}` - Get specific model metrics
- `GET /api/metrics/usage` - Get token usage statistics
- `GET /api/metrics/cost` - Get cost projections and usage

## Technology Stack

- **Framework**: FastAPI
- **Runtime**: Python with asyncio
- **Model Management**: Hugging Face Transformers, OpenAI SDK
- **Caching**: Redis for response caching
- **Storage**: S3-compatible storage for model artifacts
- **Monitoring**: Prometheus metrics, custom monitoring dashboard
- **Message Queue**: RabbitMQ for batch processing

## Service Dependencies

- **Database Service** - For storing model metadata and metrics
- **Message Queue** - For async and batch processing
- **API Gateway** - For external request routing

## Data Model

### Model
```
{
  "model_id": "string",
  "name": "string",
  "provider": "string",
  "capabilities": ["text-generation", "embedding", "etc"],
  "versions": [
    {
      "version": "string",
      "created_at": "datetime",
      "deprecated": boolean,
      "default": boolean,
      "configuration": {}
    }
  ],
  "parameters": {
    "max_tokens": int,
    "supported_languages": ["en", "fr", "etc"],
    "other_parameters": {}
  },
  "fallbacks": ["model_id_1", "model_id_2"]
}
```

### Inference Request
```
{
  "model_id": "string",
  "version": "string",  // optional, uses default if not specified
  "input": "string",
  "parameters": {
    "temperature": float,
    "max_tokens": int,
    "other_parameters": {}
  },
  "use_fallbacks": boolean
}
```

### Performance Metrics
```
{
  "model_id": "string",
  "version": "string",
  "period": "string",  // e.g., "daily", "hourly"
  "metrics": {
    "requests_count": int,
    "tokens_input": int,
    "tokens_output": int,
    "avg_response_time_ms": float,
    "error_rate": float,
    "fallback_rate": float,
    "estimated_cost": float
  }
}
```

## Sequence Diagrams

### Model Inference Flow

```
┌──────────────┐     ┌───────────────┐     ┌──────────────────┐     ┌──────────────┐
│Client Service│     │ AI Models Svc │     │ Model Manager    │     │ AI Provider  │
└──────┬───────┘     └───────┬───────┘     └────────┬─────────┘     └──────┬───────┘
       │                     │                      │                      │
       │  Inference Request  │                      │                      │
       │────────────────────>│                      │                      │
       │                     │                      │                      │
       │                     │   Get Model Config   │                      │
       │                     │─────────────────────>│                      │
       │                     │                      │                      │
       │                     │   Return Config      │                      │
       │                     │<─────────────────────│                      │
       │                     │                      │                      │
       │                     │                      │  Provider API Call   │
       │                     │─────────────────────────────────────────────>
       │                     │                      │                      │
       │                     │                      │  Provider Response   │
       │                     │<─────────────────────────────────────────────
       │                     │                      │                      │
       │                     │ Cache Result (if     │                      │
       │                     │ applicable)          │                      │
       │                     │─────────┐            │                      │
       │                     │         │            │                      │
       │                     │<────────┘            │                      │
       │                     │                      │                      │
       │  Inference Response │                      │                      │
       │<────────────────────│                      │                      │
       │                     │                      │                      │
       │                     │ Log Metrics          │                      │
       │                     │─────────┐            │                      │
       │                     │         │            │                      │
       │                     │<────────┘            │                      │
```

### Fallback Flow

```
┌──────────────┐     ┌───────────────┐     ┌──────────────────┐    ┌───────────────┐
│Client Service│     │ AI Models Svc │     │ Primary Provider │    │Fallback Provider│
└──────┬───────┘     └───────┬───────┘     └────────┬─────────┘    └───────┬────────┘
       │                     │                      │                      │
       │  Inference Request  │                      │                      │
       │────────────────────>│                      │                      │
       │                     │                      │                      │
       │                     │      API Call        │                      │
       │                     │─────────────────────>│                      │
       │                     │                      │                      │
       │                     │   Error/Timeout      │                      │
       │                     │<─────────────────────│                      │
       │                     │                      │                      │
       │                     │ Activate Fallback    │                      │
       │                     │─────────────────────────────────────────────>
       │                     │                      │                      │
       │                     │    API Response      │                      │
       │                     │<─────────────────────────────────────────────
       │                     │                      │                      │
       │  Inference Response │                      │                      │
       │<────────────────────│                      │                      │
       │                     │                      │                      │
```

## Scaling Considerations

- Horizontal scaling based on inference demand
- Consideration for specialized hardware (GPUs)
- Model caching for frequently used models
- Prioritization of requests based on importance
- Batch processing for non-interactive requests
- Efficient resource allocation across models

## Monitoring and Logging

- Model usage metrics (requests, tokens, response times)
- Error rates per model and provider
- Fallback activation frequency
- Cost monitoring and projections
- Cache hit/miss rates
- Model download/update status

## Security Considerations

- API keys for provider services stored securely
- Input validation to prevent prompt injection
- Rate limiting for expensive operations
- Content filtering for sensitive outputs
- Access control for model operations

## Implementation Plan

1. Port existing AI model components to the microservice
2. Implement core inference APIs
3. Add model versioning and management
4. Implement fallback mechanisms
5. Add performance monitoring and metrics
6. Set up batch processing capabilities
7. Implement model caching and optimizations
