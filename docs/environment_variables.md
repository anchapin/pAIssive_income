# Environment Variables

This document describes the environment variables used in the pAIssive_income project.

## Overview

Environment variables are used to configure the application without modifying the code. They are particularly important for:

1. Storing sensitive information like API keys
2. Configuring different environments (development, testing, production)
3. Setting application behavior

## Configuration Files

The project uses several files for environment variable configuration:

- `.env`: Local environment variables (not committed to the repository)
- `.env.example`: Example environment file with placeholders (committed to the repository)
- `.cursor/mcp.json`: Environment variables for Cursor AI integration

## API Keys

The following API keys are supported in the project:

| Variable               | Description                         | Format             | Required |
| ---------------------- | ----------------------------------- | ------------------ | -------- |
| `ANTHROPIC_API_KEY`    | Anthropic API key for Claude models | `sk-ant-api03-...` | Required |
| `PERPLEXITY_API_KEY`   | Perplexity API key                  | `pplx-...`         | Optional |
| `OPENAI_API_KEY`       | OpenAI API key for GPT models       | `sk-proj-...`      | Optional |
| `GOOGLE_API_KEY`       | Google API key for Gemini models    | -                  | Optional |
| `MISTRAL_API_KEY`      | Mistral AI API key                  | -                  | Optional |
| `XAI_API_KEY`          | xAI API key                         | -                  | Optional |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key                | -                  | Optional |
| `OPENROUTER_API_KEY`   | OpenRouter API key                  | -                  | Optional |
| `OLLAMA_API_KEY`       | Ollama API key                      | -                  | Optional |

## Database Configuration

Database connection is configured using the following environment variables:

| Variable       | Description                  | Default                                       |
| -------------- | ---------------------------- | --------------------------------------------- |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://myuser:mypassword@db:5432/mydb` |
| `DB_USER`      | Database username            | -                                             |
| `DB_PASSWORD`  | Database password            | -                                             |
| `DB_HOST`      | Database host                | -                                             |

## Application Configuration

General application configuration:

| Variable    | Description                                       | Default                                        |
| ----------- | ------------------------------------------------- | ---------------------------------------------- |
| `FLASK_ENV` | Flask environment (`development` or `production`) | `development`                                  |
| `DEBUG`     | Enable debug mode                                 | `true` in development                          |
| `LOG_LEVEL` | Logging level                                     | `INFO` in development, `WARNING` in production |

## Security Configuration

Security-related environment variables:

| Variable                    | Description                                    |
| --------------------------- | ---------------------------------------------- |
| `JWT_SECRET_KEY`            | Secret key for JWT token generation            |
| `PASSWORD_RESET_SECRET_KEY` | Secret key for password reset token generation |
| `REFRESH_TOKEN_SECRET_KEY`  | Secret key for refresh token generation        |

## Service Discovery

Service discovery configuration:

| Variable                | Description                      | Default       |
| ----------------------- | -------------------------------- | ------------- |
| `SERVICE_REGISTRY_HOST` | Hostname of the service registry | `localhost`   |
| `SERVICE_REGISTRY_PORT` | Port of the service registry     | `8500`        |
| `ENVIRONMENT`           | Environment name                 | `development` |

## Performance Configuration

Performance-related environment variables:

| Variable           | Description                  | Default |
| ------------------ | ---------------------------- | ------- |
| `CACHE_EXPIRY`     | Cache expiry time in seconds | `3600`  |
| `MODEL_CACHE_SIZE` | Size of the model cache      | `10000` |
| `API_TIMEOUT`      | API timeout in seconds       | `90`    |
| `BATCH_SIZE`       | Batch size for processing    | `200`   |
| `RETRY_ATTEMPTS`   | Number of retry attempts     | `5`     |
| `RATE_LIMIT`       | Rate limit for API calls     | `100`   |

## Usage

### Local Development

For local development, create a `.env` file in the project root with your environment variables:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://localhost:5432/paissive_income_dev
FLASK_ENV=development
DEBUG=true
```

### Cursor AI Integration

For Cursor AI integration, environment variables are configured in `.cursor/mcp.json`:

```json
{
    "mcpServers": {
        "ai-assistant": {
            "env": {
                "ANTHROPIC_API_KEY": "your_anthropic_api_key_here",
                "OPENAI_API_KEY": "your_openai_api_key_here"
            }
        }
    }
}
```

### Docker Deployment

For Docker deployment, environment variables can be set in `docker-compose.yml`:

```yaml
services:
  app:
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:password@db:5432/paissive_income
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

## Best Practices

1. **Never commit real secrets** to the repository
2. **Use `.env.example`** to document required environment variables
3. **Use environment-specific files** for different environments
4. **Validate environment variables** at application startup
5. **Use a secrets management system** for production deployments

## Related Documentation

- [Deployment Guide](deployment_guide.md)
- [Cursor Integration](cursor_integration.md)
- [Security Guide](security.md)
