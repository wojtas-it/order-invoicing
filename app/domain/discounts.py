from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from app.domain.errors import UnknownDiscountCodeError, ValidationError
from app.domain.money import ZERO, round_money


class DiscountPolicy(Protocol):
    def discount_for(self, net_total: Decimal) -> Decimal: ...


class NoDiscount:
    def discount_for(self, net_total: Decimal) -> Decimal:
        return ZERO


@dataclass(frozen=True)
class PercentageDiscount:
    percent: Decimal

    def __post_init__(self) -> None:
        if not 0 < self.percent <= 100:
            raise ValidationError("Rabat procentowy musi być z zakresu (0, 100]")

    def discount_for(self, net_total: Decimal) -> Decimal:
        return round_money(net_total * self.percent / Decimal(100))


@dataclass(frozen=True)
class FixedAmountDiscount:
    amount: Decimal

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValidationError("Rabat kwotowy musi być większy od zera")

    def discount_for(self, net_total: Decimal) -> Decimal:
        return min(self.amount, net_total)


DEFAULT_DISCOUNT_CODES: Mapping[str, DiscountPolicy] = {
    "WELCOME10": PercentageDiscount(Decimal("10")),
    "MINUS20": FixedAmountDiscount(Decimal("20.00")),
}


class DiscountCatalog:
    def __init__(self, policies: Mapping[str, DiscountPolicy] = DEFAULT_DISCOUNT_CODES) -> None:
        self._policies = {code.upper(): policy for code, policy in policies.items()}

    @staticmethod
    def normalize(code: str | None) -> str | None:
        if code is None or not code.strip():
            return None
        return code.strip().upper()

    def resolve(self, code: str | None) -> DiscountPolicy:
        normalized = self.normalize(code)
        if normalized is None:
            return NoDiscount()
        if normalized not in self._policies:
            raise UnknownDiscountCodeError(normalized)
        return self._policies[normalized]
