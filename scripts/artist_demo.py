"""
Demonstration script for the ArtistAgent's agentic tool use.

- Instantiates the ArtistAgent
- Prints available tools
- Sends two prompts: one handled by a tool, one unhandled
- Prints prompt and agent's response for each
"""

from ai_models.artist_agent import ArtistAgent

def main():
    print("=== ArtistAgent Tool Use Demo ===")
    agent = ArtistAgent()

    # Print/log available tools
    print("\nAvailable tools:")
    if hasattr(agent, "tools"):
        for tool in getattr(agent, "tools", []):
            print(f"  - {tool}")
    else:
        print("  (No tools attribute found on agent)")

    # Prepare prompts
    prompts = [
        "What is 12 * 8?",  # Should trigger calculator tool
        "Translate hello to French"  # Should NOT be handled
    ]

    # Process each prompt
    for prompt in prompts:
        print("\n-----------------------------")
        print(f"Prompt: {prompt}")
        try:
            # Use run() as the current interface (ArtistAgent does not implement __call__)
            response = agent.run(prompt)
        except Exception as e:
            response = f"[Error calling agent: {e}]"
        print(f"Agent output: {response}")

if __name__ == "__main__":
    main()