import os
from typing import Annotated
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from entities.products.dependencies import (
    catalog_loader_service,
    product_search_service,
    product_creation_service,
    product_fetch_service,
    product_update_service,
    product_removal_service
)
from entities.products.models import (
    ProductModel,
    ExtendedProductModel,
    ProductCardListModel
)
from core.settings import ROOT_PATH


router = APIRouter(prefix='/products', tags=['prodcuts'])


templates = Jinja2Templates(
    directory=os.path.join(ROOT_PATH, r'frontend\templates')
)


@router.get("/latest", response_model=ProductCardListModel)
def load_catalog(
        products: Annotated[ProductCardListModel, Depends(catalog_loader_service)]
):
    return products

@router.get("/search", response_model=ProductCardListModel)
def search_product(
        products: Annotated[ProductCardListModel, Depends(product_search_service)]
):
    return products

@router.post(
    "/",
    response_model=ProductModel,
    status_code=status.HTTP_201_CREATED
)
def create_product(
        product: Annotated[ProductModel, Depends(product_creation_service)]
):
    return product

@router.get("/{product_id}", response_class=HTMLResponse)
def get_product(
        request: Request,
        product: Annotated[ExtendedProductModel, Depends(product_fetch_service)]
):
    return templates.TemplateResponse(
        name='merchan.html',
        request=request,
        context={
            "product": product
        }
    )

@router.patch("/{product_id}", response_model=ProductModel)
def update_product(
        product: Annotated[ProductModel, Depends(product_update_service)]
):
    return product

@router.delete("/{product_id}", response_model=ProductModel)
def delete_product(
        product: Annotated[ProductModel, Depends(product_removal_service)]
):
    return product
