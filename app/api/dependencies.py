from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.domain.discounts import DiscountCatalog
from app.domain.pricing import PriceCalculator
from app.domain.shipping import ShippingCostPolicy
from app.infrastructure.repositories import (
    SqlInvoiceRepository,
    SqlOrderRepository,
    SqlProductRepository,
)
from app.services.invoice_service import InvoiceService
from app.services.order_service import OrderService
from app.services.product_service import ProductService


def get_session(request: Request) -> Iterator[Session]:
    session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]


def get_product_service(session: SessionDep) -> ProductService:
    return ProductService(SqlProductRepository(session))


def get_order_service(request: Request, session: SessionDep) -> OrderService:
    return OrderService(
        orders=SqlOrderRepository(session),
        calculator=PriceCalculator(ShippingCostPolicy()),
        discounts=DiscountCatalog(),
        carrier=request.app.state.carrier,
        clock=request.app.state.clock,
    )


def get_invoice_service(request: Request, session: SessionDep) -> InvoiceService:
    return InvoiceService(
        invoices=SqlInvoiceRepository(session),
        orders=SqlOrderRepository(session),
        clock=request.app.state.clock,
    )


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
InvoiceServiceDep = Annotated[InvoiceService, Depends(get_invoice_service)]
