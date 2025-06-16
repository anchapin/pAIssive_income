# Type Checking

This document provides information about the type checking system used in the pAIssive Income project.

## Migration from MyPy to Pyright

As of December 2024, the project has migrated from using MyPy to Pyright for type checking. This change was made to improve type checking performance and capabilities.

### Why Pyright?

[Pyright](https://github.com/microsoft/pyright) is a fast, feature-rich Python type checker that offers several advantages over MyPy:

- Significantly faster performance
- Better error messages and diagnostics
- More accurate type inference
- Excellent compatibility with modern Python features
- Rich IDE integration (especially with VS Code)
- Simpler configuration

### Removed Configuration Files

As part of the migration, the following MyPy configuration files have been removed:

### Using Pyright

To run type checking with Pyright:

```bash
# Install Pyright (if not already installed)
uv add --dev pyright

# Run type checking
pyright .
```

### Configuration

Pyright configuration is defined in `pyproject.toml`:

```toml
[tool.pyright]
pythonVersion = "3.10"
exclude = ["ui/react_frontend", "scripts/__init__.py", ".github/scripts/__init__.py"]
reportMissingImports = false
reportMissingTypeStubs = false
typeCheckingMode = "basic"
```

### CI/CD Integration

The CI/CD pipeline has been updated to use Pyright instead of MyPy. This includes:

- Updated GitHub Actions workflows
- Updated pre-commit hooks
- Updated development scripts

### Pre-commit Hook

The pre-commit hook for type checking has been updated to use Pyrefly. If you're using pre-commit, make sure to update your hooks:

```bash
pre-commit autoupdate
```

## Type Checking Best Practices

- Add type annotations to all function parameters and return values
- Use type hints from the `typing` module for complex types
- Use `Optional` for parameters that can be `None`
- Use `Union` for parameters that can be multiple types
- Use `TypeVar` for generic functions
- Use `Protocol` for duck typing

## Common Type Annotations

```python
from typing import Dict, List, Optional, Set, Tuple, Union

# Basic types
def func1(param: str) -> int:
    return len(param)

# Complex types
def func2(param: List[Dict[str, int]]) -> Dict[str, List[int]]:
    result = {}
    for item in param:
        for key, value in item.items():
            if key not in result:
                result[key] = []
            result[key].append(value)
    return result

# Optional parameters
def func3(param: Optional[str] = None) -> str:
    return param or "default"

# Union types
def func4(param: Union[str, int]) -> str:
    return str(param)
```

## Troubleshooting

If you encounter issues with Pyrefly:

1. Make sure you have the latest version installed
2. Check for configuration issues in `pyproject.toml`
3. Try running with verbose output: `pyrefly --verbose .`
4. Check the [Pyrefly documentation](https://github.com/pyrefly-io/pyrefly) for more information
