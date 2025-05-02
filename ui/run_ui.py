#!/usr/bin/env python
"""
UI Runner Script for pAIssive Income Framework
This script starts both the React development server and the Flask API server.
"""

import os
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
import re
import shutil

# Get the absolute path of the project
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
UI_DIR = os.path.join(PROJECT_ROOT, "ui")
REACT_APP_DIR = os.path.join(PROJECT_ROOT, "ui", "react_frontend")

# Validate paths for security
def validate_path(path, expected_base_path, path_type="directory"):
    """Securely validate a path is within the expected base path"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path_type.capitalize()} not found: {path}")
    
    # Resolve to absolute paths and check if the path is within the base path
    resolved_path = os.path.realpath(path)
    resolved_base = os.path.realpath(expected_base_path)
    
    if not resolved_path.startswith(resolved_base):
        raise ValueError(f"Security error: {path_type} path is outside of the expected base path")
    
    return path

# Validate critical directories
validate_path(UI_DIR, PROJECT_ROOT, "UI directory")
validate_path(REACT_APP_DIR, PROJECT_ROOT, "React app directory")


def start_flask_server():
    """Start the Flask API server"""
    print("Starting Flask API server...")
    flask_script = validate_path(os.path.join(UI_DIR, "api_server.py"), UI_DIR, "API server script")
    
    # Use a list for command arguments for security (no shell=True)
    flask_cmd = [sys.executable, flask_script]
    
    # Capture stdout and stderr for security monitoring
    try:
        # Prevent shell injection by not using shell=True
        flask_process = subprocess.Popen(
            flask_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
        return flask_process
    except (subprocess.SubprocessError, OSError) as e:
        print(f"Error starting Flask server: {str(e)}")
        raise


def start_react_dev_server():
    """Start the React development server"""
    # Validate node_modules path and create it if needed
    node_modules_path = validate_path(os.path.join(REACT_APP_DIR, "node_modules"), 
                                      REACT_APP_DIR, 
                                      "node_modules directory") if os.path.exists(os.path.join(REACT_APP_DIR, "node_modules")) else os.path.join(REACT_APP_DIR, "node_modules")
    
    if not os.path.exists(node_modules_path):
        print("Installing React dependencies (this may take a few minutes)...")
        try:
            # Check if npm is available in PATH
            npm_path = shutil.which("npm")
            if not npm_path:
                raise EnvironmentError("npm not found in PATH. Please install Node.js and npm.")
            
            # Use safer subprocess.run with explicit arguments
            result = subprocess.run(
                [npm_path, "install"],
                cwd=REACT_APP_DIR,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300  # 5-minute timeout for npm install
            )
            # Log output for debugging
            if result.stdout:
                print(f"npm install stdout: {result.stdout[:500]}...")
                
        except subprocess.CalledProcessError as e:
            print(f"Error installing React dependencies: {e.stderr[:500]}")
            raise
        except subprocess.TimeoutExpired:
            print("Error: npm install timed out after 5 minutes")
            raise

    print("Starting React development server...")
    # Check if npm is available in PATH
    npm_path = shutil.which("npm")
    if not npm_path:
        raise EnvironmentError("npm not found in PATH. Please install Node.js and npm.")
    
    # Use a list for command arguments for security
    react_cmd = [npm_path, "start"]
    
    # Start the process with better error handling
    try:
        react_process = subprocess.Popen(
            react_cmd,
            cwd=REACT_APP_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
        # Brief check that the process started correctly
        time.sleep(1)
        if react_process.poll() is not None:
            exit_code = react_process.poll()
            stderr_output = react_process.stderr.read() if react_process.stderr else "No error output available"
            raise RuntimeError(f"React process failed to start (exit code {exit_code}): {stderr_output[:500]}")
        
        return react_process
    except (subprocess.SubprocessError, OSError) as e:
        print(f"Error starting React development server: {str(e)}")
        raise


def open_browser(url="http://localhost:3000", delay=5):
    """Open the browser after a delay"""
    # Validate URL for security
    if not re.match(r'^https?://localhost(:[0-9]+)?(/.*)?$', url):
        print(f"Warning: Untrusted URL detected: {url}. Only localhost URLs are allowed.")
        return

    def _open_browser():
        time.sleep(delay)
        print(f"Opening browser at {url}...")
        webbrowser.open(url)

    browser_thread = threading.Thread(target=_open_browser)
    browser_thread.daemon = True
    browser_thread.start()


def monitor_process_output(process, name, max_lines=1000):
    """Monitor process output with line limiting for security"""
    line_count = 0
    
    # Monitor both stdout and stderr
    for stream_name, stream in [("stdout", process.stdout), ("stderr", process.stderr)]:
        if stream:
            for line in iter(stream.readline, ''):
                if line_count < max_lines:
                    print(f"{name} ({stream_name}): {line.strip()}")
                elif line_count == max_lines:
                    print(f"{name}: Output truncated after {max_lines} lines for security")
                line_count += 1
                
                # Check for security-related messages
                lower_line = line.lower()
                if "error" in lower_line or "warning" in lower_line or "exception" in lower_line:
                    # Log potential security issues with more visibility
                    print(f"ALERT - Potential issue in {name}: {line.strip()}")


def main():
    """Main function to start all services"""
    print("Starting pAIssive Income Framework UI...")

    # Start Flask API server
    flask_process = start_flask_server()
    
    # Monitor Flask process output for errors
    flask_monitor = threading.Thread(
        target=monitor_process_output, 
        args=(flask_process, "Flask", 500)
    )
    flask_monitor.daemon = True
    flask_monitor.start()

    # Start React development server
    react_process = start_react_dev_server()
    
    # Monitor React process output for errors
    react_monitor = threading.Thread(
        target=monitor_process_output, 
        args=(react_process, "React", 500)
    )
    react_monitor.daemon = True
    react_monitor.start()

    # Open the browser after servers have started
    open_browser()

    try:
        # Keep the script running
        print("\nServers are running. Press Ctrl+C to stop...\n")
        while True:
            # Check if processes are still running
            if flask_process.poll() is not None:
                exit_code = flask_process.poll()
                print(f"Flask server has stopped unexpectedly (exit code: {exit_code})")
                break
            if react_process.poll() is not None:
                exit_code = react_process.poll()
                print(f"React server has stopped unexpectedly (exit code: {exit_code})")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        # Gracefully terminate processes with timeout
        try:
            flask_process.terminate()
            react_process.terminate()
            
            # Give processes time to terminate gracefully
            flask_exit_code = flask_process.wait(timeout=5)
            react_exit_code = react_process.wait(timeout=5)
            
            print(f"Flask server stopped (exit code: {flask_exit_code})")
            print(f"React server stopped (exit code: {react_exit_code})")
        except subprocess.TimeoutExpired:
            print("Forcing termination of servers that didn't exit gracefully")
            if flask_process.poll() is None:
                flask_process.kill()
            if react_process.poll() is None:
                react_process.kill()
        
        print("Servers stopped successfully.")


if __name__ == "__main__":
    main()
