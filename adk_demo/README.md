# ADK Demo

This directory contains a minimal demonstration of Google's Agent Development Kit (ADK) in a multi-agent scenario.

## Overview

- **DataGathererAgent**: Receives a user query, simulates data collection, and forwards the data.
- **SummarizerAgent**: Receives the gathered data, summarizes it, and returns the result.
- **Simple CLI**: Sends the initial user query and prints the final summary.

![Workflow](https://google.github.io/adk-docs/img/adk-architecture.svg) <!-- illustrative link only -->

## Running the Demo

1. **Install ADK** (if not already):
   ```bash
   pip install adk
   ```

2. **Run the demo:**
   ```bash
   python adk_demo/main.py
   ```

You will be prompted to enter a query. Agents will coordinate and print out the summary.

## Files

- `main.py` — Entry point and agent orchestration.
- `agents.py` — Agent and skill class definitions.