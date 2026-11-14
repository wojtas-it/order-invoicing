from decimal import Decimal

from sqlalchemy.orm import Session, sessionmaker

from app.domain.product import Product
from app.domain.vat import VatRate
from app.infrastructure.repositories import SqlProductRepository


def demo_products() -> list[Product]:
    return [
        Product('Monitor 27" 4K', Decimal("899.00"), VatRate.STANDARD),
        Product("Klawiatura mechaniczna", Decimal("249.00"), VatRate.STANDARD),
        Product("Mysz bezprzewodowa", Decimal("89.00"), VatRate.STANDARD),
        Product("Słuchawki z mikrofonem", Decimal("159.00"), VatRate.STANDARD),
        Product("Kabel HDMI 2 m", Decimal("19.90"), VatRate.STANDARD),
        Product("Książka „Czysty kod”", Decimal("59.90"), VatRate.SUPER_REDUCED),
        Product("Książka „Testowanie oprogramowania”", Decimal("49.90"), VatRate.SUPER_REDUCED),
    ]


def seed_demo_products(session_factory: sessionmaker[Session]) -> None:
    """Fills an empty catalog with sample products, so the app can be tried right away."""
    with session_factory() as session:
        products = SqlProductRepository(session)
        if products.list_all():
            return
        for product in demo_products():
            products.add(product)
