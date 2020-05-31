import sys

import anyio

from ._main import main

sys.exit(anyio.run(main))
