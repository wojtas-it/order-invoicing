from decimal import ROUND_HALF_UP, Decimal

from app.domain.errors import ValidationError

ZERO = Decimal("0.00")
CENT = Decimal("0.01")


def round_money(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def validate_unit_price(amount: Decimal) -> None:
    if not amount.is_finite() or amount <= 0:
        raise ValidationError("Cena jednostkowa musi być większa od zera")
    if amount != round_money(amount):
        raise ValidationError("Cena jednostkowa może mieć maksymalnie dwa miejsca po przecinku")
