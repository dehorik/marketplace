from typing import Annotated
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from entities.products.models import ProductModel, UpdateCatalogResponseModel
from entities.products.dependencies import (
    Catalog,
    CreateProduct,
    GetProduct,
    UpdateCatalog,
    UpdateProduct,
    DeleteProduct
)


router = APIRouter(
    prefix='/products',
    tags=['prodcuts']
)


templates = Jinja2Templates(
    directory='../frontend/templates'
)


@router.get("/catalog", response_class=HTMLResponse)
def get_catalog(request: Request, products: Annotated[list, Depends(Catalog())]):
    return templates.TemplateResponse(
        name='catalog.html',
        request=request,
        context={"products": products}
    )

@router.get("/update-catalog", response_model=UpdateCatalogResponseModel)
def update_catalog(products: Annotated[list, Depends(UpdateCatalog())]):
    return {
        'products': products
    }

@router.post(
    '/create',
    response_model=ProductModel,
    status_code=status.HTTP_201_CREATED
)
def create_product(product: Annotated[ProductModel, Depends(CreateProduct())]):
    return product

@router.get("/{product_id}", response_class=HTMLResponse)
def get_product(
        request: Request,
        product: Annotated[ProductModel, Depends(GetProduct())]
):
    return templates.TemplateResponse(
        name='merchan.html',
        request=request,
        context={"product": product}
    )

@router.patch("/{product_id}", response_model=ProductModel)
def update_product(product: Annotated[ProductModel, Depends(UpdateProduct())]):
    return product

@router.delete("/{product_id}", response_model=ProductModel)
def delete_product(product: Annotated[ProductModel, Depends(DeleteProduct())]):
    return product
