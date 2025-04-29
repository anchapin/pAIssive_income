# API Query Parameters Guide

This guide explains how to use pagination, filtering, and sorting in the pAIssive Income API.

## Pagination

All collection endpoints support pagination using the following parameters:

- `page`: Page number (1-based, default: 1)
- `page_size`: Number of items per page (default: 10, max: 100)

Example:
```
GET /api/v1/niche-analysis/niches?page=2&page_size=20
```

## Sorting

Collection endpoints support sorting using the following parameters:

- `sort_by`: Field to sort by
- `sort_dir`: Sort direction (`asc` or `desc`, default: `asc`)

Example:
```
GET /api/v1/niche-analysis/niches?sort_by=opportunity_score&sort_dir=desc
```

Each endpoint has a specific set of fields that can be used for sorting. Common sortable fields include:

- `name`: Sort by name
- `created_at`: Sort by creation date
- `updated_at`: Sort by update date

Endpoint-specific sortable fields:
- Niches: `opportunity_score`, `market_segment`
- Subscription Models: `type`, `price`
- Marketing Campaigns: `status`, `start_date`, `end_date`
- AI Models: `type`, `size`
- Agents: `role`, `status`
- Users: `username`, `email`, `last_login`

## Filtering

Collection endpoints support filtering using two approaches:

### 1. Simple Filtering

Simple filtering uses dedicated query parameters for common filters:

Example:
```
GET /api/v1/niche-analysis/niches?segment=Content%20Creation&min_score=0.8
```

### 2. Advanced Filtering

Advanced filtering uses a more flexible syntax for complex filters:

```
GET /api/v1/niche-analysis/niches?filter[name][contains]=AI&filter[opportunity_score][gte]=0.8
```

The general format is:
```
filter[field][operator]=value
```

Available operators:
- `eq`: Equal (default if operator is omitted)
- `neq`: Not equal
- `gt`: Greater than
- `gte`: Greater than or equal
- `lt`: Less than
- `lte`: Less than or equal
- `contains`: Contains (string)
- `startswith`: Starts with (string)
- `endswith`: Ends with (string)
- `in`: In list (comma-separated values)
- `notin`: Not in list (comma-separated values)

Example with multiple filters:
```
GET /api/v1/niche-analysis/niches?filter[market_segment]=Content%20Creation&filter[opportunity_score][gte]=0.8&filter[name][contains]=AI
```

## Combining Parameters

You can combine pagination, sorting, and filtering parameters:

```
GET /api/v1/niche-analysis/niches?page=2&page_size=20&sort_by=opportunity_score&sort_dir=desc&filter[market_segment]=Content%20Creation
```

## Response Format

All collection endpoints return a paginated response with the following structure:

```json
{
  "items": [...],  // Array of items for the current page
  "total": 42,     // Total number of items (across all pages)
  "page": 2,       // Current page number
  "page_size": 20, // Number of items per page
  "pages": 3       // Total number of pages
}
```
