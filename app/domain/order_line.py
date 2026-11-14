from collections.abc import Iterable
from dataclasses import dataclass

from app.domain.errors import ValidationError
from app.domain.order_item import MAX_QUANTITY


@dataclass(frozen=True)
class OrderLine:
    """Product and quantity requested in an order, before prices are taken from the catalog."""

    product_id: int
    quantity: int

    def __post_init__(self) -> None:
        if not 1 <= self.quantity <= MAX_QUANTITY:
            raise ValidationError(f"Ilość musi być z zakresu 1-{MAX_QUANTITY}")


def merge_order_lines(lines: Iterable[OrderLine]) -> dict[int, int]:
    """Sums quantities of lines with the same product, keeping the order of first appearance."""
    quantities: dict[int, int] = {}
    for line in lines:
        quantities[line.product_id] = quantities.get(line.product_id, 0) + line.quantity
    return quantities
