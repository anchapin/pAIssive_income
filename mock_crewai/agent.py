class Agent:
    def __init__(self, role="", goal="", backstory="", **kwargs):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.kwargs = kwargs

    def execute_task(self, task, context=None):
        if context:
            return f"Executed task: {task.description} with context: {context}"
        return f"Executed task: {task.description}"

    def __str__(self):
        return f"Agent(role='{self.role}')"

    def __repr__(self):
        return f"Agent(role='{self.role}', goal='{self.goal}', backstory='{self.backstory}')"
