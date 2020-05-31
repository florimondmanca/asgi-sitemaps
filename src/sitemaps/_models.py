from typing import NamedTuple, Sequence, Set

import anyio
import httpx


class Config(NamedTuple):
    root_url: str
    ignore: Sequence[str]
    client: httpx.AsyncClient
    limit: anyio.CapacityLimiter
    tg: anyio.TaskGroup


class State(NamedTuple):
    discovered_urls: Set[str]
    results: Set[str]
