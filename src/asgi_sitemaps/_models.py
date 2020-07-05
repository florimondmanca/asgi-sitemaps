import contextvars
import datetime as dt
from typing import Generic, Optional

from ._types import ItemsTypes, Scope, T

SCOPE_CTX_VAR = contextvars.ContextVar[Scope]("asgi_sitemaps.scope")


class Sitemap(Generic[T]):
    protocol = "auto"

    def __init__(self) -> None:
        assert self.protocol in ("http", "https", "auto")

    def items(self) -> ItemsTypes:
        raise NotImplementedError  # pragma: no cover

    def location(self, item: T) -> str:
        raise NotImplementedError  # pragma: no cover

    def lastmod(self, item: T) -> Optional[dt.datetime]:
        return None

    def changefreq(self, item: T) -> Optional[str]:
        return None

    def priority(self, item: T) -> float:
        return 0.5

    @property
    def scope(self) -> Scope:
        try:
            return SCOPE_CTX_VAR.get()
        except LookupError:  # pragma: no cover
            raise RuntimeError("scope accessed outside of an ASGI request")
