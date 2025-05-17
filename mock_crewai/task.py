class Task:
    def __init__(self, description="", agent=None, **kwargs):
        self.description = description
        self.agent = agent
        self.kwargs = kwargs
