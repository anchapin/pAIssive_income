from adk.agent import Agent
from adk.skill import Skill
from adk.memory import SimpleMemory
from adk.communication import Message


class DataGathererSkill(Skill):
    def run(self, query):
        # Simulate data collection (in practice, fetch from a DB, API, etc.)
        return f"Data found for '{query}': [Example data about '{query}']."


class DataGathererAgent(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.memory = SimpleMemory()
        self.add_skill("gather", DataGathererSkill())

    def on_message(self, message: Message):
        if message.type == "gather":
            data = self.skills["gather"].run(message.payload["query"])
            # Send gathered data to SummarizerAgent
            self.communicator.send(
                Message(
                    sender=self.name,
                    receiver="summarizer",
                    type="summarize",
                    payload={"data": data, "original_sender": message.sender}
                )
            )


class SummarizerSkill(Skill):
    def run(self, data):
        # Simulate summarization (in practice, call an LLM, etc.)
        return data[:75] + "..." if len(data) > 75 else data


class SummarizerAgent(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.memory = SimpleMemory()
        self.add_skill("summarize", SummarizerSkill())

    def on_message(self, message: Message):
        if message.type == "summarize":
            summary = self.skills["summarize"].run(message.payload["data"])
            # Return summary to original requester (user)
            self.communicator.send(
                Message(
                    sender=self.name,
                    receiver=message.payload["original_sender"],
                    type="summary_result",
                    payload={"summary": summary}
                )
            )