from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.domain.customer import Customer
from app.domain.errors import InvalidStatusTransitionError, ValidationError
from app.domain.order_item import OrderItem
from app.domain.pricing import OrderTotals
from app.domain.shipping import ShippingMethod


class OrderStatus(StrEnum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    @property
    def label(self) -> str:
        return STATUS_LABELS[self]


STATUS_LABELS = {
    OrderStatus.NEW: "Nowe",
    OrderStatus.PAID: "Opłacone",
    OrderStatus.SHIPPED: "Wysłane",
    OrderStatus.DELIVERED: "Dostarczone",
    OrderStatus.CANCELLED: "Anulowane",
}

ALLOWED_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.NEW: frozenset({OrderStatus.PAID, OrderStatus.CANCELLED}),
    OrderStatus.PAID: frozenset({OrderStatus.SHIPPED, OrderStatus.CANCELLED}),
    OrderStatus.SHIPPED: frozenset({OrderStatus.DELIVERED}),
    OrderStatus.DELIVERED: frozenset(),
    OrderStatus.CANCELLED: frozenset(),
}
INVOICEABLE_STATUSES = frozenset({OrderStatus.PAID, OrderStatus.SHIPPED, OrderStatus.DELIVERED})


@dataclass
class Order:
    customer: Customer
    items: list[OrderItem]
    shipping_method: ShippingMethod
    totals: OrderTotals
    created_at: datetime
    discount_code: str | None = None
    status: OrderStatus = OrderStatus.NEW
    tracking_number: str | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        if not self.items:
            raise ValidationError("Zamówienie musi zawierać co najmniej jedną pozycję")

    @property
    def can_be_invoiced(self) -> bool:
        return self.status in INVOICEABLE_STATUSES

    def can_change_to(self, target: OrderStatus) -> bool:
        return target in ALLOWED_TRANSITIONS[self.status]

    def ensure_can_change_to(self, target: OrderStatus) -> None:
        if not self.can_change_to(target):
            raise InvalidStatusTransitionError(self.status.label, target.label)

    def mark_paid(self) -> None:
        self._change_to(OrderStatus.PAID)

    def mark_shipped(self, tracking_number: str) -> None:
        self._change_to(OrderStatus.SHIPPED)
        self.tracking_number = tracking_number

    def mark_delivered(self) -> None:
        self._change_to(OrderStatus.DELIVERED)

    def cancel(self) -> None:
        self._change_to(OrderStatus.CANCELLED)

    def _change_to(self, target: OrderStatus) -> None:
        self.ensure_can_change_to(target)
        self.status = target
