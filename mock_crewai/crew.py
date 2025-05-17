class Crew:
    def __init__(self, agents=None, tasks=None, **kwargs):
        self.agents = agents or []
        self.tasks = tasks or []
        self.kwargs = kwargs

    def kickoff(self, inputs=None):
        if inputs:
            return f"Mock crew output with inputs: {inputs}"
        return "Mock crew output"

    # Alias for backward compatibility
    run = kickoff
    
    def __str__(self):
        return f"Crew(agents={len(self.agents)}, tasks={len(self.tasks)})"
        
    def __repr__(self):
        return f"Crew(agents={self.agents}, tasks={self.tasks})"