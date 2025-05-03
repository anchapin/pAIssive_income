
import asyncio
import json
import random
import time
import uuid
from datetime import datetime, timezone
from unittest.mock import patch
import httpx
from api.schemas.webhook import WebhookDeliveryStatus, WebhookEventType
from api.services.webhook_service import WebhookService
import pytest



import asyncio
import json
import random
import time
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import httpx

from api.schemas.webhook import WebhookDeliveryStatus, WebhookEventType
from api.services.webhook_service import WebhookService


import pytest

"""
Load testing for the webhook system.

This module contains tests to evaluate the webhook system's performance under heavy load.
"""





# Test configuration
WEBHOOK_COUNT = 100  # Number of webhooks to create
EVENT_BATCH_SIZE = 1000  # Number of events per batch
TOTAL_EVENTS = 10000  # Total number of events to process
MAX_CONCURRENCY = 100  # Maximum number of concurrent deliveries
TEST_DURATION_SECONDS = 60  # Duration of the load test in seconds

# Mock server configuration
MOCK_SERVERS = [
    {
        "url": "https://server1.example.com/webhook",
        "avg_response_time": 0.05,
        "error_rate": 0.01,
    },
    {
        "url": "https://server2.example.com/webhook",
        "avg_response_time": 0.1,
        "error_rate": 0.05,
    },
    {
        "url": "https://server3.example.com/webhook",
        "avg_response_time": 0.2,
        "error_rate": 0.1,
    },
    {
        "url": "https://server4.example.com/webhook",
        "avg_response_time": 0.5,
        "error_rate": 0.2,
    },
    {
        "url": "https://server5.example.com/webhook",
        "avg_response_time": 1.0,
        "error_rate": 0.3,
    },
]


class MockServer:
    """Mock server for load testing."""

    def __init__(self, url: str, avg_response_time: float, error_rate: float):
        self.url = url
        self.avg_response_time = avg_response_time
        self.error_rate = error_rate
        self.requests_received = 0
        self.successful_requests = 0
        self.failed_requests = 0

    async def handle_request(self, request: httpx.Request) -> httpx.Response:
        """Handle a webhook request."""
        self.requests_received += 1

        # Simulate network delay with some randomness
        delay = random.normalvariate(
            self.avg_response_time, self.avg_response_time * 0.2
        )
        delay = max(0.01, delay)  # Ensure delay is at least 10ms
        await asyncio.sleep(delay)

        # Determine if request should fail
        should_fail = random.random() < self.error_rate

        if should_fail:
            self.failed_requests += 1
            response = httpx.Response(
                status_code=random.choice([429, 500, 502, 503, 504]),
                content=f"Error processing webhook: {random.choice(['Timeout', 'Server Error', 'Rate Limited'])}".encode(),
                request=request,
            )
        else:
            self.successful_requests += 1
            response = httpx.Response(
                status_code=200,
                content=json.dumps(
                    {"success": True, "message": "Webhook received"}
                ).encode(),
                request=request,
            )

                return response


