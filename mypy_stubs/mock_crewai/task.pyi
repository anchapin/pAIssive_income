"""Type stubs for mock_crewai.task."""
from typing import Any, Callable, Optional, TypeVar

# Define forward references
class Agent: ...
AgentType = TypeVar("AgentType", bound=Agent)

class Task:
    """Mock implementation of the Task class."""

    def __init__(
        self,
        description: str,
        expected_output: str = "",
        agent: Optional[AgentType] = None,
        tools: Optional[list[Any]] = None,
        async_execution: bool = False,
        output: Optional[str] = None,
        context: Optional[str] = None,
        callback: Optional[Callable[[str], None]] = None,
        **kwargs: Any
    ) -> None: ...

    def execute(self, agent: Optional[AgentType] = None, context: Optional[str] = None) -> str: ...

    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls, task_dict: dict[str, Any]) -> Task: ...
