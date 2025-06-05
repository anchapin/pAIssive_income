"""
Evaluation script for Artist RL module.

Measures performance of baseline and trained agents on multi-step tool-use tasks.
"""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import gymnasium as gym


def evaluate_agent(
    env: gym.Env,
    agent: object,  # noqa: ARG001
    episodes: int,
    max_steps: int,
) -> dict[str, Any]:
    """
    Evaluate the agent on the environment.

    Args:
        env: RL environment instance.
        agent: RL agent instance.
        episodes (int): Number of evaluation episodes.
        max_steps (int): Max steps per episode.

    Returns:
        dict: Evaluation metrics.

    """
    rewards = []
    for _ in range(episodes):
        obs = env.reset()
        done = False
        total_reward = 0.0
        for _ in range(max_steps):
            # Placeholder: agent policy (replace with agent.predict(obs) if available)
            action = env.action_space.sample()
            obs, reward, done, truncated, info = env.step(action)
            done = done or truncated  # Combine done and truncated flags
            total_reward += float(reward)
            if done:
                break
        rewards.append(total_reward)
    avg_reward = sum(rewards) / len(rewards) if rewards else 0.0
    return {"avg_reward": avg_reward, "all_rewards": rewards}


def main() -> None:
    """
    Evaluate RL agent on ArtistRLEnv.

    Parse arguments and run evaluation.
    """
    parser = argparse.ArgumentParser(description="Evaluate RL agent on ArtistRLEnv.")
    parser.add_argument(
        "--episodes", type=int, default=5, help="Number of evaluation episodes."
    )
    parser.add_argument(
        "--max-steps", type=int, default=50, help="Max steps per episode."
    )

    args = parser.parse_args()

    from .env import ArtistRLEnv

    env = ArtistRLEnv()
    agent = None  # Placeholder: load agent here

    metrics = evaluate_agent(env, agent, args.episodes, args.max_steps)
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Evaluation Results: %s", metrics)

    env.close()


if __name__ == "__main__":
    main()
