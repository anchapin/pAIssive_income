# niche_analysis_service

## Build and Run

```sh
docker build -t niche-analysis-service .
docker run --env-file .env -p 8001:8001 niche-analysis-service
```

## Development

- Entry point: `app.py`
- Config via environment variables (see `app.py`)
- Dependencies: `requirements.txt`