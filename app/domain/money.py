from decimal import ROUND_HALF_UP, Decimal

ZERO = Decimal("0.00")
CENT = Decimal("0.01")


def round_money(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)
