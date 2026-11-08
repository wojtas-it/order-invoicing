from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response

from app.api.dependencies import InvoiceServiceDep, OrderServiceDep
from app.domain.errors import NotFoundError
from app.web.templating import render_not_found, templates

router = APIRouter(include_in_schema=False)


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
        return render_not_found(request, not_found)
    context = {
        "invoice": invoice,
        "order": orders.get_order(invoice.order_id),
        "seller": request.app.state.settings.seller,
    }
    return templates.TemplateResponse(request, "invoice.html", context)
