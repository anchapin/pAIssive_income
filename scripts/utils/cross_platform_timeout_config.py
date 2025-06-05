#!/usr/bin/env python3
"""
Cross-platform timeout configuration utility for GitHub Actions workflows.
Provides platform-specific timeout recommendations and validation.
"""

import json
import os
import platform
import sys
from typing import Any, Dict, Optional


class CrossPlatformTimeoutConfig:
    """Manages timeout configurations across different platforms."""

    # Base timeout configurations in minutes
    BASE_TIMEOUTS = {
        "job_timeout": {
            "ubuntu": 90,
            "windows": 150,
            "macos": 120
        },
        "step_timeouts": {
            "node_install": {
                "ubuntu": 20,
                "windows": 35,
                "macos": 25
            },
            "essential_deps": {
                "ubuntu": 15,
                "windows": 30,
                "macos": 20
            },
            "unix_deps": {
                "ubuntu": 30,
                "macos": 40
            },
            "windows_deps": {
                "windows": 50
            },
            "javascript_tests": {
                "ubuntu": 15,
                "windows": 30,
                "macos": 20
            },
            "security_tools": {
                "ubuntu": 20,
                "windows": 40,
                "macos": 25
            },
            "security_scans": {
                "ubuntu": 25,
                "windows": 40,
                "macos": 35
            },
            "docker_build": {
                "ubuntu": 50
            }
        }
    }

    # Platform multipliers for different scenarios
    PLATFORM_MULTIPLIERS = {
        "ubuntu": 1.0,
        "windows": 1.5,  # Windows typically needs more time
        "macos": 1.2     # macOS sometimes needs more time
    }

    def __init__(self) -> None:
        self.current_platform = self._detect_platform()
        self.is_ci = self._is_ci_environment()

    def _detect_platform(self) -> str:
        """Detect the current platform."""
        system = platform.system().lower()
        if system == "linux":
            return "ubuntu"
        if system == "windows":
            return "windows"
        if system == "darwin":
            return "macos"
        return "ubuntu"  # Default fallback

    def _is_ci_environment(self) -> bool:
        """Check if running in CI environment."""
        ci_indicators = ["CI", "GITHUB_ACTIONS", "CONTINUOUS_INTEGRATION"]
        return any(os.getenv(indicator) for indicator in ci_indicators)

    def get_timeout(self, category: str, step: Optional[str] = None,
                   platform: Optional[str] = None) -> int:
        """Get timeout for a specific category and step."""
        target_platform = platform or self.current_platform

        if category == "job":
            return self.BASE_TIMEOUTS["job_timeout"].get(target_platform, 90)

        if step and step in self.BASE_TIMEOUTS["step_timeouts"]:
            step_config = self.BASE_TIMEOUTS["step_timeouts"][step]
            return step_config.get(target_platform, step_config.get("ubuntu", 15))

        return 15  # Default fallback

    def get_adjusted_timeout(self, base_timeout: int,
                           platform: Optional[str] = None) -> int:
        """Get platform-adjusted timeout."""
        target_platform = platform or self.current_platform
        multiplier = self.PLATFORM_MULTIPLIERS.get(target_platform, 1.0)

        # Add CI buffer if in CI environment
        if self.is_ci:
            multiplier *= 1.1

        return int(base_timeout * multiplier)

    def generate_workflow_timeouts(self) -> dict[str, Any]:
        """Generate timeout configuration for workflow files."""
        config = {
            "job_timeouts": {},
            "step_timeouts": {},
            "platform_info": {
                "current_platform": self.current_platform,
                "is_ci": self.is_ci,
                "multipliers": self.PLATFORM_MULTIPLIERS
            }
        }

        # Generate job timeouts
        for platform in ["ubuntu", "windows", "macos"]:
            config["job_timeouts"][platform] = self.get_timeout("job", platform=platform)

        # Generate step timeouts
        for step_name, step_config in self.BASE_TIMEOUTS["step_timeouts"].items():
            config["step_timeouts"][step_name] = {}
            for platform in step_config:
                config["step_timeouts"][step_name][platform] = step_config[platform]

        return config

    def validate_timeout_config(self, config: dict[str, Any]) -> bool:
        """Validate timeout configuration."""
        try:
            # Check required keys
            required_keys = ["job_timeouts", "step_timeouts"]
            if not all(key in config for key in required_keys):
                return False

            # Check timeout values are reasonable
            for timeout in config["job_timeouts"].values():
                if not isinstance(timeout, int) or timeout < 30 or timeout > 300:
                    return False

            return True
        except Exception:
            return False

    def export_config(self, output_file: str = "timeout_config.json") -> bool:
        """Export timeout configuration to JSON file."""
        try:
            config = self.generate_workflow_timeouts()
            with open(output_file, "w") as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to export config: {e}")
            return False

    def print_recommendations(self):
        """Print timeout recommendations for current platform."""
        print(f"=== Timeout Recommendations for {self.current_platform.upper()} ===")
        print(f"CI Environment: {self.is_ci}")
        print()

        print("Job Timeouts:")
        for platform in ["ubuntu", "windows", "macos"]:
            timeout = self.get_timeout("job", platform=platform)
            marker = " (current)" if platform == self.current_platform else ""
            print(f"  {platform}: {timeout} minutes{marker}")

        print("\nStep Timeouts:")
        for step_name in self.BASE_TIMEOUTS["step_timeouts"]:
            timeout = self.get_timeout("step", step_name)
            print(f"  {step_name}: {timeout} minutes")

        print(f"\nPlatform Multiplier: {self.PLATFORM_MULTIPLIERS.get(self.current_platform, 1.0)}")


def main():
    """Main function for command-line usage."""
    config = CrossPlatformTimeoutConfig()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "export":
            output_file = sys.argv[2] if len(sys.argv) > 2 else "timeout_config.json"
            if config.export_config(output_file):
                print(f"Configuration exported to {output_file}")
            else:
                print("Failed to export configuration")
                sys.exit(1)

        elif command == "validate":
            if len(sys.argv) < 3:
                print("Usage: python cross_platform_timeout_config.py validate <config_file>")
                sys.exit(1)

            config_file = sys.argv[2]
            try:
                with open(config_file) as f:
                    config_data = json.load(f)

                if config.validate_timeout_config(config_data):
                    print("Configuration is valid")
                else:
                    print("Configuration is invalid")
                    sys.exit(1)
            except Exception as e:
                print(f"Failed to validate configuration: {e}")
                sys.exit(1)

        else:
            print("Unknown command. Available commands: export, validate")
            sys.exit(1)
    else:
        config.print_recommendations()


if __name__ == "__main__":
    main()
