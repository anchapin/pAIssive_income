# ARTIST Experiments

This document provides information about the ARTIST (Agentic Reasoning and Tool Integration in Self-improving Transformers) experiments implemented in the project.

## Recent Updates

- **April 2024:** ARTIST experiment environment isolation improved. Dedicated uv-based and Docker-based setup provided, dependencies tracked in `requirements-artist.txt`, robust `.gitignore` exclusions for outputs, and documentation/testing updated for reproducibility and clarity.

## Overview

The ARTIST framework combines agentic reasoning, reinforcement learning, and dynamic tool use to enhance the capabilities of Large Language Models (LLMs). The isolated experiment environment allows for exploration of ARTIST concepts without affecting the main project.

## Directory Structure

The ARTIST experiments are organized in a dedicated `artist_experiments` directory with the following structure:

- `__init__.py` - Makes the directory a proper Python package
- `requirements-artist.txt` - ARTIST-specific dependencies
- `setup_artist_env.ps1` - Windows setup script
- `setup_artist_env.sh` - Linux/macOS setup script
- `docker-compose.artist.yml` - Docker Compose configuration
- `Dockerfile.artist` - Docker configuration
- `run_artist.py` - Flask application for running experiments
- `math_problem_solving.py` - Mathematical problem-solving experiment
- `multi_api_orchestration.py` - Multi-API orchestration experiment
- `test_artist_experiments.py` - Tests for the experiments
- `README.md` - Documentation for the ARTIST experiments

## Setup Instructions

The ARTIST experiment environment can be set up using either a Python virtual environment or Docker.

### Using Python Virtual Environment

#### Windows (PowerShell)

```powershell
# Run the setup script
.\artist_experiments\setup_artist_env.ps1

# Activate the virtual environment
.\artist_experiments\.venv-artist\Scripts\Activate.ps1
```

#### Linux/macOS

```bash
# Make the setup script executable
chmod +x artist_experiments/setup_artist_env.sh

# Run the setup script
./artist_experiments/setup_artist_env.sh

# Activate the virtual environment
source artist_experiments/.venv-artist/bin/activate
```

### Using Docker

```bash
# Build and start the Docker containers
docker-compose -f artist_experiments/docker-compose.artist.yml up -d

# Check the status of the containers
docker-compose -f artist_experiments/docker-compose.artist.yml ps

# View logs
docker-compose -f artist_experiments/docker-compose.artist.yml logs -f
```

## Available Experiments

### 1. Enhanced Mathematical Problem-Solving

This experiment extends the existing calculator tool integration with ARTIST's reinforcement learning approach to solve more complex mathematical problems. It uses the SymPy library to provide advanced mathematical capabilities such as:

- Solving equations
- Factoring expressions
- Expanding expressions

Example usage:

```python
from artist_experiments import run_math_experiment

# Run the math experiment
result = run_math_experiment("Solve the equation x^2 - 5x + 6 = 0")
print(result)  # Output: x = 2, x = 3
```

### 2. Multi-API Orchestration

This experiment implements an ARTIST-based agent that can orchestrate multiple APIs to gather and analyze data. It includes mock implementations of:

- Product search API
- Market trends API
- Competitor analysis API

Example usage:

```python
from artist_experiments import run_api_experiment

# Run the API orchestration experiment
result = run_api_experiment("Find products related to smart home automation")
print(result)  # Output: JSON with product search results
```

## Dependencies

The ARTIST experiments require the following key dependencies:

- Python 3.10+
- PyTorch 1.10.0+
- Transformers 4.20.0+
- SymPy 1.11.0+
- Flask 2.0.1+
- Pandas 1.3.0+
- Matplotlib 3.5.0+

See `artist_experiments/requirements-artist.txt` for the complete list of dependencies.

## Docker Configuration

The Docker configuration for ARTIST experiments includes:

1. A multi-stage build process:
   - Builder stage using `ghcr.io/astral-sh/uv:python3.10-bookworm-slim`
   - Runtime stage using `python:3.10-slim`

2. Separate database container:
   - PostgreSQL 15.3 Alpine
   - Custom database name, user, and password for isolation

3. Network and volume configuration:
   - Dedicated bridge network
   - Persistent volume for database data

4. Health checks:
   - Application health check via HTTP endpoint
   - Database health check via `pg_isready`

## Integration with Main Project

The ARTIST experiments leverage the existing `ArtistAgent` class from the main project's `ai_models` module and the tool registry from the `common_utils` module. This allows for experimentation with enhanced versions of these components without modifying the core codebase.

## Output Directories

The following directories within `artist_experiments/` are used for experiment outputs and are excluded from version control via `.gitignore`:

- `artist_experiments/data/`: For experiment data files
- `artist_experiments/models/`: For trained models
- `artist_experiments/logs/`: For experiment logs

## Running Tests

Tests for the ARTIST experiments can be run using pytest:

```bash
# Activate the virtual environment first
pytest artist_experiments/test_artist_experiments.py -v
```

## Future Work

Future enhancements to the ARTIST experiments may include:

1. Integration with more sophisticated LLMs
2. Implementation of reinforcement learning for tool selection
3. Development of more complex multi-step reasoning capabilities
4. Benchmarking against other agentic frameworks
5. Integration with real-world APIs and data sources
