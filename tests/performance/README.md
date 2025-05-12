# Performance Testing

This directory contains performance tests for the system. These tests evaluate various aspects of system performance, including:

## Webhook Performance Tests
- **File**: `test_webhook_performance.py`
- Tests sequential delivery performance with varying numbers of webhooks and events
- Tests concurrent delivery performance with different concurrency levels
- Tests retry mechanism performance with different retry counts and delays
- Tests memory usage with different numbers of webhooks and events

## Webhook Load Tests
- **File**: `test_webhook_load.py`
- Simulates high-volume webhook traffic with realistic conditions
- Tests system behavior under sustained load
- Measures throughput, latency, and error rates
- Collects detailed performance metrics

## Webhook Scalability Tests
- **File**: `test_webhook_scalability.py`
- Tests system behavior with different scaling factors
- Evaluates how the system scales with increasing load
- Measures resource utilization during scaling

## Load Distribution Tests
- **File**: `test_load_distribution.py`
- Tests system behavior under geographically distributed load
- Tests regional failover scenarios
- Tests load balancing optimization with different strategies

## Resource Utilization Tests
- **File**: `test_resource_utilization.py`
- Tests memory usage patterns under sustained load
- Tests CPU utilization during concurrent operations
- Tests I/O bottleneck identification

## Running the Tests

To run all performance tests:

```bash
python run_webhook_performance_tests.py
```

To run specific tests:

```bash
python run_webhook_performance_tests.py --test performance
python run_webhook_performance_tests.py --test load
python run_webhook_performance_tests.py --test scalability
python run_webhook_performance_tests.py --test distribution
python run_webhook_performance_tests.py --test resource
```

## Test Results

Test results are saved to JSON files in the current directory:
- `webhook_performance_results.json`
- `memory_usage_results.json`
- `cpu_utilization_results.json`
- `io_bottleneck_results.json`

These files can be analyzed to identify performance bottlenecks and optimize system performance.

## Dependencies

Some tests require additional dependencies:
- `psutil` for memory and CPU monitoring
- `asyncio` for asynchronous testing
- `httpx` for HTTP requests

If `psutil` is not available, some tests will be skipped.