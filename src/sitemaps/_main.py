import importlib
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Sequence

import httpx

from ._crawl import crawl
from ._xml import compare, write


async def main(argv: Sequence[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument(
        "-o", "--output", default="sitemap.xml", help="Output file path."
    )
    parser.add_argument(
        "--base-url",
        help=(
            "Base URL to use when outputting URLs in the sitemap, "
            "eg https://mysite.com."
        ),
    )
    parser.add_argument(
        "-I",
        "--ignore-path-prefix",
        action="append",
        default=[],
        help="Ignore URLs for this path prefix. Can be used multiple times.",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=100,
        help="Maximum number of concurrent tasks.",
    )
    parser.add_argument(
        "--asgi",
        action="store_true",
        help=(
            "Treat 'target' as a path to an ASGI app, "
            "formatted as '<module>:<attribute>'."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare existing output and fail if computed XML results.",
    )

    args = parser.parse_args(argv)

    async with AsyncExitStack() as exit_stack:
        if args.asgi:
            try:
                from asgi_lifespan import LifespanManager
            except ImportError:  # pragma: no cover
                print("`asgi-lifespan` must be installed to use --asgi")
                return 1

            # Treat `target` as 'path.to.module:app'.
            module, name = args.target.split(":")
            mod = importlib.import_module(module)
            app = getattr(mod, name, None)
            assert app is not None
            await exit_stack.enter_async_context(LifespanManager(app))

            client = httpx.AsyncClient(app=app)
            if not args.base_url:
                print(
                    "ERROR: --base-url is required when calling into an ASGI app",
                    file=sys.stderr,
                )
                return 1
            root_url = args.base_url
            base_url = root_url
        else:
            # Treat `target` as an URL.
            client = httpx.AsyncClient()
            root_url = args.target
            base_url = args.base_url if args.base_url else root_url

        urls = await crawl(
            root_url=root_url,
            base_url=base_url,
            ignore=args.ignore_path_prefix,
            client=client,
            max_tasks=args.max_concurrency,
        )

    if args.check:
        if not Path(args.output).exists():
            print(f"ERROR: path {args.output} does not exist")
            return 1

        is_synced = await compare(urls, args.output)
        return 0 if is_synced else 1

    await write(urls, args.output)
    return 0
