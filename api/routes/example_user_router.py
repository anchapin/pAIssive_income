"""Example user router demonstrating centralized validation per project standards.

See: docs/input_validation_and_error_handling_standards.md
"""

from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from common_utils.validation import validate_input, ValidationException, validation_error_response

router = APIRouter(prefix="/api/v1/example_users", tags=["example_users"])

class CreateUserModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr
    age: int = Field(..., ge=0, le=120)

@router.post("/", summary="Create a new user")
async def create_user(request: Request):
    try:
        payload = await request.json()
        user_in = validate_input(CreateUserModel, payload)
        # ... Insert user creation logic here ...
        return {"message": "User created", "user": user_in.model_dump()}
    except ValidationException as exc:
        return validation_error_response(exc)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from exc