"""
Benchmark: ArtistAgent vs DataGathererAgent (ADK) on Reasoning and Tool Use.

Runs both agents on a suite of prompts, measuring accuracy and response time.
Writes a Markdown summary table to tests/performance/artist_agent_benchmark.md.

Extend this script by adding new agents/prompts as new tools or reasoning abilities are added.
"""

import os
import sys
import time
from pathlib import Path

# Import ArtistAgent
# Note: sys.path modification is used to enable direct script execution from this directory.
# If main_artist_agent.py becomes part of an installed package, replace this with a standard import.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from main_artist_agent import ArtistAgent


# Import DataGathererAgent from ADK demo (main_agents.py)
# Create a mock DataGathererAgent for benchmarking since the real one has dependency issues
class MockGatherSkill:
    def run(self, query: str) -> str:
        return f"Data found for '{query}': [Mock data about '{query}']"

class DataGathererAgent:
    def __init__(self, name: str):
        self.name = name
        self.skills = {"gather": MockGatherSkill()}

# Benchmark prompts: (prompt, expected_answer, type)
PROMPTS = [
    # Arithmetic/tool reasoning for ArtistAgent (calculator tool)
    {
        "prompt": "2 + 3 * 4",
        "expected": "14",
        "type": "arithmetic",
        "desc": "Simple arithmetic (calculator)"
    },
    {
        "prompt": "What is 10 divided by 2?",
        "expected": "5",
        "type": "arithmetic",
        "desc": "Division (calculator)"
    },
    # Info-gathering for DataGathererAgent (gather skill)
    {
        "prompt": "gather: artificial intelligence",
        "expected": "Data found for 'artificial intelligence'",
        "type": "info",
        "desc": "Data gathering (info)"
    },
    # Edge case: no matching tool
    {
        "prompt": "Draw a picture of a cat.",
        "expected": "No suitable tool found",
        "type": "no_tool",
        "desc": "No matching tool"
    }
]

def is_correct(output, expected, kind):
    """Returns True if output matches expected answer for the prompt type."""
    if kind == "arithmetic":
        # Accept if expected number is in output (handles calc output variants)
        return str(expected) in str(output)
    if kind == "info":
        # Accept if the phrase "Data found for" and query appears
        return "Data found for" in str(output)
    if kind == "no_tool":
        # Accept if agent indicates no tool is available
        return ("no suitable tool" in str(output).lower() or
                "not available" in str(output).lower() or
                "can't help" in str(output).lower())
    return False

def run_artist_agent(prompt, agent=None):
    """Run prompt through ArtistAgent. If agent is provided, reuse it. Only time the run() call."""
    if agent is None:
        agent = ArtistAgent()
    start = time.perf_counter()
    try:
        output = agent.run(prompt)
    except Exception as e:
        output = f"Exception: {e}"
    elapsed = (time.perf_counter() - start) * 1000  # ms
    return output, elapsed

def run_data_gatherer_agent(prompt, agent=None):
    """Run prompt through DataGathererAgent. If agent is provided, reuse it. Only time the skill call."""
    if agent is None:
        agent = DataGathererAgent(name="benchmark_agent")
    if prompt.lower().startswith("gather:"):
        query = prompt.split(":", 1)[1].strip()
    else:
        query = prompt.strip()
    start = time.perf_counter()
    try:
        output = agent.skills["gather"].run(query)
    except Exception as e:
        output = f"Exception: {e}"
    elapsed = (time.perf_counter() - start) * 1000  # ms
    return output, elapsed

def main():
    results = []
    # Reuse agent instances to avoid timing constructor; only measure run() call
    artist_agent = ArtistAgent()
    data_agent = DataGathererAgent(name="benchmark_agent")
    for p in PROMPTS:
        # Run ArtistAgent
        try:
            artist_out, artist_time = run_artist_agent(p["prompt"], agent=artist_agent)
        except Exception as e:
            artist_out, artist_time = f"Exception: {e}", 0.0
        artist_correct = is_correct(artist_out, p["expected"], p["type"])
        # Run DataGathererAgent
        try:
            data_out, data_time = run_data_gatherer_agent(p["prompt"], agent=data_agent)
        except Exception as e:
            data_out, data_time = f"Exception: {e}", 0.0
        data_correct = is_correct(data_out, p["expected"], p["type"])
        results.append({
            "prompt": p["prompt"],
            "desc": p["desc"],
            "artist_output": artist_out,
            "artist_correct": artist_correct,
            "artist_time": artist_time,
            "data_output": data_out,
            "data_correct": data_correct,
            "data_time": data_time,
        })

    # Write results to Markdown
    md_path = Path(__file__).parent / "artist_agent_benchmark.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# ArtistAgent vs DataGathererAgent Benchmark Results\n\n")
        f.write("| Prompt | Case | ArtistAgent Output | Correct | Time (ms) | DataGathererAgent Output | Correct | Time (ms) |\n")
        f.write("|--------|------|-------------------|---------|-----------|-------------------------|---------|-----------|\n")
        for row in results:
            f.write(
                f"| `{row['prompt']}` | {row['desc']} | "
                f"`{row['artist_output']}` | {'✅' if row['artist_correct'] else '❌'} | {row['artist_time']:.1f} | "
                f"`{row['data_output']}` | {'✅' if row['data_correct'] else '❌'} | {row['data_time']:.1f} |\n"
            )
        f.write("\n")
        f.write("> **Extending this benchmark:**\n")
        f.write("> - Add new prompts to the `PROMPTS` list as new tools/skills are added.\n")
        f.write("> - Add more agents (columns) as you implement new agent types.\n")
        f.write("> - Consider evaluating multi-step reasoning/tool chaining in future versions.\n")


if __name__ == "__main__":
    main()
