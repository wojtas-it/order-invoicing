from collections.abc import Callable

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response

from app.api.dependencies import InvoiceServiceDep, OrderServiceDep
from app.domain.errors import DomainError, NotFoundError
from app.domain.order import Order
from app.domain.shipping import ShippingMethod
from app.domain.vat import VatRate
from app.services.order_service import OrderService
from app.web.formatting import shipping_price_gross
from app.web.forms import ITEM_ROWS, parse_order_form
from app.web.templating import redirect, render_not_found, templates

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
    return redirect(f"/orders/{order.id}")


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
        return render_not_found(request, not_found)
    context = {"order": order, "invoice": invoices.find_for_order(order_id), "error": error}
    return templates.TemplateResponse(request, "order_detail.html", context)


@router.post("/orders/{order_id}/actions/{action}")
def run_order_action(order_id: int, action: str, orders: OrderServiceDep) -> Response:
    handler = ORDER_ACTIONS.get(action)
    if handler is None:
        return redirect(f"/orders/{order_id}", error=f"Nieznana akcja: {action}")
    try:
        handler(orders, order_id)
    except DomainError as error:
        return redirect(f"/orders/{order_id}", error=str(error))
    return redirect(f"/orders/{order_id}")


@router.post("/orders/{order_id}/invoice")
def issue_invoice(order_id: int, invoices: InvoiceServiceDep) -> Response:
    try:
        invoice = invoices.issue_for_order(order_id)
    except DomainError as error:
        return redirect(f"/orders/{order_id}", error=str(error))
    return redirect(f"/invoices/{invoice.id}")


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
