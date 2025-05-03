"""
Tests for API rate limiting functionality.
"""


import time
import unittest

from api.config import APIConfig, RateLimitScope, RateLimitStrategy
from api.rate_limit import 

(
    FixedWindowRateLimiter,
    LeakyBucketRateLimiter,
    RateLimitManager,
    SlidingWindowRateLimiter,
    TokenBucketRateLimiter,
)


class TestRateLimiting(unittest.TestCase):
    """Test cases for API rate limiting."""

def setUp(self):
        """Set up test fixtures."""
        self.config = APIConfig(
            enable_rate_limit=True,
            rate_limit_strategy=RateLimitStrategy.TOKEN_BUCKET,
            rate_limit_scope=RateLimitScope.IP,
            rate_limit_requests=100,
            rate_limit_period=60,
            rate_limit_burst=50,
            rate_limit_tiers={
                "default": 100,
                "basic": 300,
                "premium": 1000,
                "unlimited": 0,
            },
            endpoint_rate_limits={"/api/v1/ai-models/inference": 20},
            rate_limit_exempt_ips={"127.0.0.1"},
            rate_limit_exempt_api_keys={"test-api-key"},
        )
        self.manager = RateLimitManager(self.config)

def test_fixed_window_rate_limiter(self):
        """Test fixed window rate limiting strategy."""
        limiter = FixedWindowRateLimiter(limit=5, window=1)
        client_id = "test_client"

# Test successful requests within limit
        for _ in range(5):
            allowed, info = limiter.check_rate_limit(client_id)
            self.assertTrue(allowed)
            self.assertEqual(info["limit"], 5)
            self.assertGreaterEqual(info["remaining"], 0)

# Test request exceeding limit
        allowed, info = limiter.check_rate_limit(client_id)
        self.assertFalse(allowed)
        self.assertEqual(info["remaining"], 0)
        self.assertGreater(info["retry_after"], 0)

# Test window reset
        time.sleep(1)
        allowed, info = limiter.check_rate_limit(client_id)
        self.assertTrue(allowed)
        self.assertEqual(info["remaining"], 4)

def test_token_bucket_rate_limiter(self):
        """Test token bucket rate limiting strategy."""
        limiter = TokenBucketRateLimiter(rate=10.0, burst=20)
        client_id = "test_client"

# Test burst capacity
        for _ in range(20):
            allowed, info = limiter.check_rate_limit(client_id)
            self.assertTrue(allowed)

# Test request exceeding burst capacity
        allowed, info = limiter.check_rate_limit(client_id)
        self.assertFalse(allowed)
        self.assertGreater(info["retry_after"], 0)

# Test token replenishment
        time.sleep(0.2)  # Wait for 2 tokens to be replenished
        allowed, info = limiter.check_rate_limit(client_id)
        self.assertTrue(allowed)

def test_leaky_bucket_rate_limiter(self):
        """Test leaky bucket rate limiting strategy."""
        limiter = LeakyBucketRateLimiter(rate=10.0, capacity=10)
        client_id = "test_client"

# Test filling the bucket
        for _ in range(10):
            allowed, info = limiter.check_rate_limit(client_id)
            self.assertTrue(allowed)

# Test request exceeding capacity
        allowed, info = limiter.check_rate_limit(client_id)
        self.assertFalse(allowed)
        self.assertGreater(info["retry_after"], 0)

# Test leaking
        time.sleep(0.2)  # Wait for 2 requests worth of leakage
        allowed, info = limiter.check_rate_limit(client_id)
        self.assertTrue(allowed)

def test_sliding_window_rate_limiter(self):
        """Test sliding window rate limiting strategy."""
        limiter = SlidingWindowRateLimiter(limit=5, window=1)
        client_id = "test_client"

# Test requests within window
        for _ in range(5):
            allowed, info = limiter.check_rate_limit(client_id)
            self.assertTrue(allowed)

# Test request exceeding window limit
        allowed, info = limiter.check_rate_limit(client_id)
        self.assertFalse(allowed)
        self.assertEqual(info["remaining"], 0)

# Test sliding window behavior
        time.sleep(0.5)  # Wait for half the window
        # Some old requests should have expired
        allowed, info = limiter.check_rate_limit(client_id)
        self.assertTrue(allowed)

def test_rate_limit_tiers(self):
        """Test rate limit tiers."""
        # Test default tier
        limit = self.manager.get_rate_limit_tier(None)
        self.assertEqual(limit, 100)

# Test basic tier
        limit = self.manager.get_rate_limit_tier("basic-api-key")
        self.assertEqual(
            limit, 100
        )  # Default tier since we don't have tier lookup implemented

def test_endpoint_specific_limits(self):
        """Test endpoint-specific rate limits."""
        client_id = "test_client"
        endpoint = "/api/v1/ai-models/inference"

# Test endpoint-specific limit
        for _ in range(20):
            allowed, info = self.manager.check_rate_limit(client_id, endpoint)
            self.assertTrue(allowed)

# Test request exceeding endpoint limit
        allowed, info = self.manager.check_rate_limit(client_id, endpoint)
        self.assertFalse(allowed)

def test_rate_limit_exemptions(self):
        """Test rate limit exemptions."""
        # Test exempt IP
        allowed, info = self.manager.check_rate_limit("127.0.0.1")
        self.assertTrue(allowed)
        self.assertEqual(info["limit"], 0)  # 0 means no limit

# Test exempt API key
        allowed, info = self.manager.check_rate_limit(
            "non-exempt-ip", api_key="test-api-key"
        )
        self.assertTrue(allowed)
        self.assertEqual(info["limit"], 0)

def test_rate_limit_headers(self):
        """Test rate limit headers."""
        client_id = "test_client"

# Make some requests to get non-zero rate limit info
        _, limit_info = self.manager.check_rate_limit(client_id)

# Get headers
        headers = self.manager.get_rate_limit_headers(limit_info)

# Verify required headers are present
        self.assertIn("X-RateLimit-Limit", headers)
        self.assertIn("X-RateLimit-Remaining", headers)
        self.assertIn("X-RateLimit-Reset", headers)

# Verify header values
        self.assertEqual(headers["X-RateLimit-Limit"], str(limit_info["limit"]))
        self.assertEqual(headers["X-RateLimit-Remaining"], str(limit_info["remaining"]))
        self.assertEqual(headers["X-RateLimit-Reset"], str(int(limit_info["reset"])))


if __name__ == "__main__":
    unittest.main()