#!/usr/bin/env python3
"""
Coverage validation script for the pAIssive Income project.

This script validates that the test coverage meets the required 15% threshold
and ensures that coverage.xml files are generated correctly.
"""

import sys
from pathlib import Path

try:
    from defusedxml import ElementTree as ET
except ImportError:
    # Fallback to standard library with warning
    import xml.etree.ElementTree as ET
    import warnings
    warnings.warn(
        "defusedxml not available, using xml.etree.ElementTree. "
        "Install defusedxml for better security: pip install defusedxml",
        UserWarning
    )


def validate_coverage_xml(coverage_file: str = "coverage.xml", min_threshold: float = 15.0) -> bool:
    """
    Validate that the coverage.xml file exists and meets the minimum threshold.
    
    Args:
        coverage_file: Path to the coverage.xml file
        min_threshold: Minimum coverage percentage required
        
    Returns:
        True if coverage meets threshold, False otherwise
    """
    coverage_path = Path(coverage_file)
    
    if not coverage_path.exists():
        print(f"❌ Coverage file not found: {coverage_file}")
        return False
    
    try:
        tree = ET.parse(coverage_path)
        root = tree.getroot()
        
        # Extract coverage data
        line_rate = float(root.get('line-rate', 0))
        lines_valid = int(root.get('lines-valid', 0))
        lines_covered = int(root.get('lines-covered', 0))
        
        coverage_percent = line_rate * 100
        
        print(f"📊 Coverage Report:")
        print(f"   Total lines: {lines_valid}")
        print(f"   Covered lines: {lines_covered}")
        print(f"   Coverage: {coverage_percent:.2f}%")
        print(f"   Required: {min_threshold}%")
        
        if coverage_percent >= min_threshold:
            print(f"✅ Coverage meets {min_threshold}% requirement")
            return True
        else:
            print(f"❌ Coverage below {min_threshold}% requirement")
            return False
            
    except ET.ParseError as e:
        print(f"❌ Error parsing coverage.xml: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating coverage: {e}")
        return False


def main():
    """Main function to validate coverage."""
    print("🔍 Validating test coverage...")
    
    # Validate main coverage file
    success = validate_coverage_xml()
    
    if success:
        print("\n🎉 All coverage validations passed!")
        sys.exit(0)
    else:
        print("\n💥 Coverage validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
