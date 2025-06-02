"""
Mock CrewAI module for CI environments.
Provides mock implementations of CrewAI classes to prevent import errors.
"""

__version__ = "0.120.0"

# Import submodules for top-level access
from . import agent, crew, task, tools, types
from .tools import BaseTool


class MockAgent:
    """Mock implementation of CrewAI Agent."""

    def __init__(self, role="Mock Agent", goal="Mock goal", backstory="Mock backstory", **kwargs):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.name = kwargs.get("name", role)  # Add name attribute
        self.verbose = kwargs.get("verbose", False)
        self.allow_delegation = kwargs.get("allow_delegation", False)
        self.tools = kwargs.get("tools", [])
        self.llm = kwargs.get("llm", None)  # Add LLM attribute
        self.max_iter = kwargs.get("max_iter", 5)  # Add max iterations
        self.max_execution_time = kwargs.get("max_execution_time", None)  # Add execution time limit
        self.system_template = kwargs.get("system_template", None)  # Add system template
        self.prompt_template = kwargs.get("prompt_template", None)  # Add prompt template
        self.response_template = kwargs.get("response_template", None)  # Add response template
        self.kwargs = kwargs  # Store kwargs for test compatibility

    def __str__(self):
        return f"Agent(role='{self.role}', goal='{self.goal}', backstory='{self.backstory}')"

    def __repr__(self):
        return self.__str__()

    def execute_task(self, task, context=None):
        """Mock task execution."""
        if context:
            return f"Executed task: {task.description if hasattr(task, 'description') else task} with context: {context}"
        return f"Executed task: {task.description if hasattr(task, 'description') else task}"

    def execute(self, task, context=None):
        """Alias for execute_task for compatibility."""
        return self.execute_task(task, context)


class MockTask:
    """Mock implementation of CrewAI Task."""

    def __init__(self, description="Mock task", agent=None, **kwargs):
        self.description = description
        self.agent = agent
        self.expected_output = kwargs.get("expected_output", "Mock output")
        self.tools = kwargs.get("tools", [])
        self.async_execution = kwargs.get("async_execution", False)  # Add missing attribute
        self.context = kwargs.get("context", [])  # Add context attribute
        self.output_json = kwargs.get("output_json", None)  # Add JSON output format
        self.output_pydantic = kwargs.get("output_pydantic", None)  # Add Pydantic output format
        self.output_file = kwargs.get("output_file", None)  # Add file output
        self.callback = kwargs.get("callback", None)  # Add callback function
        self.human_input = kwargs.get("human_input", False)  # Add human input flag
        self.kwargs = kwargs  # Store kwargs for test compatibility

    def __str__(self):
        return f"Task(description='{self.description}')"

    def __repr__(self):
        agent_repr = f"Agent(role='{self.agent.role}')" if self.agent else "None"
        return f"Task(description='{self.description}', agent={agent_repr})"

    def execute(self, context=None):
        """Mock task execution."""
        if self.agent:
            return f"Executed: {self.description} by {self.agent.name if hasattr(self.agent, 'name') else 'Agent'} ({self.agent.role})"
        return f"Executed: {self.description}"


class MockCrew:
    """Mock implementation of CrewAI Crew."""

    def __init__(self, agents=None, tasks=None, **kwargs):
        self.agents = agents or []
        self.tasks = tasks or []
        self.verbose = kwargs.get("verbose", False)
        self.process = kwargs.get("process", "sequential")
        self.memory = kwargs.get("memory", False)  # Add missing attribute
        self.manager_llm = kwargs.get("manager_llm", None)  # Add manager LLM
        self.function_calling_llm = kwargs.get("function_calling_llm", None)  # Add function calling LLM
        self.config = kwargs.get("config", {})  # Add config attribute
        self.max_rpm = kwargs.get("max_rpm", None)  # Add rate limiting
        self.language = kwargs.get("language", "en")  # Add language setting
        self.full_output = kwargs.get("full_output", False)  # Add full output flag
        self.step_callback = kwargs.get("step_callback", None)  # Add step callback
        self.task_callback = kwargs.get("task_callback", None)  # Add task callback
        self.share_crew = kwargs.get("share_crew", False)  # Add crew sharing flag
        self.kwargs = kwargs  # Store kwargs for test compatibility

    def __str__(self):
        return f"Crew(agents={len(self.agents)}, tasks={len(self.tasks)})"

    def __repr__(self):
        return f"Crew(agents={self.agents}, tasks={self.tasks})"

    def kickoff(self, inputs=None):
        """Mock crew execution."""
        if inputs:
            return f"Mock crew output with inputs: {inputs}"
        # Return list format for some tests that expect it
        if self.agents and self.tasks:
            results = []
            for task in self.tasks:
                if task.agent:
                    results.append(f"Executed: {task.description} by {task.agent.name if hasattr(task.agent, 'name') else 'Agent'} ({task.agent.role})")
                else:
                    results.append(f"Executed: {task.description}")
            return results
        return "Mock crew output"

    # Make run an alias to kickoff (same method object)
    run = kickoff


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

    DEFAULT = "default"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    RESEARCHER = "researcher"
    WRITER = "writer"
    ANALYST = "analyst"


class MockCrewType:
    """Mock crew type enum."""

    DEFAULT = "default"
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"


class MockTaskType:
    """Mock task type enum."""

    DEFAULT = "default"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
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
    "BaseTool",
    "Crew",
    "CrewType",
    "MockAgent",
    "MockCrew",
    "MockTask",
    "Task",
    "TaskType",
    "agent",
    "crew",
    "task",
    "tools",
    "types"
]
