from decimal import Decimal
from enum import IntEnum


class VatRate(IntEnum):
    STANDARD = 23
    REDUCED = 8
    SUPER_REDUCED = 5
    ZERO = 0

    @property
    def fraction(self) -> Decimal:
        return Decimal(self.value) / Decimal(100)
