import datetime as dt
from textwrap import dedent
from typing import Any, AsyncIterator, List, Optional

import httpx
import pytest
from starlette.applications import Starlette
from starlette.datastructures import URL
from starlette.requests import Request
from starlette.routing import Route

import asgi_sitemaps


@pytest.mark.asyncio
async def test_sitemap() -> None:
    """
    A basic example returns expected sitemap XML content.
    """

    class Sitemap(asgi_sitemaps.Sitemap[str]):
        def items(self) -> List[str]:
            return ["/", "/about"]

        def location(self, item: str) -> str:
            return item

    app = asgi_sitemaps.SitemapApp(Sitemap(), domain="example.io")

    async with httpx.AsyncClient(app=app) as client:
        r = await client.get("http://testserver")

    content = dedent(
        """
        <?xml version="1.0" encoding="utf-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>http://example.io/</loc>
                <priority>0.5</priority>
            </url>
            <url>
                <loc>http://example.io/about</loc>
                <priority>0.5</priority>
            </url>
        </urlset>
        """
    ).lstrip()

    assert r.status_code == 200
    assert r.text == content
    assert r.headers["content-type"] == "application/xml"
    assert r.headers["content-length"] == str(len(content))


@pytest.mark.asyncio
async def test_sitemap_fields() -> None:
    """
    Custom sitemap fields behave as expected.
    """

    class Sitemap(asgi_sitemaps.Sitemap[int]):
        protocol = "https"

        def items(self) -> List[int]:
            return list(range(3))

        def location(self, k: int) -> str:
            return f"/page{k + 1}"

        def lastmod(self, k: int) -> Optional[dt.datetime]:
            if k % 3 == 0:
                return dt.datetime(2020, 1, 1)
            elif k % 3 == 1:
                return None
            else:
                return dt.datetime(2018, 3, 14)

        def changefreq(self, k: int) -> Optional[str]:
            if k % 3 == 0:
                return "daily"
            elif k % 3 == 1:
                return "monthly"
            else:
                return None

        def priority(self, k: int) -> float:
            return 0.7

    app = asgi_sitemaps.SitemapApp(Sitemap(), domain="example.io")

    async with httpx.AsyncClient(app=app) as client:
        r = await client.get("http://testserver")

    content = dedent(
        """
        <?xml version="1.0" encoding="utf-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.io/page1</loc>
                <lastmod>2020-01-01</lastmod>
                <changefreq>daily</changefreq>
                <priority>0.7</priority>
            </url>
            <url>
                <loc>https://example.io/page2</loc>
                <changefreq>monthly</changefreq>
                <priority>0.7</priority>
            </url>
            <url>
                <loc>https://example.io/page3</loc>
                <lastmod>2018-03-14</lastmod>
                <priority>0.7</priority>
            </url>
        </urlset>
    """
    ).lstrip()

    assert r.status_code == 200
    assert r.text == content
    assert r.headers["content-type"] == "application/xml"
    assert r.headers["content-length"] == str(len(content))


@pytest.mark.asyncio
async def test_sitemap_async_items() -> None:
    """
    `.items()` supports returning async iterables.
    """

    class Sitemap(asgi_sitemaps.Sitemap[str]):
        async def items(self) -> AsyncIterator[str]:
            for item in ["/", "/about"]:
                yield item

        def location(self, item: str) -> str:
            return item

    app = asgi_sitemaps.SitemapApp(Sitemap(), domain="example.io")

    async with httpx.AsyncClient(app=app) as client:
        r = await client.get("http://testserver")

    content = dedent(
        """
        <?xml version="1.0" encoding="utf-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>http://example.io/</loc>
                <priority>0.5</priority>
            </url>
            <url>
                <loc>http://example.io/about</loc>
                <priority>0.5</priority>
            </url>
        </urlset>
    """
    ).lstrip()

    assert r.status_code == 200
    assert r.text == content
    assert r.headers["content-type"] == "application/xml"
    assert r.headers["content-length"] == str(len(content))


@pytest.mark.asyncio
async def test_sitemap_scope() -> None:
    """
    Sitemaps can use `self.scope` to access the ASGI scope.
    """

    class Sitemap(asgi_sitemaps.Sitemap[str]):
        def items(self) -> List[str]:
            return ["home"]

        def location(self, name: str) -> str:
            request = Request(self.scope)
            return URL(request.url_for(name)).path

    sitemap = asgi_sitemaps.SitemapApp(Sitemap(), domain="example.io")

    async def home() -> Any:
        ...  # pragma: no cover

    routes = [Route("/", home, name="home"), Route("/sitemap.xml", sitemap)]
    app = Starlette(routes=routes)

    async with httpx.AsyncClient(app=app) as client:
        r = await client.get("http://testserver/sitemap.xml")

    content = dedent(
        """
        <?xml version="1.0" encoding="utf-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>http://example.io/</loc>
                <priority>0.5</priority>
            </url>
        </urlset>
    """
    ).lstrip()

    assert r.text == content
