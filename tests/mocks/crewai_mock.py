"""Mock implementation of the crewai module for testing."""

class Agent:
    """Mock Agent class for testing."""
    
    def __init__(self, role=None, goal=None, backstory=None, **kwargs):
        """Initialize a mock Agent."""
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.kwargs = kwargs


class Task:
    """Mock Task class for testing."""
    
    def __init__(self, description=None, agent=None, **kwargs):
        """Initialize a mock Task."""
        self.description = description
        self.agent = agent
        self.kwargs = kwargs


class Crew:
    """Mock Crew class for testing."""
    
    def __init__(self, agents=None, tasks=None, **kwargs):
        """Initialize a mock Crew."""
        self.agents = agents or []
        self.tasks = tasks or []
        self.kwargs = kwargs
    
    def run(self, *args, **kwargs):
        """Mock run method."""
        return "Mock crew execution result"
