from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from app.domain.discounts import DiscountPolicy
from app.domain.errors import ValidationError
from app.domain.money import ZERO, round_money
from app.domain.order_item import OrderItem
from app.domain.shipping import ShippingCostPolicy, ShippingMethod
from app.domain.vat import VatRate

SHIPPING_VAT_RATE = VatRate.STANDARD


@dataclass(frozen=True)
class VatSummaryLine:
    rate: VatRate
    net: Decimal
    vat: Decimal

    @property
    def gross(self) -> Decimal:
        return self.net + self.vat


@dataclass(frozen=True)
class OrderTotals:
    items_net: Decimal
    discount_net: Decimal
    shipping_net: Decimal
    vat_summary: tuple[VatSummaryLine, ...]

    @property
    def total_net(self) -> Decimal:
        return sum((line.net for line in self.vat_summary), ZERO)

    @property
    def total_vat(self) -> Decimal:
        return sum((line.vat for line in self.vat_summary), ZERO)

    @property
    def total_gross(self) -> Decimal:
        return self.total_net + self.total_vat


class PriceCalculator:
    """Calculates order totals using the Polish "VAT from net sum per rate" method."""

    def __init__(self, shipping_policy: ShippingCostPolicy) -> None:
        self._shipping_policy = shipping_policy

    def calculate(
        self,
        items: Sequence[OrderItem],
        discount: DiscountPolicy,
        shipping_method: ShippingMethod,
    ) -> OrderTotals:
        if not items:
            raise ValidationError("Zamówienie musi zawierać co najmniej jedną pozycję")

        net_by_rate = _sum_net_by_rate(items)
        items_net = sum(net_by_rate.values(), ZERO)
        discount_net = discount.discount_for(items_net)
        net_by_rate = _distribute_discount(net_by_rate, discount_net)

        items_gross = sum((net + _vat_for(rate, net) for rate, net in net_by_rate.items()), ZERO)
        shipping_net = self._shipping_policy.cost_for(shipping_method, items_gross)
        if shipping_net > 0:
            net_by_rate[SHIPPING_VAT_RATE] = net_by_rate.get(SHIPPING_VAT_RATE, ZERO) + shipping_net

        vat_summary = tuple(
            VatSummaryLine(rate=rate, net=net, vat=_vat_for(rate, net))
            for rate, net in sorted(net_by_rate.items(), reverse=True)
        )
        return OrderTotals(items_net, discount_net, shipping_net, vat_summary)


def _vat_for(rate: VatRate, net: Decimal) -> Decimal:
    return round_money(net * rate.fraction)


def _sum_net_by_rate(items: Sequence[OrderItem]) -> dict[VatRate, Decimal]:
    net_by_rate: dict[VatRate, Decimal] = {}
    for item in items:
        net_by_rate[item.vat_rate] = net_by_rate.get(item.vat_rate, ZERO) + item.net_total
    return net_by_rate


def _distribute_discount(
    net_by_rate: dict[VatRate, Decimal], discount: Decimal
) -> dict[VatRate, Decimal]:
    """Splits the discount proportionally between VAT rates.

    Rounding leftovers are assigned to the rate with the largest net value.
    """
    if discount == 0:
        return dict(net_by_rate)

    total_net = sum(net_by_rate.values(), ZERO)
    rates_by_net = sorted(net_by_rate, key=lambda rate: net_by_rate[rate])
    largest_rate = rates_by_net.pop()

    discounted: dict[VatRate, Decimal] = {}
    remaining_discount = discount
    for rate in rates_by_net:
        share = round_money(discount * net_by_rate[rate] / total_net)
        discounted[rate] = net_by_rate[rate] - share
        remaining_discount -= share
    discounted[largest_rate] = net_by_rate[largest_rate] - remaining_discount
    return discounted
