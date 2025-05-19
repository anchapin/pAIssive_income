"""
Type stubs for mock_crewai.agent
"""
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union, TypeVar

# Define forward references
class Task: pass
TaskType = TypeVar("TaskType", bound=Task)
AgentType = TypeVar("AgentType", bound="Agent")

class Agent:
    """Mock implementation of the Agent class."""

    def __init__(
        self,
        role: str = "",
        goal: str = "",
        backstory: str = "",
        verbose: bool = False,
        allow_delegation: bool = True,
        tools: Optional[List[Any]] = None,
        llm: Any = None,
        max_iter: int = 5,
        max_rpm: Optional[int] = None,
        max_tokens: Optional[int] = None,
        cache: bool = False,
        memory: bool = False,
        **kwargs: Any
    ) -> None: ...

    def execute_task(self, task: TaskType, context: Optional[str] = None) -> str: ...

    def create_task(self, description: str, expected_output: str = "", tools: Optional[List[Any]] = None) -> TaskType: ...

    def delegate_task(self, task: TaskType, agent: AgentType) -> str: ...

    def to_dict(self) -> Dict[str, Any]: ...

    @classmethod
    def from_dict(cls, agent_dict: Dict[str, Any]) -> 'Agent': ...
