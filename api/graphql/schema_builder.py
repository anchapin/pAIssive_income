"""Builds the Strawberry GraphQL schema for math tools."""

from __future__ import annotations

import strawberry

from api.graphql.schemas.math_schema import Query

schema = strawberry.Schema(query=Query)