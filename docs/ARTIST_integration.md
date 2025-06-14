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

**Important Note:** The `requirements-artist.txt` file, mentioned below for ARTIST-specific setup, is currently a placeholder. The actual dependencies required for ARTIST experiments need to be identified and added to this file. Until then, the ARTIST-specific setup instructions may not result in a functional environment.

### A. Using `uv` (Preferred) or venv

1. **Clone the repository and navigate to the root:**
   ```bash
   git clone <repo-url>
   cd pAIssive_income
   ```

2. **Set up the Python environment (choose one of the following based on your needs):**

   - **For ARTIST-only development:**  
     Install only the dependencies required for ARTIST experiments. This is the recommended and safest approach if you are not working on the broader project codebase.
     ```bash
     # Install uv if not present
     pip install uv

     # Create and activate a virtual environment (optional step for isolation)
     python3 -m venv .venv
     source .venv/bin/activate  # or .venv\Scripts\activate on Windows

     # Install ARTIST dependencies using uv
     uv pip install -r requirements-artist.txt (ensure this file is populated with necessary dependencies, as it's currently a placeholder)
     ```
     This command installs dependencies listed in `requirements-artist.txt`, which are intended to be specific to ARTIST experiments.

   - **For full project development (including ARTIST integration):**  
     Use the general project setup script. This script installs general project dependencies from `requirements.txt` and `requirements-dev.txt` but does **not** automatically install ARTIST-specific dependencies from `requirements-artist.txt`.
     ```bash
     ./setup_with_uv.sh  # or setup_with_uv.ps1 on Windows
     ```
     > **Note:** If you are working on ARTIST experiments within the broader project, you will likely need to run the command `uv pip install -r requirements-artist.txt` (after ensuring it's populated) **in addition to** `./setup_with_uv.sh`. Be mindful of potential package version conflicts if dependencies overlap between the main project and ARTIST. Using separate, isolated virtual environments for ARTIST development versus main project development is a good practice to avoid such conflicts.

**Tip:**  
If you are focusing *only* on ARTIST experiments, setting up a dedicated virtual environment and installing dependencies *only* from `requirements-artist.txt` (once populated) is the cleanest approach. If you are working on the broader project and also need to run ARTIST experiments, ensure all necessary dependency sets are installed, ideally in a way that avoids version conflicts (e.g., separate environments or careful management of a shared environment).

### B. Using Docker

1. **Build and run the container:**
   ```bash
   docker compose up --build
   ```
   - For ARTIST-specific experiments, use the dedicated `artist_experiments/Dockerfile.artist`. This Dockerfile is pre-configured to use `requirements-artist.txt` (once populated) and is recommended for isolated ARTIST experiment execution.
   - If, for some reason, you need to run ARTIST experiments from the main project Dockerfile, you may need to customize it to ensure it installs dependencies from `requirements-artist.txt` (once populated). However, using `artist_experiments/Dockerfile.artist` is generally preferred for ARTIST-related workflows.

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
The `artist_experiments/math_problem_solving.py` module contains logic for this experiment. To run it, you can use a command like the following, assuming the `run_experiment` function exists within the module:
```bash
python -c "from artist_experiments import math_problem_solving; print(math_problem_solving.run_experiment('Solve 2 + 3 * 4'))"
```
Alternatively, if the module is structured to be executable (e.g., with an `if __name__ == '__main__':` block), you might run it directly:
```bash
python artist_experiments/math_problem_solving.py --problem "Solve 2 + 3 * 4"
```
(Note: The exact command-line arguments for direct execution would depend on the implementation within `math_problem_solving.py`.)

Example: **Multi-API Orchestration**
Similarly, the `artist_experiments/multi_api_orchestration.py` module handles this experiment. You can run it using:
```bash
python -c "from artist_experiments import multi_api_orchestration; print(multi_api_orchestration.run_experiment('Find products related to smart home automation'))"
```
Or, if executable directly:
```bash
python artist_experiments/multi_api_orchestration.py --task "Find products related to smart home automation"
```
(Note: The exact command-line arguments depend on the module's implementation.)

- Inspect each experiment module (e.g., `artist_experiments/math_problem_solving.py`) to understand its specific functions (like `run_experiment`) and whether it supports direct execution with command-line arguments.
- To extend, add new tools to the registry or modify the agent logic, then update the experiment module and tests.

**Tip:** For more convenient execution, especially for frequently run experiments, consider creating simple wrapper scripts (e.g., a `run_math_exp.sh` or `run_api_exp.py`) or adding an `if __name__ == '__main__':` block to the experiment modules if not already present. This can simplify the command needed to start an experiment.

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
- Make sure you’ve activated your virtual environment and installed with `uv` using `requirements-artist.txt` (ensure this file is populated with necessary dependencies).
- If using Docker, rebuild the container (`docker compose build`).

**Q2: Dependency version conflicts**
- ARTIST requires specific library versions; do not mix `pip` and `uv`.
- If you see version mismatches, remove your `.venv` and reinstall all dependencies with `uv`.

**Q3: Docker issues (missing dependencies, agent errors)**
- Ensure you are using the correct Dockerfile for your use case:
  - For ARTIST experiments, the recommended approach is to use `artist_experiments/Dockerfile.artist`, which is already set up to install dependencies from `requirements-artist.txt` (once populated).
  - If running via a different Dockerfile, make sure it also installs the necessary dependencies from `requirements-artist.txt` (once populated).
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
