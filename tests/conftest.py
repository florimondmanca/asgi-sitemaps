from typing import Iterator

import pytest
import uvicorn

from .app import app
from .utils import Server, serve_in_thread


@pytest.fixture(scope="session")
def server() -> Iterator[Server]:
    config = uvicorn.Config(
        app=app, host="localhost", port=8000, lifespan="off", loop="asyncio"
    )
    server = Server(config=config)
    yield from serve_in_thread(server)
