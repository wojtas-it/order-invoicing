from app.domain.errors import (
    InvoiceAlreadyIssuedError,
    InvoiceNotAllowedError,
    InvoiceNotFoundError,
    OrderNotFoundError,
)
from app.domain.invoice import Invoice, format_invoice_number
from app.services.ports import Clock, InvoiceRepository, OrderRepository


class InvoiceService:
    def __init__(self, invoices: InvoiceRepository, orders: OrderRepository, clock: Clock) -> None:
        self._invoices = invoices
        self._orders = orders
        self._clock = clock

    def issue_for_order(self, order_id: int) -> Invoice:
        order = self._orders.get(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        if not order.can_be_invoiced:
            raise InvoiceNotAllowedError(order_id)
        if self._invoices.find_by_order(order_id) is not None:
            raise InvoiceAlreadyIssuedError(order_id)

        issue_date = self._clock.now().date()
        sequence = self._invoices.count_issued_in_month(issue_date.year, issue_date.month) + 1
        invoice = Invoice(
            number=format_invoice_number(issue_date, sequence),
            order_id=order_id,
            issue_date=issue_date,
            total_net=order.totals.total_net,
            total_vat=order.totals.total_vat,
            total_gross=order.totals.total_gross,
        )
        return self._invoices.add(invoice)

    def get_invoice(self, invoice_id: int) -> Invoice:
        invoice = self._invoices.get(invoice_id)
        if invoice is None:
            raise InvoiceNotFoundError(invoice_id)
        return invoice

    def find_for_order(self, order_id: int) -> Invoice | None:
        return self._invoices.find_by_order(order_id)

    def list_invoices(self) -> list[Invoice]:
        return self._invoices.list_all()
