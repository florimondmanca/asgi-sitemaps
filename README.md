# sitemaps

[![Build Status](https://dev.azure.com/florimondmanca/public/_apis/build/status/florimondmanca.wsx?branchName=master)](https://dev.azure.com/florimondmanca/public/_build/latest?definitionId=10&branchName=master)
[![Coverage](https://codecov.io/gh/florimondmanca/wsx/branch/master/graph/badge.svg)](https://codecov.io/gh/florimondmanca/wsx)
![Python versions](https://img.shields.io/pypi/pyversions/wsx.svg)
[![Package version](https://badge.fury.io/py/wsx.svg)](https://pypi.org/project/wsx)

Asynchronous sitemap generation with support for crawling Python ASGI web apps directly. Powered by [HTTPX](https://github.com/encode/httpx) and [anyio](https://github.com/agronholm/anyio).

## Quickstart

Generate a sitemap for a live website:

```bash
python -m sitemaps 'https://example.org'
```

Generate a sitemap for an ASGI app:

```bash
python -m sitemaps --asgi --base-url 'https://mysite.io' '<MODULE>:<ATTRIBUTE>'
```

Run in check mode to verify the sitemap is in sync (e.g. as part of CI checks):

```bash
python -m sitemaps --check [...]
```

## Installation

Install with pip:

```shell
$ pip install sitemaps
```

Sitemaps requires Python 3.7+.

## Features

- Support for crawling any live website.
- Support for crawling ASGI web applications directly (i.e. without having to spin up a server).
- Command line or programmatic async API usage, with support for asyncio, trio or curio.
- Fully type annotated.
- 100% test coverage.

## Command line usage

```console
$ python -m sitemaps --help
usage: __main__.py [-h] [-o OUTPUT] [--base-url BASE_URL]
                   [-I IGNORE_PATH_PREFIX] [--max-concurrency MAX_CONCURRENCY]
                   [--asgi] [--check]
                   target

positional arguments:
  target

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file path.
  --base-url BASE_URL   Base URL to use when outputting URLs in the sitemap,
                        eg https://mysite.com.
  -I IGNORE_PATH_PREFIX, --ignore-path-prefix IGNORE_PATH_PREFIX
                        Ignore URLs for this path prefix. Can be used multiple
                        times.
  --max-concurrency MAX_CONCURRENCY
                        Maximum number of concurrent tasks.
  --asgi                Treat 'target' as a path to an ASGI app, formatted as
                        '<module>:<attribute>'.
  --check               Compare existing output and fail if computed XML
                        results.
```

## Programmatic usage

```python
import sitemaps

async def main():
    urls = await sitemaps.crawl("https://example.org")
    await sitemaps.write(urls, "sitemap.xml")
```

## License

MIT
