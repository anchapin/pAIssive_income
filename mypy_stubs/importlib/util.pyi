"""Type stubs for importlib.util."""
import types
from typing import Any, Callable, Optional, Union

class _Finder:
    """Abstract base class for import finders."""
    def find_module(self, fullname: str, path: Optional[list[str]] = None) -> Optional[types.ModuleType]: ...

class _Loader:
    """Abstract base class for import loaders."""
    def load_module(self, fullname: str) -> types.ModuleType: ...

class _ModuleSpec:
    """Module specification."""
    name: str
    loader: Optional[_Loader]
    origin: Optional[str]
    submodule_search_locations: Optional[list[str]]
    loader_state: Any
    cached: Optional[str]
    parent: Optional[str]
    has_location: bool

    def __init__(
        self,
        name: str,
        loader: Optional[_Loader],
        *,
        origin: Optional[str] = None,
        loader_state: Any = None,
        is_package: Optional[bool] = None,
    ) -> None: ...

def spec_from_loader(
    name: str,
    loader: Optional[_Loader],
    *,
    origin: Optional[str] = None,
    loader_state: Any = None,
    is_package: Optional[bool] = None,
) -> _ModuleSpec: ...

def spec_from_file_location(
    name: str,
    location: Union[str, bytes, int, types.ModuleType],
    *,
    loader: Optional[_Loader] = None,
    submodule_search_locations: Optional[list[str]] = None,
) -> Optional[_ModuleSpec]: ...

def module_from_spec(spec: _ModuleSpec) -> types.ModuleType: ...

def find_spec(
    name: str,
    package: Optional[str] = None,
    path: Optional[list[str]] = None,
    target: Optional[types.ModuleType] = None,
) -> Optional[_ModuleSpec]: ...

def resolve_name(name: str, package: Optional[str]) -> str: ...

def cache_from_source(path: str, debug_override: Optional[bool] = None, *, optimization: Optional[Any] = None) -> str: ...

def source_from_cache(path: str) -> str: ...

def decode_source(source_bytes: bytes) -> str: ...

def source_hash(source_bytes: bytes) -> str: ...

def set_package(fxn: Callable[..., Any]) -> Callable[..., Any]: ...

def set_loader(fxn: Callable[..., Any]) -> Callable[..., Any]: ...

def module_for_loader(fxn: Callable[..., Any]) -> Callable[..., Any]: ...

def find_loader(name: str, path: Optional[list[str]] = None) -> tuple[Optional[_Loader], list[str]]: ...

def LazyLoader(loader: _Loader) -> _Loader: ...
