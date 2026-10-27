import json
from dataclasses import replace
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.customer import Customer
from app.domain.errors import OrderNotFoundError
from app.domain.invoice import Invoice
from app.domain.order import Order, OrderStatus
from app.domain.order_item import OrderItem
from app.domain.pricing import OrderTotals, VatSummaryLine
from app.domain.shipping import ShippingMethod
from app.domain.vat import VatRate
from app.infrastructure.orm import InvoiceRecord, OrderItemRecord, OrderRecord


class SqlOrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, order: Order) -> Order:
        record = _order_to_record(order)
        self._session.add(record)
        self._session.commit()
        order.id = record.id
        return order

    def get(self, order_id: int) -> Order | None:
        record = self._session.get(OrderRecord, order_id)
        return _order_to_domain(record) if record else None

    def list_all(self) -> list[Order]:
        records = self._session.scalars(select(OrderRecord).order_by(OrderRecord.id.desc()))
        return [_order_to_domain(record) for record in records]

    def update(self, order: Order) -> None:
        record = self._session.get(OrderRecord, order.id)
        if record is None:
            raise OrderNotFoundError(order.id)
        record.status = order.status.value
        record.tracking_number = order.tracking_number
        self._session.commit()


class SqlInvoiceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, invoice: Invoice) -> Invoice:
        record = InvoiceRecord(
            number=invoice.number,
            order_id=invoice.order_id,
            issue_date=invoice.issue_date,
            total_net=str(invoice.total_net),
            total_vat=str(invoice.total_vat),
            total_gross=str(invoice.total_gross),
        )
        self._session.add(record)
        self._session.commit()
        return replace(invoice, id=record.id)

    def get(self, invoice_id: int) -> Invoice | None:
        record = self._session.get(InvoiceRecord, invoice_id)
        return _invoice_to_domain(record) if record else None

    def find_by_order(self, order_id: int) -> Invoice | None:
        record = self._session.scalar(
            select(InvoiceRecord).where(InvoiceRecord.order_id == order_id)
        )
        return _invoice_to_domain(record) if record else None

    def list_all(self) -> list[Invoice]:
        records = self._session.scalars(select(InvoiceRecord).order_by(InvoiceRecord.id.desc()))
        return [_invoice_to_domain(record) for record in records]

    def count_issued_in_month(self, year: int, month: int) -> int:
        month_start = date(year, month, 1)
        next_month_start = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
        query = select(func.count(InvoiceRecord.id)).where(
            InvoiceRecord.issue_date >= month_start,
            InvoiceRecord.issue_date < next_month_start,
        )
        return self._session.scalar(query) or 0


def _order_to_record(order: Order) -> OrderRecord:
    customer = order.customer
    return OrderRecord(
        status=order.status.value,
        created_at=order.created_at,
        customer_name=customer.name,
        customer_email=customer.email,
        customer_street=customer.street,
        customer_city=customer.city,
        customer_postal_code=customer.postal_code,
        customer_tax_id=customer.tax_id,
        shipping_method=order.shipping_method.value,
        discount_code=order.discount_code,
        tracking_number=order.tracking_number,
        totals_json=_totals_to_json(order.totals),
        items=[
            OrderItemRecord(
                name=item.name,
                quantity=item.quantity,
                unit_price_net=str(item.unit_price_net),
                vat_rate=item.vat_rate.value,
            )
            for item in order.items
        ],
    )


def _order_to_domain(record: OrderRecord) -> Order:
    return Order(
        id=record.id,
        customer=Customer(
            name=record.customer_name,
            email=record.customer_email,
            street=record.customer_street,
            city=record.customer_city,
            postal_code=record.customer_postal_code,
            tax_id=record.customer_tax_id,
        ),
        items=[
            OrderItem(
                name=item.name,
                quantity=item.quantity,
                unit_price_net=Decimal(item.unit_price_net),
                vat_rate=VatRate(item.vat_rate),
            )
            for item in record.items
        ],
        shipping_method=ShippingMethod(record.shipping_method),
        totals=_totals_from_json(record.totals_json),
        created_at=record.created_at,
        discount_code=record.discount_code,
        status=OrderStatus(record.status),
        tracking_number=record.tracking_number,
    )


def _invoice_to_domain(record: InvoiceRecord) -> Invoice:
    return Invoice(
        id=record.id,
        number=record.number,
        order_id=record.order_id,
        issue_date=record.issue_date,
        total_net=Decimal(record.total_net),
        total_vat=Decimal(record.total_vat),
        total_gross=Decimal(record.total_gross),
    )


def _totals_to_json(totals: OrderTotals) -> str:
    return json.dumps(
        {
            "items_net": str(totals.items_net),
            "discount_net": str(totals.discount_net),
            "shipping_net": str(totals.shipping_net),
            "vat_summary": [
                {"rate": line.rate.value, "net": str(line.net), "vat": str(line.vat)}
                for line in totals.vat_summary
            ],
        }
    )


def _totals_from_json(raw: str) -> OrderTotals:
    data = json.loads(raw)
    return OrderTotals(
        items_net=Decimal(data["items_net"]),
        discount_net=Decimal(data["discount_net"]),
        shipping_net=Decimal(data["shipping_net"]),
        vat_summary=tuple(
            VatSummaryLine(
                rate=VatRate(line["rate"]), net=Decimal(line["net"]), vat=Decimal(line["vat"])
            )
            for line in data["vat_summary"]
        ),
    )
