# GraphQL API Documentation

The pAIssive Income API provides a GraphQL endpoint alongside the REST API for more flexible and efficient data querying. GraphQL allows clients to request exactly the data they need, reducing over-fetching and under-fetching of data.

## GraphQL Endpoint

The GraphQL API is available at:

```
/graphql
```

## GraphiQL Interface

The GraphiQL interface is an interactive in-browser GraphQL IDE that allows you to explore the API schema and execute queries. It is available at:

```
/graphql
```

## Authentication

Authentication for GraphQL works the same way as for the REST API. You can use API keys or JWT tokens for authentication.

## Basic Usage

### Queries

Queries are used to fetch data from the API. Here's an example query to get a list of niches:

```graphql
query {
  niches(limit: 5) {
    id
    name
    description
    marketSize
    growthRate
    competitionLevel
  }
}
```

### Mutations

Mutations are used to create, update, or delete data. Here's an example mutation to create a new niche:

```graphql
mutation {
  createNicheAnalysis(input: {
    name: "AI-powered Content Generation",
    description: "Tools for generating content using AI models",
    marketSize: 5000000,
    growthRate: 25.5,
    competitionLevel: 3
  }) {
    id
    name
    description
  }
}
```

## Schema

The GraphQL schema defines the types, queries, and mutations available in the API. You can explore the schema using the GraphiQL interface.

### Main Types

- **Niche Analysis**: Types related to niche analysis, including niches, market segments, problems, and opportunities.
- **Monetization**: Types related to monetization, including subscription models, pricing tiers, and revenue projections.
- **Marketing**: Types related to marketing, including marketing strategies, content templates, and campaigns.
- **AI Models**: Types related to AI models, including model information, versions, and inference.
- **Agent Team**: Types related to agent teams, including agents, teams, and tasks.
- **User**: Types related to users, including user information, projects, and collaborations.

## Examples

### Fetching a Niche with Related Opportunities

```graphql
query {
  niche(id: "123") {
    id
    name
    description
    marketSize
    growthRate
    competitionLevel
    opportunities {
      id
      title
      description
      score
    }
  }
}
```

### Creating a Marketing Strategy

```graphql
mutation {
  createMarketingStrategy(input: {
    name: "Content Marketing Strategy",
    description: "Strategy focused on content marketing",
    targetAudience: ["Small businesses", "Startups"],
    channels: ["Blog", "Social Media", "Email"],
    goals: ["Increase brand awareness", "Generate leads"]
  }) {
    id
    name
    description
  }
}
```

### Running Model Inference

```graphql
mutation {
  runInference(input: {
    modelId: "456",
    inputData: {
      prompt: "Generate a marketing tagline for an AI-powered content generation tool"
    },
    parameters: {
      temperature: 0.7,
      maxTokens: 50
    }
  }) {
    output
    latency
    tokenUsage
  }
}
```

## Error Handling

GraphQL errors are returned in the `errors` field of the response. Each error includes a message and optional additional information.

Example error response:

```json
{
  "errors": [
    {
      "message": "Niche not found",
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ],
      "path": ["niche"]
    }
  ],
  "data": {
    "niche": null
  }
}
```

## Rate Limiting

GraphQL requests are subject to the same rate limiting as REST API requests. Rate limit information is included in the response headers.

## Batch Requests

The GraphQL API supports batch requests, allowing you to send multiple queries or mutations in a single HTTP request. This can significantly reduce the number of round trips to the server.

Example batch request:

```json
[
  {
    "query": "query { niches(limit: 5) { id name } }"
  },
  {
    "query": "query { marketingStrategies(limit: 5) { id name } }"
  }
]
```

## Introspection

The GraphQL API supports introspection, allowing clients to query the schema for information about the available types, queries, and mutations. This is useful for generating documentation and client-side code.

Example introspection query:

```graphql
{
  __schema {
    types {
      name
      description
    }
  }
}
```
