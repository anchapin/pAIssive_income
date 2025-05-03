"""
Load distribution tests for the system.

This module contains tests to evaluate the system's behavior under
geographically distributed load, regional failover scenarios, and
load balancing optimization.
"""

import asyncio
import json
import os
import random
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytest

from services.discovery.load_balancing import (
    LeastConnectionsLoadBalancer,
    RoundRobinLoadBalancer,
    WeightedRandomLoadBalancer,
)

# Import necessary services and utilities
from services.discovery.service_registry import ServiceRegistry


# Mock classes for testing
class MockRegionalEndpoint:
    """Mock regional endpoint for testing."""

    def __init__(self, region: str, latency: float, failure_rate: float = 0.0):
        """
        Initialize a mock regional endpoint.

        Args:
            region: Region name (e.g., 'us - east', 'eu - west')
            latency: Simulated latency in seconds
            failure_rate: Probability of request failure (0.0 to 1.0)
        """
        self.region = region
        self.latency = latency
        self.failure_rate = failure_rate
        self.request_count = 0
        self.failed_requests = 0
        self.total_latency = 0
        self.is_available = True

    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a request to this endpoint.

        Args:
            request_data: The request data

        Returns:
            Response data

        Raises:
            Exception: If the endpoint fails the request
        """
        if not self.is_available:
            raise Exception(f"Region {self.region} is unavailable")

        # Simulate latency
        await asyncio.sleep(self.latency)

        # Record metrics
        self.request_count += 1
        self.total_latency += self.latency

        # Simulate failure
        if random.random() < self.failure_rate:
            self.failed_requests += 1
            raise Exception(f"Request failed in region {self.region}")

        # Return mock response
        return {
            "region": self.region,
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4()),
            "data": request_data,
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics for this endpoint."""
        return {
            "region": self.region,
            "request_count": self.request_count,
            "failed_requests": self.failed_requests,
            "failure_rate": (
                self.failed_requests / self.request_count if self.request_count > 0 else 0
            ),
            "average_latency": (
                self.total_latency / self.request_count if self.request_count > 0 else 0
            ),
            "is_available": self.is_available,
        }


