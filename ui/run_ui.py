
import os
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path



#!/usr/bin/env python
"""
UI Runner Script for pAIssive Income Framework
This script starts both the React development server and the Flask API server.
"""






# Get the absolute path of the project
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
UI_DIR = os.path.join(PROJECT_ROOT, "ui")
REACT_APP_DIR = os.path.join(UI_DIR, "react_frontend")


def start_flask_server():
    """Start the Flask API server"""
    print("Starting Flask API server...")
    flask_cmd = [sys.executable, os.path.join(UI_DIR, "api_server.py")]
    flask_process = subprocess.Popen(flask_cmd)
    return flask_process


def start_react_dev_server():
    """Start the React development server"""
    if not os.path.exists(os.path.join(REACT_APP_DIR, "node_modules")):
        print("Installing React dependencies (this may take a few minutes)...")
        npm_install_cmd = ["npm", "install"]
        subprocess.run(npm_install_cmd, cwd=REACT_APP_DIR, check=True)

    print("Starting React development server...")
    react_cmd = ["npm", "start"]
    react_process = subprocess.Popen(react_cmd, cwd=REACT_APP_DIR)
    return react_process


def open_browser(url="http://localhost:3000", delay=5):
    """Open the browser after a delay"""

    def _open_browser():
        time.sleep(delay)
        print(f"Opening browser at {url}...")
        webbrowser.open(url)

    browser_thread = threading.Thread(target=_open_browser)
    browser_thread.daemon = True
    browser_thread.start()


def main():
    """Main function to start all services"""
    print("Starting pAIssive Income Framework UI...")

    # Start Flask API server
    flask_process = start_flask_server()

    # Start React development server
    react_process = start_react_dev_server()

    # Open the browser after servers have started
    open_browser()

    try:
        # Keep the script running
        print("\nServers are running. Press Ctrl+C to stop...\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        flask_process.terminate()
        react_process.terminate()
        print("Servers stopped successfully.")


if __name__ == "__main__":
    main()