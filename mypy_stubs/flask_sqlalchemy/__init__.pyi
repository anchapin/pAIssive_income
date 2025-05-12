from typing import (Any, Callable, Dict, Generic, List, Optional, Type, TypeVar, Union,
                    overload)

T = TypeVar('T')
_T = TypeVar('_T')

# Define Model class
class ModelBase:
    query_property: Any
    __tablename__: str

    @classmethod
    def query(cls) -> Any: ...

    def save(self) -> None: ...
    def delete(self) -> None: ...

# Define SQLAlchemy class
class SQLAlchemy:
    Model: Type[ModelBase]
    Column: Any
    String: Any
    Integer: Any
    Float: Any
    Boolean: Any
    Text: Any
    DateTime: Any
    ForeignKey: Any
    relationship: Any
    backref: Any
    session: Any
    func: Any

    def __init__(self, app: Optional[Any] = None, **kwargs: Any) -> None: ...
    def init_app(self, app: Any) -> None: ...
    def create_all(self) -> None: ...
    def drop_all(self) -> None: ...
    def get_engine(self) -> Any: ...