class GeoDistributedLoadTester:
    """Test harness for geographically distributed load testing."""

    def __init__(self):
        """Initialize the load tester."""
        # Create mock regional endpoints with different latencies
        self.endpoints = {
            "us - east": MockRegionalEndpoint("us - east", 0.05),
            "us - west": MockRegionalEndpoint("us - west", 0.08),
            "eu - west": MockRegionalEndpoint("eu - west", 0.15),
            "eu - central": MockRegionalEndpoint("eu - central", 0.12),
            "ap - southeast": MockRegionalEndpoint("ap - southeast", 0.20),
            "ap - northeast": MockRegionalEndpoint("ap - northeast", 0.18),
        }

        # Initialize results
        self.results = {
            "start_time": None,
            "end_time": None,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_latency": 0,
            "regional_metrics": {},
        }

    async def run_distributed_load_test(
        self,
        requests_per_region: int,
        concurrency: int,
        request_distribution: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Run a geographically distributed load test.

        Args:
            requests_per_region: Number of requests to send to each region
            concurrency: Maximum number of concurrent requests
            request_distribution: Optional distribution of requests across regions
                                 (e.g., {"us - east": 0.4, "eu - west": 0.3, "ap - southeast": 0.3})

        Returns:
            Test results
        """
        # Reset results
        self.results = {
            "start_time": time.time(),
            "end_time": None,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_latency": 0,
            "regional_metrics": {},
        }

        # Create request distribution if not provided
        if request_distribution is None:
            # Equal distribution across all regions
            request_distribution = {region: 1.0 / len(self.endpoints) for region in self.endpoints}

        # Calculate number of requests per region based on distribution
        total_requests = requests_per_region * len(self.endpoints)
        region_requests = {
            region: int(total_requests * weight) for region, weight in request_distribution.items()
        }

        # Ensure we're not missing any requests due to rounding
        remaining = total_requests - sum(region_requests.values())
        if remaining > 0:
            # Add remaining requests to the region with the highest weight
            max_region = max(request_distribution.items(), key=lambda x: x[1])[0]
            region_requests[max_region] += remaining

        # Create a queue of requests
        request_queue = asyncio.Queue()

        # Add requests to the queue
        for region, count in region_requests.items():
            for i in range(count):
                request_data = {"id": i, "region": region, "timestamp": time.time()}
                await request_queue.put((region, request_data))

        # Start worker tasks
        workers = [
            asyncio.create_task(self._process_request(request_queue)) for _ in range(concurrency)
        ]

        # Wait for all requests to be processed
        await request_queue.join()

        # Cancel worker tasks
        for worker in workers:
            worker.cancel()

        # Calculate final results
        self.results["end_time"] = time.time()
        self.results["total_duration"] = self.results["end_time"] - self.results["start_time"]

        # Get regional metrics
        for region, endpoint in self.endpoints.items():
            self.results["regional_metrics"][region] = endpoint.get_metrics()

        # Calculate overall metrics
        self.results["total_requests"] = sum(e.request_count for e in self.endpoints.values())
        self.results["failed_requests"] = sum(e.failed_requests for e in self.endpoints.values())
        self.results["successful_requests"] = (
            self.results["total_requests"] - self.results["failed_requests"]
        )

        total_latency = sum(e.total_latency for e in self.endpoints.values())
        if self.results["total_requests"] > 0:
            self.results["average_latency"] = total_latency / self.results["total_requests"]

        return self.results

    async def _process_request(self, queue: asyncio.Queue) -> None:
        """
        Process requests from the queue.

        Args:
            queue: Queue of requests to process
        """
        while True:
            # Get a request from the queue
            region, request_data = await queue.get()

            try:
                # Get the endpoint for this region
                endpoint = self.endpoints.get(region)
                if endpoint is None:
                    raise ValueError(f"Unknown region: {region}")

                # Send the request
                await endpoint.handle_request(request_data)

            except Exception as e:
                # Log the error
                print(f"Error processing request: {str(e)}")

            finally:
                # Mark the task as done
                queue.task_done()

    async def simulate_regional_failure(self, region: str, duration: float) -> None:
        """
        Simulate a regional failure.

        Args:
            region: The region to fail
            duration: Duration of the failure in seconds
        """
        endpoint = self.endpoints.get(region)
        if endpoint is None:
            raise ValueError(f"Unknown region: {region}")

        # Mark the region as unavailable
        endpoint.is_available = False

        # Wait for the specified duration
        await asyncio.sleep(duration)

        # Mark the region as available again
        endpoint.is_available = True


async def test_geographically_distributed_load():
    """Test system behavior under geographically distributed load."""
    # Create the load tester
    tester = GeoDistributedLoadTester()

    # Run a distributed load test with equal distribution
    results = await tester.run_distributed_load_test(requests_per_region=100, concurrency=20)

    # Verify results
    assert results["total_requests"] == 600  # 100 requests * 6 regions
    assert results["successful_requests"] == 600  # All should succeed

    # Run a distributed load test with custom distribution
    custom_distribution = {
        "us - east": 0.4,  # 40% of requests
        "eu - west": 0.3,  # 30% of requests
        "ap - southeast": 0.3,  # 30% of requests
    }

    results = await tester.run_distributed_load_test(
        requests_per_region=100, concurrency=20, request_distribution=custom_distribution
    )

    # Verify results
    assert results["total_requests"] == 600  # 100 requests * 6 regions
    assert results["regional_metrics"]["us - east"]["request_count"] > 200  # ~40% of 600
    assert results["regional_metrics"]["eu - west"]["request_count"] > 150  # ~30% of 600
    assert results["regional_metrics"]["ap - southeast"]["request_count"] > 150  # ~30% of 600

    # Print results
    print(json.dumps(results, indent=2))


async def test_regional_failover():
    """Test regional failover scenarios."""
    # Create the load tester
    tester = GeoDistributedLoadTester()

    # Set up a custom distribution focusing on us - east
    distribution = {
        "us - east": 0.6,  # 60% of requests
        "us - west": 0.2,  # 20% of requests
        "eu - west": 0.1,  # 10% of requests
        "eu - central": 0.1,  # 10% of requests
        "ap - southeast": 0.0,
        "ap - northeast": 0.0,
    }

    # Start a background task to simulate a regional failure after 1 second
    failover_task = asyncio.create_task(tester.simulate_regional_failure("us - east", duration=2.0))

    # Run a distributed load test
    results = await tester.run_distributed_load_test(
        requests_per_region=50, concurrency=20, request_distribution=distribution
    )

    # Wait for the failover task to complete
    await failover_task

    # Verify results
    assert results["failed_requests"] > 0  # Some requests should have failed
    assert results["regional_metrics"]["us - east"]["failed_requests"] > 0

    # Print results
    print(json.dumps(results, indent=2))


async def test_load_balancing_optimization():
    """Test load balancing optimization."""
    # Create a service registry
    registry = ServiceRegistry()

    # Register services in different regions
    services = []
    for i, region in enumerate(["us - east", "us - west", "eu - west", "ap - southeast"]):
        service = {
            "service_id": f"api - service-{i + 1}",
            "service_name": "api - service",
            "host": f"api-{region}.example.com",
            "port": 8080,
            "region": region,
            "health": "healthy",
            "metadata": {
                "region": region,
                "latency": 50 + i * 25,  # Simulated latency in ms
                "capacity": 100 - i * 20,  # Simulated capacity
            },
        }
        registry.register_service(**service)
        services.append(service)

    # Test round - robin load balancer
    round_robin = RoundRobinLoadBalancer()

    # Get instances multiple times
    selected_regions = []
    for _ in range(8):  # Should cycle through all instances twice
        instance = round_robin.get_instance(registry.get_services("api - service"))
        selected_regions.append(instance["region"])

    # Verify round - robin distribution
    assert len(set(selected_regions)) == 4  # All regions used
    assert selected_regions[:4] != selected_regions[4:]  # Different order in cycles

    # Test weighted load balancer based on capacity
    def capacity_weight(instance):
        """Calculate weight based on capacity."""
        return instance["metadata"].get("capacity", 50)

    weighted = WeightedRandomLoadBalancer(weight_function=capacity_weight)

    # Select instances multiple times
    region_counts = {"us - east": 0, "us - west": 0, "eu - west": 0, "ap - southeast": 0}
    for _ in range(1000):
        instance = weighted.get_instance(registry.get_services("api - service"))
        region_counts[instance["region"]] += 1

    # Verify weighted distribution - regions with higher capacity should be selected more often
    assert region_counts["us - east"] > region_counts["us - west"]
    assert region_counts["us - west"] > region_counts["eu - west"]
    assert region_counts["eu - west"] > region_counts["ap - southeast"]

    # Test least connections load balancer
    least_conn = LeastConnectionsLoadBalancer()

    # Simulate connections
    connections = {
        "api - service - 1": 50,  # us - east
        "api - service - 2": 30,  # us - west
        "api - service - 3": 10,  # eu - west
        "api - service - 4": 5,  # ap - southeast
    }

    for service_id, count in connections.items():
        for _ in range(count):
            least_conn.increment_connections(service_id)

    # Select an instance - should be the one with fewest connections
    instance = least_conn.get_instance(registry.get_services("api - service"))
    assert instance["region"] == "ap - southeast"  # Should be the one with fewest connections

    # Print results
    print(f"Round - robin distribution: {selected_regions}")
    print(f"Weighted distribution: {region_counts}")
    print(f"Least connections selected: {instance['region']}")


async def main():
    """Run all tests."""
    print("\n=== Testing Geographically Distributed Load ===")
    await test_geographically_distributed_load()

    print("\n=== Testing Regional Failover ===")
    await test_regional_failover()

    print("\n=== Testing Load Balancing Optimization ===")
    await test_load_balancing_optimization()


if __name__ == "__main__":
    asyncio.run(main())
