"""
Test suite for the Artist RL environment.

Includes:
- Environment reset/step tests
- Minimal train/test cycle stub
"""

import unittest

from ai_models.artist_rl.env import ArtistRLEnv


class TestArtistRLEnv(unittest.TestCase):
    """Unit tests for ArtistRLEnv."""

    def setUp(self) -> None:
        self.env = ArtistRLEnv()

    def tearDown(self) -> None:
        self.env.close()

    def test_reset_returns_observation(self) -> None:
        """reset() should return an initial observation."""
        obs = self.env.reset()
        assert obs is not None

    def test_step_returns_tuple(self) -> None:
        """step() should return (obs, reward, done, info)."""
        self.env.reset()
        action = self.env.action_space.sample()
        result = self.env.step(action)
        assert len(result) == 4
        obs, reward, done, info = result
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        assert isinstance(info, dict)

    def test_minimal_train_test_cycle(self) -> None:
        """Minimal train/test loop: run env for a few steps."""
        obs = self.env.reset()
        total_reward = 0.0
        for _ in range(5):
            action = self.env.action_space.sample()
            obs, reward, done, info = self.env.step(action)
            total_reward += reward
            if done:
                break
        assert isinstance(total_reward, float)

if __name__ == "__main__":
    unittest.main()
