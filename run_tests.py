#!/usr/bin/env python3
import subprocess
import sys
import shlex

# Maximum number of workers
MAX_WORKERS = 12
# Threshold: if test count > threshold, use MAX_WORKERS, else use 1
THRESHOLD = 2 * MAX_WORKERS

def get_test_count(pytest_args):
    """
    Returns the number of collected tests for the given pytest arguments.
    """
    cmd = ["pytest", "--collect-only", "-q"] + pytest_args
    try:
        # Capture output of pytest collection
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, universal_newlines=True)
        # Each test is one line in the output
        # Filter out empty lines and lines starting with '<' (pytest's summary lines)
        test_lines = [line for line in output.splitlines() if line.strip() and not line.startswith("<")]
        return len(test_lines)
    except subprocess.CalledProcessError:
        print("Error collecting tests. Falling back to single worker.", file=sys.stderr)
        return 1

def main():
    # Forward all command-line arguments to pytest except the script name
    pytest_args = sys.argv[1:]

    # Get number of tests that would be run
    test_count = get_test_count(pytest_args)

    if test_count > THRESHOLD:
        n_workers = MAX_WORKERS
    else:
        n_workers = 1

    print(f"Collected {test_count} tests. Using {n_workers} pytest worker(s).")

    # Build pytest command
    pytest_cmd = ["pytest", f"-n={n_workers}"] + pytest_args

    # Run pytest with the chosen number of workers
    result = subprocess.call(pytest_cmd)
    sys.exit(result)

if __name__ == "__main__":
    main()