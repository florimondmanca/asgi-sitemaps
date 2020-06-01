import argparse
import difflib
import importlib
import sys
from typing import IO, Callable, Optional, Sequence, Tuple

from ._crawl import crawl
from ._xml import make_xml


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


def compare(xml_a: str, xml_b: str) -> Tuple[list, bool]:
    xml_a = xml_a.strip("\n")
    xml_b = xml_b.strip("\n")
    lines_a = xml_a.splitlines(keepends=True)
    lines_b = xml_b.splitlines(keepends=True)
    differences = list(difflib.ndiff(lines_a, lines_b))
    return differences, "".join(line[2:] for line in differences) == xml_a == xml_b


async def main(
    argv: Sequence[str],
    stdin: IO[str] = sys.stdin,
    stdout: IO[str] = sys.stdout,
    stderr: IO[str] = sys.stderr,
) -> int:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "app", help="Path to an ASGI app, formatted as '<module>:<attribute>'.",
    )
    parser.add_argument(
        "--base-url",
        default="http://testserver/",
        help="Base URL to use when building sitemap entries.",
    )
    parser.add_argument(
        "-I",
        "--ignore-path-prefix",
        action="append",
        default=[],
        help=(
            "Prevent crawling URLs that start with this path prefix. "
            "Can be used multiple times."
        ),
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=100,
        help="Maximum number of concurrently processed URLs.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Read existing sitemap from stdin and fail if computed sitemap differs.",
    )

    args = parser.parse_args(argv)

    app = load_asgi_app(args.app)
    if app is None:
        stderr.write(
            f"ERROR: Could not load ASGI app. Import string {args.app!r} "
            f"must be formatted as '<module>:<attribute>'."
        )
        return 1

    urls = await crawl(
        app=app,
        base_url=args.base_url,
        ignore=args.ignore_path_prefix,
        max_concurrency=args.max_concurrency,
    )

    xml = make_xml(urls)

    if args.check:
        differences, matches = compare(stdin.read(), xml)
        if not matches:
            stderr.writelines(differences)
            return 1
        return 0

    stdout.write(xml)
    return 0
