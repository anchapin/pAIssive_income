#!/usr/bin/env python3
"""
Validate GitHub Actions workflows for common issues.

This script checks for:
1. YAML syntax errors
2. Matrix strategy issues
3. Missing required files
4. Complex conditional expressions
5. Dependency issues
"""

import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any


def validate_yaml_syntax(file_path: Path) -> List[str]:
    """Validate YAML syntax in workflow files."""
    issues = []
    try:
        # Try multiple encodings to handle encoding issues
        for encoding in ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']:
            try:
                with file_path.open(encoding=encoding) as f:
                    yaml.safe_load(f)
                break  # Success, exit the encoding loop
            except UnicodeDecodeError:
                continue  # Try next encoding
        else:
            # If all encodings failed
            issues.append(f"Encoding error in {file_path}: Unable to decode with any encoding")
    except yaml.YAMLError as e:
        issues.append(f"YAML syntax error in {file_path}: {e}")
    except Exception as e:
        issues.append(f"Error reading {file_path}: {e}")
    return issues


def check_matrix_strategy(workflow_data: Dict[str, Any], file_path: Path) -> List[str]:
    """Check for problematic matrix strategies."""
    issues = []
    
    if 'jobs' not in workflow_data:
        return issues
    
    for job_name, job_data in workflow_data['jobs'].items():
        if isinstance(job_data, dict) and 'strategy' in job_data:
            strategy = job_data['strategy']
            if isinstance(strategy, dict) and 'matrix' in strategy:
                matrix = strategy['matrix']
                
                # Check for complex conditional expressions in matrix
                for key, value in matrix.items():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and '${{' in item and '&&' in item:
                                issues.append(
                                    f"Complex conditional in matrix {key} in job {job_name} "
                                    f"in {file_path}: {item}"
                                )
                            elif isinstance(item, str) and item == '':
                                issues.append(
                                    f"Empty string in matrix {key} in job {job_name} "
                                    f"in {file_path}"
                                )
    
    return issues


def check_required_files() -> List[str]:
    """Check for missing required files that workflows expect."""
    issues = []
    
    required_files = [
        "package.json",
        "requirements.txt",
        "src/math.js",
        "src/math.test.js",
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"Missing required file: {file_path}")
    
    return issues


def check_directory_structure() -> List[str]:
    """Check for missing required directories."""
    issues = []
    
    required_dirs = [
        "security-reports",
        "coverage",
        "ci-reports",
        "src",
        "ui/static/css",
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            issues.append(f"Missing required directory: {dir_path}")
    
    return issues


def check_workflow_triggers(workflow_data: Dict[str, Any], file_path: Path) -> List[str]:
    """Check for problematic workflow triggers."""
    issues = []
    
    if 'on' not in workflow_data:
        issues.append(f"No triggers defined in {file_path}")
        return issues
    
    triggers = workflow_data['on']
    
    # Check for overly broad path filters
    if isinstance(triggers, dict):
        for trigger_type in ['push', 'pull_request']:
            if trigger_type in triggers and isinstance(triggers[trigger_type], dict):
                trigger_config = triggers[trigger_type]
                if 'paths' in trigger_config:
                    paths = trigger_config['paths']
                    if isinstance(paths, list) and len(paths) > 10:
                        issues.append(
                            f"Too many path filters in {trigger_type} trigger in {file_path}"
                        )
    
    return issues


def validate_workflow_file(file_path: Path) -> List[str]:
    """Validate a single workflow file."""
    issues = []
    
    # Check YAML syntax
    issues.extend(validate_yaml_syntax(file_path))
    
    try:
        # Try multiple encodings to handle encoding issues
        workflow_data = None
        for encoding in ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']:
            try:
                with file_path.open(encoding=encoding) as f:
                    workflow_data = yaml.safe_load(f)
                break  # Success, exit the encoding loop
            except UnicodeDecodeError:
                continue  # Try next encoding
        
        if workflow_data is None:
            issues.append(f"Unable to read {file_path} with any encoding")
            return issues
        
        if not isinstance(workflow_data, dict):
            issues.append(f"Invalid workflow structure in {file_path}")
            return issues
        
        # Check matrix strategies
        issues.extend(check_matrix_strategy(workflow_data, file_path))
        
        # Check workflow triggers
        issues.extend(check_workflow_triggers(workflow_data, file_path))
        
    except Exception as e:
        issues.append(f"Error validating {file_path}: {e}")
    
    return issues


def main():
    """Main validation function."""
    print("🔍 Validating GitHub Actions workflows...")
    
    all_issues = []
    
    # Check required files and directories
    all_issues.extend(check_required_files())
    all_issues.extend(check_directory_structure())
    
    # Validate workflow files
    workflows_dir = Path(".github/workflows")
    if workflows_dir.exists():
        for workflow_file in workflows_dir.glob("*.yml"):
            if workflow_file.name.endswith(('.yml', '.yaml')):
                issues = validate_workflow_file(workflow_file)
                all_issues.extend(issues)
    
    # Report results
    if all_issues:
        print(f"\n❌ Found {len(all_issues)} issues:")
        for issue in all_issues:
            print(f"  • {issue}")
        
        print("\n🔧 Suggested fixes:")
        print("  1. Run: python fix_pr_166_workflows.py")
        print("  2. Use simplified workflow files (*-simplified.yml, *-fixed.yml)")
        print("  3. Check matrix strategies for complex conditionals")
        print("  4. Ensure all required files and directories exist")
        
        return 1
    else:
        print("✅ All workflows validated successfully!")
        return 0


if __name__ == "__main__":
    exit(main())
