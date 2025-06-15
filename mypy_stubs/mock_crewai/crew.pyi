"""Type stubs for mock_crewai.crew."""
from typing import Any, TypeVar

# Define forward references
class Agent: ...
class Task: ...
AgentType = TypeVar("AgentType", bound=Agent)
TaskType = TypeVar("TaskType", bound=Task)

class Crew:
    """Mock implementation of the Crew class."""

    def __init__(
        self,
        agents: list[AgentType],
        tasks: list[TaskType],
        verbose: bool = False,
        process: str = "sequential",
        memory: bool = False,
        cache: bool = False,
        **kwargs: Any
    ) -> None: ...

    def kickoff(self) -> str: ...

    def run(self) -> str: ...

    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    def from_dict(cls, crew_dict: dict[str, Any]) -> Crew: ...
