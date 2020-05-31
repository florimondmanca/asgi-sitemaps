# sitemaps

[![Build Status](https://dev.azure.com/florimondmanca/public/_apis/build/status/florimondmanca.sitemaps?branchName=master)](https://dev.azure.com/florimondmanca/public/_build/latest?definitionId=11&branchName=master)
[![Coverage](https://codecov.io/gh/florimondmanca/sitemaps/branch/master/graph/badge.svg)](https://codecov.io/gh/florimondmanca/sitemaps)
![Python versions](https://img.shields.io/pypi/pyversions/sitemaps.svg)
[![Package version](https://badge.fury.io/py/wsx.svg)](https://pypi.org/project/sitemaps)

Sitemaps is a Python command line tool and library to automatically generate `sitemap.xml` files from a web server or ASGI application. Powered by [HTTPX](https://github.com/encode/httpx) and [anyio](https://github.com/agronholm/anyio).

_**Note**: This is alpha software. Be sure to pin your dependencies to the latest minor release._

## Quickstart

### Live server

```bash
python -m sitemaps https://example.org
```

Example output:

```console
$ cat sitemap.xml
<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
    <url><loc>https://example.org/</loc><changefreq>daily</changefreq></url>
</urlset>
```

### ASGI app

HTTP requests are issued to the ASGI app directly. The target URL is only used as a base URL for building sitemap entries.

```bash
python -m sitemaps --asgi '<module>:<attribute>' http://testserver
```

### Check mode

Useful to verify that the sitemap is in sync (e.g. as part of CI checks):

```bash
python -m sitemaps --check [...]
```

## Features

- Support for crawling a live web server.
- Support for crawling an ASGI app directly (i.e. without having to spin up a server).
- `--check` mode.
- Invoke from the command line, or use the programmatic async API (supports asyncio and trio).
- Fully type annotated.
- 100% test coverage.

## Installation

Install with pip:

```shell
$ pip install sitemaps
```

Sitemaps requires Python 3.7+.

## Command line usage

```console
$ python -m sitemaps --help
usage: __main__.py [-h] [-o OUTPUT] [-I IGNORE_PATH_PREFIX] [--asgi ASGI]
                   [--max-concurrency MAX_CONCURRENCY] [--check]
                   target

positional arguments:
  target                The base URL used to crawl the website and build
                        sitemap URL tags.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file path.
  -I IGNORE_PATH_PREFIX, --ignore-path-prefix IGNORE_PATH_PREFIX
                        Ignore URLs for this path prefix. Can be used multiple
                        times.
  --asgi ASGI           Path to an ASGI app, formatted as
                        '<module>:<attribute>'.
  --max-concurrency MAX_CONCURRENCY
                        Maximum number of URLs to process concurrently.
  --check               Compare existing output and fail if computed XML
                        differs.
```

## Programmatic usage

### Live server

```python
import sitemaps

async def main():
    urls = await sitemaps.crawl("https://example.org")
    with open("sitemap.xml") as f:
        f.write(sitemaps.make_xml(urls))
```

### ASGI app

```python
import httpx
import sitemaps

from .app import app

async def main():
    async with httpx.AsyncClient(app=app) as client:
        urls = await sitemaps.crawl("http://mysite.io", client=client)

    with open("sitemap.xml") as f:
        f.write(sitemaps.make_xml(urls))
```

### Customizing URL tags

By default, `.make_xml()` generates `<url>` tags with a `daily` change frequency. You can customize the generation of URL tags by passing a custom `urltag` callable:

```python
from urllib.parse import urlsplit

def urltag(url):
    path = urlsplit(url).path
    changefreq = "monthly" if path.startswith("/reports") else "daily"
    return f"<url><loc>{url}</loc><changefreq>{changefreq}</changefreq></url>"

async def main():
    urls = await sitemaps.crawl(...)
    with open("sitemap.xml", "w") as f:
      f.write(sitemaps.make_xml(urls, urltag=urltag))
```

## License

MIT
