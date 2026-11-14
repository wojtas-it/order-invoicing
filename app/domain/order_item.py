from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from app.domain.errors import ValidationError
from app.domain.money import validate_unit_price
from app.domain.product import Product
from app.domain.vat import VatRate

MAX_QUANTITY = 999


@dataclass(frozen=True)
class OrderItem:
    """Order position with product data copied at the moment of purchase.

    Later changes in the catalog (e.g. a new price) do not affect placed orders.
    """

    product_id: int
    name: str
    quantity: int
    unit_price_net: Decimal
    vat_rate: VatRate

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("Nazwa pozycji nie może być pusta")
        if not 1 <= self.quantity <= MAX_QUANTITY:
            raise ValidationError(f"Ilość musi być z zakresu 1-{MAX_QUANTITY}")
        validate_unit_price(self.unit_price_net)

    @classmethod
    def from_product(cls, product: Product, quantity: int) -> Self:
        if product.id is None:
            raise ValueError("Product must be saved before it can be ordered")
        return cls(
            product_id=product.id,
            name=product.name,
            quantity=quantity,
            unit_price_net=product.unit_price_net,
            vat_rate=product.vat_rate,
        )

    @property
    def net_total(self) -> Decimal:
        return self.unit_price_net * self.quantity
