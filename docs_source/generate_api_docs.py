#!/usr/bin/env python3
"""
Script to automatically generate API documentation for the pAIssive_income project.
This script:
1. Scans the project structure to identify modules and submodules
2. Creates or updates .rst files for modules
3. Updates index files with the latest module structure
"""

import os
import sys
import importlib
import inspect
import pkgutil
from typing import List, Dict, Set, Tuple, Optional


def create_directory(path: str) -> None:
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")


def write_file(path: str, content: str) -> None:
    """Write content to a file."""
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created/updated: {path}")


def get_module_docstring(module_name: str) -> str:
    """Get the docstring for a module."""
    try:
        module = importlib.import_module(module_name)
        if module.__doc__:
            return module.__doc__.strip()
    except (ImportError, AttributeError):
        pass
    return f"{module_name} module"


def get_module_members(module_name: str) -> Dict[str, List[str]]:
    """Get classes, functions, and other members from a module."""
    members = {
        'classes': [],
        'functions': [],
        'modules': []
    }
    
    try:
        module = importlib.import_module(module_name)
        
        for name, obj in inspect.getmembers(module):
            # Skip private/special members
            if name.startswith('_'):
                continue
            
            # Identify classes
            if inspect.isclass(obj):
                if obj.__module__ == module_name:
                    members['classes'].append(name)
            
            # Identify functions
            elif inspect.isfunction(obj):
                if obj.__module__ == module_name:
                    members['functions'].append(name)
            
            # Identify submodules
            elif inspect.ismodule(obj):
                members['modules'].append(name)
        
    except ImportError:
        pass
    
    return members


def is_package(module_name: str) -> bool:
    """Check if a module is a package (i.e., has __init__.py)."""
    try:
        module = importlib.import_module(module_name)
        return hasattr(module, '__path__')
    except ImportError:
        return False


def get_submodules(package_name: str) -> List[str]:
    """Get submodules of a package."""
    submodules = []
    try:
        package = importlib.import_module(package_name)
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package_name + '.'):
            submodules.append(name)
            if is_pkg:
                submodules.extend(get_submodules(name))
    except ImportError:
        pass
    return submodules


def generate_module_rst(module_name: str, output_dir: str) -> None:
    """Generate .rst file for a module."""
    output_file = os.path.join(output_dir, f"{module_name.split('.')[-1]}.rst")
    
    # Get module information
    docstring = get_module_docstring(module_name)
    members = get_module_members(module_name)
    
    # Create RST content
    lines = [
        f"{module_name.split('.')[-1]}",
        "=" * len(module_name.split('.')[-1]),
        "",
        f"{docstring}",
        "",
        ".. automodule:: " + module_name,
        "   :members:",
        "   :undoc-members:",
        "   :show-inheritance:",
        ""
    ]
    
    # Add sections for classes, functions, etc. if present
    if members['classes']:
        lines.extend([
            "Classes",
            "-------",
            ""
        ])
        for cls in sorted(members['classes']):
            lines.extend([
                f".. autoclass:: {module_name}.{cls}",
                "   :members:",
                "   :undoc-members:",
                "   :show-inheritance:",
                ""
            ])
    
    if members['functions']:
        lines.extend([
            "Functions",
            "---------",
            ""
        ])
        for func in sorted(members['functions']):
            lines.extend([
                f".. autofunction:: {module_name}.{func}",
                ""
            ])
    
    write_file(output_file, "\n".join(lines))


def generate_package_index(package_name: str, output_dir: str, submodules: List[str]) -> None:
    """Generate index.rst file for a package."""
    # Create output directory if it doesn't exist
    create_directory(output_dir)
    
    # Get module information
    docstring = get_module_docstring(package_name)
    
    # Create RST content
    title = package_name.split('.')[-1].replace('_', ' ').title()
    lines = [
        f".. _{package_name.replace('.', '_')}:",
        "",
        title,
        "=" * len(title),
        "",
        f"{docstring}",
        "",
        ".. toctree::",
        "   :maxdepth: 2",
        "",
    ]
    
    # Add submodules to toctree
    for submodule in sorted(submodules):
        module_name = submodule.split('.')[-1]
        if module_name != "__init__":
            lines.append(f"   {module_name}")
    
    lines.extend([
        "",
        "Module Overview",
        "--------------",
        "",
        f".. automodule:: {package_name}",
        "   :members:",
        "   :undoc-members:",
        "   :show-inheritance:",
        ""
    ])
    
    # Write the index file
    index_file = os.path.join(output_dir, "index.rst")
    write_file(index_file, "\n".join(lines))


def process_module(module_name: str, base_output_dir: str, processed_modules: Set[str]) -> None:
    """Process a module or package to generate documentation."""
    if module_name in processed_modules:
        return
    
    print(f"Processing {module_name}...")
    processed_modules.add(module_name)
    
    # Determine output directory based on module hierarchy
    parts = module_name.split('.')
    relative_path = os.path.join(*parts) if len(parts) > 1 else parts[0]
    output_dir = os.path.join(base_output_dir, 'api', relative_path)
    
    # Create output directory
    create_directory(output_dir)
    
    if is_package(module_name):
        # Get submodules
        direct_submodules = []
        for _, name, is_pkg in pkgutil.iter_modules([os.path.dirname(importlib.import_module(module_name).__file__)], 
                                                  module_name + '.'):
            direct_submodules.append(name)
            # Process each submodule
            process_module(name, base_output_dir, processed_modules)
        
        # Create package index
        generate_package_index(module_name, output_dir, direct_submodules)
    else:
        # Generate .rst file for the module
        generate_module_rst(module_name, os.path.dirname(output_dir))


def main() -> None:
    """Main function to generate API documentation."""
    print("Generating API documentation...")
    
    # Define the base directory for docs
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, 'source')
    
    # Ensure we can import our project modules
    project_dir = os.path.dirname(base_dir)  # Parent of docs directory
    sys.path.insert(0, project_dir)
    
    # Define main modules to document
    main_modules = [
        'ai_models',
        'agent_team',
        'monetization',
        'niche_analysis',
        'marketing',
        'ui',
        'common_utils',
        'interfaces'
    ]
    
    processed_modules = set()
    
    # Process each main module
    for module_name in main_modules:
        process_module(module_name, output_dir, processed_modules)
    
    print("API documentation generation complete!")


if __name__ == "__main__":
    main()