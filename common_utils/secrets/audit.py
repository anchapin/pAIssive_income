"""
Secrets Auditing Tool

This module provides tools to scan the codebase for potentially hardcoded secrets.
"""

import os
import re
import sys
import argparse
import logging
from typing import List, Dict, Set, Tuple, Pattern, Any
from pathlib import Path
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# Common patterns that might indicate hardcoded secrets
SECRET_PATTERNS = [
    # API keys
    r'(?i)(?:api|access|auth|app|secret|private)[-_]?key\s*=\s*[\'"`]([^\'"`\s]{10,})[\'"`]',
    # Passwords
    r'(?i)(?:password|passwd|pwd|auth)[-_]?\s*=\s*[\'"`]([^\'"`\s]{4,})[\'"`]',
    # Tokens
    r'(?i)(?:token|auth[-_]?token|jwt|bearer)\s*=\s*[\'"`]([^\'"`\s]{10,})[\'"`]',
    # Connection strings
    r'(?i)(?:connection[-_]?string|conn[-_]?str)\s*=\s*[\'"`]([^\'"`]{10,})[\'"`]',
    # Database credentials
    r'(?i)mongodb(?:\+srv)?:\/\/[^:]+:([^@]+)@',
    r'(?i)(?:postgres|mysql|postgresql):\/\/[^:]+:([^@]+)@',
    # AWS
    r'(?i)(?:aws)?_?(?:access|secret|account)_?(?:key|token|id)\s*=\s*[\'"`]([^\'"`\s]{10,})[\'"`]',
    # OAuth
    r'(?i)(?:oauth|client)[-_]?(?:token|secret)\s*=\s*[\'"`]([^\'"`\s]{10,})[\'"`]',
]

# File patterns to include/exclude
INCLUDE_PATTERNS = [
    r'\.py$',         # Python files
    r'\.js$',         # JavaScript files
    r'\.ts$',         # TypeScript files
    r'\.jsx$',        # React JSX files
    r'\.tsx$',        # React TSX files
    r'\.env$',        # Env files
    r'\.yaml$',       # YAML files
    r'\.yml$',        # YAML files
    r'\.json$',       # JSON files
    r'\.xml$',        # XML files
    r'\.properties$', # Properties files
    r'\.cfg$',        # Config files
    r'\.ini$',        # Init files
    r'\.conf$',       # Conf files
]

EXCLUDE_PATTERNS = [
    r'(?i)/venv/',
    r'(?i)/node_modules/',
    r'(?i)/__pycache__/',
    r'(?i)/\.[^/]+/',  # Hidden directories
    r'(?i)\.min\.',    # Minified files
    r'(?i)\.pyc$',     # Compiled Python
    r'\.git',          # Git directory
]


def is_file_included(filepath: str) -> bool:
    """
    Check if a file should be included in the scan.
    
    Args:
        filepath: Path to the file
        
    Returns:
        True if the file should be included, False otherwise
    """
    # Check exclude patterns first
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, filepath):
            return False
    
    # Then check include patterns
    for pattern in INCLUDE_PATTERNS:
        if re.search(pattern, filepath):
            return True
    
    # Default to exclude
    return False


def is_likely_secret(value: str) -> bool:
    """
    Determine if a string is likely to be a secret.
    
    Args:
        value: The string to check
        
    Returns:
        True if the string is likely a secret, False otherwise
    """
    # Skip very short strings
    if len(value) < 8:
        return False
    
    # Skip strings that are clearly not secrets
    if value.lower() in ('true', 'false', 'yes', 'no', 'none', 'null'):
        return False
    
    # Skip URL without credentials
    if value.startswith(('http://', 'https://')) and not re.search(r':|@', value):
        return False
    
    # Look for entropy and patterns that suggest a secret
    # Has mixed case, numbers, special chars, etc.
    has_uppercase = bool(re.search(r'[A-Z]', value))
    has_lowercase = bool(re.search(r'[a-z]', value))
    has_numbers = bool(re.search(r'[0-9]', value))
    has_special = bool(re.search(r'[^A-Za-z0-9]', value))
    
    # If it has good entropy, it's more likely to be a secret
    entropy_score = sum([has_uppercase, has_lowercase, has_numbers, has_special])
    return entropy_score >= 2


