"""
Performance testing for the webhook system.

This module contains tests to evaluate the performance of the webhook delivery system
under various load conditions.
"""

import asyncio
import time
import statistics
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
import httpx
from unittest.mock import patch

from api.services.webhook_service import WebhookService
from api.schemas.webhook import WebhookEventType

# Test configuration
NUM_WEBHOOKS = [1, 10, 50, 100]  # Number of webhooks to test with
NUM_EVENTS = [1, 10, 50, 100]    # Number of events to deliver per test
CONCURRENT_DELIVERIES = [1, 5, 10, 20, 50]  # Number of concurrent deliveries

# Mock server response times (in seconds)
RESPONSE_TIMES = [0.01, 0.05, 0.1, 0.5, 1.0]

class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, status_code=200, content="OK", delay=0.0):
        self.status_code = status_code
        self.text = content
        self.delay = delay
    
    async def __call__(self, *args, **kwargs):
        """Simulate network delay."""
        await asyncio.sleep(self.delay)
        return self

    def raise_for_status(self):
        """Raise an exception if status code is 4xx or 5xx."""
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP Error {self.status_code}", 
                request=httpx.Request("POST", "https://example.com/webhook"),
                response=self
            )

async def create_test_webhooks(service: WebhookService, count: int) -> List[Dict[str, Any]]:
    """Create test webhooks for performance testing."""
    webhooks = []
    for i in range(count):
        webhook_data = {
            "url": f"https://example.com/webhook/{i}",
            "events": [WebhookEventType.USER_CREATED, WebhookEventType.PAYMENT_RECEIVED],
            "description": f"Test webhook {i}",
            "headers": {"Authorization": f"Bearer test-token-{i}"},
            "is_active": True
        }
        webhook = await service.register_webhook(webhook_data)
        webhooks.append(webhook)
    return webhooks

