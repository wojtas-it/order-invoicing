from decimal import Decimal
from enum import IntEnum

from app.domain.money import round_money


class VatRate(IntEnum):
    STANDARD = 23
    REDUCED = 8
    SUPER_REDUCED = 5
    ZERO = 0

    @property
    def fraction(self) -> Decimal:
        return Decimal(self.value) / Decimal(100)

    def vat_for(self, net: Decimal) -> Decimal:
        return round_money(net * self.fraction)
