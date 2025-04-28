# Database Service Design

## Overview

The Database Service acts as a centralized data access layer for all microservices in the pAIssive income platform. It provides a unified interface for database operations, abstracts underlying database technologies, and ensures consistent data access patterns across the system.

## Responsibilities

- Provide unified database access for all microservices
- Support multiple database technologies (SQL and NoSQL)
- Handle database connections and connection pooling
- Implement data access patterns (repository, unit of work)
- Manage database migrations and schema evolution
- Monitor database performance and health
- Implement data caching strategies
- Handle data partitioning and sharding
- Enforce data access security and permissions
- Support transactional operations

## API Design

### External API (Service-to-Service)

#### Generic Data Operations
- `POST /api/db/{collection}` - Create a document
- `GET /api/db/{collection}/{id}` - Get a document by ID
- `GET /api/db/{collection}` - Query documents (with filters)
- `PUT /api/db/{collection}/{id}` - Update a document
- `DELETE /api/db/{collection}/{id}` - Delete a document
- `POST /api/db/transaction` - Execute a transaction

#### Query Operations
- `POST /api/db/{collection}/query` - Execute a complex query
- `GET /api/db/{collection}/count` - Count documents
- `POST /api/db/{collection}/aggregate` - Aggregate query
- `POST /api/db/search` - Full-text search across collections

#### Schema Management
- `GET /api/db/schema/{collection}` - Get collection schema
- `POST /api/db/migrations` - Execute a migration
- `GET /api/db/migrations` - List migrations
- `GET /api/db/migrations/status` - Get migration status

#### Database Monitoring
- `GET /api/db/stats` - Get database statistics
- `GET /api/db/health` - Get health status
- `GET /api/db/performance` - Get performance metrics
- `GET /api/db/connections` - Get connection statistics

## Technology Stack

- **Framework**: FastAPI
- **Database Adapters**: 
  - MongoDB for document storage
  - PostgreSQL for relational data
  - Redis for caching
- **ORM/ODM**: SQLAlchemy for SQL, Motor for MongoDB
- **Migration Tools**: Alembic for SQL migrations
- **Connection Pooling**: Built-in connection pooling
- **Monitoring**: Prometheus integration
- **Caching**: Redis-based caching layer

## Service Dependencies

- None (Database Service is a foundational service)

## Data Model

### Database Configuration
```
{
  "name": "string",
  "type": "mongodb|postgresql|redis",
  "connection_string": "string",
  "pool_settings": {
    "min_connections": int,
    "max_connections": int,
    "timeout_seconds": int
  },
  "read_preference": "primary|secondary|nearest",
  "write_concern": "string",
  "replicas": [
    {
      "host": "string",
      "port": int,
      "role": "primary|secondary|analytics"
    }
  ]
}
```

### Collection/Table Schema
```
{
  "name": "string",
  "database": "string",
  "fields": [
    {
      "name": "string",
      "type": "string",
      "required": boolean,
      "default_value": "any",
      "constraints": ["string"]
    }
  ],
  "indexes": [
    {
      "name": "string",
      "fields": ["string"],
      "unique": boolean
    }
  ],
  "partitioning": {
    "strategy": "string",
    "key": "string"
  },
  "security": {
    "access_control": "string"
  }
}
```

### Migration
```
{
  "id": "string",
  "name": "string",
  "created_at": "datetime",
  "executed_at": "datetime",
  "status": "pending|executing|completed|failed",
  "database": "string",
  "collection_or_table": "string",
  "description": "string",
  "version": "string",
  "script": "string",
  "dependencies": ["string"]
}
```

### Query Execution Stats
```
{
  "query_id": "string",
  "timestamp": "datetime",
  "service_name": "string",
  "collection": "string",
  "operation_type": "find|insert|update|delete|aggregate",
  "execution_time_ms": float,
  "documents_processed": int,
  "index_used": boolean,
  "query_pattern": "string",
  "success": boolean,
  "error_message": "string"
}
```

## Sequence Diagrams

### Data Access Flow

