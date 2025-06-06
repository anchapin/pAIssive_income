"""
Type stubs for mock_crewai.crew
"""
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union, TypeVar

# Define forward references
class Agent: pass
class Task: pass
AgentType = TypeVar("AgentType", bound=Agent)
TaskType = TypeVar("TaskType", bound=Task)

class Crew:
    """Mock implementation of the Crew class."""

    def __init__(
        self,
        agents: List[AgentType],
        tasks: List[TaskType],
        verbose: bool = False,
        process: str = "sequential",
        memory: bool = False,
        cache: bool = False,
        **kwargs: Any
    ) -> None: ...

    def kickoff(self) -> str: ...

    def run(self) -> str: ...

    def to_dict(self) -> Dict[str, Any]: ...

    @classmethod
    def from_dict(cls, crew_dict: Dict[str, Any]) -> 'Crew': ...
