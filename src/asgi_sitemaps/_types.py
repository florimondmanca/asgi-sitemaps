from typing import Any, AsyncIterable, Awaitable, Dict, Iterable, TypeVar, Union

T = TypeVar("T")
ItemsTypes = Union[Iterable[T], Awaitable[Iterable[T]], AsyncIterable[T]]
Scope = Dict[str, Any]
