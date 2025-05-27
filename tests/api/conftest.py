"""Fixtures for API tests."""

import pytest
from fastapi import Depends, FastAPI, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr, Field

# Create a mock FastAPI app for testing
mock_app = FastAPI()

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Mock user database
USERS_DB = {
    "testuser": {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "hashed_password": "hashed_test-password-123",
        "is_active": True,
    }
}

# Mock token database
TOKENS_DB = {
    "validtoken": {"user_id": 1, "exp": 9999999999},
    "expiredtoken": {"user_id": 1, "exp": 1000000000},
    "nonadmintoken": {"user_id": 2, "exp": 9999999999},
}

# Mock refresh tokens
REFRESH_TOKENS = {
    "validrefreshtoken": {"user_id": 1, "exp": 9999999999},
    "expiredtoken": {"user_id": 1, "exp": 1000000000},
}

# Rate limiting counters
RATE_LIMITS = {
    "counter": 0,
    "reset_at": 9999999999,
    "revoked_tokens": set()  # Set to store revoked tokens
}


# Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr = None


class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Dependency to get current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Handle empty or malformed tokens
    if not token or token == "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token is revoked
    if token in RATE_LIMITS["revoked_tokens"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Handle known test tokens
    if token == "invalidtoken":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token == "expiredtoken":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token is valid and not expired
    if token not in TOKENS_DB and token != "validtoken":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token in TOKENS_DB and TOKENS_DB[token]["exp"] < 9999999999:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # For test token "validtoken", return a test user
    if token == "validtoken":
        return {
            "id": 999,
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True,
        }

    # Get user data for real tokens
    user_id = TOKENS_DB[token]["user_id"]
    for username, user_data in USERS_DB.items():
        if user_data["id"] == user_id:
            return user_data

    raise HTTPException(status_code=404, detail="User not found")


# Rate limiting middleware
@mock_app.middleware("http")
async def rate_limit_middleware(request, call_next):
    import time

    # Check if it's time to reset the counter
    current_time = int(time.time())
    if current_time > RATE_LIMITS.get("reset_at", 0):
        RATE_LIMITS["counter"] = 0
        RATE_LIMITS["reset_at"] = current_time + 60  # Reset after 60 seconds

    # For token management API tests, don't increment the counter
    # This is to prevent rate limiting from interfering with token tests
    if request.url.path.startswith("/auth/") or request.url.path == "/users/me":
        # Don't increment counter for auth endpoints or token validation tests
        pass
    else:
        # Increment counter for other endpoints
        RATE_LIMITS["counter"] += 1

    # Calculate remaining requests and reset time
    limit = 5  # Low rate limit for tests (requests per minute)
    remaining = max(0, limit - RATE_LIMITS["counter"])
    reset_time = RATE_LIMITS["reset_at"]

    # Process the request
    response = await call_next(request)

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_time)

    # If over limit, return 429 Too Many Requests
    if RATE_LIMITS["counter"] > limit and not (
        request.url.path.startswith("/auth/") or
        request.url.path == "/users/me"
    ):
        response.headers["Retry-After"] = str(reset_time - current_time)
        response.status_code = 429

    return response


# Auth endpoints
@mock_app.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)
    if not user or user["hashed_password"] != f"hashed_{form_data.password}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": "validtoken",
        "refresh_token": "validrefreshtoken",
        "token_type": "bearer",
    }


@mock_app.post("/auth/token/refresh", response_model=Token)
async def refresh_token(refresh_token: str = Form(...)):
    # Handle known test tokens
    if refresh_token == "invalid":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if refresh_token == "expiredtoken":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # For test token "validrefreshtoken", return new tokens
    if refresh_token == "validrefreshtoken":
        return {
            "access_token": "validtoken",
            "refresh_token": "validrefreshtoken",
            "token_type": "bearer",
        }

    # Check if token is in the database
    if refresh_token not in REFRESH_TOKENS or REFRESH_TOKENS[refresh_token]["exp"] < 9999999999:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return new tokens
    return {
        "access_token": "validtoken",
        "refresh_token": "validrefreshtoken",
        "token_type": "bearer",
    }


@mock_app.post("/auth/token/revoke", status_code=204)
async def revoke_token(current_user: dict = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    # Add the token to the revoked tokens set
    RATE_LIMITS["revoked_tokens"].add(token)
    return {}


# User endpoints
@mock_app.post("/users/", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    if user.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already registered")

    for existing_user in USERS_DB.values():
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    if len(user.password) < 8:
        raise HTTPException(status_code=422, detail="Password too short")

    user_id = len(USERS_DB) + 1
    USERS_DB[user.username] = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "hashed_password": f"hashed_{user.password}",
        "is_active": True,
    }

    return {
        "id": user_id,
        "username": user.username,
        "email": user.email,
    }


@mock_app.get("/users/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    # This endpoint is used for token validation tests
    return current_user


@mock_app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    if user_id == 999999:
        raise HTTPException(status_code=404, detail="User not found")

    for user in USERS_DB.values():
        if user["id"] == user_id:
            return user

    raise HTTPException(status_code=404, detail="User not found")


@mock_app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserUpdate):
    if user_id == 999999:
        raise HTTPException(status_code=404, detail="User not found")

    for username, user_data in USERS_DB.items():
        if user_data["id"] == user_id:
            if user_update.username:
                user_data["username"] = user_update.username
            if user_update.email:
                user_data["email"] = user_update.email
            return user_data

    raise HTTPException(status_code=404, detail="User not found")


@mock_app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    if user_id == 999999:
        raise HTTPException(status_code=404, detail="User not found")

    for username, user_data in list(USERS_DB.items()):
        if user_data["id"] == user_id:
            del USERS_DB[username]
            return {}

    raise HTTPException(status_code=404, detail="User not found")


@pytest.fixture
def mock_fastapi_app():
    return mock_app


@pytest.fixture
def mock_client(mock_fastapi_app):
    return TestClient(mock_fastapi_app)
