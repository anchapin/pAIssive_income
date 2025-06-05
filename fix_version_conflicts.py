#!/usr/bin/env python3
"""
Fix version conflicts in dependencies for PR #139.

This script addresses specific version conflicts identified in the dependency check.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def fix_pydantic_version_conflict() -> bool:
    """Fix pydantic version conflict with safety package."""
    logger.info("=== Fixing Pydantic Version Conflict ===")
    
    try:
        # Downgrade pydantic to be compatible with safety
        logger.info("Downgrading pydantic to version compatible with safety...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pydantic>=2.6.0,<2.10.0"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            logger.info("✓ Pydantic version fixed")
            return True
        else:
            logger.warning(f"✗ Failed to fix pydantic version: {result.stderr}")
            return False
            
    except Exception as e:
        logger.warning(f"✗ Error fixing pydantic version: {e}")
        return False


def fix_click_version_conflict() -> bool:
    """Fix click version conflict with safety package."""
    logger.info("=== Fixing Click Version Conflict ===")
    
    try:
        # Downgrade click to be compatible with safety
        logger.info("Downgrading click to version compatible with safety...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "click>=8.0.2,<8.2.0"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            logger.info("✓ Click version fixed")
            return True
        else:
            logger.warning(f"✗ Failed to fix click version: {result.stderr}")
            return False
            
    except Exception as e:
        logger.warning(f"✗ Error fixing click version: {e}")
        return False


def verify_dependency_resolution() -> bool:
    """Verify that dependency conflicts are resolved."""
    logger.info("=== Verifying Dependency Resolution ===")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            logger.info("✓ All dependency conflicts resolved")
            return True
        else:
            logger.warning(f"✗ Remaining dependency conflicts:\n{result.stdout}\n{result.stderr}")
            return False
            
    except Exception as e:
        logger.warning(f"✗ Error verifying dependencies: {e}")
        return False


def update_requirements_with_fixed_versions() -> bool:
    """Update requirements files with the fixed versions."""
    logger.info("=== Updating Requirements Files ===")
    
    # Update main requirements.txt
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update pydantic version constraint
            content = content.replace(
                "pydantic>=2.6.0",
                "pydantic>=2.6.0,<2.10.0"
            )
            
            # Add click version constraint if not present
            if "click>=" not in content:
                content += "\nclick>=8.0.2,<8.2.0  # Version constraint for safety compatibility\n"
            
            with open(requirements_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info("✓ Updated requirements.txt")
            return True
            
        except Exception as e:
            logger.warning(f"✗ Error updating requirements.txt: {e}")
            return False
    else:
        logger.warning("✗ requirements.txt not found")
        return False


def main() -> int:
    """Main function to fix version conflicts."""
    logger.info("Starting version conflict fixes for PR #139")
    
    success = True
    
    # Fix pydantic version conflict
    if not fix_pydantic_version_conflict():
        success = False
    
    # Fix click version conflict  
    if not fix_click_version_conflict():
        success = False
    
    # Update requirements files
    if not update_requirements_with_fixed_versions():
        logger.warning("Failed to update requirements files")
    
    # Verify resolution
    if not verify_dependency_resolution():
        logger.warning("Some dependency conflicts may remain")
    
    if success:
        logger.info("✅ Version conflicts have been resolved!")
        return 0
    else:
        logger.error("❌ Some version conflicts could not be resolved")
        return 1


if __name__ == "__main__":
    sys.exit(main())
