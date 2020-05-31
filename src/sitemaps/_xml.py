from typing import Callable, Iterator, Sequence

import anyio

URLTagFunc = Callable[[str], str]


def default_urltag(url: str) -> str:
    return f"<url><loc>{url}</loc><changefreq>daily</changefreq></url>"


def make_xml(urls: Sequence[str], urltag: URLTagFunc = default_urltag) -> str:
    def lines() -> Iterator[str]:
        yield '<?xml version="1.0" encoding="utf-8"?>'
        yield (
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 '
            'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">'
        )
        for url in urls:
            yield 4 * " " + urltag(url)
        yield "</urlset>"

    content = "\n".join(lines())
    return f"{content}\n"


async def compare(urls: Sequence[str], output: str) -> bool:
    async with await anyio.aopen(output) as f:
        content = await f.read()
        return content == make_xml(urls)


async def write(urls: Sequence[str], output: str) -> None:
    async with await anyio.aopen(output, mode="w") as f:
        await f.write(make_xml(urls))
