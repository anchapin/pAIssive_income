#!/usr/bin/env python3
"""
Manual workflow trigger script for PR #166.

This script helps trigger workflows that don't run automatically 
when PRs are created by GitHub Actions.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - Timeout")
        return False
    except Exception as e:
        print(f"💥 {description} - Exception: {e}")
        return False


def trigger_workflows(branch_name: str = None) -> None:
    """Trigger the main workflows for the current branch."""
    if not branch_name:
        # Try to get current branch
        result = subprocess.run(
            "git branch --show-current",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            branch_name = result.stdout.strip()
        else:
            branch_name = "main"
    
    print(f"🚀 Triggering workflows for branch: {branch_name}")
    print("=" * 50)
    
    workflows = [
        ("consolidated-ci-cd.yml", "Consolidated CI/CD"),
        ("frontend-vitest.yml", "Frontend Vitest Tests"),
        ("frontend-e2e.yml", "Frontend E2E Tests"),
        ("codeql.yml", "CodeQL Analysis"),
        ("pr-166-fixes.yml", "PR 166 Fixes"),
    ]
    
    success_count = 0
    total_count = len(workflows)
    
    for workflow_file, description in workflows:
        command = f"gh workflow run {workflow_file} --ref {branch_name}"
        if run_command(command, f"Triggering {description}"):
            success_count += 1
        time.sleep(2)  # Small delay between triggers
    
    print("=" * 50)
    print(f"📊 Results: {success_count}/{total_count} workflows triggered successfully")
    
    if success_count > 0:
        print("\n🔍 Check workflow status with:")
        print("   gh run list --limit 10")
        print("\n🌐 Or visit: https://github.com/anchapin/pAIssive_income/actions")


def check_prerequisites() -> bool:
    """Check if required tools are available."""
    print("🔍 Checking prerequisites...")
    
    # Check if gh CLI is available
    if not run_command("gh --version", "GitHub CLI availability"):
        print("❌ GitHub CLI (gh) is required. Install from: https://cli.github.com/")
        return False
    
    # Check if authenticated
    if not run_command("gh auth status", "GitHub CLI authentication"):
        print("❌ Please authenticate with: gh auth login")
        return False
    
    # Check if in a git repository
    if not Path(".git").exists():
        print("❌ This script must be run from the root of the git repository")
        return False
    
    print("✅ All prerequisites met!")
    return True


def main():
    """Main function."""
    print("🤖 PR #166 Workflow Trigger Script")
    print("=" * 50)
    
    if not check_prerequisites():
        sys.exit(1)
    
    branch_name = None
    if len(sys.argv) > 1:
        branch_name = sys.argv[1]
    
    trigger_workflows(branch_name)
    
    print("\n💡 Tip: If workflows still don't run, try:")
    print("   1. Close and reopen the PR")
    print("   2. Make a small commit to the PR branch")
    print("   3. Use the manual workflow_dispatch trigger in GitHub UI")


if __name__ == "__main__":
    main() 