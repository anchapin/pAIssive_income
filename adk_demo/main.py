from adk.communication import AgentCommunicator, Message
from agents import DataGathererAgent, SummarizerAgent

def main():
    # Set up communicator
    communicator = AgentCommunicator()

    # Instantiate agents
    gatherer = DataGathererAgent(name="gatherer")
    summarizer = SummarizerAgent(name="summarizer")

    # Register agents with communicator
    gatherer.set_communicator(communicator)
    summarizer.set_communicator(communicator)

    # Start agents (non-blocking)
    gatherer.start()
    summarizer.start()

    # Simple CLI user interface
    user_name = "user"
    query = input("Enter your research query: ").strip()
    if not query:
        print("No query entered. Exiting.")
        return

    # Send initial message to DataGathererAgent
    communicator.send(
        Message(
            sender=user_name,
            receiver="gatherer",
            type="gather",
            payload={"query": query}
        )
    )

    # Wait for summary result (very basic loop)
    while True:
        msg = communicator.receive(receiver=user_name, timeout=5.0)
        if msg and msg.type == "summary_result":
            print(f"\nSummary: {msg.payload['summary']}")
            break

    # Clean up
    gatherer.stop()
    summarizer.stop()

if __name__ == "__main__":
    main()