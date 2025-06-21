"""FastAPI application with CORS middleware, tool router, and GraphQL."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from api.routes.tool_router import router as tool_router
from api.errors import http_exception_handler
from api.routes.tool_router import api_key_auth

# GraphQL Setup
from api.graphql.schema_builder import schema
from strawberry.fastapi import GraphQLRouter
from fastapi import APIRouter

# Create FastAPI app
app = FastAPI(
    title="pAIssive Income API",
    description="API for exposing mathematical tools and other services",
    version="1.0.0",
)

# Register global HTTPException handler
app.add_exception_handler(HTTPException, http_exception_handler)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tool_router)

# Secure GraphQL endpoint using same API key auth
graphql_app = GraphQLRouter(schema)
graphql_router = APIRouter(prefix="/graphql", dependencies=[Depends(api_key_auth)])
graphql_router.include_router(graphql_app, prefix="")
app.include_router(graphql_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "pAIssive Income API is running"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
