
from typing import Any, TypeVar

from typing_extensions import TypeAlias

# Define type variables for forward references
AgentType = TypeVar("AgentType", bound=Agent)
TaskType = TypeVar("TaskType", bound=Task)
CrewType = TypeVar("CrewType", bound=Crew)

# Define type aliases
AgentDict: TypeAlias = dict[str, Any]
TaskDict: TypeAlias = dict[str, Any]
CrewDict: TypeAlias = dict[str, Any]

# These empty class definitions are just for type checking
# and will be replaced by the actual implementations
class Agent:
    ...

class Task:
    ...

class Crew:
    ...
