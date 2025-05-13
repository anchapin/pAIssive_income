# Getting Started with pAIssive Income Framework

> **Audience:** New users, developers, and contributors looking to set up or use the framework.

This guide will help you get started with the pAIssive Income Framework. It covers installation, basic configuration, and a simple example to demonstrate the framework's capabilities.

**If you arrived here from the main README, you're in the right place!**

## Prerequisites

- Python 3.8 or higher
- [`uv`](https://github.com/astral-sh/uv) (Python package installer and resolver)
- Node.js 16.10+ (for UI components)
- [`pnpm`](https://pnpm.io/) (Node.js package manager)
- Git (optional, for cloning the repository)

> **Important:** This project requires using `uv` for Python package management and `pnpm` for Node.js package management. Do not use `pip`, `venv`, `npm`, or `yarn` directly.

## Installation

### Step 1: Install Required Package Managers

#### Install uv

```bash
# Recommended (Linux/macOS/Windows with curl)
curl -LsSf https://astral.sh/uv/install.sh | sh

# If curl is unavailable, you may use pip ONLY for this step:
pip install uv
```

#### Install pnpm

```bash
# Recommended (using Corepack, included with Node.js v16.10+)
corepack enable

# If Corepack is not available, you may use npm ONLY for this step:
npm install -g pnpm
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/anchapin/pAIssive_income.git
cd pAIssive_income
```

### Step 3: Set Up Development Environment

#### Automated Setup (Recommended)

```bash
# On Windows
enhanced_setup_dev_environment.bat

# On Unix/Linux
./enhanced_setup_dev_environment.sh
```

#### Manual Setup

```bash
# Create virtual environment with uv
uv venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies with uv
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
uv pip install -e .

# Install Node.js dependencies with pnpm
pnpm install
```

### Option 2: Install from Source

```bash
uv pip install git+https://github.com/anchapin/pAIssive_income.git
```

## Development Tools

### Code Quality and Testing

- **Lint and format code:**

  ```bash
  python scripts/manage_quality.py lint
  ```

- **Run tests:**

  ```bash
  python scripts/manage_quality.py test
  ```

- **Fix syntax/formatting issues:**

  ```bash
  python scripts/manage_quality.py fix
  ```

- **Run local CI workflow:**

  ```bash
  python run_github_actions_locally.py --list
  ```

## Basic Configuration

...

```python
from ai_models import ModelConfig

## Environment Setup (Recommended)
```

## Running the UI

The framework includes a web interface that you can use to interact with the framework components. To run the UI:

```bash
python run_ui.py
```

This will start a web server at `http://localhost:5000` where you can access the UI.

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