def find_secrets_in_file(filepath: str, compiled_patterns: List[Pattern]) -> List[Dict[str, Any]]:
    """
    Scan a file for potential secrets.
    
    Args:
        filepath: Path to the file
        compiled_patterns: List of compiled regex patterns
        
    Returns:
        List of findings (dicts with filename, line number, pattern, etc.)
    """
    findings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            for pattern_index, pattern in enumerate(compiled_patterns):
                matches = pattern.findall(line)
                for match in matches:
                    # Skip false positives
                    if not isinstance(match, str):
                        if isinstance(match, tuple):
                            # Some patterns capture groups
                            match = match[0] if match else ""
                        else:
                            continue
                    
                    # Further filtering to reduce false positives
                    if is_likely_secret(match):
                        findings.append({
                            'file': filepath,
                            'line': line_num,
                            'pattern_index': pattern_index,
                            'content': line.strip(),
                            'match': match
                        })
        
        return findings
    except Exception as e:
        logger.warning(f"Error scanning file {filepath}: {str(e)}")
        return []


def scan_directory(directory: str, exclude_dirs: List[str] = None) -> List[Dict[str, Any]]:
    """
    Recursively scan a directory for files containing potential secrets.
    
    Args:
        directory: Directory to scan
        exclude_dirs: List of directories to exclude
        
    Returns:
        List of findings across all files
    """
    exclude_dirs = exclude_dirs or []
    all_findings = []
    
    # Compile regex patterns for better performance
    compiled_patterns = [re.compile(pattern) for pattern in SECRET_PATTERNS]
    
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for filename in files:
            filepath = os.path.join(root, filename)
            
            # Check if the file should be included
            if is_file_included(filepath):
                file_findings = find_secrets_in_file(filepath, compiled_patterns)
                all_findings.extend(file_findings)
    
    return all_findings


def format_findings(findings: List[Dict[str, Any]]) -> str:
    """
    Format the findings into a readable report.
    
    Args:
        findings: List of findings
        
    Returns:
        Formatted report
    """
    if not findings:
        return "No potential secrets found."
    
    report = f"Found {len(findings)} potential hardcoded secrets:\n\n"
    
    for i, finding in enumerate(findings, 1):
        report += f"{i}. File: {finding['file']}\n"
        report += f"   Line {finding['line']}: {finding['content']}\n"
        report += f"   Potential secret: {finding['match']}\n\n"
    
    report += "\nRecommendation: Replace hardcoded secrets with proper secret management.\n"
    report += "Use the secrets management module: common_utils.secrets\n"
    report += "Example: secret_value = get_secret('API_KEY')\n"
    
    return report


def main() -> int:
    """
    Main entry point for the secrets audit tool.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="Scan codebase for potential hardcoded secrets."
    )
    parser.add_argument(
        "directory", 
        nargs="?", 
        default=".", 
        help="Directory to scan (default: current directory)"
    )
    parser.add_argument(
        "--output", 
        help="Output file for the report (default: print to console)"
    )
    parser.add_argument(
        "--json", 
        action="store_true", 
        help="Output in JSON format"
    )
    parser.add_argument(
        "--exclude", 
        nargs="+", 
        default=[], 
        help="Additional directories to exclude"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Scanning directory: {args.directory}")
    findings = scan_directory(args.directory, args.exclude)
    
    if args.json:
        # Output in JSON format
        report = json.dumps(findings, indent=2)
    else:
        # Output in human-readable format
        report = format_findings(findings)
    
    if args.output:
        # Write to output file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report written to {args.output}")
    else:
        # Print to console
        print(report)
    
    return 0 if len(findings) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())