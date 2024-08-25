from typing import Annotated
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from entities.products.models import ProductModel, UpdateCatalogResponseModel
from entities.products.dependencies import (
    CreateProduct,
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


@router.get("/update-catalog", response_model=UpdateCatalogResponseModel)
def update_catalog(obj: Annotated[UpdateCatalog, Depends(UpdateCatalog)]):
    return {
        'products': obj.products
    }

@router.post(
    '/create',
    response_model=ProductModel,
    status_code=status.HTTP_201_CREATED
)
def create_product(obj: Annotated[CreateProduct, Depends(CreateProduct)]):
    return obj.product

@router.get("/{product_id}", response_class=HTMLResponse)
def get_product(product_id: int, request: Request):
    return templates.TemplateResponse(
        name='cart.html',
        request=request
    )

@router.patch("/{product_id}", response_model=ProductModel)
def update_product(obj: Annotated[UpdateProduct, Depends(UpdateProduct)]):
    return obj.product

@router.delete("/{product_id}", response_model=ProductModel)
def delete_product(obj: Annotated[DeleteProduct, Depends(DeleteProduct)]):
    return obj.product
