#!/usr/bin/env python3
"""
Test that key dependencies can be imported without conflicts.

This script attempts to import key packages to verify that there are no
import conflicts or missing dependencies.
"""

import sys
from typing import List, Tuple


def test_import(package_name: str, import_statement: str = None) -> Tuple[bool, str]:
    """Test importing a package and return success status and message."""
    if import_statement is None:
        import_statement = f"import {package_name}"
    
    try:
        exec(import_statement)
        return True, f"✅ {package_name}: OK"
    except ImportError as e:
        return False, f"❌ {package_name}: ImportError - {e}"
    except Exception as e:
        return False, f"⚠️  {package_name}: Error - {e}"


def main():
    """Test importing key dependencies."""
    print("🧪 Testing dependency imports...")
    
    # Core dependencies to test
    test_packages = [
        ("fastapi", "import fastapi"),
        ("uvicorn", "import uvicorn"),
        ("pydantic", "import pydantic"),
        ("flask", "import flask"),
        ("httpx", "import httpx"),
        ("click", "import click"),
        ("bcrypt", "import bcrypt"),
        ("cryptography", "import cryptography"),
        ("pytest", "import pytest"),
        ("requests", "import requests"),
        ("numpy", "import numpy"),
        ("jinja2", "import jinja2"),
        ("psutil", "import psutil"),
        ("tqdm", "import tqdm"),
        ("safety", "import safety"),
        ("bandit", "import bandit"),
        ("ruff", "import ruff"),
    ]
    
    # Optional dependencies (may not be installed)
    optional_packages = [
        ("torch", "import torch"),
        ("transformers", "import transformers"),
        ("matplotlib", "import matplotlib"),
        ("pandas", "import pandas"),
        ("plotly", "import plotly"),
        ("sqlalchemy", "import sqlalchemy"),
        ("redis", "import redis"),
        ("celery", "import celery"),
    ]
    
    # Test core dependencies
    print("\n📦 Testing core dependencies:")
    failed_core = []
    for package_name, import_stmt in test_packages:
        success, message = test_import(package_name, import_stmt)
        print(f"  {message}")
        if not success:
            failed_core.append(package_name)
    
    # Test optional dependencies
    print("\n📦 Testing optional dependencies:")
    failed_optional = []
    for package_name, import_stmt in optional_packages:
        success, message = test_import(package_name, import_stmt)
        print(f"  {message}")
        if not success:
            failed_optional.append(package_name)
    
    # Test version compatibility for key packages
    print("\n🔍 Testing version compatibility:")
    try:
        import pydantic
        print(f"  ✅ pydantic version: {pydantic.__version__}")
        
        import fastapi
        print(f"  ✅ fastapi version: {fastapi.__version__}")
        
        import click
        print(f"  ✅ click version: {click.__version__}")
        
        import pytest
        print(f"  ✅ pytest version: {pytest.__version__}")
        
    except Exception as e:
        print(f"  ⚠️  Version check failed: {e}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  - Core dependencies tested: {len(test_packages)}")
    print(f"  - Core dependencies failed: {len(failed_core)}")
    print(f"  - Optional dependencies tested: {len(optional_packages)}")
    print(f"  - Optional dependencies failed: {len(failed_optional)}")
    
    if failed_core:
        print(f"\n❌ Failed core dependencies: {', '.join(failed_core)}")
        print("These dependencies are required and must be installed.")
        sys.exit(1)
    else:
        print("\n✅ All core dependencies imported successfully!")
    
    if failed_optional:
        print(f"\n⚠️  Failed optional dependencies: {', '.join(failed_optional)}")
        print("These are optional and can be installed as needed.")
    
    print("\n✅ Dependency import test completed!")


if __name__ == "__main__":
    main()
