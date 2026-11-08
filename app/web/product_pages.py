from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response

from app.api.dependencies import ProductServiceDep
from app.domain.errors import DomainError, NotFoundError
from app.domain.vat import VatRate
from app.web.forms import parse_product_form
from app.web.templating import redirect, render_not_found, templates

router = APIRouter(include_in_schema=False)


@router.get("/products", response_class=HTMLResponse)
def product_list(request: Request, products: ProductServiceDep) -> Response:
    context = {"products": products.list_products()}
    return templates.TemplateResponse(request, "products.html", context)


@router.get("/products/new", response_class=HTMLResponse)
def new_product_form(request: Request) -> Response:
    return _render_product_form(request, form={"active": "on"})


@router.post("/products", response_class=HTMLResponse)
async def create_product(request: Request, products: ProductServiceDep) -> Response:
    form = await request.form()
    try:
        products.add_product(parse_product_form(form))
    except DomainError as error:
        return _render_product_form(request, form=form, error=str(error), status_code=422)
    return redirect("/products")


@router.get("/products/{product_id}/edit", response_class=HTMLResponse)
def edit_product_form(request: Request, product_id: int, products: ProductServiceDep) -> Response:
    try:
        product = products.get_product(product_id)
    except NotFoundError as not_found:
        return render_not_found(request, not_found)
    form = {
        "name": product.name,
        "unit_price_net": f"{product.unit_price_net:.2f}".replace(".", ","),
        "vat_rate": str(product.vat_rate.value),
        "active": "on" if product.active else None,
    }
    return _render_product_form(request, form=form, product_id=product_id)


@router.post("/products/{product_id}", response_class=HTMLResponse)
async def update_product(
    request: Request, product_id: int, products: ProductServiceDep
) -> Response:
    form = await request.form()
    try:
        products.update_product(parse_product_form(form, product_id))
    except NotFoundError as not_found:
        return render_not_found(request, not_found)
    except DomainError as error:
        return _render_product_form(
            request, form=form, product_id=product_id, error=str(error), status_code=422
        )
    return redirect("/products")


def _render_product_form(
    request: Request,
    form: object,
    product_id: int | None = None,
    error: str | None = None,
    status_code: int = 200,
) -> Response:
    context = {
        "form": form,
        "product_id": product_id,
        "error": error,
        "vat_rates": list(VatRate),
    }
    return templates.TemplateResponse(
        request, "product_form.html", context, status_code=status_code
    )
