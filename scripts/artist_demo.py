"""
Demonstration script for the ArtistAgent's agentic tool use.

- Instantiates the ArtistAgent
- Prints available tools
- Supports example and interactive modes
- In example mode: runs prompts for calculator, text analyzer, and unhandled cases
- In interactive mode: user enters prompts in a loop
"""

import argparse
from ai_models.artist_agent import ArtistAgent

def example_prompts():
    return [
        "What is 12 * 8?",  # Should trigger calculator tool
        "Analyze the sentiment of this phrase: 'This is a fantastic development!'",  # For text analyzer
        "Translate hello to French"  # Should NOT be handled
    ]

def main():
    parser = argparse.ArgumentParser(
        description="Demo for ArtistAgent: agentic tool use (calculator, text analyzer, fallback)."
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true",
        help="Run in interactive mode (enter prompts manually)."
    )
    args = parser.parse_args()

    print("=== ArtistAgent Tool Use Demo ===")
    agent = ArtistAgent()

    # Print/log available tools
    print("\nAvailable tools:")
    if hasattr(agent, "tools"):
        for tool in getattr(agent, "tools", []):
            print(f"  - {tool}")
    else:
        print("  (No tools attribute found on agent)")

    if args.interactive:
        print("\nInteractive mode. Type your prompt and press Enter. Type 'exit' to quit.")
        while True:
            prompt = input("\nPrompt: ")
            if prompt.strip().lower() in {"exit", "quit"}:
                print("Exiting interactive mode.")
                break
            response = agent.run(prompt)
            print(f"Agent output: {response}")
    else:
        prompts = example_prompts()
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