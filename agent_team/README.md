# CrewAI Integration (`agent_team/crewai_agents.py`)

This document explains how to use and extend the [CrewAI](https://docs.crewai.com/) multi-agent orchestration framework in this project.

---

## 1. **Setup**

1. **Install dependencies**

   Ensure you’ve installed project dependencies, including CrewAI:

   ```bash
   pip install -e .
   ```

   Or, if not using editable installs:

   ```bash
   pip install crewai
   ```

2. **Configure API keys**

   CrewAI relies on LLM providers (e.g., OpenAI).
   - Set your API key as an environment variable, for example:
     ```
     export OPENAI_API_KEY=your-key-here
     ```

---

## 2. **Usage**

- The scaffold in `agent_team/crewai_agents.py` defines example agent roles and a simple workflow.
- To run the included workflow:

  ```bash
  python agent_team/crewai_agents.py
  ```

- You should see log output indicating the sample agents and tasks have run.

---

## 3. **Extending CrewAI Agents**

- **Define new agents:** Edit or add to the `Agent` instances in `crewai_agents.py`.
- **Create tasks:** Define `Task` instances and assign them to agents.
- **Assemble your team:** Use the `Crew` class to group agents and tasks into a workflow.
- **Integration:** Import and trigger agent teams from your services, API endpoints, CLI commands, or other application modules as needed.

---

## 4. **References**

- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI GitHub](https://github.com/VisionBlack/CrewAI)

---

## 5. **Testing**

A minimal test scaffold is provided in `tests/test_crewai_agents.py` to verify CrewAI integration.

---

## 6. **Support**

For troubleshooting CrewAI integration:
- Check [CrewAI docs](https://docs.crewai.com/)
- Ask in your project’s communication channels