async def create_test_events(count: int) -> List[Dict[str, Any]]:
    """Create test events for performance testing."""
    events = []
    for i in range(count):
        event_data = {
            "user_id": f"user-{i}",
            "username": f"testuser{i}",
            "email": f"test{i}@example.com",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        events.append(event_data)
    return events

async def test_sequential_delivery(
    service: WebhookService, 
    webhooks: List[Dict[str, Any]], 
    events: List[Dict[str, Any]],
    response_time: float
) -> Dict[str, Any]:
    """Test sequential delivery of events to webhooks."""
    # Create a mock response with the specified delay
    mock_response = MockResponse(status_code=200, content="OK", delay=response_time)
    
    # Patch the httpx.AsyncClient.post method to return our mock response
    with patch("httpx.AsyncClient.post", mock_response):
        start_time = time.time()
        
        # Deliver events sequentially
        deliveries = []
        for webhook in webhooks:
            for event in events:
                delivery = await service.deliver_event(
                    webhook_id=webhook["id"],
                    event_type=WebhookEventType.USER_CREATED,
                    event_data=event
                )
                deliveries.append(delivery)
        
        end_time = time.time()
        
        # Calculate metrics
        total_time = end_time - start_time
        total_deliveries = len(webhooks) * len(events)
        deliveries_per_second = total_deliveries / total_time if total_time > 0 else 0
        
        return {
            "test_type": "sequential",
            "num_webhooks": len(webhooks),
            "num_events": len(events),
            "response_time": response_time,
            "total_deliveries": total_deliveries,
            "total_time": total_time,
            "deliveries_per_second": deliveries_per_second
        }

async def test_concurrent_delivery(
    service: WebhookService, 
    webhooks: List[Dict[str, Any]], 
    events: List[Dict[str, Any]],
    response_time: float,
    concurrency: int
) -> Dict[str, Any]:
    """Test concurrent delivery of events to webhooks."""
    # Create a mock response with the specified delay
    mock_response = MockResponse(status_code=200, content="OK", delay=response_time)
    
    # Patch the httpx.AsyncClient.post method to return our mock response
    with patch("httpx.AsyncClient.post", mock_response):
        start_time = time.time()
        
        # Create tasks for concurrent delivery
        tasks = []
        semaphore = asyncio.Semaphore(concurrency)
        
        async def deliver_with_semaphore(webhook_id, event_type, event_data):
            async with semaphore:
                return await service.deliver_event(
                    webhook_id=webhook_id,
                    event_type=event_type,
                    event_data=event_data
                )
        
        for webhook in webhooks:
            for event in events:
                task = asyncio.create_task(
                    deliver_with_semaphore(
                        webhook_id=webhook["id"],
                        event_type=WebhookEventType.USER_CREATED,
                        event_data=event
                    )
                )
                tasks.append(task)
        
        # Wait for all tasks to complete
        deliveries = await asyncio.gather(*tasks)
        
        end_time = time.time()
        
        # Calculate metrics
        total_time = end_time - start_time
        total_deliveries = len(webhooks) * len(events)
        deliveries_per_second = total_deliveries / total_time if total_time > 0 else 0
        
        return {
            "test_type": "concurrent",
            "num_webhooks": len(webhooks),
            "num_events": len(events),
            "response_time": response_time,
            "concurrency": concurrency,
            "total_deliveries": total_deliveries,
            "total_time": total_time,
            "deliveries_per_second": deliveries_per_second
        }

async def test_retry_performance(
    service: WebhookService, 
    webhooks: List[Dict[str, Any]], 
    events: List[Dict[str, Any]],
    retry_count: int,
    retry_delay: float
) -> Dict[str, Any]:
    """Test performance of retry mechanism."""
    # Create a sequence of responses: first failure, then success
    mock_failure = MockResponse(status_code=503, content="Service Unavailable", delay=0.05)
    mock_success = MockResponse(status_code=200, content="OK", delay=0.05)
    
    # Create a sequence of responses based on retry count
    responses = [mock_failure] * retry_count + [mock_success]
    
    # Patch the httpx.AsyncClient.post method to return our sequence of responses
    with patch("httpx.AsyncClient.post", side_effect=responses):
        start_time = time.time()
        
        # Deliver an event with retry
        delivery = await service.deliver_event(
            webhook_id=webhooks[0]["id"],
            event_type=WebhookEventType.USER_CREATED,
            event_data=events[0],
            retry_count=retry_count,
            retry_delay=retry_delay
        )
        
        end_time = time.time()
        
        # Calculate metrics
        total_time = end_time - start_time
        expected_time = retry_count * retry_delay + (retry_count + 1) * 0.05
        
        return {
            "test_type": "retry",
            "retry_count": retry_count,
            "retry_delay": retry_delay,
            "total_time": total_time,
            "expected_time": expected_time,
            "attempts": len(delivery["attempts"]),
            "final_status": delivery["status"]
        }

async def test_memory_usage(
    service: WebhookService, 
    num_webhooks: int,
    num_events: int
) -> Dict[str, Any]:
    """Test memory usage of the webhook system."""
    import psutil
    import os
    
    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create webhooks and events
    webhooks = await create_test_webhooks(service, num_webhooks)
    events = await create_test_events(num_events)
    
    # Get memory usage after creation
    after_creation_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Mock response for delivery
    mock_response = MockResponse(status_code=200, content="OK", delay=0.01)
    
    # Deliver events
    with patch("httpx.AsyncClient.post", mock_response):
        for webhook in webhooks:
            for event in events:
                await service.deliver_event(
                    webhook_id=webhook["id"],
                    event_type=WebhookEventType.USER_CREATED,
                    event_data=event
                )
    
    # Get final memory usage
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    return {
        "test_type": "memory",
        "num_webhooks": num_webhooks,
        "num_events": num_events,
        "total_deliveries": num_webhooks * num_events,
        "initial_memory_mb": initial_memory,
        "after_creation_memory_mb": after_creation_memory,
        "final_memory_mb": final_memory,
        "memory_increase_mb": final_memory - initial_memory,
        "memory_per_delivery_kb": (final_memory - initial_memory) * 1024 / (num_webhooks * num_events) if num_webhooks * num_events > 0 else 0
    }

async def run_performance_tests():
    """Run all performance tests."""
    results = []
    
    # Create webhook service
    service = WebhookService()
    await service.start()
    
    try:
        print("Starting webhook performance tests...")
        
        # Test sequential delivery with different numbers of webhooks and events
        print("\nTesting sequential delivery...")
        for num_webhook in NUM_WEBHOOKS[:2]:  # Use fewer webhooks for sequential tests
            for num_event in NUM_EVENTS[:2]:  # Use fewer events for sequential tests
                for response_time in RESPONSE_TIMES[:3]:  # Use shorter response times
                    print(f"  Testing {num_webhook} webhooks, {num_event} events, {response_time}s response time...")
                    webhooks = await create_test_webhooks(service, num_webhook)
                    events = await create_test_events(num_event)
                    
                    result = await test_sequential_delivery(service, webhooks, events, response_time)
                    results.append(result)
                    
                    print(f"    Completed in {result['total_time']:.2f}s, {result['deliveries_per_second']:.2f} deliveries/second")
                    
                    # Clean up webhooks
                    for webhook in webhooks:
                        await service.delete_webhook(webhook["id"])
        
        # Test concurrent delivery with different concurrency levels
        print("\nTesting concurrent delivery...")
        for num_webhook in NUM_WEBHOOKS[1:3]:  # Use medium number of webhooks
            for num_event in NUM_EVENTS[1:3]:  # Use medium number of events
                for response_time in RESPONSE_TIMES[1:3]:  # Use medium response times
                    for concurrency in CONCURRENT_DELIVERIES:
                        print(f"  Testing {num_webhook} webhooks, {num_event} events, {response_time}s response time, {concurrency} concurrency...")
                        webhooks = await create_test_webhooks(service, num_webhook)
                        events = await create_test_events(num_event)
                        
                        result = await test_concurrent_delivery(service, webhooks, events, response_time, concurrency)
                        results.append(result)
                        
                        print(f"    Completed in {result['total_time']:.2f}s, {result['deliveries_per_second']:.2f} deliveries/second")
                        
                        # Clean up webhooks
                        for webhook in webhooks:
                            await service.delete_webhook(webhook["id"])
        
        # Test retry performance
        print("\nTesting retry performance...")
        for retry_count in [1, 3, 5]:
            for retry_delay in [0.1, 0.5, 1.0]:
                print(f"  Testing {retry_count} retries with {retry_delay}s delay...")
                webhooks = await create_test_webhooks(service, 1)
                events = await create_test_events(1)
                
                result = await test_retry_performance(service, webhooks, events, retry_count, retry_delay)
                results.append(result)
                
                print(f"    Completed in {result['total_time']:.2f}s (expected ~{result['expected_time']:.2f}s)")
                
                # Clean up webhooks
                for webhook in webhooks:
                    await service.delete_webhook(webhook["id"])
        
        # Test memory usage
        try:
            print("\nTesting memory usage...")
            for num_webhook in [10, 50]:
                for num_event in [10, 50]:
                    print(f"  Testing memory usage with {num_webhook} webhooks and {num_event} events...")
                    result = await test_memory_usage(service, num_webhook, num_event)
                    results.append(result)
                    
                    print(f"    Memory usage: {result['memory_increase_mb']:.2f} MB total, {result['memory_per_delivery_kb']:.2f} KB per delivery")
        except ImportError:
            print("Skipping memory usage tests (psutil not available)")
        
        # Save results to file
        with open("webhook_performance_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print("\nPerformance test summary:")
        
        # Sequential delivery summary
        sequential_results = [r for r in results if r["test_type"] == "sequential"]
        if sequential_results:
            print("\n  Sequential delivery:")
            print(f"    Average deliveries/second: {statistics.mean([r['deliveries_per_second'] for r in sequential_results]):.2f}")
            print(f"    Max deliveries/second: {max([r['deliveries_per_second'] for r in sequential_results]):.2f}")
        
        # Concurrent delivery summary
        concurrent_results = [r for r in results if r["test_type"] == "concurrent"]
        if concurrent_results:
            print("\n  Concurrent delivery:")
            print(f"    Average deliveries/second: {statistics.mean([r['deliveries_per_second'] for r in concurrent_results]):.2f}")
            print(f"    Max deliveries/second: {max([r['deliveries_per_second'] for r in concurrent_results]):.2f}")
            
            # Group by concurrency
            for concurrency in CONCURRENT_DELIVERIES:
                concurrency_results = [r for r in concurrent_results if r["concurrency"] == concurrency]
                if concurrency_results:
                    print(f"    Concurrency {concurrency}: {statistics.mean([r['deliveries_per_second'] for r in concurrency_results]):.2f} deliveries/second")
        
        # Retry performance summary
        retry_results = [r for r in results if r["test_type"] == "retry"]
        if retry_results:
            print("\n  Retry performance:")
            print(f"    Average time ratio (actual/expected): {statistics.mean([r['total_time'] / r['expected_time'] for r in retry_results]):.2f}")
        
        # Memory usage summary
        memory_results = [r for r in results if r["test_type"] == "memory"]
        if memory_results:
            print("\n  Memory usage:")
            print(f"    Average memory per delivery: {statistics.mean([r['memory_per_delivery_kb'] for r in memory_results]):.2f} KB")
        
    finally:
        # Stop the webhook service
        await service.stop()

if __name__ == "__main__":
    asyncio.run(run_performance_tests())
