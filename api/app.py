"""Main FastAPI app for pAIssive Income API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.tool_router import router as tool_router

app = FastAPI(
    title="pAIssive Income API",
    description="RESTful API endpoints for agent-accessible tools and core services.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for development purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to the specific allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(tool_router)
