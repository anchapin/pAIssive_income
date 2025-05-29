"""
Mock CrewAI module for CI environments.
Provides mock implementations of CrewAI classes to prevent import errors.
"""

__version__ = "0.1.0"

# Import submodules for top-level access
from . import agent, crew, task, tools, types
from .tools import BaseTool

class MockAgent:
    """Mock implementation of CrewAI Agent."""

    def __init__(self, role="Mock Agent", goal="Mock goal", backstory="Mock backstory", **kwargs):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = kwargs.get("verbose", False)
        self.allow_delegation = kwargs.get("allow_delegation", False)
        self.tools = kwargs.get("tools", [])

    def __str__(self):
        return f"Agent(role='{self.role}')"

    def __repr__(self):
        return self.__str__()

    def execute_task(self, task, context=None):
        """Mock task execution."""
        return f"Mock execution of task: {task}"


class MockTask:
    """Mock implementation of CrewAI Task."""

    def __init__(self, description="Mock task", agent=None, **kwargs):
        self.description = description
        self.agent = agent
        self.expected_output = kwargs.get("expected_output", "Mock output")
        self.tools = kwargs.get("tools", [])

    def __str__(self):
        return f"Task(description='{self.description}')"

    def __repr__(self):
        return self.__str__()


class MockCrew:
    """Mock implementation of CrewAI Crew."""

    def __init__(self, agents=None, tasks=None, **kwargs):
        self.agents = agents or []
        self.tasks = tasks or []
        self.verbose = kwargs.get("verbose", False)
        self.process = kwargs.get("process", "sequential")

    def __str__(self):
        return f"Crew(agents={len(self.agents)}, tasks={len(self.tasks)})"

    def __repr__(self):
        return self.__str__()

    def kickoff(self, inputs=None):
        """Mock crew execution."""
        return "Mock crew output"

    def run(self, inputs=None):
        """Alias for kickoff."""
        return self.kickoff(inputs)


# Mock tools module
class MockBaseTool:
    """Mock implementation of CrewAI BaseTool."""

    def __init__(self, name="Mock Tool", description="Mock tool description"):
        self.name = name
        self.description = description

    def execute(self, *args, **kwargs):
        """Mock tool execution."""
        return "Mock tool result"


# Mock enums
class MockAgentType:
    """Mock agent type enum."""

    RESEARCHER = "researcher"
    WRITER = "writer"
    ANALYST = "analyst"


class MockCrewType:
    """Mock crew type enum."""

    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"


class MockTaskType:
    """Mock task type enum."""

    RESEARCH = "research"
    WRITING = "writing"
    ANALYSIS = "analysis"


# Export all classes
Agent = MockAgent
Task = MockTask
Crew = MockCrew

# Tools module
class tools:
    BaseTool = MockBaseTool

# Type enums
AgentType = MockAgentType
CrewType = MockCrewType
TaskType = MockTaskType

# Module-level attributes for compatibility
__all__ = [
    "Agent",
    "AgentType",
    "Crew",
    "CrewType",
    "MockAgent",
    "MockCrew",
    "MockTask",
    "Task",
    "TaskType",
    "BaseTool",
    "agent",
    "crew",
    "task",
    "tools",
    "types"
]
