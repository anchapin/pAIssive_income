#!/usr/bin/env python3
"""
CI Environment Test Script.

This script tests the CI environment detection functionality by running the
detect_ci_environment.py script in various simulated CI environments.

Usage:
    python test_ci_environment.py [--all] [--github] [--jenkins] [--gitlab] [--docker] [--kubernetes]

Options:
    --all           Test all CI environments
    --github        Test GitHub Actions environment
    --jenkins       Test Jenkins environment
    --gitlab        Test GitLab CI environment
    --docker        Test Docker environment
    --kubernetes    Test Kubernetes environment
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run_detect_script(env_vars: dict[str, str] | None = None, verbose: bool = False):
    """
    Run the detect_ci_environment.py script with the specified environment variables.

    Args:
        env_vars (dict): Environment variables to set
        verbose (bool): Whether to run in verbose mode

    Returns:
        tuple: (return_code, stdout, stderr)

    """
    script_path = Path(__file__).parent / "detect_ci_environment.py"

    if not script_path.exists():
        print(f"Error: {script_path} not found")
        return 1, "", f"Error: {script_path} not found"

    # Create a copy of the current environment
    env = os.environ.copy()

    # Add the specified environment variables
    if env_vars:
        env.update(env_vars)

    # Build the command
    cmd = [sys.executable, str(script_path)]
    if verbose:
        cmd.append("--verbose")

    # Run the command
    try:
        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True, check=False
        )
    except (subprocess.SubprocessError, OSError, FileNotFoundError) as e:
        return 1, "", str(e)
    else:
        return result.returncode, result.stdout, result.stderr


def test_github_actions():
    """Test GitHub Actions environment detection."""
    print("\n=== Testing GitHub Actions Environment ===")
    env_vars = {
        "CI": "true",
        "GITHUB_ACTIONS": "true",
        "GITHUB_WORKFLOW": "test-workflow",
        "GITHUB_RUN_ID": "1234567890",
        "GITHUB_REPOSITORY": "user/repo",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_SHA": "1234567890abcdef1234567890abcdef12345678",
        "GITHUB_EVENT_NAME": "push",
    }

    return_code, stdout, stderr = run_detect_script(env_vars, verbose=True)

    if return_code == 0:
        print("✅ GitHub Actions environment detection test passed")
        if "GitHub Actions" in stdout:
            print("✅ Correctly identified as GitHub Actions")
        else:
            print("❌ Failed to identify as GitHub Actions")
    else:
        print("❌ GitHub Actions environment detection test failed")
        print(f"Error: {stderr}")

    return return_code == 0 and "GitHub Actions" in stdout


def test_jenkins():
    """Test Jenkins environment detection."""
    print("\n=== Testing Jenkins Environment ===")
    env_vars = {
        "CI": "true",
        "JENKINS_URL": "http://jenkins.example.com/",
        "BUILD_ID": "1234",
        "BUILD_NUMBER": "1234",
        "BUILD_URL": "http://jenkins.example.com/job/project/1234/",
        "JOB_NAME": "project",
    }

    return_code, stdout, stderr = run_detect_script(env_vars, verbose=True)

    if return_code == 0:
        print("✅ Jenkins environment detection test passed")
        if "Jenkins" in stdout:
            print("✅ Correctly identified as Jenkins")
        else:
            print("❌ Failed to identify as Jenkins")
    else:
        print("❌ Jenkins environment detection test failed")
        print(f"Error: {stderr}")

    return return_code == 0 and "Jenkins" in stdout


def test_gitlab_ci():
    """Test GitLab CI environment detection."""
    print("\n=== Testing GitLab CI Environment ===")
    env_vars = {
        "CI": "true",
        "GITLAB_CI": "true",
        "CI_PROJECT_ID": "12345",
        "CI_PROJECT_NAME": "project",
        "CI_PIPELINE_ID": "123456",
        "CI_COMMIT_SHA": "1234567890abcdef1234567890abcdef12345678",
    }

    return_code, stdout, stderr = run_detect_script(env_vars, verbose=True)

    if return_code == 0:
        print("✅ GitLab CI environment detection test passed")
        if "GitLab CI" in stdout:
            print("✅ Correctly identified as GitLab CI")
        else:
            print("❌ Failed to identify as GitLab CI")
    else:
        print("❌ GitLab CI environment detection test failed")
        print(f"Error: {stderr}")

    return return_code == 0 and "GitLab CI" in stdout


def test_docker():
    """Test Docker environment detection."""
    print("\n=== Testing Docker Environment ===")
    env_vars = {
        "DOCKER_ENVIRONMENT": "true",
        "DOCKER": "true",
    }

    # Create temporary files to simulate Docker environment
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create .dockerenv file
        docker_env_path = Path(temp_dir) / ".dockerenv"
        docker_env_path.touch()

        # Create cgroup file
        cgroup_dir = Path(temp_dir) / "proc" / "1" / "cgroup"
        cgroup_dir.parent.mkdir(parents=True, exist_ok=True)
        cgroup_dir.write_text("12:memory:/docker/abcdef1234567890\n")

        # Add the temporary directory to the environment variables
        env_vars["TEMP_DOCKER_DIR"] = str(temp_dir)

        return_code, stdout, stderr = run_detect_script(env_vars, verbose=True)

    if return_code == 0:
        print("✅ Docker environment detection test passed")
        if "Docker" in stdout:
            print("✅ Correctly identified as Docker")
        else:
            print("❌ Failed to identify as Docker")
    else:
        print("❌ Docker environment detection test failed")
        print(f"Error: {stderr}")

    return return_code == 0 and "Docker" in stdout


def test_kubernetes():
    """Test Kubernetes environment detection."""
    print("\n=== Testing Kubernetes Environment ===")
    env_vars = {
        "KUBERNETES_SERVICE_HOST": "10.0.0.1",
        "KUBERNETES_SERVICE_PORT": "443",
    }

    # Create temporary files to simulate Kubernetes environment
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create Kubernetes secrets directory
        k8s_dir = Path(temp_dir) / "var" / "run" / "secrets" / "kubernetes.io"
        k8s_dir.mkdir(parents=True, exist_ok=True)

        # Create token file
        token_path = k8s_dir / "token"
        token_path.write_text("eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9...")

        # Add the temporary directory to the environment variables
        env_vars["TEMP_K8S_DIR"] = str(temp_dir)

        return_code, stdout, stderr = run_detect_script(env_vars, verbose=True)

    if return_code == 0:
        print("✅ Kubernetes environment detection test passed")
        if "Kubernetes" in stdout:
            print("✅ Correctly identified as Kubernetes")
        else:
            print("❌ Failed to identify as Kubernetes")
    else:
        print("❌ Kubernetes environment detection test failed")
        print(f"Error: {stderr}")

    return return_code == 0 and "Kubernetes" in stdout


def main():
    """Run the main function."""
    parser = argparse.ArgumentParser(description="Test CI environment detection")
    parser.add_argument("--all", action="store_true", help="Test all CI environments")
    parser.add_argument(
        "--github", action="store_true", help="Test GitHub Actions environment"
    )
    parser.add_argument(
        "--jenkins", action="store_true", help="Test Jenkins environment"
    )
    parser.add_argument(
        "--gitlab", action="store_true", help="Test GitLab CI environment"
    )
    parser.add_argument("--docker", action="store_true", help="Test Docker environment")
    parser.add_argument(
        "--kubernetes", action="store_true", help="Test Kubernetes environment"
    )

    args = parser.parse_args()

    # If no specific tests are specified, test all
    if not (
        args.github or args.jenkins or args.gitlab or args.docker or args.kubernetes
    ):
        args.all = True

    # Run the specified tests
    results = {}

    if args.all or args.github:
        results["GitHub Actions"] = test_github_actions()

    if args.all or args.jenkins:
        results["Jenkins"] = test_jenkins()

    if args.all or args.gitlab:
        results["GitLab CI"] = test_gitlab_ci()

    if args.all or args.docker:
        results["Docker"] = test_docker()

    if args.all or args.kubernetes:
        results["Kubernetes"] = test_kubernetes()

    # Print summary
    print("\n=== Test Summary ===")
    for env, result in results.items():
        status = "✅ Passed" if result else "❌ Failed"
        print(f"{env}: {status}")

    # Return success if all tests passed
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
