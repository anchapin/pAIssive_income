# ARTIST Integration Guide

_Agentic Reasoning and Tool Integration in Self-improving Transformers (ARTIST)_

---

## 1. Introduction: What is ARTIST?

**ARTIST** stands for **Agentic Reasoning and Tool Integration in Self-improving Transformers**. It is a research-driven framework enabling Large Language Models (LLMs) and agent teams to reason, plan, and dynamically select and use tools to solve complex tasks in a self-improving loop.

**Why ARTIST for This Codebase?**
- **Advanced Agent Orchestration:** Elevate our agent teams with deep reasoning, multi-step planning, and dynamic tool use.
- **Experimentation:** Provides a platform for agentic experiments (e.g., math problem solving, multi-API workflows).
- **Extensibility:** ARTIST's modular architecture allows us to integrate new tools, APIs, and agent behaviors with minimal friction.
- **Research Alignment:** Brings state-of-the-art agentic reasoning into our practical, product-focused AI stack.

---

## 2. Integration Points

To work with ARTIST in this repository, familiarize yourself with these key locations:

- **`ai_models/artist_agent.py`**  
  Central implementation of the ARTIST agent. Entry point for running, extending, or integrating the main agent logic.

- **Tool Registry**  
  ARTIST uses a tool registry system to expose and manage callable tools for agents.  
  - Review the tool registry logic in `ai_models/artist_agent.py` or any supporting modules.
  - To add new tools, follow the registration patterns already present.

- **`artist_experiments/`**  
  Contains self-contained experiments and workflows demonstrating ARTIST capabilities:
    - `math_problem_solving/`
    - `multi_api_orchestration/`
  Add new experiments here, following the directory structure and README conventions.

- **Setup and Utility Scripts**  
  - Use `setup_with_uv.sh` or `setup_with_uv.ps1` for streamlined environment setup.
  - Python requirements for ARTIST are tracked in `requirements-artist.txt`.

---

## 3. Setup Instructions

### A. Using `uv` (Preferred) or venv

1. **Clone the repository and navigate to the root:**
   ```bash
   git clone <repo-url>
   cd pAIssive_income
   ```

2. **Set up the Python environment:**
   ```bash
   # Install uv if not present
   pip install uv

   # Create and activate a virtual environment (optional step for isolation)
   python3 -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows

   # Install ARTIST dependencies using uv
   uv pip install -r requirements-artist.txt
   ```

3. **Run the setup script (optional, but recommended for first-time setup):**
   ```bash
   ./setup_with_uv.sh  # or setup_with_uv.ps1 on Windows
   ```

### B. Using Docker

1. **Build and run the container:**
   ```bash
   docker compose up --build
   ```
   - For ARTIST-specific experiments, you may need to customize the Dockerfile to include `requirements-artist.txt`.

2. **Environment and .gitignore Best Practices**

   - Experiments and scratch files in `artist_experiments/` should be excluded from version control unless meant for collaboration.  
   - Add temporary scripts, outputs, or venvs to `.gitignore` as needed.
   - Keep `.env` files (with secrets or API keys) out of version control.

---

## 4. Usage Guide

### A. Running the Main ARTIST Agent

To run the ARTIST agent directly:
```bash
python ai_models/artist_agent.py
```
- This will launch the main agentic reasoning loop with available registered tools.
- Command-line arguments or config may be supported; see the script for options.

### B. Running and Extending Experiments

Example: **Math Problem Solving**
```bash
python artist_experiments/math_problem_solving/run.py
```
Example: **Multi-API Orchestration**
```bash
python artist_experiments/multi_api_orchestration/run.py
```
- Each experiment folder contains a README and a `run.py` entrypoint.
- To extend, add new tools to the registry or modify the agent logic, then update the experiment script and tests.

**Tips:**
- Follow the codebase convention: keep new experiments, tools, and outputs organized and .gitignore-aware.
- For cross-experiment integration, factor shared logic into `common_utils/` or similar.

### C. Running Tests

To run ARTIST-related tests:
```bash
pytest artist_experiments/
# Or for all tests
pytest
```
- Tests follow the standard repo conventions. See `run_tests.py` or `run_tests.sh` for orchestration.

---

## 5. Troubleshooting & FAQ

**Q1: "ModuleNotFoundError" or import errors**
- Make sure you’ve activated your virtual environment and installed with `uv` using `requirements-artist.txt`.
- If using Docker, rebuild the container (`docker compose build`).

**Q2: Dependency version conflicts**
- ARTIST requires specific library versions; do not mix `pip` and `uv`.
- If you see version mismatches, remove your `.venv` and reinstall all dependencies with `uv`.

**Q3: Docker issues (missing dependencies, agent errors)**
- Ensure the Dockerfile installs from `requirements-artist.txt`.
- Rebuild images on requirements changes.

**Q4: Experiment/test failures**
- Check for missing test dependencies; rerun setup scripts.
- Ensure your environment matches the documented setup.
- Look for missing config files or .env variables.

**Q5: Adding new tools or experiments**
- Follow the tool registration pattern in `ai_models/artist_agent.py`.
- Keep new experiments in their own subdirectory under `artist_experiments/`. Document them with a README.

---

## 6. Demo & Knowledge Sharing Checklist

When presenting ARTIST to the team, consider the following:

- [ ] Show the main agent workflow (`python ai_models/artist_agent.py`): reasoning, tool selection, and self-improvement.
- [ ] Run a sample experiment (e.g., math problem solving or API orchestration).
- [ ] Highlight integration points: agent code, tool registry, experiment directory.
- [ ] Demonstrate how to add a new tool or experiment.
- [ ] Review troubleshooting tips and .gitignore best practices.
- [ ] Point to this guide and deeper research docs for onboarding.

---

## 7. References

- **ARTIST Paper:**  
  [Agentic Reasoning and Tool Integration in Self-improving Transformers (arXiv:2402.00838)](https://arxiv.org/abs/2402.00838)
- **Project Research Docs:**  
  See `docs/research/` for related research summaries, benchmarking, and analysis.

---

For further help, reach out via the team chat or open an issue.