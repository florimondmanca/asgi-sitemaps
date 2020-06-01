import pytest

import asgi_sitemaps

from .app import app


EXPECTED_URLS = """
{0}/
{0}/child/
""".strip()


@pytest.mark.asyncio
async def test_crawl() -> None:
    urls = await asgi_sitemaps.crawl(app)
    assert urls == EXPECTED_URLS.format("http://testserver").splitlines()