```
┌──────────────┐     ┌───────────────┐     ┌───────────────┐     ┌────────────┐
│Client Service│     │Database Service│     │Connection Pool│     │Database    │
└──────┬───────┘     └───────┬───────┘     └───────┬───────┘     └─────┬──────┘
       │                     │                     │                   │
       │ Data Request        │                     │                   │
       │───────────────────> │                     │                   │
       │                     │                     │                   │
       │                     │ Validate Request    │                   │
       │                     │─────┐               │                   │
       │                     │     │               │                   │
       │                     │<────┘               │                   │
       │                     │                     │                   │
       │                     │ Get Connection      │                   │
       │                     │────────────────────>│                   │
       │                     │                     │                   │
       │                     │ Return Connection   │                   │
       │                     │<────────────────────│                   │
       │                     │                     │                   │
       │                     │ Execute Query       │                   │
       │                     │───────────────────────────────────────> │
       │                     │                     │                   │
       │                     │ Query Results       │                   │
       │                     │<─────────────────────────────────────── │
       │                     │                     │                   │
       │                     │ Release Connection  │                   │
       │                     │────────────────────>│                   │
       │                     │                     │                   │
       │                     │ Connection Released │                   │
       │                     │<────────────────────│                   │
       │                     │                     │                   │
       │ Data Response       │                     │                   │
       │<─────────────────── │                     │                   │
       │                     │                     │                   │
```

### Transaction Flow

```
┌──────────────┐     ┌───────────────┐     ┌────────────┐
│Client Service│     │Database Service│     │Database    │
└──────┬───────┘     └───────┬───────┘     └─────┬──────┘
       │                     │                   │
       │ Begin Transaction   │                   │
       │───────────────────> │                   │
       │                     │                   │
       │                     │ Start Transaction │
       │                     │──────────────────>│
       │                     │                   │
       │                     │ Transaction ID    │
       │                     │<──────────────────│
       │                     │                   │
       │ Transaction ID      │                   │
       │<─────────────────── │                   │
       │                     │                   │
       │ Operation 1         │                   │
       │ (with txn_id)       │                   │
       │───────────────────> │                   │
       │                     │                   │
       │                     │ Execute in Txn    │
       │                     │──────────────────>│
       │                     │                   │
       │                     │ Result 1          │
       │                     │<──────────────────│
       │                     │                   │
       │ Result 1            │                   │
       │<─────────────────── │                   │
       │                     │                   │
       │ Operation 2         │                   │
       │ (with txn_id)       │                   │
       │───────────────────> │                   │
       │                     │                   │
       │                     │ Execute in Txn    │
       │                     │──────────────────>│
       │                     │                   │
       │                     │ Result 2          │
       │                     │<──────────────────│
       │                     │                   │
       │ Result 2            │                   │
       │<─────────────────── │                   │
       │                     │                   │
       │ Commit Transaction  │                   │
       │───────────────────> │                   │
       │                     │                   │
       │                     │ Commit            │
       │                     │──────────────────>│
       │                     │                   │
       │                     │ Committed         │
       │                     │<──────────────────│
       │                     │                   │
       │ Commit Confirmed    │                   │
       │<─────────────────── │                   │
       │                     │                   │
```

## Scaling Considerations

- Read replicas for read-heavy workloads
- Write sharding for high write volumes
- Connection pooling optimization
- Query optimization and monitoring
- Data partitioning strategies
- Caching frequently accessed data
- Asynchronous operations for non-critical writes
- Database-specific scaling strategies
- Circuit breakers for database protection

## Monitoring and Logging

- Query execution times and patterns
- Connection pool utilization
- Database CPU, memory, and disk usage
- Slow query detection and logging
- Error rate monitoring
- Cache hit/miss rates
- Transaction success/failure rates
- Query volume by service
- Database capacity planning metrics
- Replication lag monitoring

## Security Considerations

- Connection string encryption
- Data access permissions by service
- Query injection prevention
- Data encryption at rest and in transit
- Audit logging for data modifications
- Rate limiting for expensive queries
- Parameterized queries enforcement
- Database credential management
- Regular security audits
- Sanitization of data inputs

## Implementation Plan

1. Port existing database abstraction layer to the microservice
2. Implement core CRUD operations
3. Add transaction support
4. Implement connection pooling
5. Create schema migration tools
6. Add performance monitoring
7. Implement caching strategies
8. Add security and access control
9. Create data partitioning strategies
10. Add support for additional database technologies