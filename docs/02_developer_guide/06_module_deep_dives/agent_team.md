# CrewAI Integration — Deep Dive

This document provides a detailed guide to the CrewAI multi-agent orchestration framework as integrated in this project.

---

<!--
The content below was migrated from agent_team/README.md. For a summary, see the module directory.
-->

## Setup

1. **Install dependencies**

   Ensure you’ve installed project dependencies, including CrewAI, by running:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys**

   CrewAI relies on LLM providers (e.g., OpenAI).
   - Set your API key as an environment variable, for example:
     ```
     export OPENAI_API_KEY=your-key-here
     ```

---

## Usage

- The scaffold in `agent_team/crewai_agents.py` defines example agent roles and a simple workflow.
- To run the included workflow:

  ```bash
  python agent_team/crewai_agents.py
  ```

- You should see log output indicating the sample agents and tasks have run.

---

## Extending CrewAI Agents

- **Define new agents:** Edit or add to the `Agent` instances in `crewai_agents.py`.
- **Create tasks:** Define `Task` instances and assign them to agents.
- **Assemble your team:** Use the `Crew` class to group agents and tasks into a workflow.
- **Integration:** Import and trigger agent teams from your services, API endpoints, CLI commands, or other application modules as needed.

---

## References

- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI GitHub](https://github.com/VisionBlack/CrewAI)

---

## Testing

A minimal test scaffold is provided in `tests/test_crewai_agents.py` to verify CrewAI integration.

---

## Support

For troubleshooting CrewAI integration:
- Check [CrewAI docs](https://docs.crewai.com/)
- Ask in your project’s communication channels