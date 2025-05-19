# ai_models_service

## Build and Run

```sh
docker build -t ai-models-service .
docker run --env-file .env -p 8000:8000 ai-models-service
```

## Development

- Entry point: `app.py`
- Config via environment variables (see `app.py`)
- Dependencies: `requirements.txt`