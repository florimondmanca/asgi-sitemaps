from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


async def home(request: Request) -> Response:
    return templates.TemplateResponse("index.html", context={"request": request})


async def child(request: Request) -> Response:
    return templates.TemplateResponse("child.html", context={"request": request})


async def not_found(request: Request) -> Response:
    return HTMLResponse("<h1>Not Found</h1>", status_code=404)


async def api_hello(request: Request) -> Response:
    return JSONResponse({"message": "Hello, world!"})


routes = [
    Route("/", home, name="home"),
    Route("/child", child, name="child"),
    Route("/404", not_found, name="404"),
    Route("/api/hello", api_hello, name="api:hello"),
]

app = Starlette(routes=routes)
