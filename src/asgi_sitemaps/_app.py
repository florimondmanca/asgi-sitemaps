from typing import Callable, Sequence, Union

from ._generation import generate_sitemap
from ._models import Sitemap
from ._types import Scope


class SitemapApp:
    def __init__(
        self, sitemaps: Union[Sitemap, Sequence[Sitemap]], *, domain: str
    ) -> None:
        self._sitemaps = [sitemaps] if isinstance(sitemaps, Sitemap) else sitemaps
        self._domain = domain

    async def __call__(self, scope: Scope, receive: Callable, send: Callable) -> None:
        assert scope["type"] == "http"

        content = await generate_sitemap(
            self._sitemaps, scope=scope, domain=self._domain
        )

        headers = [
            [b"content-type", b"application/xml"],
            [b"content-length", b"%d" % len(content)],
        ]

        message = await receive()
        assert message["type"] == "http.request"
        await send({"type": "http.response.start", "status": 200, "headers": headers})
        await send({"type": "http.response.body", "body": content})
