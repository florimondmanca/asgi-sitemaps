import threading
import time
from typing import Iterator

import httpx
import uvicorn


class Server(uvicorn.Server):
    def install_signal_handlers(self) -> None:
        pass

    @property
    def url(self) -> httpx.URL:
        return httpx.URL(f"http://{self.config.host}:{self.config.port}/")


def serve_in_thread(server: Server) -> Iterator[Server]:
    thread = threading.Thread(target=server.run)
    thread.start()
    try:
        while not server.started:
            time.sleep(1e-3)
        yield server
    finally:
        server.should_exit = True
        thread.join()
