"""Mock CrewAI module."""
__version__ = "0.120.0"

class Agent:
    def __init__(self, role="", goal="", backstory="", **kwargs):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.kwargs = kwargs
    
    def execute_task(self, task):
        return f"Mock agent executed task: {getattr(task, 'description', 'unknown task')}"

class Task:
    def __init__(self, description="", agent=None, **kwargs):
        self.description = description
        self.agent = agent
        self.kwargs = kwargs

class Crew:
    def __init__(self, agents=None, tasks=None, **kwargs):
        self.agents = agents or []
        self.tasks = tasks or []
        self.kwargs = kwargs
    
    def kickoff(self):
        return "Mock crew execution completed"
    
    def run(self):
        return self.kickoff()
