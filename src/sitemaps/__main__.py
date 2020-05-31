if __name__ == "__main__":  # pragma: no cover
    import sys
    import anyio
    from ._main import main

    sys.exit(anyio.run(main, sys.argv[1:]))
