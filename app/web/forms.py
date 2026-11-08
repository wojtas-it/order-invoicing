from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from typing import Any

from app.domain.customer import Customer
from app.domain.errors import ValidationError
from app.domain.order_item import OrderItem
from app.domain.product import Product
from app.domain.shipping import ShippingMethod
from app.domain.vat import VatRate
from app.services.order_service import PlaceOrderCommand

ITEM_ROWS = 5


def parse_order_form(form: Mapping[str, Any]) -> PlaceOrderCommand:
    customer = Customer(
        name=_text(form, "customer_name"),
        email=_text(form, "customer_email"),
        street=_text(form, "customer_street"),
        city=_text(form, "customer_city"),
        postal_code=_text(form, "customer_postal_code"),
        tax_id=_text(form, "customer_tax_id") or None,
    )
    items = [_parse_item(form, row) for row in range(ITEM_ROWS) if _text(form, f"item_name_{row}")]
    if not items:
        raise ValidationError("Dodaj co najmniej jedną pozycję zamówienia")
    return PlaceOrderCommand(
        customer=customer,
        items=items,
        shipping_method=_parse_shipping_method(form),
        discount_code=_text(form, "discount_code") or None,
    )


def parse_product_form(form: Mapping[str, Any], product_id: int | None = None) -> Product:
    try:
        unit_price_net = _parse_decimal(_text(form, "unit_price_net"))
        vat_rate = VatRate(int(_text(form, "vat_rate")))
    except (ValueError, InvalidOperation) as error:
        raise ValidationError("Podaj poprawną cenę netto i stawkę VAT") from error
    return Product(
        id=product_id,
        name=_text(form, "name"),
        unit_price_net=unit_price_net,
        vat_rate=vat_rate,
        active=form.get("active") is not None,
    )


def _parse_item(form: Mapping[str, Any], row: int) -> OrderItem:
    try:
        quantity = int(_text(form, f"item_quantity_{row}"))
        unit_price_net = _parse_decimal(_text(form, f"item_price_{row}"))
        vat_rate = VatRate(int(_text(form, f"item_vat_{row}")))
    except (ValueError, InvalidOperation) as error:
        raise ValidationError(f"Niepoprawne dane w pozycji nr {row + 1}") from error
    return OrderItem(
        name=_text(form, f"item_name_{row}"),
        quantity=quantity,
        unit_price_net=unit_price_net,
        vat_rate=vat_rate,
    )


def _parse_shipping_method(form: Mapping[str, Any]) -> ShippingMethod:
    try:
        return ShippingMethod(_text(form, "shipping_method"))
    except ValueError as error:
        raise ValidationError("Wybierz sposób dostawy") from error


def _parse_decimal(text: str) -> Decimal:
    """Parses an amount typed by a user, accepting both "12.50" and "12,50"."""
    return Decimal(text.replace(",", "."))


def _text(form: Mapping[str, Any], key: str) -> str:
    return str(form.get(key, "")).strip()
