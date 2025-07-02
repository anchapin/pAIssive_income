"""Mock CrewAI module."""

__version__ = "0.120.0"


class Agent:
    def __init__(self, role="", goal="", backstory="", **kwargs) -> None:
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.kwargs = kwargs

    def execute_task(self, task) -> str:
        return f"Mock agent executed task: {getattr(task, 'description', 'unknown task')}"


class Task:
    def __init__(self, description="", agent=None, **kwargs) -> None:
        self.description = description
        self.agent = agent
        self.kwargs = kwargs


class Crew:
    def __init__(self, agents=None, tasks=None, **kwargs) -> None:
        self.agents = agents or []
        self.tasks = tasks or []
        self.kwargs = kwargs

    def kickoff(self) -> str:
        return "Mock crew execution completed"

    def run(self):
        return self.kickoff()
