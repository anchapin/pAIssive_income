class Crew:
    def __init__(self, agents=None, tasks=None, **kwargs):
        self.agents = agents or []
        self.tasks = tasks or []
        self.kwargs = kwargs

    def kickoff(self):
        return "Mock crew output"

    # Alias for backward compatibility
    run = kickoff
