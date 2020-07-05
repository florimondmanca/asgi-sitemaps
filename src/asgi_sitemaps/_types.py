from typing import AsyncIterable, Dict, Iterable, TypeVar, Union

T = TypeVar("T")
ItemsTypes = Union[Iterable[T], AsyncIterable[T]]
Scope = Dict[str, str]
