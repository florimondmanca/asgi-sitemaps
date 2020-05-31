import re
from functools import partial
from typing import Sequence
from urllib.parse import urljoin, urldefrag

import anyio
import httpx

from ._models import Config, State


async def crawl(
    root_url: str,
    ignore: Sequence[str] = (),
    client: httpx.AsyncClient = None,
    max_tasks: int = 100,
) -> Sequence[str]:
    client = httpx.AsyncClient() if client is None else client

    root_url = urljoin(root_url, "/")

    async with client, anyio.create_task_group() as tg:
        config = Config(
            root_url=root_url,
            ignore=[urljoin(root_url, path) for path in ignore],
            client=client,
            limit=anyio.create_capacity_limiter(max_tasks),
            tg=tg,
        )
        state = State(discovered_urls=set(), results=set())
        await _add(root_url, parent_url="", config=config, state=state)

    return sorted(state.results)


async def _add(url: str, parent_url: str, config: Config, state: State) -> None:
    url = urljoin(parent_url, url)
    url, _ = urldefrag(url)
    if not url.endswith("/"):
        url = f"{url}/"

    if (
        not url.startswith(config.root_url)
        or any(url.startswith(prefix) for prefix in config.ignore)
        or url in state.discovered_urls
    ):
        return

    state.discovered_urls.add(url)
    await config.tg.spawn(partial(_process, url, config=config, state=state))


async def _process(url: str, config: Config, state: State) -> None:
    async with config.limit:
        response = await config.client.get(url)

        if "text/html" in response.headers.get("content-type", ""):
            hrefs = re.findall(r'(?i)href=["\']?([^\s"\'<>]+)', response.text)
            for href in hrefs:
                await config.tg.spawn(
                    partial(_add, href, url, config=config, state=state)
                )

        state.results.add(url)
