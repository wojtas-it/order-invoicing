from fastapi import APIRouter

from app.api.dependencies import InvoiceServiceDep, OrderServiceDep
from app.api.responses import CARRIER_UNAVAILABLE, INVALID_DATA, NOT_FOUND, STATUS_CONFLICT
from app.api.schemas import InvoiceResponse, OrderCreateRequest, OrderResponse

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", status_code=201, summary="Złóż zamówienie", responses=INVALID_DATA)
def create_order(payload: OrderCreateRequest, service: OrderServiceDep) -> OrderResponse:
    return OrderResponse.from_domain(service.place_order(payload.to_command()))


@router.get("", summary="Lista zamówień")
def list_orders(service: OrderServiceDep) -> list[OrderResponse]:
    return [OrderResponse.from_domain(order) for order in service.list_orders()]


@router.get("/{order_id}", summary="Szczegóły zamówienia", responses=NOT_FOUND)
def get_order(order_id: int, service: OrderServiceDep) -> OrderResponse:
    return OrderResponse.from_domain(service.get_order(order_id))


@router.post("/{order_id}/pay", summary="Oznacz jako opłacone", responses=STATUS_CONFLICT)
def pay_order(order_id: int, service: OrderServiceDep) -> OrderResponse:
    return OrderResponse.from_domain(service.pay(order_id))


@router.post(
    "/{order_id}/ship",
    summary="Nadaj przesyłkę u przewoźnika",
    responses={**STATUS_CONFLICT, **CARRIER_UNAVAILABLE},
)
def ship_order(order_id: int, service: OrderServiceDep) -> OrderResponse:
    return OrderResponse.from_domain(service.ship(order_id))


@router.post("/{order_id}/deliver", summary="Oznacz jako dostarczone", responses=STATUS_CONFLICT)
def deliver_order(order_id: int, service: OrderServiceDep) -> OrderResponse:
    return OrderResponse.from_domain(service.deliver(order_id))


@router.post("/{order_id}/cancel", summary="Anuluj zamówienie", responses=STATUS_CONFLICT)
def cancel_order(order_id: int, service: OrderServiceDep) -> OrderResponse:
    return OrderResponse.from_domain(service.cancel(order_id))


@router.post(
    "/{order_id}/invoice",
    status_code=201,
    summary="Wystaw fakturę do zamówienia",
    responses=STATUS_CONFLICT,
)
def issue_invoice(order_id: int, service: InvoiceServiceDep) -> InvoiceResponse:
    return InvoiceResponse.from_domain(service.issue_for_order(order_id))
