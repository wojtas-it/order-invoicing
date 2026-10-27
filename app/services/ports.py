from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.domain.invoice import Invoice
from app.domain.order import Order
from app.domain.shipping import ShippingMethod


class OrderRepository(Protocol):
    def add(self, order: Order) -> Order: ...

    def get(self, order_id: int) -> Order | None: ...

    def list_all(self) -> list[Order]: ...

    def update(self, order: Order) -> None: ...


class InvoiceRepository(Protocol):
    def add(self, invoice: Invoice) -> Invoice: ...

    def get(self, invoice_id: int) -> Invoice | None: ...

    def find_by_order(self, order_id: int) -> Invoice | None: ...

    def list_all(self) -> list[Invoice]: ...

    def count_issued_in_month(self, year: int, month: int) -> int: ...


@dataclass(frozen=True)
class ShipmentRequest:
    order_id: int
    recipient_name: str
    recipient_email: str
    street: str
    city: str
    postal_code: str
    shipping_method: ShippingMethod


class CarrierClient(Protocol):
    def create_shipment(self, request: ShipmentRequest) -> str:
        """Registers a shipment and returns its tracking number."""
        ...


class Clock(Protocol):
    def now(self) -> datetime: ...
