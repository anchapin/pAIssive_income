class Task:
    def __init__(self, description="", agent=None, **kwargs):
        self.description = description
        self.agent = agent
        self.kwargs = kwargs

    def __str__(self):
        return f"Task(description='{self.description}')"

    def __repr__(self):
        return f"Task(description='{self.description}', agent={self.agent})"
