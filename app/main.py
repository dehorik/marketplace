from os.path import join
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from entities import (
    products_router,
    comments_router,
    users_router,
    orders_router,
    cart_items_router
)
from auth import get_redis_client, auth_router
from core.database import get_session
from core.settings import ROOT_PATH


@asynccontextmanager
async def lifespan(application: FastAPI):
    session = get_session()
    redis = get_redis_client()
    yield
    session.close()
    redis.close()


app = FastAPI(lifespan=lifespan, title='marketplace')

app.mount(
    '/static',
    StaticFiles(directory=join(ROOT_PATH, "frontend", "static")),
    name='static'
)
app.mount(
    '/images',
    StaticFiles(directory=join(ROOT_PATH, "images")),
    name='images'
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(comments_router)
app.include_router(users_router)
app.include_router(orders_router)
app.include_router(cart_items_router)


templates = Jinja2Templates(directory=join(ROOT_PATH, "frontend", "templates"))


@app.get("/", response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse(
        name='index.html',
        request=request
    )
