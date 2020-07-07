# asgi-sitemaps

[![Build Status](https://dev.azure.com/florimondmanca/public/_apis/build/status/florimondmanca.asgi-sitemaps?branchName=master)](https://dev.azure.com/florimondmanca/public/_build/latest?definitionId=11&branchName=master)
[![Coverage](https://codecov.io/gh/florimondmanca/asgi-sitemaps/branch/master/graph/badge.svg)](https://codecov.io/gh/florimondmanca/asgi-sitemaps)
![Python versions](https://img.shields.io/pypi/pyversions/asgi-sitemaps.svg)
[![Package version](https://badge.fury.io/py/asgi-sitemaps.svg)](https://pypi.org/project/asgi-sitemaps)

[Sitemap](https://www.sitemaps.org) generation for ASGI applications. Inspired by [Django's sitemap framework](https://docs.djangoproject.com/en/3.0/ref/contrib/sitemaps/).

_**Note**: This is alpha software. Be sure to pin your dependencies to the latest minor release._

**Contents**

- [Features](#features)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [How-To](#how-to)
  - [Sitemap sections](#sitemap-sections)
  - [Dynamic generation from database queries](#dynamic-generation-from-database-queries)
  - [Advanced web framework integration](#advanced-web-framework-integration)
- [API Reference](#api-reference)
  - [`Sitemap`](#class-sitemap)
  - [`SitemapApp`](#class-sitemapapp)

## Features

- Build and compose sitemap sections into a single dynamic ASGI endpoint.
- Supports drawing sitemap items from a variety of sources (static lists, (async) ORM queries, etc).
- Compatible with any ASGI framework.
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

Here is the project file structure:

```console
.
└── server
    ├── __init__.py
    ├── app.py
    └── sitemap.py
```

First, declare a sitemap section by subclassing `Sitemap`, then wrap it in a `SitemapApp`:

```python
# server/sitemap.py
import asgi_sitemaps

class Sitemap(asgi_sitemaps.Sitemap):
    def items(self):
        return ["/"]

    def location(self, item: str):
        return item

    def changefreq(self, item: str):
        return "monthly"

sitemap = asgi_sitemaps.SitemapApp(Sitemap(), domain="example.io")
```

Now, register the `sitemap` endpoint as a route onto your ASGI app. For example, if using Starlette:

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
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>
```

Tada!

To learn more:

- See [How-To](#how-to) for more advanced usage, including splitting the sitemap in multiple sections, and dynamically generating entries from database queries.
- See the [`Sitemap` API reference](#class-sitemap) for all supported sitemap options.

## How-To

### Sitemap sections

You can combine multiple sitemap classes into a single sitemap endpoint. This is useful to split the sitemap in multiple sections that may have different `items()` and/or sitemap attributes. Such sections could be static pages, blog posts, recent articles, etc.

To do so, declare multiple sitemap classes, then pass them as a list to `SitemapApp`:

```python
# server/sitemap.py
import asgi_sitemaps

class StaticSitemap(asgi_sitemaps.Sitemap):
    ...

class BlogSitemap(asgi_sitemaps.Sitemap):
    ...

sitemap = asgi_sitemaps.SitemapApp([StaticSitemap(), BlogSitemap()], domain="example.io")
```

Entries from each sitemap will be concatenated when building the final `sitemap.xml`.

### Dynamic generation from database queries

`Sitemap.items()` supports consuming any async iterable. This means you can easily integrate with an async database client or ORM so that `Sitemap.items()` fetches and returns relevant rows for generating your sitemap.

Here's an example using [Databases](https://github.com/encode/databases), assuming you have a `Database` instance in `server/resources.py`:

```python
# server/sitemap.py
import asgi_sitemaps
from .resources import database

class Sitemap(asgi_sitemaps.Sitemap):
    async def items(self):
        query = "SELECT permalink, updated_at FROM articles;"
        return await database.fetch_all(query)

    def location(self, row: dict):
        return row["permalink"]
```

### Advanced web framework integration

While `asgi-sitemaps` is framework-agnostic, you can use the [`.scope` attribute](#scope) available on `Sitemap` instances to feed the ASGI scope into your framework-specific APIs for inspecting and manipulating request information.

Here is an example with [Starlette](https://www.starlette.io) where we build sitemap of static pages. To decouple from the raw URL paths, pages are referred to by view name. We reverse-lookup their URLs by building a `Request` instance from the ASGI `.scope`, and using `.url_for()`:

```python
# server/sitemap.py
import asgi_sitemaps
from starlette.datastructures import URL
from starlette.requests import Request

class StaticSitemap(asgi_sitemaps.Sitemap):
    def items(self):
        return ["home", "about", "blog:home"]

    def location(self, name: str):
        request = Request(scope=self.scope)
        url = request.url_for(name)
        return URL(url).path
```

The corresponding Starlette routing table could look something like this:

```python
# server/routes.py
from starlette.routing import Mount, Route
from . import views
from .sitemap import sitemap

routes = [
    Route("/", views.home, name="home"),
    Route("/about", views.about, name="about"),
    Route("/blog/", views.blog_home, name="blog:home"),
    Route("/sitemap.xml", sitemap),
]
```

## API Reference

### _class_ `Sitemap`

Represents a source of sitemap entries.

You can specify the type `T` of sitemap items for extra type safety:

```python
import asgi_sitemaps

class MySitemap(asgi_sitemaps.Sitemap[str]):
    ...
```

#### _async_ `items`

Signature: `async def () -> Union[Iterable[T], AsyncIterable[T]]`

_(**Required**)_ Return an [iterable](https://docs.python.org/3/glossary.html#term-iterable) or an [asynchronous iterable](https://docs.python.org/3/glossary.html#term-asynchronous-iterable) of items of the same type. Each item will be passed as-is to `.location()`, `.lastmod()`, `.changefreq()`, and `.priority()`.

Examples:

```python
# Simplest usage: return a list
def items(self) -> List[str]:
    return ["/", "/contact"]

# Async operations are also supported
async def items(self) -> List[dict]:
    query = "SELECT permalink, updated_at FROM pages;"
    return await database.fetch_all(query)

# Sync and async generators are also supported
async def items(self) -> AsyncIterator[dict]:
    query = "SELECT permalink, updated_at FROM pages;"
    async for row in database.aiter_rows(query):
        yield row
```

#### `location`

Signature: `def (item: T) -> str`

_(**Required**)_ Return the absolute path of a sitemap item.

"Absolute path" means an URL path without a protocol or domain. For example: `/blog/my-article`. (So `https://mydomain.com/blog/my-article` is not a valid location, nor is `mydomain.com/blog/my-article`.)

#### `lastmod`

Signature: `def (item: T) -> Optional[datetime.datetime]`

_(Optional)_ Return the [date of last modification](https://www.sitemaps.org/protocol.html#lastmoddef) of a sitemap item as a [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime) object, or `None` (the default) for no `lastmod` field.

#### `changefreq`

Signature: `def (item: T) -> Optional[str]`

_(Optional)_ Return the [change frequency](https://www.sitemaps.org/protocol.html#changefreqdef) of a sitemap item.

Possible values are:

- `None` - No `changefreq` field (the default).
- `"always"`
- `"hourly"`
- `"daily"`
- `"weekly"`
- `"monthly"`
- `"yearly"`
- `"never"`

#### `priority`

Signature: `def (item: T) -> float`

_(Optional)_ Return the [priority](https://www.sitemaps.org/protocol.html#prioritydef) of a sitemap item. Must be between 0 and 1. Defaults to `0.5`.

#### `protocol`

Type: `str`

_(Optional)_ This attribute defines the protocol used to build URLs of the sitemap.

Possible values are:

- `"auto"` - The protocol with which the sitemap was requested (the default).
- `"http"`
- `"https"`

#### `scope`

This property returns the [ASGI scope](https://asgi.readthedocs.io/en/latest/specs/www.html#connection-scope) of the current HTTP request.

### _class_ `SitemapApp`

An ASGI application that responds to HTTP requests with the `sitemap.xml` contents of the sitemap.

Parameters:

- _(**Required**)_ `sitemaps` - A `Sitemap` object or a list of `Sitemap` objects, used to generate sitemap entries.
- _(**Required**)_ `domain` - The domain to use when generating sitemap URLs.

Examples:

```python
sitemap = SitemapApp(Sitemap(), domain="mydomain.com")
sitemap = SitemapApp([StaticSitemap(), BlogSitemap()], domain="mydomain.com")
```

## License

MIT
