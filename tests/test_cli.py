from pathlib import Path
from textwrap import dedent

import pytest

import sitemaps

from .utils import Server

EXPECTED_SITEMAP = dedent(
    """
<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
    <url><loc>https://mysite.io/</loc><changefreq>daily</changefreq></url>
    <url><loc>https://mysite.io/child</loc><changefreq>daily</changefreq></url>
</urlset>
"""  # noqa
).strip()


@pytest.mark.asyncio
async def test_website(tmp_path: Path, server: Server) -> None:
    output = tmp_path / "sitemap.xml"
    target = str(server.url)
    args = ["--base-url", "https://mysite.io", "-o", str(output), target]

    code = await sitemaps.main(args)
    assert code == 0
    assert output.read_text().strip() == EXPECTED_SITEMAP


@pytest.mark.asyncio
async def test_check(tmp_path: Path, server: Server) -> None:
    output = tmp_path / "sitemap.xml"
    target = str(server.url)
    args = ["--base-url", "https://mysite.io", "-o", str(output), target]

    code = await sitemaps.main(args + ["--check"])
    assert code == 1

    code = await sitemaps.main(args)
    assert code == 0

    code = await sitemaps.main(args + ["--check"])
    assert code == 0

    output.write_text(EXPECTED_SITEMAP + "some difference")
    code = await sitemaps.main(args + ["--check"])
    assert code == 1


@pytest.mark.asyncio
async def test_asgi(tmp_path: Path) -> None:
    output = tmp_path / "sitemap.xml"
    target = "tests.app:app"
    args = [
        "--asgi",
        "--base-url",
        "https://mysite.io",
        "-o",
        str(output),
        target,
    ]

    code = await sitemaps.main(args)
    assert code == 0
    assert output.read_text().strip() == EXPECTED_SITEMAP


@pytest.mark.asyncio
async def test_asgi_base_url_required(tmp_path: Path) -> None:
    output = tmp_path / "sitemap.xml"
    target = "tests.app:app"
    args = [
        "--asgi",
        "-o",
        str(output),
        target,
    ]
    code = await sitemaps.main(args)
    assert code == 1
