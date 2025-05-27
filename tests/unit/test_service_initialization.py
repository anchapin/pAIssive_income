"""Tests for service_initialization.py."""

import logging
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the scripts/utils directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "utils"))

import pytest

from service_initialization import Service, initialize_services, main


class TestService(unittest.TestCase):
    """Test cases for the Service class."""

    def test_init(self):
        """Test Service initialization."""
        service = Service("test_service")
        self.assertEqual(service.name, "test_service")
        self.assertFalse(service.initialized)

    def test_initialize(self):
        """Test Service.initialize method."""
        with self.assertLogs(level=logging.INFO) as logs:
            service = Service("test_service")
            service.initialize()
            self.assertTrue(service.initialized)
            self.assertIn("Service 'test_service' initialized", logs.output[0])


class TestInitializeServices(unittest.TestCase):
    """Test cases for the initialize_services function."""

    def test_initialize_services_empty(self):
        """Test initialize_services with empty list."""
        services = initialize_services([])
        self.assertEqual(len(services), 0)

    def test_initialize_services_single(self):
        """Test initialize_services with a single service."""
        services = initialize_services(["test_service"])
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].name, "test_service")
        self.assertTrue(services[0].initialized)

    def test_initialize_services_multiple(self):
        """Test initialize_services with multiple services."""
        service_names = ["service1", "service2", "service3"]
        services = initialize_services(service_names)
        self.assertEqual(len(services), 3)
        for i, service in enumerate(services):
            self.assertEqual(service.name, service_names[i])
            self.assertTrue(service.initialized)


class TestMain(unittest.TestCase):
    """Test cases for the main function."""

    @patch("service_initialization.initialize_services")
    @patch("service_initialization.logging.basicConfig")
    def test_main(self, mock_logging_config, mock_initialize_services):
        """Test main function."""
        main()
        mock_logging_config.assert_called_once_with(level=logging.INFO)
        mock_initialize_services.assert_called_once_with(["auth", "database", "api"])


if __name__ == "__main__":
    unittest.main()
