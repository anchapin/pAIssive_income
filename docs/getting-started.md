# Getting Started with pAIssive Income Framework

> **Audience:** New users, developers, and contributors looking to set up or use the framework.

This guide will help you get started with the pAIssive Income Framework. It covers installation, basic configuration, and a simple example to demonstrate the framework's capabilities.

**If you arrived here from the main README, you're in the right place!**

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Installation

### Option 1: Clone the Repository

```bash
git clone https://github.com/anchapin/pAIssive_income.git
cd pAIssive_income
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

### Option 2: Install from Source

```bash
pip install git+https://github.com/anchapin/pAIssive_income.git
```

### Environment Setup (Recommended)

- Create a virtual environment:
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\Scripts\activate
  ```
- Set up pre-commit hooks:
  ```bash
  pip install pre-commit
  pre-commit install
  ```

## Development Tools

- **Lint and format code:**  
  ```bash
  python run_linting.py
  ```
- **Run tests:**  
  ```bash
  python run_tests.py
  ```
- **Fix syntax/formatting issues:**  
  ```bash
  python fix_all_issues_final.py
  ```
- **Run local CI workflow:**  
  ```bash
  python run_github_actions_locally.py --list
  ```

## Basic Configuration

...

```python
from agent_team import AgentTeam
from niche_analysis import MarketAnalyzer, ProblemIdentifier, OpportunityScorer

# Create the agent team
team = AgentTeam("Niche AI Tools")

# Define market segments to analyze
market_segments = [
    "e-commerce",
    "content creation",
    "freelancing",
    "education",
    "real estate",
]

# Run niche analysis
niches = team.run_niche_analysis(market_segments)

# Print identified niches
for i, niche in enumerate(niches):
    print(f"{i+1}. {niche['name']} (Score: {niche['opportunity_score']:.2f})")

# Select a niche
selected_niche = niches[0]

# Develop a solution
solution = team.develop_solution(selected_niche["id"])

# Create a monetization strategy
monetization_strategy = team.create_monetization_strategy(solution["id"])

# Create a marketing campaign
marketing_campaign = team.create_marketing_campaign(solution["id"], monetization_strategy["id"])

# Print the results
print(f"Solution: {solution['name']}")
print(f"Monetization Strategy: {monetization_strategy['name']}")
print(f"Marketing Campaign: {marketing_campaign['name']}")
```

## Running the UI

The framework includes a web interface that you can use to interact with the framework components. To run the UI:

```bash
python run_ui.py
```

This will start a web server at http://localhost:5000 where you can access the UI.

## Next Steps

Now that you have the framework installed and running, you can:

1. Explore the [Agent Team](agent-team.md) documentation to learn about the different agents and how they collaborate.
2. Learn about [Niche Analysis](niche-analysis.md) to identify profitable niches.
3. Explore the [AI Models](ai-models.md) documentation to learn how to use local AI models.
4. Learn about [Monetization](monetization.md) to create effective subscription models.
5. Explore the [Marketing](marketing.md) documentation to create targeted marketing campaigns.
6. Learn about the [UI](ui.md) to interact with the framework through a web interface.

---

**Feedback:**  
To request changes or suggest improvements to this guide, [open a documentation issue](https://github.com/anchapin/pAIssive_income/issues/new?labels=documentation) or see [documentation-guide.md](documentation-guide.md).

Now that you have the framework installed and running, you can:

1. Explore the [Agent Team](agent-team.md) documentation to learn about the different agents and how they collaborate.
2. Learn about [Niche Analysis](niche-analysis.md) to identify profitable niches.
3. Explore the [AI Models](ai-models.md) documentation to learn how to use local AI models.
4. Learn about [Monetization](monetization.md) to create effective subscription models.
5. Explore the [Marketing](marketing.md) documentation to create targeted marketing campaigns.
6. Learn about the [UI](ui.md) to interact with the framework through a web interface.
