from collections.abc import Callable, Sequence
from dataclasses import dataclass

from app.domain.customer import Customer
from app.domain.discounts import DiscountCatalog
from app.domain.errors import OrderNotFoundError
from app.domain.order import Order, OrderStatus
from app.domain.order_item import OrderItem
from app.domain.pricing import PriceCalculator
from app.domain.shipping import ShippingMethod
from app.services.ports import CarrierClient, Clock, OrderRepository, ShipmentRequest


@dataclass(frozen=True)
class PlaceOrderCommand:
    customer: Customer
    items: Sequence[OrderItem]
    shipping_method: ShippingMethod
    discount_code: str | None = None


class OrderService:
    def __init__(
        self,
        orders: OrderRepository,
        calculator: PriceCalculator,
        discounts: DiscountCatalog,
        carrier: CarrierClient,
        clock: Clock,
    ) -> None:
        self._orders = orders
        self._calculator = calculator
        self._discounts = discounts
        self._carrier = carrier
        self._clock = clock

    def place_order(self, command: PlaceOrderCommand) -> Order:
        discount = self._discounts.resolve(command.discount_code)
        totals = self._calculator.calculate(command.items, discount, command.shipping_method)
        order = Order(
            customer=command.customer,
            items=list(command.items),
            shipping_method=command.shipping_method,
            totals=totals,
            created_at=self._clock.now(),
            discount_code=self._discounts.normalize(command.discount_code),
        )
        return self._orders.add(order)

    def get_order(self, order_id: int) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order

    def list_orders(self) -> list[Order]:
        return self._orders.list_all()

    def pay(self, order_id: int) -> Order:
        return self._apply(order_id, Order.mark_paid)

    def cancel(self, order_id: int) -> Order:
        return self._apply(order_id, Order.cancel)

    def deliver(self, order_id: int) -> Order:
        return self._apply(order_id, Order.mark_delivered)

    def ship(self, order_id: int) -> Order:
        order = self.get_order(order_id)
        order.ensure_can_change_to(OrderStatus.SHIPPED)
        tracking_number = self._carrier.create_shipment(_shipment_request_for(order))
        order.mark_shipped(tracking_number)
        self._orders.update(order)
        return order

    def _apply(self, order_id: int, action: Callable[[Order], None]) -> Order:
        order = self.get_order(order_id)
        action(order)
        self._orders.update(order)
        return order


def _shipment_request_for(order: Order) -> ShipmentRequest:
    assert order.id is not None
    return ShipmentRequest(
        order_id=order.id,
        recipient_name=order.customer.name,
        recipient_email=order.customer.email,
        street=order.customer.street,
        city=order.customer.city,
        postal_code=order.customer.postal_code,
        shipping_method=order.shipping_method,
    )
