from typing import Annotated
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from entities.products.dependencies import (
    load_catalog_dependency,
    search_product_dependency,
    create_product_dependency,
    get_product_dependency,
    update_product_dependency,
    delete_product_dependency
)
from entities.products.models import (
    ProductModel,
    ExtendedProductModel,
    ProductCardListModel
)


router = APIRouter(
    prefix='/products',
    tags=['prodcuts']
)


templates = Jinja2Templates(
    directory='../frontend/templates'
)


@router.get("", response_class=HTMLResponse)
def get_catalog(
        request: Request,
        products_list: Annotated[
            ProductCardListModel,
            Depends(load_catalog_dependency)
        ]
):
    return templates.TemplateResponse(
        name='catalog.html',
        request=request,
        context={
            "products_list": products_list
        }
    )

@router.get("/latest", response_model=ProductCardListModel)
def load_catalog(
        products_list: Annotated[
            ProductCardListModel,
            Depends(load_catalog_dependency)
        ]
):
    return products_list

@router.get("/search", response_model=ProductCardListModel)
def search_product(
        products: Annotated[
            ProductCardListModel,
            Depends(search_product_dependency)
        ]
):
    return products

@router.post(
    '/create',
    response_model=ProductModel,
    status_code=status.HTTP_201_CREATED
)
def create_product(
        product: Annotated[ProductModel, Depends(create_product_dependency)]
):
    return product

@router.get("/{product_id}", response_class=HTMLResponse)
def get_product(
        request: Request,
        product: Annotated[
            ExtendedProductModel,
            Depends(get_product_dependency)
        ]
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
        product: Annotated[ProductModel, Depends(update_product_dependency)]
):
    return product

@router.delete("/{product_id}", response_model=ProductModel)
def delete_product(
        product: Annotated[ProductModel, Depends(delete_product_dependency)]
):
    return product
