# ADK Demo

This directory contains a minimal demonstration of Google's Agent Development Kit (ADK) in a multi-agent scenario.

## Overview

- **DataGathererAgent**: Receives a user query, simulates data collection, and forwards the data.
- **SummarizerAgent**: Receives the gathered data, summarizes it, and returns the result.
- **Simple CLI**: Sends the initial user query and prints the final summary.

![Workflow](https://google.github.io/adk-docs/img/adk-architecture.svg) <!-- illustrative link only -->

## How it Works

1. User enters a query through the CLI interface
2. DataGathererAgent:
   - Receives the query and simulates data collection
   - Forwards gathered data to SummarizerAgent
3. SummarizerAgent:
   - Processes received data
   - Creates a summary
   - Returns results to the user
4. CLI displays the final summary or timeout message

## Configuration

### Message Reception
- **Retry Settings**:
  - Maximum retries: 10 attempts
  - Timeout per attempt: 5.0 seconds
  - Total maximum wait time: 50 seconds

### Dependencies
- **Core Requirements**:
  - adk>=1.0.0: Required for stable message routing
- **Optional Extensions**:
  - adk[monitoring]>=1.0.0: Enables monitoring capabilities
  - adk[testing]>=1.0.0: Provides testing utilities

### Agent Communication
- **Message Flow**:
  1. User → DataGatherer: 'gather' type with query
  2. DataGatherer → Summarizer: 'summarize' type with data
  3. Summarizer → User: 'summary_result' type with result
- **Retry Mechanism**: 
  - Implements progressive retry for message reception
  - Graceful timeout handling after max attempts

## Installation

1. **Install ADK** (if not already):
   ```bash
   uv pip install adk
   ```

2. **Run the demo:**
   ```bash
   python adk_demo/main.py
   ```

You will be prompted to enter a query. Agents will coordinate and print out the summary.

## Files

- `main.py` — Entry point and agent orchestration
  - Handles agent setup and communication
  - Implements CLI interface with retry mechanism
  - Manages message flow and cleanup
- `agents.py` — Agent and skill class definitions
  - DataGathererAgent: Query processing and data collection
  - SummarizerAgent: Data summarization
  - Includes memory management and message routing
- `requirements.txt` — Project dependencies
  - Core ADK package requirement
  - Ensures consistent environment setup

## Error Handling

- Implements retry mechanism for message reception
- Graceful timeout handling if no response received
- Proper agent cleanup on completion or failure
