"""
Type stubs for mock_crewai.task
"""
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union, TypeVar

# Define forward references
class Agent: pass
AgentType = TypeVar("AgentType", bound=Agent)

class Task:
    """Mock implementation of the Task class."""

    def __init__(
        self,
        description: str,
        expected_output: str = "",
        agent: Optional[AgentType] = None,
        tools: Optional[List[Any]] = None,
        async_execution: bool = False,
        output: Optional[str] = None,
        context: Optional[str] = None,
        callback: Optional[Callable[[str], None]] = None,
        **kwargs: Any
    ) -> None: ...

    def execute(self, agent: Optional[AgentType] = None, context: Optional[str] = None) -> str: ...

    def to_dict(self) -> Dict[str, Any]: ...

    @classmethod
    def from_dict(cls, task_dict: Dict[str, Any]) -> 'Task': ...
