"""Configuration loader using centralized validation.

All configuration schemas/loads must comply with:
docs/input_validation_and_error_handling_standards.md
"""

import json

from pydantic import BaseModel, Field

from common_utils.logging import get_logger
from common_utils.validation.core import ValidationError, validate_input

# Initialize logger
logger = get_logger(__name__)


class ExampleConfigModel(BaseModel):
    """Configuration model for application settings."""

    db_url: str = Field(..., min_length=10)
    debug: bool = False
    max_connections: int = Field(..., ge=1, le=100)


def load_config(config_path: str) -> ExampleConfigModel:
    """Load and validate configuration file using centralized validation."""
    with open(config_path) as f:
        data = json.load(f)
    try:
        config = validate_input(ExampleConfigModel, data)
        return config
    except ValidationError as exc:
        # Log the validation error
        logger.error("Config validation failed: %s", exc.details)
        raise
