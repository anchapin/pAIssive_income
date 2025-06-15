# Database Setup and Migration Guide

This guide provides instructions for setting up and migrating the PostgreSQL database for the project.

## Configuration

The project uses PostgreSQL as the backend database. Connection configuration is in `config.py` and may be overridden by environment variables.

### Default Connection

```python
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", "postgresql://myuser:mypassword@db:5432/mydb"
)
```

- `DATABASE_URL`: PostgreSQL connection string

## Database Models

Models are defined in `flask/models.py`:
- **User**: System user
- **Team**: AI agent teams
- **Agent**: AI agent (belongs to a team)

## Migrations

Migrations are managed with Flask-Migrate (Alembic):

1. Ensure database is running
2. Run migrations:

```bash
python run_migrations.py
```

## Initialization

To initialize with tables and seed data:

```bash
python init_db.py
```

- Creates tables if missing
- Creates admin user (if needed)
- Creates default team/sample agents

## Docker Compose

`docker-compose.yml` includes a PostgreSQL service:

```yaml
db:
  image: postgres:15-alpine
  container_name: paissive-postgres
  restart: unless-stopped
  ports:
    - "5432:5432"
  volumes:
    - postgres-data:/var/lib/postgresql/data
  environment:
    - POSTGRES_USER=myuser
    - POSTGRES_PASSWORD=mypassword
    - POSTGRES_DB=mydb
```

## Development Setup

- Use Docker Compose (recommended)
- Or install PostgreSQL locally and update connection string
- SQLite may be used for testing (see test fixtures)

## Backup and Restore

Backup:

```bash
docker exec paissive-postgres pg_dump -U myuser mydb > backup.sql
```

Restore:

```bash
cat backup.sql | docker exec -i paissive-postgres psql -U myuser mydb
```