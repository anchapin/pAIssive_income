#!/usr/bin/env python3
"""
PR #166 Workflow Fix Trigger Script

This script helps trigger and monitor the workflow fixes for PR #166.
It can be used to manually run workflows and check their status.
"""

import subprocess
import sys
import json
import time
from datetime import datetime

def run_command(cmd, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=True,
            check=False
        )
        return result
    except Exception as e:
        print(f"❌ Error running command: {cmd}")
        print(f"Error: {e}")
        return None

def check_gh_cli():
    """Check if GitHub CLI is available."""
    result = run_command("gh --version")
    if result and result.returncode == 0:
        print("✅ GitHub CLI is available")
        return True
    else:
        print("❌ GitHub CLI not found. Please install it: https://cli.github.com/")
        return False

def trigger_workflow(workflow_name, branch=None):
    """Trigger a specific workflow."""
    print(f"🚀 Triggering workflow: {workflow_name}")
    
    cmd = f"gh workflow run {workflow_name}"
    if branch:
        cmd += f" --ref {branch}"
    
    result = run_command(cmd)
    if result and result.returncode == 0:
        print(f"✅ Successfully triggered {workflow_name}")
        return True
    else:
        print(f"❌ Failed to trigger {workflow_name}")
        if result:
            print(f"Error: {result.stderr}")
        return False

def list_workflows():
    """List available workflows."""
    print("📋 Available workflows:")
    result = run_command("gh workflow list")
    if result and result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print("❌ Failed to list workflows")
        return False

def check_workflow_status():
    """Check the status of recent workflow runs."""
    print("📊 Recent workflow runs:")
    result = run_command("gh run list --limit 10")
    if result and result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print("❌ Failed to get workflow status")
        return False

def trigger_pr_166_fixes(branch=None):
    """Trigger all PR #166 fix workflows."""
    workflows = [
        "pr-166-comprehensive-fix.yml",
        "test-setup-script-fixed.yml", 
        "codeql-simplified.yml"
    ]
    
    print("🎯 Triggering PR #166 fix workflows...")
    print(f"Branch: {branch or 'current branch'}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    success_count = 0
    for workflow in workflows:
        if trigger_workflow(workflow, branch):
            success_count += 1
        time.sleep(2)  # Small delay between triggers
    
    print("-" * 50)
    print(f"✅ Successfully triggered {success_count}/{len(workflows)} workflows")
    
    if success_count > 0:
        print("\n⏳ Waiting 10 seconds before checking status...")
        time.sleep(10)
        check_workflow_status()

def main():
    """Main function."""
    print("🔧 PR #166 Workflow Fix Trigger Script")
    print("=" * 50)
    
    # Check if GitHub CLI is available
    if not check_gh_cli():
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        branch = sys.argv[2] if len(sys.argv) > 2 else None
        
        if command == "trigger":
            trigger_pr_166_fixes(branch)
        elif command == "list":
            list_workflows()
        elif command == "status":
            check_workflow_status()
        elif command == "help":
            print_help()
        else:
            print(f"❌ Unknown command: {command}")
            print_help()
    else:
        # Interactive mode
        print("\n🎯 What would you like to do?")
        print("1. Trigger PR #166 fix workflows")
        print("2. List all workflows")
        print("3. Check workflow status")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            branch = input("Enter branch name (or press Enter for current): ").strip()
            trigger_pr_166_fixes(branch if branch else None)
        elif choice == "2":
            list_workflows()
        elif choice == "3":
            check_workflow_status()
        elif choice == "4":
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice")

def print_help():
    """Print help information."""
    print("""
Usage: python trigger_pr_166_fixes.py [command] [branch]

Commands:
  trigger [branch]  - Trigger PR #166 fix workflows
  list             - List all available workflows
  status           - Check recent workflow run status
  help             - Show this help message

Examples:
  python trigger_pr_166_fixes.py trigger
  python trigger_pr_166_fixes.py trigger main
  python trigger_pr_166_fixes.py list
  python trigger_pr_166_fixes.py status

Interactive mode:
  python trigger_pr_166_fixes.py

Requirements:
  - GitHub CLI (gh) must be installed and authenticated
  - Must be run from within a Git repository
  - Must have appropriate permissions to trigger workflows
""")

if __name__ == "__main__":
    main() 