"""Mock skill class for ADK."""
from typing import Any


class Skill:
    """Base skill class."""
    
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the skill. Override in subclasses."""
        pass