class LoadTestEnvironment:
    """Environment for load testing webhooks."""

    def __init__(self):
        self.service = WebhookService()
        self.mock_servers = [MockServer(**server) for server in MOCK_SERVERS]
        self.webhooks = []
        self.events_queue = asyncio.Queue()
        self.results = {
            "start_time": None,
            "end_time": None,
            "total_duration": 0,
            "total_events": 0,
            "successful_events": 0,
            "failed_events": 0,
            "events_per_second": 0,
            "webhook_stats": [],
            "server_stats": [],
            "latency_stats": {
                "min": 0,
                "max": 0,
                "avg": 0,
                "p50": 0,
                "p90": 0,
                "p95": 0,
                "p99": 0,
            },
        }
        self.latencies = []

    async def setup(self):
        """Set up the test environment."""
        # Start the webhook service
        await self.service.start()

        # Create test webhooks
        for i in range(WEBHOOK_COUNT):
            # Select a random mock server
            server = random.choice(self.mock_servers)

            # Create webhook data
            webhook_data = {
                "url": server.url,
                "events": [
                    WebhookEventType.USER_CREATED,
                    WebhookEventType.PAYMENT_RECEIVED,
                    WebhookEventType.SUBSCRIPTION_CREATED,
                ],
                "description": f"Load test webhook {i}",
                "headers": {"Authorization": f"Bearer test-token-{i}"},
                "is_active": True,
            }

            # Register webhook
            webhook = await self.service.register_webhook(webhook_data)
            webhook["server"] = server  # Store reference to mock server
            self.webhooks.append(webhook)

    async def teardown(self):
        """Clean up the test environment."""
        # Delete all webhooks
        for webhook in self.webhooks:
            await self.service.delete_webhook(webhook["id"])

        # Stop the webhook service
        await self.service.stop()

    async def generate_events(self, count: int):
        """Generate test events and add them to the queue."""
        for i in range(count):
            # Create event data
            event_data = {
                "id": str(uuid.uuid4()),
                "user_id": f"user-{random.randint(1, 1000)}",
                "username": f"testuser{random.randint(1, 1000)}",
                "email": f"test{random.randint(1, 1000)}@example.com",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "source": "load_test",
                    "batch": i // EVENT_BATCH_SIZE,
                    "index": i,
                },
            }

            # Select a random webhook and event type
            webhook = random.choice(self.webhooks)
            event_type = random.choice(webhook["events"])

            # Add to queue
            await self.events_queue.put((webhook, event_type, event_data))

    async def process_events(self, worker_id: int):
        """Process events from the queue."""
        while True:
            try:
                # Get next event from queue with timeout
                try:
                    webhook, event_type, event_data = await asyncio.wait_for(
                        self.events_queue.get(), timeout=0.1
                    )
                except asyncio.TimeoutError:
                    # Check if we should continue
                    if (
                        self.events_queue.empty()
                        and time.time() - self.results["start_time"]
                        >= TEST_DURATION_SECONDS
                    ):
                        break
                    continue

                # Mock the server response
                server = webhook["server"]

                # Patch httpx.AsyncClient.post to use our mock server
                async def mock_post(*args, **kwargs):
                            return await server.handle_request(
                        httpx.Request("POST", server.url)
                    )

                with patch("httpx.AsyncClient.post", mock_post):
                    # Record start time
                    start_time = time.time()

                    # Deliver event
                    try:
                        delivery = await self.service.deliver_event(
                            webhook_id=webhook["id"],
                            event_type=event_type,
                            event_data=event_data,
                        )

                        # Record latency
                        latency = time.time() - start_time
                        self.latencies.append(latency)

                        # Update stats
                        if delivery["status"] == WebhookDeliveryStatus.SUCCESS:
                            self.results["successful_events"] += 1
                        else:
                            self.results["failed_events"] += 1

                        self.results["total_events"] += 1

                    except Exception as e:
                        self.results["failed_events"] += 1
                        self.results["total_events"] += 1
                        print(f"Worker {worker_id} error: {str(e)}")

                # Mark task as done
                self.events_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker {worker_id} unexpected error: {str(e)}")

    def calculate_latency_percentiles(self):
        """Calculate latency percentiles."""
        if not self.latencies:
                    return sorted_latencies = sorted(self.latencies)
        self.results["latency_stats"]["min"] = sorted_latencies[0]
        self.results["latency_stats"]["max"] = sorted_latencies[-1]
        self.results["latency_stats"]["avg"] = sum(sorted_latencies) / len(
            sorted_latencies
        )
        self.results["latency_stats"]["p50"] = sorted_latencies[
            int(len(sorted_latencies) * 0.5)
        ]
        self.results["latency_stats"]["p90"] = sorted_latencies[
            int(len(sorted_latencies) * 0.9)
        ]
        self.results["latency_stats"]["p95"] = sorted_latencies[
            int(len(sorted_latencies) * 0.95)
        ]
        self.results["latency_stats"]["p99"] = sorted_latencies[
            int(len(sorted_latencies) * 0.99)
        ]

    def collect_stats(self):
        """Collect statistics from the test."""
        # Calculate duration
        self.results["end_time"] = time.time()
        self.results["total_duration"] = (
            self.results["end_time"] - self.results["start_time"]
        )

        # Calculate events per second
        if self.results["total_duration"] > 0:
            self.results["events_per_second"] = (
                self.results["total_events"] / self.results["total_duration"]
            )

        # Collect server stats
        for server in self.mock_servers:
            self.results["server_stats"].append(
                {
                    "url": server.url,
                    "requests_received": server.requests_received,
                    "successful_requests": server.successful_requests,
                    "failed_requests": server.failed_requests,
                    "success_rate": (
                        server.successful_requests / server.requests_received
                        if server.requests_received > 0
                        else 0
                    ),
                }
            )

        # Calculate latency percentiles
        self.calculate_latency_percentiles()

    async def run_load_test(self):
        """Run the load test."""
        try:
            # Set up the environment
            print("Setting up test environment...")
            await self.setup()

            # Start timing
            self.results["start_time"] = time.time()

            # Generate initial batch of events
            print(f"Generating {EVENT_BATCH_SIZE} initial events...")
            await self.generate_events(EVENT_BATCH_SIZE)

            # Start worker tasks
            print(f"Starting {MAX_CONCURRENCY} worker tasks...")
            workers = [
                asyncio.create_task(self.process_events(i))
                for i in range(MAX_CONCURRENCY)
            ]

            # Generate events periodically
            events_generated = EVENT_BATCH_SIZE
            while (
                time.time() - self.results["start_time"] < TEST_DURATION_SECONDS
                and events_generated < TOTAL_EVENTS
            ):
                # Generate more events if queue is getting empty
                if self.events_queue.qsize() < EVENT_BATCH_SIZE / 2:
                    batch_size = min(EVENT_BATCH_SIZE, TOTAL_EVENTS - events_generated)
                    if batch_size > 0:
                        print(f"Generating {batch_size} more events...")
                        await self.generate_events(batch_size)
                        events_generated += batch_size

                # Wait a bit before checking again
                await asyncio.sleep(1)

            # Wait for all events to be processed
            print("Waiting for all events to be processed...")
            await self.events_queue.join()

            # Cancel worker tasks
            print("Cancelling worker tasks...")
            for worker in workers:
                worker.cancel()

            await asyncio.gather(*workers, return_exceptions=True)

            # Collect stats
            print("Collecting statistics...")
            self.collect_stats()

            # Print results
            self.print_results()

            # Save results to file
            with open("webhook_load_test_results.json", "w") as f:
                # Convert datetime to string for JSON serialization
                results_copy = self.results.copy()
                results_copy["start_time"] = datetime.fromtimestamp(
                    results_copy["start_time"]
                ).isoformat()
                results_copy["end_time"] = datetime.fromtimestamp(
                    results_copy["end_time"]
                ).isoformat()
                json.dump(results_copy, f, indent=2)

        finally:
            # Clean up
            print("Cleaning up...")
            await self.teardown()

    def print_results(self):
        """Print the test results."""
        print("\n=== Webhook Load Test Results ===")
        print(f"Duration: {self.results['total_duration']:.2f} seconds")
        print(f"Total events: {self.results['total_events']}")
        print(
            f"Successful events: {self.results['successful_events']} ({self.results['successful_events'] / self.results['total_events'] * 100:.2f}%)"
        )
        print(
            f"Failed events: {self.results['failed_events']} ({self.results['failed_events'] / self.results['total_events'] * 100:.2f}%)"
        )
        print(f"Events per second: {self.results['events_per_second']:.2f}")

        print("\nLatency Statistics:")
        print(f"  Min: {self.results['latency_stats']['min'] * 1000:.2f} ms")
        print(f"  Max: {self.results['latency_stats']['max'] * 1000:.2f} ms")
        print(f"  Avg: {self.results['latency_stats']['avg'] * 1000:.2f} ms")
        print(f"  P50: {self.results['latency_stats']['p50'] * 1000:.2f} ms")
        print(f"  P90: {self.results['latency_stats']['p90'] * 1000:.2f} ms")
        print(f"  P95: {self.results['latency_stats']['p95'] * 1000:.2f} ms")
        print(f"  P99: {self.results['latency_stats']['p99'] * 1000:.2f} ms")

        print("\nServer Statistics:")
        for server in self.results["server_stats"]:
            print(f"  {server['url']}:")
            print(f"    Requests: {server['requests_received']}")
            print(f"    Success rate: {server['success_rate'] * 100:.2f}%")


async def main():
    """Run the load test."""
    env = LoadTestEnvironment()
    await env.run_load_test()


if __name__ == "__main__":
    asyncio.run(main())

# Add a simple test function for pytest to collect



@pytest.mark.asyncio
async def test_webhook_load_environment_initialization():
    """Test that the LoadTestEnvironment can be initialized."""
    env = LoadTestEnvironment()
    assert env is not None
    assert env.service is not None
    assert isinstance(env.mock_servers, list)
    assert len(env.mock_servers) == len(MOCK_SERVERS)