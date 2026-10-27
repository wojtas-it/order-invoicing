from datetime import date, datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field

from app.domain.customer import Customer
from app.domain.invoice import Invoice
from app.domain.order import Order, OrderStatus
from app.domain.order_item import OrderItem
from app.domain.pricing import OrderTotals, VatSummaryLine
from app.domain.shipping import ShippingMethod
from app.domain.vat import VatRate
from app.services.order_service import PlaceOrderCommand


class ErrorResponse(BaseModel):
    detail: str


class CustomerPayload(BaseModel):
    name: str = Field(examples=["Jan Kowalski"])
    email: str = Field(examples=["jan.kowalski@example.com"])
    street: str = Field(examples=["ul. Długa 5"])
    city: str = Field(examples=["Kraków"])
    postal_code: str = Field(examples=["30-001"])
    tax_id: str | None = Field(default=None, examples=["1234563218"])

    def to_domain(self) -> Customer:
        return Customer(
            name=self.name,
            email=self.email,
            street=self.street,
            city=self.city,
            postal_code=self.postal_code,
            tax_id=self.tax_id or None,
        )

    @classmethod
    def from_domain(cls, customer: Customer) -> Self:
        return cls(
            name=customer.name,
            email=customer.email,
            street=customer.street,
            city=customer.city,
            postal_code=customer.postal_code,
            tax_id=customer.tax_id,
        )


class OrderItemPayload(BaseModel):
    name: str = Field(examples=["Kubek ceramiczny"])
    quantity: int = Field(examples=[2])
    unit_price_net: Decimal = Field(examples=["24.39"])
    vat_rate: VatRate = Field(examples=[23])

    def to_domain(self) -> OrderItem:
        return OrderItem(
            name=self.name,
            quantity=self.quantity,
            unit_price_net=self.unit_price_net,
            vat_rate=self.vat_rate,
        )

    @classmethod
    def from_domain(cls, item: OrderItem) -> Self:
        return cls(
            name=item.name,
            quantity=item.quantity,
            unit_price_net=item.unit_price_net,
            vat_rate=item.vat_rate,
        )


class OrderCreateRequest(BaseModel):
    customer: CustomerPayload
    items: list[OrderItemPayload] = Field(min_length=1)
    shipping_method: ShippingMethod
    discount_code: str | None = Field(default=None, examples=["WELCOME10"])

    def to_command(self) -> PlaceOrderCommand:
        return PlaceOrderCommand(
            customer=self.customer.to_domain(),
            items=[item.to_domain() for item in self.items],
            shipping_method=self.shipping_method,
            discount_code=self.discount_code,
        )


class VatSummaryResponse(BaseModel):
    rate: VatRate
    net: Decimal
    vat: Decimal
    gross: Decimal

    @classmethod
    def from_domain(cls, line: VatSummaryLine) -> Self:
        return cls(rate=line.rate, net=line.net, vat=line.vat, gross=line.gross)


class TotalsResponse(BaseModel):
    items_net: Decimal
    discount_net: Decimal
    shipping_net: Decimal
    total_net: Decimal
    total_vat: Decimal
    total_gross: Decimal
    vat_summary: list[VatSummaryResponse]

    @classmethod
    def from_domain(cls, totals: OrderTotals) -> Self:
        return cls(
            items_net=totals.items_net,
            discount_net=totals.discount_net,
            shipping_net=totals.shipping_net,
            total_net=totals.total_net,
            total_vat=totals.total_vat,
            total_gross=totals.total_gross,
            vat_summary=[VatSummaryResponse.from_domain(line) for line in totals.vat_summary],
        )


class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    created_at: datetime
    customer: CustomerPayload
    items: list[OrderItemPayload]
    shipping_method: ShippingMethod
    discount_code: str | None
    tracking_number: str | None
    totals: TotalsResponse

    @classmethod
    def from_domain(cls, order: Order) -> Self:
        assert order.id is not None
        return cls(
            id=order.id,
            status=order.status,
            created_at=order.created_at,
            customer=CustomerPayload.from_domain(order.customer),
            items=[OrderItemPayload.from_domain(item) for item in order.items],
            shipping_method=order.shipping_method,
            discount_code=order.discount_code,
            tracking_number=order.tracking_number,
            totals=TotalsResponse.from_domain(order.totals),
        )


class InvoiceResponse(BaseModel):
    id: int
    number: str
    order_id: int
    issue_date: date
    total_net: Decimal
    total_vat: Decimal
    total_gross: Decimal

    @classmethod
    def from_domain(cls, invoice: Invoice) -> Self:
        assert invoice.id is not None
        return cls(
            id=invoice.id,
            number=invoice.number,
            order_id=invoice.order_id,
            issue_date=invoice.issue_date,
            total_net=invoice.total_net,
            total_vat=invoice.total_vat,
            total_gross=invoice.total_gross,
        )
