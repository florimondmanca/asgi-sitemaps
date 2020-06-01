import re
from typing import Callable, NamedTuple, Sequence, Set, Tuple
from urllib.parse import urldefrag, urljoin

import anyio
import httpx
from asgi_lifespan import LifespanManager


class Config(NamedTuple):
    base_url: str
    ignore: Tuple[str, ...]
    client: httpx.AsyncClient
    limit: anyio.CapacityLimiter
    tg: anyio.TaskGroup


class State(NamedTuple):
    discovered_urls: Set[str]
    results: Set[str]


async def crawl(
    app: Callable,
    base_url: str = "http://testserver/",
    ignore: Sequence[str] = (),
    max_concurrency: int = 10,
) -> Sequence[str]:
    base_url = _normalize(base_url)

    lifespan = LifespanManager(app)
    client = httpx.AsyncClient(app=app)

    async with lifespan, client, anyio.create_task_group() as tg:
        config = Config(
            base_url=base_url,
            ignore=tuple(urljoin(base_url, path) for path in ignore),
            client=client,
            limit=anyio.create_capacity_limiter(max_concurrency),
            tg=tg,
        )
        state = State(discovered_urls=set(), results=set())
        assert _should_crawl(base_url, config, state)
        await tg.spawn(_process, base_url, config, state)

    return sorted(state.results)


def _normalize(url: str) -> str:
    url, _ = urldefrag(url)
    if not url.endswith("/"):
        url = f"{url}/"
    return url


def _should_crawl(url: str, config: Config, state: State) -> bool:
    return (
        url.startswith(config.base_url)
        and not url.startswith(config.ignore)
        and url not in state.discovered_urls
    )


async def _process(url: str, config: Config, state: State) -> None:
    async with config.limit:
        response = await config.client.get(url)

        if response.status_code != 200:
            return

        if "text/html" not in response.headers.get("content-type", ""):
            return

        hrefs = re.findall(r'(?i)href=["\']?([^\s"\'<>]+)', response.text)
        child_urls = [_normalize(urljoin(url, href)) for href in hrefs]
        child_urls = [url for url in child_urls if _should_crawl(url, config, state)]

        for child_url in child_urls:
            state.discovered_urls.add(child_url)
            await config.tg.spawn(_process, child_url, config, state)

        state.results.add(url)
