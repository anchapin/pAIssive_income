# Database Setup and Migration Guide

This document provides instructions for setting up and migrating the PostgreSQL database for the pAIssive_income project.

## Database Configuration

The project uses PostgreSQL as the database backend. The database connection is configured in `config.py` and can be overridden using environment variables.

### Default Configuration

```python
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", "postgresql://myuser:mypassword@db:5432/mydb"
)
```

### Environment Variables

- `DATABASE_URL`: The PostgreSQL connection string

## Database Models

The project uses SQLAlchemy ORM for database operations. The models are defined in `flask/models.py`:

- `User`: Represents a user of the system
- `Team`: Represents a team of AI agents
- `Agent`: Represents an AI agent that belongs to a team

## Running Migrations

Database migrations are managed using Flask-Migrate (Alembic). To run migrations:

1. Ensure the database is running
2. Run the migration script:

```bash
python run_migrations.py
```

## Initializing the Database

To initialize the database with tables and initial data:

```bash
python init_db.py
```

This will:
1. Create all tables if they don't exist
2. Create an admin user if it doesn't exist
3. Create a default team and sample agents

## Docker Compose Setup

The `docker-compose.yml` file includes a PostgreSQL service:

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

For local development, you can:

1. Use the Docker Compose setup
2. Install PostgreSQL locally and update the connection string
3. Use SQLite for testing (configured in the test fixtures)

## Backup and Restore

To backup the database:

```bash
docker exec paissive-postgres pg_dump -U myuser mydb > backup.sql
```

To restore the database:

```bash
cat backup.sql | docker exec -i paissive-postgres psql -U myuser mydb
```
