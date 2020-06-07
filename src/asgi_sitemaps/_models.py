from typing import Generic, Iterable

from ._types import T


class Sitemap(Generic[T]):
    protocol = "http"

    async def items(self) -> Iterable[T]:
        raise NotImplementedError  # pragma: no cover

    def location(self, item: T) -> str:
        raise NotImplementedError  # pragma: no cover

    def lastmod(self, item: T) -> str:
        return ""

    def changefreq(self, item: T) -> str:
        return ""

    def priority(self, item: T) -> str:
        return ""
