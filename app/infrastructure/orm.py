from datetime import date, datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Monetary values are stored as strings to keep exact Decimal precision in SQLite.
MONEY = String(20)


class Base(DeclarativeBase):
    pass


class OrderItemRecord(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    name: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[int]
    unit_price_net: Mapped[str] = mapped_column(MONEY)
    vat_rate: Mapped[int]


class OrderRecord(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime]
    customer_name: Mapped[str] = mapped_column(String(200))
    customer_email: Mapped[str] = mapped_column(String(200))
    customer_street: Mapped[str] = mapped_column(String(200))
    customer_city: Mapped[str] = mapped_column(String(100))
    customer_postal_code: Mapped[str] = mapped_column(String(6))
    customer_tax_id: Mapped[str | None] = mapped_column(String(10))
    shipping_method: Mapped[str] = mapped_column(String(20))
    discount_code: Mapped[str | None] = mapped_column(String(50))
    tracking_number: Mapped[str | None] = mapped_column(String(100))
    totals_json: Mapped[str] = mapped_column(Text)
    items: Mapped[list[OrderItemRecord]] = relationship(
        cascade="all, delete-orphan", lazy="selectin", order_by=OrderItemRecord.id
    )


class InvoiceRecord(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(30), unique=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), unique=True)
    issue_date: Mapped[date]
    total_net: Mapped[str] = mapped_column(MONEY)
    total_vat: Mapped[str] = mapped_column(MONEY)
    total_gross: Mapped[str] = mapped_column(MONEY)
