from fastapi import APIRouter

from app.api.dependencies import ProductServiceDep
from app.api.responses import INVALID_DATA, NOT_FOUND
from app.api.schemas import ProductRequest, ProductResponse

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", summary="Lista produktów")
def list_products(service: ProductServiceDep, active_only: bool = False) -> list[ProductResponse]:
    return [ProductResponse.from_domain(product) for product in service.list_products(active_only)]


@router.get("/{product_id}", summary="Szczegóły produktu", responses=NOT_FOUND)
def get_product(product_id: int, service: ProductServiceDep) -> ProductResponse:
    return ProductResponse.from_domain(service.get_product(product_id))


@router.post("", status_code=201, summary="Dodaj produkt", responses=INVALID_DATA)
def create_product(payload: ProductRequest, service: ProductServiceDep) -> ProductResponse:
    return ProductResponse.from_domain(service.add_product(payload.to_domain()))


@router.put(
    "/{product_id}",
    summary="Zmień produkt (nazwa, cena, VAT, dostępność)",
    responses={**NOT_FOUND, **INVALID_DATA},
)
def update_product(
    product_id: int, payload: ProductRequest, service: ProductServiceDep
) -> ProductResponse:
    return ProductResponse.from_domain(service.update_product(payload.to_domain(product_id)))
