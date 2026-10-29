from collections.abc import Mapping
from decimal import Decimal
from enum import StrEnum

from app.domain.money import ZERO


class ShippingMethod(StrEnum):
    COURIER = "courier"
    PARCEL_LOCKER = "parcel_locker"

    @property
    def label(self) -> str:
        return SHIPPING_LABELS[self]


SHIPPING_LABELS = {
    ShippingMethod.COURIER: "Kurier",
    ShippingMethod.PARCEL_LOCKER: "Paczkomat",
}

DEFAULT_SHIPPING_PRICES_NET: Mapping[ShippingMethod, Decimal] = {
    ShippingMethod.COURIER: Decimal("13.00"),
    ShippingMethod.PARCEL_LOCKER: Decimal("10.56"),
}
DEFAULT_FREE_SHIPPING_THRESHOLD_GROSS = Decimal("200.00")


class ShippingCostPolicy:
    def __init__(
        self,
        prices_net: Mapping[ShippingMethod, Decimal] = DEFAULT_SHIPPING_PRICES_NET,
        free_shipping_threshold_gross: Decimal = DEFAULT_FREE_SHIPPING_THRESHOLD_GROSS,
    ) -> None:
        self._prices_net = prices_net
        self._free_shipping_threshold_gross = free_shipping_threshold_gross

    def cost_for(self, method: ShippingMethod, items_gross: Decimal) -> Decimal:
        if items_gross >= self._free_shipping_threshold_gross:
            return ZERO
        return self._prices_net[method]
