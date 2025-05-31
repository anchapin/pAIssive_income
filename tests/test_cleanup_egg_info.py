"""Tests for cleanup_egg_info.py."""

import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the scripts/utils directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "utils"))

from cleanup_egg_info import cleanup_egg_info


class TestCleanupEggInfo:
    """Test suite for cleanup_egg_info.py."""

    def setup_method(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Clean up after tests."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)

    def test_cleanup_egg_info_no_directories(self):
        """Test cleanup_egg_info with no .egg-info directories."""
        with patch("cleanup_egg_info.logger.info") as mock_info:
            cleanup_egg_info()
            mock_info.assert_called_with("No .egg-info directories found.")

    def test_cleanup_egg_info_with_directories(self):
        """Test cleanup_egg_info with .egg-info directories."""
        # Create some .egg-info directories
        os.makedirs(os.path.join(self.temp_dir, "package1.egg-info"))
        os.makedirs(os.path.join(self.temp_dir, "package2.egg-info"))
        os.makedirs(os.path.join(self.temp_dir, "subdir", "package3.egg-info"), exist_ok=True)

        with patch("cleanup_egg_info.logger.info") as mock_info:
            cleanup_egg_info()
            # Check that the directories were removed
            assert not os.path.exists(os.path.join(self.temp_dir, "package1.egg-info"))
            assert not os.path.exists(os.path.join(self.temp_dir, "package2.egg-info"))
            assert not os.path.exists(os.path.join(self.temp_dir, "subdir", "package3.egg-info"))
            # Check that the correct log messages were produced
            mock_info.assert_any_call("Removed %d .egg-info directories.", 3)

    def test_cleanup_egg_info_with_error(self):
        """Test cleanup_egg_info with an error during removal."""
        # Create a .egg-info directory
        os.makedirs(os.path.join(self.temp_dir, "package.egg-info"))

        # Mock shutil.rmtree to raise an exception
        with patch("cleanup_egg_info.shutil.rmtree") as mock_rmtree:
            mock_rmtree.side_effect = OSError("Permission denied")
            # The function doesn't handle errors, so it should raise
            with pytest.raises(OSError):
                cleanup_egg_info()
