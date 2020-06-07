# asgi-sitemaps

[![Build Status](https://dev.azure.com/florimondmanca/public/_apis/build/status/florimondmanca.asgi-sitemaps?branchName=master)](https://dev.azure.com/florimondmanca/public/_build/latest?definitionId=11&branchName=master)
[![Coverage](https://codecov.io/gh/florimondmanca/asgi-sitemaps/branch/master/graph/badge.svg)](https://codecov.io/gh/florimondmanca/asgi-sitemaps)
![Python versions](https://img.shields.io/pypi/pyversions/asgi-sitemaps.svg)
[![Package version](https://badge.fury.io/py/asgi-sitemaps.svg)](https://pypi.org/project/asgi-sitemaps)

[Sitemap](https://www.sitemaps.org) generation for ASGI apps. Inspired by [Django's sitemap framework](https://docs.djangoproject.com/en/3.0/ref/contrib/sitemaps/).

_**Note**: This is alpha software. Be sure to pin your dependencies to the latest minor release._

## Features

- Build and compose sitemap sections into a single ASGI endpoint.
- Compatible with any ASGI framework.
- Any iterable can be used as a source of sitemap entries (e.g. static lists, (async) ORM queries, etc).
- Fully type annotated.
- 100% test coverage.

## Installation

Install with pip:

```shell
$ pip install asgi-sitemaps
```

`asgi-sitemaps` requires Python 3.7+.

## Quickstart

Let's build a static sitemap for a "Hello, world!" application. The sitemap will contain a single URL entry for the home `/` endpoint.

First, declare a sitemap section by subclassing `Sitemap`, then wire it up in a `SitemapApp` instance:

```python
# server/sitemap.py
import asgi_sitemaps

class DefaultSitemap(asgi_sitemaps.Sitemap):
    async def items(self):
        return ["/"]

    def location(self, item):
        return item

sitemap = asgi_sitemaps.SitemapApp({"default": DefaultSitemap()}, domain="example.io")
```

Now, register `sitemap` as a route onto your ASGI app. For example, if using Starlette:

```python
# server/app.py
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from .sitemap import sitemap

async def home(request):
    return PlainTextResponse("Hello, world!")

routes = [
    Route("/", home),
    Route("/sitemap.xml", sitemap),
]

app = Starlette(routes=routes)
```

Serve the app using `$ uvicorn server.app:app`, then request the sitemap:

```bash
curl http://localhost:8000/sitemap.xml
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>http://example.io/</loc>
  </url>
</urlset>
```

## How-To

### Integrate with a database client or an ORM

> TODO

## API Reference

### `Sitemap`

> TODO

### `SitemapApp`

> TODO

## License

MIT
