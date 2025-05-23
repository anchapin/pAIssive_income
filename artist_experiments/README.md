# ARTIST Experiments

## Recent Updates

- **April 2024:** ARTIST experiment environment isolation improved. Dedicated uv-based and Docker-based setup provided, dependencies tracked in `requirements-artist.txt`, robust `.gitignore` exclusions for outputs, and documentation/testing updated for reproducibility and clarity.

This directory contains experiments related to the ARTIST (Agentic Reasoning and Tool Integration in Self-improving Transformers) framework developed by Microsoft Research.

## Overview

The ARTIST framework combines agentic reasoning, reinforcement learning, and dynamic tool use to enhance the capabilities of Large Language Models (LLMs). This isolated environment allows for experimentation with ARTIST concepts without affecting the main project.

## Setup

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

## Directory Structure

- `data/`: Data files for experiments
- `logs/`: Log files
- `models/`: Saved models and checkpoints
- `requirements-artist.txt`: Python dependencies for ARTIST experiments
- `setup_artist_env.ps1`: Windows setup script
- `setup_artist_env.sh`: Linux/macOS setup script
- `docker-compose.artist.yml`: Docker Compose configuration
- `Dockerfile.artist`: Docker configuration
- `run_artist.py`: Flask application for running experiments

## Available Experiments

### 1. Enhanced Mathematical Problem-Solving

This experiment extends the existing calculator tool integration with ARTIST's reinforcement learning approach to solve more complex mathematical problems.

### 2. Multi-API Orchestration for Market Research

This experiment implements an ARTIST-based agent that can orchestrate multiple APIs to gather and analyze market research data.

## Dependencies

The ARTIST experiments require the following key dependencies:

- Python 3.10+
- PyTorch 1.10.0+
- Transformers 4.20.0+
- SymPy 1.11.0+
- Flask 2.0.1+
- Pandas 1.3.0+
- Matplotlib 3.5.0+

See `requirements-artist.txt` for the complete list of dependencies.

## References

- [ARTIST Framework Research Report](../docs/research/artist_framework_research_report.md)
- [ARTIST Framework Summary](../docs/research/artist_framework_summary.md)
- [ARTIST Framework Pilot Use Cases](../docs/research/artist_framework_pilot_use_cases.md)
- [ARTIST Framework Implementation Recommendations](../docs/research/artist_framework_implementation_recommendations.md)
