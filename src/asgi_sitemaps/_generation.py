import inspect
from typing import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Dict,
    Iterable,
    Sequence,
    cast,
)
from urllib.parse import urljoin, urlsplit

from ._models import SCOPE_CTX_VAR, Sitemap
from ._types import ItemsTypes, Scope, T


async def generate_sitemap(
    sitemaps: Sequence[Sitemap], *, scope: Scope, domain: str
) -> bytes:
    SCOPE_CTX_VAR.set(scope)

    async def _lines() -> AsyncIterator[bytes]:
        yield b'<?xml version="1.0" encoding="utf-8"?>'
        yield b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'

        for sitemap in sitemaps:
            async for item in _ensure_async_iterator(sitemap.items()):
                yield 4 * b" " + b"<url>"

                fields = get_fields(sitemap, item, scope=scope, domain=domain)
                for name, value in fields.items():
                    yield 8 * b" " + f"<{name}>{value}</{name}>".encode("utf-8")

                yield 4 * b" " + b"</url>"

        yield b"</urlset>"
        yield b""

    return b"\n".join([line async for line in _lines()])


async def _ensure_async_iterator(items: ItemsTypes[T]) -> AsyncIterator[T]:
    if hasattr(items, "__aiter__"):
        items = cast(AsyncIterable[T], items)
        async for item in items:
            yield item
    elif inspect.isawaitable(items):
        items = cast(Awaitable[Iterable[T]], items)
        for item in await items:
            yield item
    else:
        items = cast(Iterable[T], items)
        for item in items:
            yield item


def get_fields(
    sitemap: Sitemap[T], item: T, *, scope: Scope, domain: str
) -> Dict[str, str]:
    if sitemap.protocol == "auto":
        protocol = scope["scheme"]
    else:
        protocol = sitemap.protocol

    location = sitemap.location(item)
    lastmod = sitemap.lastmod(item)
    changefreq = sitemap.changefreq(item)
    priority = sitemap.priority(item)

    r = urlsplit(location)
    if r.scheme or r.netloc:
        raise ValueError(f"Location contains scheme or domain: {location}")

    fields = {}
    fields["loc"] = urljoin(f"{protocol}://{domain}", location)
    if lastmod is not None:
        fields["lastmod"] = lastmod.strftime("%Y-%m-%d")
    if changefreq is not None:
        fields["changefreq"] = changefreq
    fields["priority"] = str(priority)

    return fields
