"""
RL training script for ArtistRLEnv.

This script sets up argument parsing, environment creation, and the main RL training loop.
"""

from __future__ import annotations

import argparse


def main() -> None:
    """
    Main entry point for RL training.
    Parses arguments, initializes environment, and runs the training loop.
    """
    parser = argparse.ArgumentParser(description="Train an RL agent on ArtistRLEnv.")
    parser.add_argument(
        "--episodes", type=int, default=10, help="Number of training episodes."
    )
    parser.add_argument(
        "--max-steps", type=int, default=50, help="Max steps per episode."
    )
    # Add more arguments as needed (e.g., learning rate, agent type)

    args = parser.parse_args()

    # Lazy import to avoid unnecessary dependencies for docs/tests
    from .env import ArtistRLEnv

    env = ArtistRLEnv()

    for episode in range(args.episodes):
        obs = env.reset()
        done = False
        total_reward = 0.0
        for step in range(args.max_steps):
            # Placeholder: random action
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)
            total_reward += reward
            if done:
                break
        print(f"Episode {episode + 1}: Total Reward = {total_reward}")

    env.close()


if __name__ == "__main__":
    main()
