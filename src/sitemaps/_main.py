import importlib
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Callable, Optional, Sequence

import httpx

from ._crawl import crawl
from ._xml import compare, write


def echo_error(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def load_asgi_app(app_path: str) -> Optional[Callable]:
    try:
        module, attribute = app_path.split(":")
    except ValueError:
        return None

    try:
        moduleobj = importlib.import_module(module)
    except ImportError:
        return None

    return getattr(moduleobj, attribute, None)


async def main(argv: Sequence[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target",
        help="The base URL used to crawl the website and build sitemap URL tags.",
    )
    parser.add_argument(
        "-o", "--output", default="sitemap.xml", help="Output file path."
    )
    parser.add_argument(
        "-I",
        "--ignore-path-prefix",
        action="append",
        default=[],
        help="Ignore URLs for this path prefix. Can be used multiple times.",
    )
    parser.add_argument(
        "--asgi", help="Path to an ASGI app, formatted as '<module>:<attribute>'.",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=100,
        help="Maximum number of URLs to process concurrently.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare existing output and fail if computed XML differs.",
    )

    args = parser.parse_args(argv)

    async with AsyncExitStack() as exit_stack:
        if args.asgi:
            # Make requests to an ASGI app.
            try:
                from asgi_lifespan import LifespanManager
            except ImportError:  # pragma: no cover
                echo_error("`asgi-lifespan` must be installed to use --asgi")
                return 1

            app = load_asgi_app(args.asgi)
            if app is None:
                echo_error(
                    f"Could not load ASGI app. Import string {args.asgi!r} "
                    f"must be formatted as '<module>:<attribute>'."
                )
                return 1

            await exit_stack.enter_async_context(LifespanManager(app))
            client = httpx.AsyncClient(app=app)
        else:
            # Make requests over the network.
            client = httpx.AsyncClient()

        urls = await crawl(
            root_url=args.target,
            ignore=args.ignore_path_prefix,
            client=client,
            max_tasks=args.max_concurrency,
        )

    if args.check:
        if not Path(args.output).exists():
            echo_error(f"Path {args.output} does not exist")
            return 1

        is_synced = await compare(urls, args.output)
        return 0 if is_synced else 1

    await write(urls, args.output)
    return 0
