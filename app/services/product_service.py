from app.domain.errors import ProductNotFoundError
from app.domain.product import Product
from app.services.ports import ProductRepository


class ProductService:
    def __init__(self, products: ProductRepository) -> None:
        self._products = products

    def add_product(self, product: Product) -> Product:
        return self._products.add(product)

    def update_product(self, product: Product) -> Product:
        if product.id is None or self._products.get(product.id) is None:
            raise ProductNotFoundError(product.id)
        self._products.update(product)
        return product

    def get_product(self, product_id: int) -> Product:
        product = self._products.get(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return product

    def list_products(self, active_only: bool = False) -> list[Product]:
        return self._products.list_all(active_only)
