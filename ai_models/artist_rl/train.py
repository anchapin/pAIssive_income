"""
RL training script for ArtistRLEnv.

This script sets up argument parsing, environment creation, and the main RL training loop.
"""

import argparse


def main() -> None:
    """
    Train RL agent on ArtistRLEnv.

    Parse arguments, initialize environment, and run the training loop.
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
        for _step in range(args.max_steps):
            # Placeholder: random action
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)
            total_reward += reward
            if done:
                break
        import logging

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info("Episode %d: Total Reward = %f", episode + 1, total_reward)

    env.close()


if __name__ == "__main__":
    main()
