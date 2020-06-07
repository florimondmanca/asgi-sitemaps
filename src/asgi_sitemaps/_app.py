from typing import Any, AsyncIterator, Callable, Mapping, Tuple
from urllib.parse import urljoin

from ._models import Sitemap


class SitemapApp:
    def __init__(self, sitemaps: Mapping[str, Sitemap[Any]], *, domain: str) -> None:
        self._sitemaps = sitemaps
        self._domain = domain

    async def _lines(self) -> AsyncIterator[bytes]:
        yield b'<?xml version="1.0" encoding="utf-8"?>'
        yield b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'

        for sitemap in self._sitemaps.values():
            items = await sitemap.items()

            for item in items:
                protocol = sitemap.protocol

                location = sitemap.location(item)

                url = urljoin(f"{protocol}://{self._domain}", location).encode("utf-8")

                spaces = 2 * b" "
                yield spaces + b"<url>"

                spaces = 4 * b" "
                yield spaces + b"<loc>%s</loc>" % url

                lastmod = sitemap.lastmod(item).encode("utf-8")
                if lastmod:
                    yield spaces + b"<lastmod>%s</lastmod>" % lastmod

                changefreq = sitemap.changefreq(item).encode("utf-8")
                if changefreq:
                    yield spaces + b"<changefreq>%s</changefreq>" % changefreq

                priority = sitemap.priority(item).encode("utf-8")
                if priority:
                    yield spaces + b"<priority>%s</priority>" % priority

                spaces = 2 * b" "
                yield spaces + b"</url>"

        yield b"</urlset>"

    async def _response_chunks(self) -> AsyncIterator[Tuple[bytes, bool]]:
        async for line in self._lines():
            yield b"%s\n" % line, True
        yield b"", False

    async def __call__(self, scope: Mapping, receive: Callable, send: Callable) -> None:
        assert scope["type"] == "http"
        message = await receive()
        assert message["type"] == "http.request"
        await send({"type": "http.response.start", "status": 200, "headers": []})
        async for chunk, more_body in self._response_chunks():
            await send(
                {"type": "http.response.body", "body": chunk, "more_body": more_body}
            )
