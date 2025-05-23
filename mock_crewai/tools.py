"""Mock tools module for CrewAI."""


class BaseTool:
    """Base class for all tools."""

    def __init__(self, name="", description=""):
        """Initialize a tool.

        Args:
            name: The name of the tool
            description: A description of what the tool does
        """
        self.name = name
        self.description = description

    def execute(self, input_text):
        """Execute the tool with the given input.

        Args:
            input_text: The input text to process

        Returns:
            str: The result of executing the tool
        """
        return f"Executed tool: {self.name} with input: {input_text}"
