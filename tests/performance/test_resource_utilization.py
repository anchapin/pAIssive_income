"""
Resource utilization tests for the system.

This module contains tests to evaluate the system's resource utilization patterns,
including memory usage under sustained load, CPU utilization during concurrent
operations, and I/O bottleneck identification.
"""

import asyncio
import time
import json
import os
import random
import threading
import multiprocessing
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import tempfile
import shutil
import pytest

# Try to import psutil for system metrics
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("psutil not available, some tests will be skipped")

# Import necessary services and utilities
from api.services.webhook_service import WebhookService
from api.schemas.webhook import WebhookEventType


class ResourceMonitor:
    """Monitor system resource utilization."""
    
    def __init__(self, interval: float = 0.1):
        """
        Initialize the resource monitor.
        
        Args:
            interval: Sampling interval in seconds
        """
        self.interval = interval
        self.running = False
        self.thread = None
        self.process = psutil.Process(os.getpid()) if PSUTIL_AVAILABLE else None
        
        # Metrics
        self.cpu_samples = []
        self.memory_samples = []
        self.io_samples = []
        self.timestamps = []
    
    def start(self) -> None:
        """Start monitoring resources."""
        if not PSUTIL_AVAILABLE:
            print("psutil not available, resource monitoring disabled")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_resources)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self) -> None:
        """Stop monitoring resources."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
    
    def _monitor_resources(self) -> None:
        """Monitor resources in a background thread."""
        while self.running:
            try:
                # Record timestamp
                timestamp = time.time()
                self.timestamps.append(timestamp)
                
                # CPU usage
                cpu_percent = self.process.cpu_percent(interval=None)
                self.cpu_samples.append(cpu_percent)
                
                # Memory usage
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
                self.memory_samples.append(memory_mb)
                
                # I/O counters
                io_counters = self.process.io_counters()
                self.io_samples.append({
                    "read_bytes": io_counters.read_bytes,
                    "write_bytes": io_counters.write_bytes,
                    "read_count": io_counters.read_count,
                    "write_count": io_counters.write_count
                })
                
                # Wait for next sample
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"Error monitoring resources: {str(e)}")
                break
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics."""
        if not PSUTIL_AVAILABLE or not self.timestamps:
            return {
                "error": "No metrics collected"
            }
        
        # Calculate statistics
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
        max_cpu = max(self.cpu_samples) if self.cpu_samples else 0
        
        avg_memory = sum(self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0
        max_memory = max(self.memory_samples) if self.memory_samples else 0
        
        # Calculate I/O rates
        io_rates = []
        for i in range(1, len(self.io_samples)):
            time_diff = self.timestamps[i] - self.timestamps[i-1]
            if time_diff > 0:
                read_rate = (self.io_samples[i]["read_bytes"] - self.io_samples[i-1]["read_bytes"]) / time_diff
                write_rate = (self.io_samples[i]["write_bytes"] - self.io_samples[i-1]["write_bytes"]) / time_diff
                io_rates.append({
                    "timestamp": self.timestamps[i],
                    "read_rate": read_rate,
                    "write_rate": write_rate
                })
        
        avg_read_rate = sum(r["read_rate"] for r in io_rates) / len(io_rates) if io_rates else 0
        avg_write_rate = sum(r["write_rate"] for r in io_rates) / len(io_rates) if io_rates else 0
        max_read_rate = max(r["read_rate"] for r in io_rates) if io_rates else 0
        max_write_rate = max(r["write_rate"] for r in io_rates) if io_rates else 0
        
        return {
            "duration": self.timestamps[-1] - self.timestamps[0] if len(self.timestamps) > 1 else 0,
            "samples": len(self.timestamps),
            "cpu": {
                "average": avg_cpu,
                "max": max_cpu,
                "samples": self.cpu_samples
            },
            "memory": {
                "average_mb": avg_memory,
                "max_mb": max_memory,
                "samples": self.memory_samples
            },
            "io": {
                "average_read_rate": avg_read_rate,
                "average_write_rate": avg_write_rate,
                "max_read_rate": max_read_rate,
                "max_write_rate": max_write_rate,
                "rates": io_rates
            }
        }


class MemoryLeakTester:
    """Test for memory leaks under sustained load."""
    
    def __init__(self, service: Any):
        """
        Initialize the memory leak tester.
        
        Args:
            service: The service to test
        """
        self.service = service
        self.monitor = ResourceMonitor(interval=0.5)
    
    async def run_memory_test(self, 
                             iterations: int, 
                             operation_func: callable, 
                             cleanup_func: Optional[callable] = None) -> Dict[str, Any]:
        """
        Run a memory leak test.
        
        Args:
            iterations: Number of iterations to run
            operation_func: Function to call on each iteration
            cleanup_func: Optional function to call for cleanup after test
            
        Returns:
            Test results
        """
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available, test skipped"}
        
        # Start monitoring
        self.monitor.start()
        
        # Run the test
        start_time = time.time()
        
        try:
            for i in range(iterations):
                # Run the operation
                await operation_func(i)
                
                # Print progress
                if (i + 1) % 10 == 0 or i == 0:
                    print(f"Completed {i + 1}/{iterations} iterations")
        
        finally:
            # Stop monitoring
            self.monitor.stop()
            
            # Run cleanup if provided
            if cleanup_func:
                await cleanup_func()
        
        # Calculate results
        end_time = time.time()
        duration = end_time - start_time
        
        metrics = self.monitor.get_metrics()
        
        # Analyze memory growth
        memory_samples = metrics["memory"]["samples"]
        if len(memory_samples) >= 2:
            # Calculate linear regression to detect memory growth trend
            n = len(memory_samples)
            x = list(range(n))
            y = memory_samples
            
            # Calculate slope using least squares method
            x_mean = sum(x) / n
            y_mean = sum(y) / n
            
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            slope = numerator / denominator if denominator != 0 else 0
            
            # Determine if there's a memory leak
            memory_growth_rate = slope * 3600  # MB per hour
            has_leak = memory_growth_rate > 10  # More than 10MB/hour growth
            
            metrics["memory"]["growth_rate_mb_per_hour"] = memory_growth_rate
            metrics["memory"]["potential_leak_detected"] = has_leak
        
        return {
            "iterations": iterations,
            "duration": duration,
            "iterations_per_second": iterations / duration,
            "metrics": metrics
        }


class CPUUtilizationTester:
    """Test CPU utilization during concurrent operations."""
    
    def __init__(self, service: Any):
        """
        Initialize the CPU utilization tester.
        
        Args:
            service: The service to test
        """
        self.service = service
        self.monitor = ResourceMonitor(interval=0.1)
    
    async def run_cpu_test(self, 
                          concurrency_levels: List[int],
                          operation_func: callable,
                          operations_per_level: int = 100) -> Dict[str, Any]:
        """
        Run a CPU utilization test with different concurrency levels.
        
        Args:
            concurrency_levels: List of concurrency levels to test
            operation_func: Async function that takes concurrency level and returns a coroutine
            operations_per_level: Number of operations to perform at each concurrency level
            
        Returns:
            Test results
        """
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available, test skipped"}
        
        results = []
        
        for concurrency in concurrency_levels:
            print(f"\nTesting with concurrency level: {concurrency}")
            
            # Start monitoring
            self.monitor.start()
            
            # Run the test
            start_time = time.time()
            
            try:
                # Create tasks
                tasks = []
                for i in range(concurrency):
                    task = asyncio.create_task(
                        operation_func(concurrency, i, operations_per_level // concurrency)
                    )
                    tasks.append(task)
                
                # Wait for all tasks to complete
                await asyncio.gather(*tasks)
            
            finally:
                # Stop monitoring
                self.monitor.stop()
            
            # Calculate results
            end_time = time.time()
            duration = end_time - start_time
            
            metrics = self.monitor.get_metrics()
            
            result = {
                "concurrency": concurrency,
                "operations": operations_per_level,
                "duration": duration,
                "operations_per_second": operations_per_level / duration,
                "metrics": metrics
            }
            
            results.append(result)
            
            print(f"  Completed in {duration:.2f}s")
            print(f"  Average CPU: {metrics['cpu']['average']:.2f}%")
            print(f"  Max CPU: {metrics['cpu']['max']:.2f}%")
            print(f"  Average memory: {metrics['memory']['average_mb']:.2f} MB")
        
        return {
            "concurrency_levels": concurrency_levels,
            "results": results
        }


class IOBottleneckTester:
    """Test for I/O bottlenecks."""
    
    def __init__(self):
        """Initialize the I/O bottleneck tester."""
        self.monitor = ResourceMonitor(interval=0.1)
        self.temp_dir = tempfile.mkdtemp()
    
    def cleanup(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    async def run_io_test(self, 
                         file_sizes: List[int],
                         concurrency_levels: List[int],
                         operations_per_test: int = 100) -> Dict[str, Any]:
        """
        Run an I/O bottleneck test.
        
        Args:
            file_sizes: List of file sizes to test (in KB)
            concurrency_levels: List of concurrency levels to test
            operations_per_test: Number of operations to perform for each test
            
        Returns:
            Test results
        """
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available, test skipped"}
        
        results = []
        
        try:
            for file_size in file_sizes:
                for concurrency in concurrency_levels:
                    print(f"\nTesting with file size: {file_size}KB, concurrency: {concurrency}")
                    
                    # Start monitoring
                    self.monitor.start()
                    
                    # Run the test
                    start_time = time.time()
                    
                    try:
                        # Create tasks
                        tasks = []
                        for i in range(concurrency):
                            task = asyncio.create_task(
                                self._io_worker(
                                    file_size=file_size,
                                    worker_id=i,
                                    operations=operations_per_test // concurrency
                                )
                            )
                            tasks.append(task)
                        
                        # Wait for all tasks to complete
                        await asyncio.gather(*tasks)
                    
                    finally:
                        # Stop monitoring
                        self.monitor.stop()
                    
                    # Calculate results
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    metrics = self.monitor.get_metrics()
                    
                    result = {
                        "file_size_kb": file_size,
                        "concurrency": concurrency,
                        "operations": operations_per_test,
                        "duration": duration,
                        "operations_per_second": operations_per_test / duration,
                        "throughput_mb_per_second": (file_size * operations_per_test) / (1024 * duration),
                        "metrics": metrics
                    }
                    
                    results.append(result)
                    
                    print(f"  Completed in {duration:.2f}s")
                    print(f"  Throughput: {result['throughput_mb_per_second']:.2f} MB/s")
                    print(f"  Average read rate: {metrics['io']['average_read_rate'] / (1024*1024):.2f} MB/s")
                    print(f"  Average write rate: {metrics['io']['average_write_rate'] / (1024*1024):.2f} MB/s")
        
        finally:
            # Clean up
            self.cleanup()
        
        return {
            "file_sizes": file_sizes,
            "concurrency_levels": concurrency_levels,
            "results": results
        }
    
    async def _io_worker(self, file_size: int, worker_id: int, operations: int) -> None:
        """
        Worker function for I/O testing.
        
        Args:
            file_size: Size of files to create (in KB)
            worker_id: Worker ID
            operations: Number of operations to perform
        """
        # Create random data
        data = os.urandom(file_size * 1024)
        
        for i in range(operations):
            # Create a unique filename
            filename = os.path.join(self.temp_dir, f"test_file_{worker_id}_{i}.dat")
            
            # Write file
            with open(filename, "wb") as f:
                f.write(data)
            
            # Read file
            with open(filename, "rb") as f:
                _ = f.read()
            
            # Delete file
            os.unlink(filename)
            
            # Simulate some processing
            await asyncio.sleep(0.01)


async def test_memory_usage_patterns():
    """Test memory usage patterns under sustained load."""
    if not PSUTIL_AVAILABLE:
        pytest.skip("psutil not available")
    
    # Create a webhook service for testing
    service = WebhookService()
    
    # Create a memory leak tester
    tester = MemoryLeakTester(service)
    
    # Define the operation function
    async def create_and_deliver_webhook(iteration):
        # Create a webhook
        webhook = await service.create_webhook(
            url=f"https://example.com/webhook-{iteration}",
            events=[WebhookEventType.USER_CREATED],
            description=f"Test webhook {iteration}"
        )
        
        # Create event data
        event_data = {
            "id": f"user-{iteration}",
            "name": f"User {iteration}",
            "email": f"user{iteration}@example.com",
            "created_at": datetime.now().isoformat()
        }
        
        # Deliver an event
        await service.deliver_event(
            webhook_id=webhook["id"],
            event_type=WebhookEventType.USER_CREATED,
            event_data=event_data
        )
        
        return webhook["id"]
    
    # Define the cleanup function
    async def cleanup():
        # Get all webhooks
        webhooks = await service.list_webhooks()
        
        # Delete all webhooks
        for webhook in webhooks:
            await service.delete_webhook(webhook["id"])
    
    # Run the memory test
    results = await tester.run_memory_test(
        iterations=100,
        operation_func=create_and_deliver_webhook,
        cleanup_func=cleanup
    )
    
    # Print results
    print("\nMemory Usage Test Results:")
    print(f"Iterations: {results['iterations']}")
    print(f"Duration: {results['duration']:.2f}s")
    print(f"Iterations per second: {results['iterations_per_second']:.2f}")
    print(f"Average memory usage: {results['metrics']['memory']['average_mb']:.2f} MB")
    print(f"Max memory usage: {results['metrics']['memory']['max_mb']:.2f} MB")
    
    if "growth_rate_mb_per_hour" in results["metrics"]["memory"]:
        print(f"Memory growth rate: {results['metrics']['memory']['growth_rate_mb_per_hour']:.2f} MB/hour")
        print(f"Potential memory leak: {results['metrics']['memory']['potential_leak_detected']}")
    
    # Save results to file
    with open("memory_usage_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


async def test_cpu_utilization():
    """Test CPU utilization during concurrent operations."""
    if not PSUTIL_AVAILABLE:
        pytest.skip("psutil not available")
    
    # Create a webhook service for testing
    service = WebhookService()
    
    # Create a CPU utilization tester
    tester = CPUUtilizationTester(service)
    
    # Define the operation function
    async def process_webhooks(concurrency, worker_id, operations):
        webhooks = []
        
        try:
            # Create webhooks
            for i in range(operations):
                webhook = await service.create_webhook(
                    url=f"https://example.com/webhook-{worker_id}-{i}",
                    events=[WebhookEventType.USER_CREATED],
                    description=f"Test webhook {worker_id}-{i}"
                )
                webhooks.append(webhook)
                
                # Create and deliver event
                event_data = {
                    "id": f"user-{worker_id}-{i}",
                    "name": f"User {worker_id}-{i}",
                    "email": f"user{worker_id}{i}@example.com",
                    "created_at": datetime.now().isoformat()
                }
                
                await service.deliver_event(
                    webhook_id=webhook["id"],
                    event_type=WebhookEventType.USER_CREATED,
                    event_data=event_data
                )
        
        finally:
            # Clean up webhooks
            for webhook in webhooks:
                await service.delete_webhook(webhook["id"])
    
    # Run the CPU test with different concurrency levels
    results = await tester.run_cpu_test(
        concurrency_levels=[1, 2, 4, 8, 16],
        operation_func=process_webhooks,
        operations_per_level=50
    )
    
    # Print results
    print("\nCPU Utilization Test Results:")
    for result in results["results"]:
        print(f"Concurrency: {result['concurrency']}")
        print(f"  Operations per second: {result['operations_per_second']:.2f}")
        print(f"  Average CPU: {result['metrics']['cpu']['average']:.2f}%")
        print(f"  Max CPU: {result['metrics']['cpu']['max']:.2f}%")
    
    # Save results to file
    with open("cpu_utilization_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


async def test_io_bottleneck():
    """Test I/O bottleneck identification."""
    if not PSUTIL_AVAILABLE:
        pytest.skip("psutil not available")
    
    # Create an I/O bottleneck tester
    tester = IOBottleneckTester()
    
    # Run the I/O test with different file sizes and concurrency levels
    results = await tester.run_io_test(
        file_sizes=[10, 100, 1000],  # 10KB, 100KB, 1MB
        concurrency_levels=[1, 4, 16],
        operations_per_test=50
    )
    
    # Print results
    print("\nI/O Bottleneck Test Results:")
    for result in results["results"]:
        print(f"File size: {result['file_size_kb']}KB, Concurrency: {result['concurrency']}")
        print(f"  Throughput: {result['throughput_mb_per_second']:.2f} MB/s")
        print(f"  Average read rate: {result['metrics']['io']['average_read_rate'] / (1024*1024):.2f} MB/s")
        print(f"  Average write rate: {result['metrics']['io']['average_write_rate'] / (1024*1024):.2f} MB/s")
    
    # Save results to file
    with open("io_bottleneck_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results


async def main():
    """Run all tests."""
    if not PSUTIL_AVAILABLE:
        print("psutil not available, tests will be skipped")
        return
    
    print("\n=== Testing Memory Usage Patterns ===")
    await test_memory_usage_patterns()
    
    print("\n=== Testing CPU Utilization ===")
    await test_cpu_utilization()
    
    print("\n=== Testing I/O Bottleneck Identification ===")
    await test_io_bottleneck()


if __name__ == "__main__":
    asyncio.run(main())
