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
        """Set up the test environment."""
        self.env = ArtistRLEnv()

    def tearDown(self) -> None:
        """Tear down the test environment."""
        self.env.close()

    def test_reset_returns_observation(self) -> None:
        """Test that reset() returns an initial observation."""
        obs = self.env.reset()
        assert obs is not None  # noqa: S101

    def test_step_returns_tuple(self) -> None:
        """Test that step() returns a tuple of length 4 and correct types."""
        self.env.reset()
        action = self.env.action_space.sample()
        result = self.env.step(action)
        tuple_len = 4
        assert len(result) == tuple_len  # noqa: S101
        obs, reward, done, info = result
        assert isinstance(reward, float)  # noqa: S101
        assert isinstance(done, bool)  # noqa: S101
        assert isinstance(info, dict)  # noqa: S101

    def test_minimal_train_test_cycle(self) -> None:
        """Test a minimal train/test cycle for the environment."""
        obs = self.env.reset()
        total_reward = 0.0
        for _ in range(5):
            action = self.env.action_space.sample()
            obs, reward, done, info = self.env.step(action)
            total_reward += reward
            if done:
                break
        assert isinstance(total_reward, float)  # noqa: S101


if __name__ == "__main__":
    unittest.main()
