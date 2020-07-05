from typing import Any, AsyncIterable, Dict, Iterable, TypeVar, Union

T = TypeVar("T")
ItemsTypes = Union[Iterable[T], AsyncIterable[T]]
Scope = Dict[str, Any]
