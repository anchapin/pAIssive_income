"""
Scalability testing for the webhook system.

This module tests how the webhook system scales with increasing load and resources.
"""

import asyncio
import time
import json
import uuid
import os
import psutil
import multiprocessing
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx
from unittest.mock import patch, MagicMock

from api.services.webhook_service import WebhookService
from api.schemas.webhook import WebhookEventType, WebhookDeliveryStatus

# Test configuration
SCALING_FACTORS = [1, 2, 4, 8, 16]  # Scaling factors to test
BASE_WEBHOOK_COUNT = 10             # Base number of webhooks
BASE_EVENT_COUNT = 100              # Base number of events
BASE_CONCURRENCY = 5                # Base concurrency level


class ScalabilityTest:
    """Test the scalability of the webhook system."""
    
    def __init__(self, scaling_factor: int):
        self.scaling_factor = scaling_factor
        self.webhook_count = BASE_WEBHOOK_COUNT * scaling_factor
        self.event_count = BASE_EVENT_COUNT * scaling_factor
        self.concurrency = BASE_CONCURRENCY * scaling_factor
        self.service = WebhookService()
        self.webhooks = []
        self.events = []
        self.results = {
            "scaling_factor": scaling_factor,
            "webhook_count": self.webhook_count,
            "event_count": self.event_count,
            "concurrency": self.concurrency,
            "start_time": None,
            "end_time": None,
            "total_duration": 0,
            "events_per_second": 0,
            "cpu_usage": [],
            "memory_usage": [],
            "success_rate": 0
        }
    
    async def setup(self):
        """Set up the test environment."""
        # Start the webhook service
        await self.service.start()
        
        # Create test webhooks
        for i in range(self.webhook_count):
            webhook_data = {
                "url": f"https://example.com/webhook/{i}",
                "events": [WebhookEventType.USER_CREATED],
                "description": f"Scalability test webhook {i}",
                "headers": {"Authorization": f"Bearer test-token-{i}"},
                "is_active": True
            }
            webhook = await self.service.register_webhook(webhook_data)
            self.webhooks.append(webhook)
        
        # Create test events
        for i in range(self.event_count):
            event_data = {
                "id": str(uuid.uuid4()),
                "user_id": f"user-{i}",
                "username": f"testuser{i}",
                "email": f"test{i}@example.com",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            self.events.append(event_data)
    
    async def teardown(self):
        """Clean up the test environment."""
        # Delete all webhooks
        for webhook in self.webhooks:
            await self.service.delete_webhook(webhook["id"])
        
        # Stop the webhook service
        await self.service.stop()
    
    async def monitor_resources(self, stop_event):
        """Monitor CPU and memory usage."""
        process = psutil.Process(os.getpid())
        
        while not stop_event.is_set():
            # Record CPU and memory usage
            cpu_percent = process.cpu_percent(interval=0.1)
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            
            self.results["cpu_usage"].append(cpu_percent)
            self.results["memory_usage"].append(memory_mb)
            
            # Wait before next measurement
            await asyncio.sleep(0.5)
    
    async def run_test(self):
        """Run the scalability test."""
        try:
            # Set up the environment
            print(f"Setting up test environment (scaling factor: {self.scaling_factor})...")
            await self.setup()
            
            # Create a mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            mock_response.raise_for_status = MagicMock()
            
            # Create an event to signal the resource monitor to stop
            stop_monitoring = asyncio.Event()
            
            # Start resource monitoring
            monitor_task = asyncio.create_task(self.monitor_resources(stop_monitoring))
            
            # Start timing
            self.results["start_time"] = time.time()
            
            # Patch the httpx.AsyncClient.post method to return our mock response
            with patch("httpx.AsyncClient.post", return_value=mock_response):
                # Create tasks for concurrent delivery
                tasks = []
                semaphore = asyncio.Semaphore(self.concurrency)
                
                async def deliver_with_semaphore(webhook, event):
                    async with semaphore:
                        return await self.service.deliver_event(
                            webhook_id=webhook["id"],
                            event_type=WebhookEventType.USER_CREATED,
                            event_data=event
                        )
                
                # Create delivery tasks
                for webhook in self.webhooks:
                    for event in self.events:
                        task = asyncio.create_task(
                            deliver_with_semaphore(webhook, event)
                        )
                        tasks.append(task)
                
                # Wait for all tasks to complete
                deliveries = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Record end time
                self.results["end_time"] = time.time()
                
                # Stop resource monitoring
                stop_monitoring.set()
                await monitor_task
                
                # Calculate results
                self.results["total_duration"] = self.results["end_time"] - self.results["start_time"]
                total_deliveries = len(self.webhooks) * len(self.events)
                if self.results["total_duration"] > 0:
                    self.results["events_per_second"] = total_deliveries / self.results["total_duration"] 
                else:
                    self.results["events_per_second"] = 0
                
                # Calculate success rate
                successful_deliveries = sum(
                    1 for d in deliveries 
                    if not isinstance(d, Exception) and d["status"] == WebhookDeliveryStatus.SUCCESS
                )
                if total_deliveries > 0:
                    self.results["success_rate"] = successful_deliveries / total_deliveries
                else:
                    self.results["success_rate"] = 0
                
                # Calculate average CPU and memory usage
                if self.results["cpu_usage"]:
                    self.results["avg_cpu_percent"] = sum(self.results["cpu_usage"]) / len(self.results["cpu_usage"])
                    self.results["max_cpu_percent"] = max(self.results["cpu_usage"])
                
                if self.results["memory_usage"]:
                    self.results["avg_memory_mb"] = sum(self.results["memory_usage"]) / len(self.results["memory_usage"])
                    self.results["max_memory_mb"] = max(self.results["memory_usage"])
                
                # Print results
                print(f"\nResults for scaling factor {self.scaling_factor}:")
                print(f"  Webhooks: {self.webhook_count}")
                print(f"  Events: {self.event_count}")
                print(f"  Concurrency: {self.concurrency}")
                print(f"  Total deliveries: {total_deliveries}")
                print(f"  Duration: {self.results['total_duration']:.2f} seconds")
                print(f"  Events per second: {self.results['events_per_second']:.2f}")
                print(f"  Success rate: {self.results['success_rate'] * 100:.2f}%")
                
                if hasattr(self.results, "avg_cpu_percent"):
                    print(f"  Avg CPU usage: {self.results['avg_cpu_percent']:.2f}%")
                    print(f"  Max CPU usage: {self.results['max_cpu_percent']:.2f}%")
                
                if hasattr(self.results, "avg_memory_mb"):
                    print(f"  Avg memory usage: {self.results['avg_memory_mb']:.2f} MB")
                    print(f"  Max memory usage: {self.results['max_memory_mb']:.2f} MB")
                
                return self.results
                
        finally:
            # Clean up
            await self.teardown()


async def run_scalability_tests():
    """Run scalability tests with different scaling factors."""
    results = []
    
    for factor in SCALING_FACTORS:
        print(f"\n=== Running scalability test with scaling factor {factor} ===")
        test = ScalabilityTest(factor)
        result = await test.run_test()
        results.append(result)
        
        # Wait a bit between tests to let system resources recover
        await asyncio.sleep(2)
    
    # Save results to file
    with open("webhook_scalability_results.json", "w") as f:
        # Convert datetime to string for JSON serialization
        results_copy = []
        for r in results:
            r_copy = r.copy()
            if "start_time" in r_copy:
                r_copy["start_time"] = datetime.fromtimestamp(r_copy["start_time"]).isoformat()
            if "end_time" in r_copy:
                r_copy["end_time"] = datetime.fromtimestamp(r_copy["end_time"]).isoformat()
            
            # Remove detailed CPU and memory usage arrays from JSON output
            if "cpu_usage" in r_copy:
                r_copy["cpu_usage_points"] = len(r_copy["cpu_usage"])
                del r_copy["cpu_usage"]
            if "memory_usage" in r_copy:
                r_copy["memory_usage_points"] = len(r_copy["memory_usage"])
                del r_copy["memory_usage"]
                
            results_copy.append(r_copy)
            
        json.dump(results_copy, f, indent=2)
    
    # Print summary
    print("\n=== Scalability Test Summary ===")
    print("Scaling Factor | Events/Second | Success Rate | Avg CPU % | Avg Memory (MB)")
    print("-------------- | ------------- | ------------ | --------- | --------------")
    
    for r in results:
        cpu_percent = r.get("avg_cpu_percent", 0)
        memory_mb = r.get("avg_memory_mb", 0)
        print(
            f"{r['scaling_factor']:14} | {r['events_per_second']:13.2f} | "
            f"{r['success_rate']*100:10.2f}% | {cpu_percent:9.2f} | {memory_mb:14.2f}"
        )
    
    # Calculate scaling efficiency
    base_result = next((r for r in results if r["scaling_factor"] == 1), None)
    if base_result:
        base_events_per_second = base_result["events_per_second"]
        
        print("\nScaling Efficiency:")
        print("Scaling Factor | Ideal Throughput | Actual Throughput | Efficiency")
        print("-------------- | --------------- | ---------------- | ----------")
        
        for r in results:
            if r["scaling_factor"] > 1:
                ideal_throughput = base_events_per_second * r["scaling_factor"]
                actual_throughput = r["events_per_second"]
                if ideal_throughput > 0:
                    efficiency = actual_throughput / ideal_throughput
                else:
                    efficiency = 0
                
                print(
                    f"{r['scaling_factor']:14} | {ideal_throughput:15.2f} | "
                    f"{actual_throughput:16.2f} | {efficiency*100:8.2f}%"
                )


async def main():
    """Run the scalability tests."""
    await run_scalability_tests()


if __name__ == "__main__":
    asyncio.run(main())
