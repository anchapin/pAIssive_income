# Artist RL Module

This module provides a Gym-style reinforcement learning (RL) environment and training utilities for multi-step tool-use tasks using an `ArtistAgent`. It is intended for research and development of RL agents capable of reasoning and acting in complex, multi-step scenarios.

## Structure

- `env.py`: RL environment (`ArtistRLEnv`) wrapping the `ArtistAgent`.
- `train.py`: Script for training RL agents on tool-use tasks.
- `evaluate.py`: Script for evaluating baseline or trained agents.
- `test_artist_rl.py`: Test suite for the environment and minimal RL loop.
- `__init__.py`: Module docstring.
- `README.md`: This file.

## Usage

- **Training**:  
  ```bash
  python -m ai_models.artist_rl.train --episodes 100 --max-steps 50
  ```

- **Evaluation**:  
  ```bash
  python -m ai_models.artist_rl.evaluate --episodes 10 --max-steps 50
  ```

## Setup

1. **Dependencies**:  
   This module requires Python 3.8+ and [Gymnasium](https://gymnasium.farama.org/) or [Gym](https://www.gymlibrary.dev/).
   Install dependencies using [uv](https://github.com/astral-sh/uv) (recommended for this project):

   ```
   uv pip install gymnasium
   ```

   (Or install additional RL libraries as needed.)

2. **Project conventions**:
   - Do not use `pip` or `venv`; use `uv` for Python dependency management.
   - Respect `.gitignore` for all scripts, tests, and outputs.

## Intended Use

- Develop, train, and evaluate RL agents for artistic, tool-use, or reasoning tasks.
- Extend the environment to support richer observation/action spaces and real ArtistAgent integration.

## Notes

- All files are stubs or placeholders; fill in with actual environment logic and agent implementations as needed.
- Keep tests and documentation up to date with code changes.