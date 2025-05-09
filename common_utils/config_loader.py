"""Configuration loader using centralized validation.

All configuration schemas/loads must comply with:
docs/input_validation_and_error_handling_standards.md
"""

import json
from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel, Field
from common_utils.validation import validate_input, ValidationException

class ExampleConfigModel(BaseModel):
    db_url: str = Field(..., min_length=10)
    debug: bool = False
    max_connections: int = Field(..., ge=1, le=100)

def load_config(config_path: str) -> ExampleConfigModel:
    """Load and validate configuration file using centralized validation."""
    with open(config_path, "r") as f:
        data = json.load(f)
    try:
        config = validate_input(ExampleConfigModel, data)
        return config
    except ValidationException as exc:
        # In production, log or handle as appropriate
        print("Config validation failed:", exc.details)
        raise