"""Type stubs for importlib."""
import types
from typing import Any, Optional

# Define util module
class _util:
    def find_spec(self: str, package: Optional[str] = None) -> Any: ...
    def module_from_spec(self: Any) -> types.ModuleType: ...
    def spec_from_file_location(self: str, location: str) -> Any: ...

util = _util()

def import_module(name: str, package: Optional[str] = None) -> types.ModuleType: ...

def invalidate_caches() -> None: ...

def reload(module: types.ModuleType) -> types.ModuleType: ...

def __import__(
    name: str,
    globals: Optional[dict[str, Any]] = None,
    locals: Optional[dict[str, Any]] = None,
    fromlist: tuple[str, ...] = (),
    level: int = 0,
) -> types.ModuleType: ...
