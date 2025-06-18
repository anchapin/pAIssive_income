"""schemas.py - Module for .marketing."""

# Standard library imports

# Third-party imports
from pydantic import BaseModel

# Local imports


class ContentTemplate(BaseModel):
    """Schema for content templates."""
    title: str
    content: str
    template_type: str


class MarketingCampaign(BaseModel):
    """Schema for marketing campaigns."""
    name: str
    description: str
    target_audience: str
