import io
from textwrap import dedent

import pytest

import asgi_sitemaps

EXPECTED_SITEMAP = dedent(
    """
<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
    <url><loc>{0}/</loc><changefreq>daily</changefreq></url>
    <url><loc>{0}/child/</loc><changefreq>daily</changefreq></url>
</urlset>
"""  # noqa
).strip()


@pytest.mark.asyncio
async def test_main() -> None:
    args = ["tests.app:app"]
    stdout = io.StringIO()
    code = await asgi_sitemaps.main(args, stdout=stdout)
    assert code == 0
    stdout.seek(0)
    assert stdout.read().strip() == EXPECTED_SITEMAP.format("http://testserver")


@pytest.mark.asyncio
async def test_base_url() -> None:
    args = ["tests.app:app", "--base-url", "https://mysite.io"]
    stdout = io.StringIO()
    code = await asgi_sitemaps.main(args, stdout=stdout)
    assert code == 0
    stdout.seek(0)
    assert stdout.read().strip() == EXPECTED_SITEMAP.format("https://mysite.io")


@pytest.mark.asyncio
async def test_check() -> None:
    args = ["--check", "tests.app:app"]
    stdin = io.StringIO(EXPECTED_SITEMAP.format("http://testserver"))

    code = await asgi_sitemaps.main(args, stdin=stdin)
    assert code == 0

    stdin.seek(0)
    stdin.write("different")
    code = await asgi_sitemaps.main(args, stdin=stdin)
    assert code == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("app", ["doesnotexist:app", "wrongformat"])
async def test_invalid_path(app: str) -> None:
    args = [app]
    code = await asgi_sitemaps.main(args)
    assert code == 1
