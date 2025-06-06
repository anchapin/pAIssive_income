#!/usr/bin/env python3
"""
Validate dependency versions across requirements files.

This script checks for version conflicts between requirements.txt, 
requirements-dev.txt, and requirements-ci.txt files.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def parse_requirements_file(file_path: Path) -> Dict[str, str]:
    """Parse a requirements file and return package name to version mapping."""
    packages = {}
    
    if not file_path.exists():
        print(f"Warning: {file_path} does not exist")
        return packages
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Skip lines with -r or -e flags
            if line.startswith(('-r', '-e')):
                continue
            
            # Extract package name and version constraint
            # Handle formats like: package>=1.0.0,<2.0.0
            match = re.match(r'^([a-zA-Z0-9_-]+)([><=!,.\d\s]+)?', line)
            if match:
                package_name = match.group(1).lower()
                version_spec = match.group(2) or ""
                packages[package_name] = version_spec.strip()
            else:
                print(f"Warning: Could not parse line {line_num} in {file_path}: {line}")
    
    return packages


def find_conflicts(files_packages: Dict[str, Dict[str, str]]) -> List[Tuple[str, Dict[str, str]]]:
    """Find packages with conflicting version specifications."""
    conflicts = []
    
    # Get all unique package names
    all_packages: Set[str] = set()
    for packages in files_packages.values():
        all_packages.update(packages.keys())
    
    # Check each package for conflicts
    for package in sorted(all_packages):
        package_versions = {}
        
        for file_name, packages in files_packages.items():
            if package in packages:
                package_versions[file_name] = packages[package]
        
        # If package appears in multiple files with different versions, it's a conflict
        if len(package_versions) > 1:
            unique_versions = set(package_versions.values())
            if len(unique_versions) > 1:
                conflicts.append((package, package_versions))
    
    return conflicts


def check_missing_security_tools(files_packages: Dict[str, Dict[str, str]]) -> List[str]:
    """Check for missing security tools."""
    security_tools = ['safety', 'bandit', 'click']
    missing_tools = []
    
    # Check if security tools are present in any requirements file
    all_packages: Set[str] = set()
    for packages in files_packages.values():
        all_packages.update(packages.keys())
    
    for tool in security_tools:
        if tool not in all_packages:
            missing_tools.append(tool)
    
    return missing_tools


def main():
    """Main validation function."""
    print("🔍 Validating dependency versions...")
    
    # Define requirements files to check
    requirements_files = {
        'requirements.txt': Path('requirements.txt'),
        'requirements-dev.txt': Path('requirements-dev.txt'),
        'requirements-ci.txt': Path('requirements-ci.txt'),
    }
    
    # Parse all requirements files
    files_packages = {}
    for name, path in requirements_files.items():
        files_packages[name] = parse_requirements_file(path)
        print(f"📄 Parsed {name}: {len(files_packages[name])} packages")
    
    # Find conflicts
    conflicts = find_conflicts(files_packages)
    
    # Check for missing security tools
    missing_tools = check_missing_security_tools(files_packages)
    
    # Report results
    if conflicts:
        print("\n❌ Version conflicts found:")
        for package, versions in conflicts:
            print(f"  📦 {package}:")
            for file_name, version in versions.items():
                print(f"    - {file_name}: {version}")
        print()
    else:
        print("\n✅ No version conflicts found!")
    
    if missing_tools:
        print(f"⚠️  Missing security tools: {', '.join(missing_tools)}")
    else:
        print("✅ All required security tools are present!")
    
    # Summary
    total_packages = len(set().union(*[packages.keys() for packages in files_packages.values()]))
    print(f"\n📊 Summary:")
    print(f"  - Total unique packages: {total_packages}")
    print(f"  - Version conflicts: {len(conflicts)}")
    print(f"  - Missing security tools: {len(missing_tools)}")
    
    # Exit with error code if there are issues
    if conflicts or missing_tools:
        print("\n❌ Dependency validation failed!")
        sys.exit(1)
    else:
        print("\n✅ Dependency validation passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
