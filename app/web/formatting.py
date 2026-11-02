from decimal import Decimal

from app.domain.shipping import DEFAULT_SHIPPING_PRICES_NET, ShippingMethod
from app.domain.vat import VatRate

NON_BREAKING_SPACE = "\u00a0"


def format_money(amount: Decimal) -> str:
    """Formats an amount in Polish notation, e.g. 1 234,50 zł."""
    formatted = f"{amount:,.2f}".replace(",", NON_BREAKING_SPACE).replace(".", ",")
    return f"{formatted}{NON_BREAKING_SPACE}zł"


def shipping_price_gross(method: ShippingMethod) -> Decimal:
    net = DEFAULT_SHIPPING_PRICES_NET[method]
    return net + VatRate.STANDARD.vat_for(net)
