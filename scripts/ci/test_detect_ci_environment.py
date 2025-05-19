#!/usr/bin/env python3
"""
Unit tests for the CI environment detection script.

This script tests the detect_ci_environment.py script by mocking different environments.

Usage:
    python -m unittest test_detect_ci_environment.py
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the path so we can import the script
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the script to test
from scripts.ci.detect_ci_environment import detect_ci_environment, safe_file_exists, safe_read_file


class TestDetectCIEnvironment(unittest.TestCase):
    """Test cases for the detect_ci_environment.py script."""

    def setUp(self):
        """Set up the test environment."""
        # Save original environment variables
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up after each test."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_safe_file_exists(self):
        """Test the safe_file_exists function."""
        # Test with a file that exists
        self.assertTrue(safe_file_exists(__file__))

        # Test with a file that doesn't exist
        self.assertFalse(safe_file_exists("/path/to/nonexistent/file"))

    def test_safe_read_file(self):
        """Test the safe_read_file function."""
        # Test with a file that exists
        self.assertIsNotNone(safe_read_file(__file__))

        # Test with a file that doesn't exist
        self.assertIsNone(safe_read_file("/path/to/nonexistent/file"))

    def test_detect_os_environment(self):
        """Test OS environment detection."""
        env_info = detect_ci_environment()

        # Should detect one of these operating systems
        self.assertTrue(
            env_info["os"]["is_windows"] or
            env_info["os"]["is_macos"] or
            env_info["os"]["is_linux"]
        )

        # Platform should match the detected OS
        if env_info["os"]["is_windows"]:
            self.assertEqual(env_info["os"]["platform"], "Windows")
        elif env_info["os"]["is_macos"]:
            self.assertEqual(env_info["os"]["platform"], "Darwin")
        elif env_info["os"]["is_linux"]:
            self.assertEqual(env_info["os"]["platform"], "Linux")

    @patch.dict(os.environ, {"WSL_DISTRO_NAME": "Ubuntu"})
    @patch("platform.system", return_value="Linux")
    def test_detect_wsl_environment(self, mock_system):
        """Test WSL environment detection."""
        env_info = detect_ci_environment()

        # Should detect WSL
        self.assertTrue(env_info["os"]["is_wsl"])

    @patch.dict(os.environ, {"CI": "true", "GITHUB_ACTIONS": "true", "GITHUB_WORKFLOW": "test", "GITHUB_RUN_ID": "12345"})
    def test_detect_github_actions_environment(self):
        """Test GitHub Actions environment detection."""
        env_info = detect_ci_environment()

        # Should detect CI and GitHub Actions
        self.assertTrue(env_info["ci"]["is_ci"])
        self.assertEqual(env_info["ci"]["ci_type"], "github")
        self.assertEqual(env_info["ci"]["ci_platform"], "GitHub Actions")

        # Should include GitHub environment variables
        self.assertIn("GITHUB_ACTIONS", env_info["ci"]["ci_environment_variables"])
        self.assertIn("GITHUB_WORKFLOW", env_info["ci"]["ci_environment_variables"])
        self.assertIn("GITHUB_RUN_ID", env_info["ci"]["ci_environment_variables"])

    @patch.dict(os.environ, {"CI": "true", "JENKINS_URL": "http://jenkins.example.com/"})
    def test_detect_jenkins_environment(self):
        """Test Jenkins environment detection."""
        env_info = detect_ci_environment()

        # Should detect CI and Jenkins
        self.assertTrue(env_info["ci"]["is_ci"])
        self.assertEqual(env_info["ci"]["ci_type"], "jenkins")
        self.assertEqual(env_info["ci"]["ci_platform"], "Jenkins")

        # Should include Jenkins environment variables
        self.assertIn("JENKINS_URL", env_info["ci"]["ci_environment_variables"])

    @patch.dict(os.environ, {"CI": "true", "GITLAB_CI": "true"})
    def test_detect_gitlab_ci_environment(self):
        """Test GitLab CI environment detection."""
        env_info = detect_ci_environment()

        # Should detect CI and GitLab CI
        self.assertTrue(env_info["ci"]["is_ci"])
        self.assertEqual(env_info["ci"]["ci_type"], "gitlab")
        self.assertEqual(env_info["ci"]["ci_platform"], "GitLab CI")

        # Should include GitLab CI environment variables
        self.assertIn("GITLAB_CI", env_info["ci"]["ci_environment_variables"])

    @patch.dict(os.environ, {"CI": "true", "CI_TYPE": "github", "CI_PLATFORM": "GitHub Actions"})
    def test_detect_ci_with_type_and_platform(self):
        """Test CI environment detection with CI_TYPE and CI_PLATFORM."""
        env_info = detect_ci_environment()

        # Should detect CI
        self.assertTrue(env_info["ci"]["is_ci"])

        # CI_TYPE and CI_PLATFORM are not automatically added to ci_environment_variables
        # because they don't match any of the specific CI platform prefixes
        # Just check that CI is detected
        self.assertEqual(env_info["ci"]["ci_type"], "generic")
        self.assertEqual(env_info["ci"]["ci_platform"], "Generic CI")

    @patch("scripts.ci.detect_ci_environment.safe_file_exists")
    @patch("scripts.ci.detect_ci_environment.safe_read_file", return_value="12:memory:/docker/abcdef1234567890\n")
    def test_detect_docker_environment(self, mock_read_file, mock_file_exists):
        """Test Docker environment detection."""
        # Mock the file exists check to return True only for specific paths
        mock_file_exists.side_effect = lambda path: path == "/proc/1/cgroup"

        env_info = detect_ci_environment()

        # Should detect Docker
        self.assertTrue(env_info["container"]["is_docker"])
        self.assertTrue(env_info["container"]["is_containerized"])
        self.assertEqual(env_info["container"]["detection_method"], "cgroup file")

    @patch.dict(os.environ, {"DOCKER_ENVIRONMENT": "true"})
    def test_detect_docker_environment_from_env(self):
        """Test Docker environment detection from environment variables."""
        env_info = detect_ci_environment()

        # Should detect Docker
        self.assertTrue(env_info["container"]["is_docker"])
        self.assertTrue(env_info["container"]["is_containerized"])
        self.assertEqual(env_info["container"]["detection_method"], "environment variable")

    @patch.dict(os.environ, {"KUBERNETES_SERVICE_HOST": "10.0.0.1", "KUBERNETES_PORT": "443"})
    def test_detect_kubernetes_environment(self):
        """Test Kubernetes environment detection."""
        env_info = detect_ci_environment()

        # Should detect Kubernetes
        self.assertTrue(env_info["container"]["is_kubernetes"])
        self.assertTrue(env_info["container"]["is_containerized"])

    @patch.dict(os.environ, {"COMPOSE_PROJECT_NAME": "test"})
    def test_detect_docker_compose_environment(self):
        """Test Docker Compose environment detection."""
        env_info = detect_ci_environment()

        # Should detect Docker Compose
        self.assertTrue(env_info["container"]["is_docker_compose"])
        self.assertTrue(env_info["container"]["is_containerized"])

    @patch.dict(os.environ, {"DOCKER_SWARM": "true"})
    def test_detect_docker_swarm_environment(self):
        """Test Docker Swarm environment detection."""
        env_info = detect_ci_environment()

        # Should detect Docker Swarm
        self.assertTrue(env_info["container"]["is_docker_swarm"])
        self.assertTrue(env_info["container"]["is_containerized"])

    @patch.dict(os.environ, {"AWS_REGION": "us-west-2"})
    def test_detect_aws_environment(self):
        """Test AWS environment detection."""
        env_info = detect_ci_environment()

        # Should detect AWS
        self.assertTrue(env_info["cloud"]["is_aws"])
        self.assertTrue(env_info["cloud"]["is_cloud"])

    @patch.dict(os.environ, {"AWS_REGION": "us-west-2", "AWS_LAMBDA_FUNCTION_NAME": "test-function"})
    def test_detect_aws_lambda_environment(self):
        """Test AWS Lambda environment detection."""
        env_info = detect_ci_environment()

        # Should detect AWS and AWS Lambda
        self.assertTrue(env_info["cloud"]["is_aws"])
        self.assertTrue(env_info["cloud"]["is_lambda"])
        self.assertTrue(env_info["cloud"]["is_serverless"])

    @patch.dict(os.environ, {"AZURE_FUNCTIONS_ENVIRONMENT": "Development"})
    def test_detect_azure_functions_environment(self):
        """Test Azure Functions environment detection."""
        env_info = detect_ci_environment()

        # Should detect Azure and Azure Functions
        self.assertTrue(env_info["cloud"]["is_azure"])
        self.assertTrue(env_info["cloud"]["is_azure_functions"])
        self.assertTrue(env_info["cloud"]["is_serverless"])

    @patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project", "FUNCTION_NAME": "test-function", "FUNCTION_REGION": "us-central1"})
    def test_detect_gcp_cloud_functions_environment(self):
        """Test GCP Cloud Functions environment detection."""
        env_info = detect_ci_environment()

        # Should detect GCP and GCP Cloud Functions
        self.assertTrue(env_info["cloud"]["is_gcp"])
        self.assertTrue(env_info["cloud"]["is_cloud_functions"])
        self.assertTrue(env_info["cloud"]["is_serverless"])


if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
