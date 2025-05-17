# Test Runner Script

## Overview

The `run_tests.py` script is a utility that optimizes the number of pytest workers based on the number of tests to be executed. This improves test performance by:

1. Using all available workers for large test suites
2. Defaulting to a single worker for small test runs to reduce overhead

## Usage

```bash
# Run all tests with optimized worker count
python run_tests.py

# Run specific tests with optimized worker count
python run_tests.py tests/test_specific.py

# Pass additional pytest arguments
python run_tests.py -xvs tests/test_specific.py
```

## How It Works

The script:

1. Counts the number of tests to be run using pytest's collection phase
2. If the test count exceeds a threshold (2x MAX_WORKERS), it uses all available workers
3. Otherwise, it defaults to a single worker to reduce overhead

## Configuration

The script has two main configuration constants:

- `MAX_WORKERS`: Maximum number of workers to use (default: 12)
- `THRESHOLD`: Test count threshold for using multiple workers (default: 2 * MAX_WORKERS)

These can be adjusted in the script based on your system's capabilities.

## Benefits

- **Development Efficiency**: Uses a single worker for small test runs, reducing the overhead of initializing multiple workers
- **CI Performance**: Automatically scales to use all workers for large test suites in CI environments
- **Consistent Interface**: Provides the same command interface as pytest, making it a drop-in replacement

## Integration with GitHub Actions

The script is designed to work seamlessly with GitHub Actions workflows. It can be used in place of direct pytest calls to optimize test performance in CI/CD pipelines.
