"""
Evaluation script for Artist RL module.

Measures performance of baseline and trained agents on multi-step tool-use tasks.
"""

import argparse

from .env import ArtistRLEnv


def evaluate_agent(env: ArtistRLEnv, episodes: int, max_steps: int) -> dict:
    """
    Evaluate the agent on the environment.

    Args:
        env: RL environment instance.
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
            obs, reward, done, info = env.step(action)
            total_reward += reward
            if done:
                break
        rewards.append(total_reward)
    avg_reward = sum(rewards) / len(rewards) if rewards else 0.0
    return {"avg_reward": avg_reward, "all_rewards": rewards}


def main() -> None:
    """Run evaluation of RL agent."""
    parser = argparse.ArgumentParser(description="Evaluate RL agent on ArtistRLEnv.")
    parser.add_argument(
        "--episodes", type=int, default=5, help="Number of evaluation episodes."
    )
    parser.add_argument(
        "--max-steps", type=int, default=50, help="Max steps per episode."
    )
    args = parser.parse_args()

    env = ArtistRLEnv()
    evaluate_agent(env, args.episodes, args.max_steps)

    env.close()


if __name__ == "__main__":
    main()
