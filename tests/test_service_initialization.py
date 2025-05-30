"""test_service_initialization - Module for tests.test_service_initialization."""

import logging
import unittest
from unittest.mock import MagicMock, patch

from scripts.utils.service_initialization import Service, initialize_services


class TestService(unittest.TestCase):
    """Test cases for the Service class."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = Service("test_service")

    def test_service_initialization(self):
        """Test basic service initialization."""
        self.assertEqual(self.service.name, "test_service")
        self.assertFalse(self.service.initialized)

    def test_service_initialize(self):
        """Test service initialization method."""
        with patch("logging.Logger.info") as mock_info:
            self.service.initialize()
            self.assertTrue(self.service.initialized)
            mock_info.assert_called_once_with("Service '%s' initialized.", "test_service")

    def test_service_initialize_multiple_times(self):
        """Test that initializing a service multiple times doesn't cause issues."""
        with patch("logging.Logger.info") as mock_info:
            self.service.initialize()
            self.service.initialize()
            self.assertTrue(self.service.initialized)
            self.assertEqual(mock_info.call_count, 2)

    def test_service_with_empty_name(self):
        """Test service initialization with empty name."""
        service = Service("")
        self.assertEqual(service.name, "")
        self.assertFalse(service.initialized)


class TestInitializeServices(unittest.TestCase):
    """Test cases for the initialize_services function."""

    def test_initialize_services_empty_list(self):
        """Test initializing services with an empty list."""
        services = initialize_services([])
        self.assertEqual(len(services), 0)

    def test_initialize_services_single_service(self):
        """Test initializing a single service."""
        with patch("logging.Logger.info") as mock_info:
            services = initialize_services(["auth"])
            self.assertEqual(len(services), 1)
            self.assertEqual(services[0].name, "auth")
            self.assertTrue(services[0].initialized)
            mock_info.assert_called_once_with("Service '%s' initialized.", "auth")

    def test_initialize_services_multiple_services(self):
        """Test initializing multiple services."""
        service_names = ["auth", "database", "api"]
        with patch("logging.Logger.info") as mock_info:
            services = initialize_services(service_names)
            self.assertEqual(len(services), 3)
            for service in services:
                self.assertTrue(service.initialized)
            self.assertEqual(mock_info.call_count, 3)

    def test_initialize_services_with_duplicates(self):
        """Test initializing services with duplicate names."""
        service_names = ["auth", "auth", "database"]
        with patch("logging.Logger.info") as mock_info:
            services = initialize_services(service_names)
            self.assertEqual(len(services), 3)
            self.assertEqual(services[0].name, "auth")
            self.assertEqual(services[1].name, "auth")
            self.assertEqual(services[2].name, "database")
            self.assertEqual(mock_info.call_count, 3)

    def test_initialize_services_with_special_characters(self):
        """Test initializing services with special characters in names."""
        service_names = ["auth-service", "db_connection", "api/v1"]
        with patch("logging.Logger.info") as mock_info:
            services = initialize_services(service_names)
            self.assertEqual(len(services), 3)
            for service in services:
                self.assertTrue(service.initialized)
            self.assertEqual(mock_info.call_count, 3)


if __name__ == "__main__":
    unittest.main()
