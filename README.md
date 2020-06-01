# asgi-sitemaps

[![Build Status](https://dev.azure.com/florimondmanca/public/_apis/build/status/florimondmanca.asgi-sitemaps?branchName=master)](https://dev.azure.com/florimondmanca/public/_build/latest?definitionId=11&branchName=master)
[![Coverage](https://codecov.io/gh/florimondmanca/asgi-sitemaps/branch/master/graph/badge.svg)](https://codecov.io/gh/florimondmanca/asgi-sitemaps)
![Python versions](https://img.shields.io/pypi/pyversions/asgi-sitemaps.svg)
[![Package version](https://badge.fury.io/py/asgi-sitemaps.svg)](https://pypi.org/project/asgi-sitemaps)

Generate and check sitemap files from ASGI apps without having to spin up a server. Powered by [HTTPX](https://github.com/encode/httpx) and [anyio](https://github.com/agronholm/anyio).

_**Note**: This is alpha software. Be sure to pin your dependencies to the latest minor release._

## Quickstart

```bash
python -m asgi_sitemaps 'example:app' --base-url https://app.example.io > sitemap.xml
```

```console
$ cat sitemap.xml
<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
    <url><loc>https://app.example.io/</loc><changefreq>daily</changefreq></url>
</urlset>
```

Use the `--check` mode to verify that the sitemap is in sync (e.g. as part of CI checks):

```bash
cat sitemap.xml | python -m asgi_sitemaps --check 'example:app' --base-url https://app.example.io
```

## Features

- Offline sitemap generation from an ASGI app callable.
- Support for `--check` mode.
- Invoke from the command line, or use the programmatic async API (supports asyncio and trio).
- Fully type annotated.
- 100% test coverage.

## Installation

Install with pip:

```shell
$ pip install asgi-sitemaps
```

`asgi-sitemaps` requires Python 3.7+.

## Command line reference

```console
$ python -m asgi_sitemaps --help
usage: __main__.py [-h] [--base-url BASE_URL] [-I IGNORE_PATH_PREFIX]
                   [--max-concurrency MAX_CONCURRENCY] [--check]
                   app

positional arguments:
  app                   Path to an ASGI app, formatted as
                        '<module>:<attribute>'.

optional arguments:
  -h, --help            show this help message and exit
  --base-url BASE_URL   Base URL to use when building sitemap entries.
                        (default: http://testserver/)
  -I IGNORE_PATH_PREFIX, --ignore-path-prefix IGNORE_PATH_PREFIX
                        Prevent crawling URLs that start with this path
                        prefix. Can be used multiple times. (default: [])
  --max-concurrency MAX_CONCURRENCY
                        Maximum number of concurrently processed URLs.
                        (default: 100)
  --check               Read existing sitemap from stdin and fail if computed
                        sitemap differs. (default: False)
```

## Programmatic API

The `.crawl()` async function takes the following arguments:

- `app`: an ASGI application instance.
- `base_url`: see `--base-url`
- `ignore`: see `--ignore-path-prefix`.
- `max_concurrency`: see `--max-concurrency`.

It returns a list of strings referring to the discovered URLs.

You can use the `.make_url(urls)` helper to generate the sitemap XML and save it as is appropriate for your use case.

Example usage, outputting the sitemap to a `sitemap.xml` file (mimicking the CLI behavior):

```python
import asgi_sitemaps

from .app import app

async def main():
    urls = await asgi_sitemaps.crawl(app)
    with open("sitemap.xml", "w") as f:
        f.write(asgi_sitemaps.make_xml(urls))
```

By default, `.make_xml()` generates `<url>` tags with a `daily` change frequency. You can customize the generation of URL tags by passing a custom `urltag` callable:

```python
from urllib.parse import urlsplit

import asgi_sitemaps

def urltag(url):
    path = urlsplit(url).path
    changefreq = "monthly" if path.startswith("/reports") else "daily"
    return f"<url><loc>{url}</loc><changefreq>{changefreq}</changefreq></url>"

urls = ...
xml = asgi_sitemaps.make_xml(urls, urltag=urltag)
```

## License

MIT
