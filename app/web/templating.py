from pathlib import Path
from urllib.parse import urlencode

from fastapi import Request
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.domain.errors import NotFoundError
from app.domain.order import OrderStatus
from app.web.formatting import format_money

TEMPLATES_DIR = Path(__file__).parent / "templates"

templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.filters["money"] = format_money
templates.env.globals["OrderStatus"] = OrderStatus


def redirect(url: str, error: str | None = None) -> Response:
    if error:
        url = f"{url}?{urlencode({'error': error})}"
    return RedirectResponse(url, status_code=303)


def render_not_found(request: Request, error: NotFoundError) -> Response:
    return templates.TemplateResponse(
        request, "not_found.html", {"message": str(error)}, status_code=404
    )
