from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.api.dependencies import InvoiceServiceDep, OrderServiceDep
from app.domain.errors import DomainError, NotFoundError
from app.domain.order import Order, OrderStatus
from app.domain.shipping import ShippingMethod
from app.domain.vat import VatRate
from app.services.order_service import OrderService
from app.web.formatting import format_money, shipping_price_gross
from app.web.forms import ITEM_ROWS, parse_order_form

TEMPLATES_DIR = Path(__file__).parent / "templates"

templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.filters["money"] = format_money
templates.env.globals["OrderStatus"] = OrderStatus

ORDER_ACTIONS: dict[str, Callable[[OrderService, int], Order]] = {
    "pay": OrderService.pay,
    "ship": OrderService.ship,
    "deliver": OrderService.deliver,
    "cancel": OrderService.cancel,
}

router = APIRouter(include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
def order_list(request: Request, orders: OrderServiceDep) -> Response:
    return templates.TemplateResponse(request, "orders.html", {"orders": orders.list_orders()})


@router.get("/orders/new", response_class=HTMLResponse)
def new_order_form(request: Request) -> Response:
    return _render_order_form(request, form={})


@router.post("/orders", response_class=HTMLResponse)
async def create_order(request: Request, orders: OrderServiceDep) -> Response:
    form = await request.form()
    try:
        order = orders.place_order(parse_order_form(form))
    except DomainError as error:
        return _render_order_form(request, form=form, error=str(error), status_code=422)
    return _redirect(f"/orders/{order.id}")


@router.get("/orders/{order_id}", response_class=HTMLResponse)
def order_detail(
    request: Request,
    order_id: int,
    orders: OrderServiceDep,
    invoices: InvoiceServiceDep,
    error: str | None = None,
) -> Response:
    try:
        order = orders.get_order(order_id)
    except NotFoundError as not_found:
        return _render_not_found(request, not_found)
    context = {"order": order, "invoice": invoices.find_for_order(order_id), "error": error}
    return templates.TemplateResponse(request, "order_detail.html", context)


@router.post("/orders/{order_id}/actions/{action}")
def run_order_action(order_id: int, action: str, orders: OrderServiceDep) -> Response:
    handler = ORDER_ACTIONS.get(action)
    if handler is None:
        return _redirect_to_order(order_id, error=f"Nieznana akcja: {action}")
    try:
        handler(orders, order_id)
    except DomainError as error:
        return _redirect_to_order(order_id, error=str(error))
    return _redirect_to_order(order_id)


@router.post("/orders/{order_id}/invoice")
def issue_invoice(order_id: int, invoices: InvoiceServiceDep) -> Response:
    try:
        invoice = invoices.issue_for_order(order_id)
    except DomainError as error:
        return _redirect_to_order(order_id, error=str(error))
    return _redirect(f"/invoices/{invoice.id}")


@router.get("/invoices", response_class=HTMLResponse)
def invoice_list(request: Request, invoices: InvoiceServiceDep) -> Response:
    context = {"invoices": invoices.list_invoices()}
    return templates.TemplateResponse(request, "invoices.html", context)


@router.get("/invoices/{invoice_id}", response_class=HTMLResponse)
def invoice_detail(
    request: Request,
    invoice_id: int,
    invoices: InvoiceServiceDep,
    orders: OrderServiceDep,
) -> Response:
    try:
        invoice = invoices.get_invoice(invoice_id)
    except NotFoundError as not_found:
        return _render_not_found(request, not_found)
    context = {
        "invoice": invoice,
        "order": orders.get_order(invoice.order_id),
        "seller": request.app.state.settings.seller,
    }
    return templates.TemplateResponse(request, "invoice.html", context)


def _render_order_form(
    request: Request, form: object, error: str | None = None, status_code: int = 200
) -> Response:
    context = {
        "form": form,
        "error": error,
        "item_rows": range(ITEM_ROWS),
        "vat_rates": list(VatRate),
        "shipping_options": [(method, shipping_price_gross(method)) for method in ShippingMethod],
    }
    return templates.TemplateResponse(request, "order_form.html", context, status_code=status_code)


def _render_not_found(request: Request, error: NotFoundError) -> Response:
    return templates.TemplateResponse(
        request, "not_found.html", {"message": str(error)}, status_code=404
    )


def _redirect_to_order(order_id: int, error: str | None = None) -> Response:
    query = f"?{urlencode({'error': error})}" if error else ""
    return _redirect(f"/orders/{order_id}{query}")


def _redirect(url: str) -> Response:
    return RedirectResponse(url, status_code=303)
