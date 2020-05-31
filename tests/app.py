from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


async def home(request: Request) -> Response:
    return templates.TemplateResponse("index.html", context={"request": request})


async def child(request: Request) -> Response:
    return templates.TemplateResponse("child.html", context={"request": request})


routes = [
    Route("/", home, name="home"),
    Route("/child", child, name="child"),
]

app = Starlette(routes=routes)
