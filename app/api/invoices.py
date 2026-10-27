from fastapi import APIRouter

from app.api.dependencies import InvoiceServiceDep
from app.api.schemas import ErrorResponse, InvoiceResponse

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.get("", summary="Lista faktur")
def list_invoices(service: InvoiceServiceDep) -> list[InvoiceResponse]:
    return [InvoiceResponse.from_domain(invoice) for invoice in service.list_invoices()]


@router.get(
    "/{invoice_id}",
    summary="Szczegóły faktury",
    responses={404: {"model": ErrorResponse}},
)
def get_invoice(invoice_id: int, service: InvoiceServiceDep) -> InvoiceResponse:
    return InvoiceResponse.from_domain(service.get_invoice(invoice_id))
