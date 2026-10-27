from dataclasses import dataclass
from datetime import date
from decimal import Decimal

INVOICE_NUMBER_PREFIX = "FV"


@dataclass(frozen=True)
class Invoice:
    number: str
    order_id: int
    issue_date: date
    total_net: Decimal
    total_vat: Decimal
    total_gross: Decimal
    id: int | None = None


def format_invoice_number(issue_date: date, sequence: int) -> str:
    if sequence < 1:
        raise ValueError("Invoice sequence must be a positive number")
    return f"{INVOICE_NUMBER_PREFIX}/{issue_date.year}/{issue_date.month:02d}/{sequence:03d}"
