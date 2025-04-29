# API Versioning Strategy

This document outlines the versioning strategy for the pAIssive Income API.

## Overview

The API uses a versioning strategy to ensure backward compatibility while allowing for evolution of the API. The versioning strategy follows these principles:

1. **Semantic Versioning**: API versions follow a `vX` format (e.g., `v1`, `v2`), where `X` is the major version number.
2. **URL-Based Versioning**: The version is included in the URL path (e.g., `/api/v1/niche-analysis`).
3. **Multiple Active Versions**: Multiple API versions can be active simultaneously to allow clients time to migrate.
4. **Deprecation Process**: Deprecated versions go through a sunset period before being removed.

## Version Lifecycle

API versions go through the following lifecycle:

1. **Active**: The version is fully supported and recommended for use.
2. **Deprecated**: The version is still available but will be removed in the future. Clients should migrate to a newer version.
3. **Sunset**: The version has been removed and is no longer available.

## Breaking vs. Non-Breaking Changes

Changes to the API are categorized as follows:

### Breaking Changes

Breaking changes require a new API version. Examples include:

- Removing an endpoint
- Removing a required request parameter
- Changing the type of a parameter or response field
- Changing the structure of a response
- Renaming a parameter or response field
- Changing the behavior of an endpoint in a way that affects existing clients

### Non-Breaking Changes

Non-breaking changes can be made without incrementing the API version. Examples include:

- Adding a new endpoint
- Adding an optional request parameter
- Adding new fields to a response
- Fixing bugs that don't affect the API contract
- Performance improvements

## Deprecation Process

When an API version or endpoint is deprecated:

1. The deprecation is announced with a target sunset date (typically 6 months in the future).
2. Deprecated endpoints return a `X-API-Deprecated: true` header.
3. Deprecated endpoints return a `X-API-Sunset-Date` header with the date when the endpoint will be removed.
4. Documentation is updated to indicate the deprecation.
5. After the sunset date, the deprecated version or endpoint is removed.

## Version Headers

The API includes the following version-related headers in responses:

- `X-API-Version`: The version of the API that processed the request.
- `X-API-Deprecated`: Set to `true` if the endpoint or version is deprecated.
- `X-API-Sunset-Date`: The date when the deprecated endpoint or version will be removed.

## Version Discovery

Clients can discover available API versions using the following endpoints:

- `GET /api/versions`: Returns a list of available API versions.
- `GET /api/changelog`: Returns a changelog for all API versions.
- `GET /api/changelog/{version}`: Returns a changelog for a specific API version.

## Migration Guidelines

When migrating to a new API version:

1. Review the changelog to understand the changes between versions.
2. Update client code to use the new version's endpoints and parameters.
3. Test thoroughly before deploying to production.
4. If possible, implement feature detection rather than version detection to make your client more resilient to API changes.

## Example

### URL Structure

```
/api/v1/niche-analysis/analyze  # Version 1 endpoint
/api/v2/niche-analysis/analyze  # Version 2 endpoint
```

### Version Headers

```
X-API-Version: v1
X-API-Deprecated: true
X-API-Sunset-Date: 2023-12-31T00:00:00Z
```

### Version Discovery

```json
// GET /api/versions
{
  "versions": [
    {
      "version": "v1",
      "is_latest": false,
      "is_deprecated": true,
      "sunset_date": "2023-12-31T00:00:00Z"
    },
    {
      "version": "v2",
      "is_latest": true,
      "is_deprecated": false,
      "sunset_date": null
    }
  ],
  "latest_version": "v2"
}
```

## Best Practices for API Consumers

1. Always specify the API version in your requests.
2. Check for deprecation headers in responses.
3. Plan to migrate to newer versions before the sunset date.
4. Subscribe to API announcements to stay informed about new versions and deprecations.
5. Test your application with new API versions before migrating.
