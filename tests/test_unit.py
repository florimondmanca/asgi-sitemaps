import pytest

import asgi_sitemaps
from asgi_sitemaps._generation import get_fields


def test_invalid_absolute_location() -> None:
    """
    Location cannot be a full URL with scheme or domain.
    """

    class Sitemap(asgi_sitemaps.Sitemap[str]):
        def location(self, path: str) -> str:
            return "https://example.org{path}"

    sitemap = Sitemap()
    with pytest.raises(ValueError):
        get_fields(sitemap, "/", scope={"scheme": "http"}, domain="example.io")
