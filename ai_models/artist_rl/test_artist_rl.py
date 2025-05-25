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

    def setUp(self):
        self.env = ArtistRLEnv()

    def tearDown(self):
        self.env.close()

    def test_reset_returns_observation(self):
        """reset() should return an initial observation."""
        obs = self.env.reset()
        self.assertIsNotNone(obs)

    def test_step_returns_tuple(self):
        """step() should return (obs, reward, done, info)."""
        self.env.reset()
        action = self.env.action_space.sample()
        result = self.env.step(action)
        self.assertEqual(len(result), 4)
        obs, reward, done, info = result
        self.assertIsInstance(reward, float)
        self.assertIsInstance(done, bool)
        self.assertIsInstance(info, dict)

    def test_minimal_train_test_cycle(self):
        """Minimal train/test loop: run env for a few steps."""
        obs = self.env.reset()
        total_reward = 0.0
        for _ in range(5):
            action = self.env.action_space.sample()
            obs, reward, done, info = self.env.step(action)
            total_reward += reward
            if done:
                break
        self.assertIsInstance(total_reward, float)

if __name__ == "__main__":
    unittest.main()
