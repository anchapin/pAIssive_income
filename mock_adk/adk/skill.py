"""Mock skill class for ADK."""


class Skill:
    """Base skill class."""

    def run(self, *args: object, **kwargs: object) -> object:
        """Execute the skill. Override in subclasses."""
