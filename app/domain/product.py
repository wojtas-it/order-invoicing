from dataclasses import dataclass
from decimal import Decimal

from app.domain.errors import ValidationError
from app.domain.money import round_money, validate_unit_price
from app.domain.vat import VatRate


@dataclass
class Product:
    name: str
    unit_price_net: Decimal
    vat_rate: VatRate
    active: bool = True
    id: int | None = None

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValidationError("Nazwa produktu nie może być pusta")
        validate_unit_price(self.unit_price_net)
        self.unit_price_net = round_money(self.unit_price_net)

    @property
    def unit_price_gross(self) -> Decimal:
        return self.unit_price_net + self.vat_rate.vat_for(self.unit_price_net)
