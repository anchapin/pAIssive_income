"""
Type stubs for importlib
"""
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union
import sys
import types

# Define util module
class _util:
    def find_spec(name: str, package: Optional[str] = None) -> Any: ...
    def module_from_spec(spec: Any) -> types.ModuleType: ...
    def spec_from_file_location(name: str, location: str) -> Any: ...

util = _util()

def import_module(name: str, package: Optional[str] = None) -> types.ModuleType: ...

def invalidate_caches() -> None: ...

def reload(module: types.ModuleType) -> types.ModuleType: ...

def __import__(
    name: str,
    globals: Optional[Dict[str, Any]] = None,
    locals: Optional[Dict[str, Any]] = None,
    fromlist: Tuple[str, ...] = (),
    level: int = 0,
) -> types.ModuleType: ...
