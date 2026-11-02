from dataclasses import dataclass
from decimal import Decimal

from app.domain.errors import ValidationError
from app.domain.money import validate_unit_price
from app.domain.vat import VatRate

MAX_QUANTITY = 999


@dataclass(frozen=True)
class OrderItem:
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

    @property
    def net_total(self) -> Decimal:
        return self.unit_price_net * self.quantity
