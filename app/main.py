import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from entities import (
    products_router,
    comments_router,
    users_router,
    orders_router
)
from auth import RedisClient, auth_router
from core.database import Session
from core.settings import ROOT_PATH


@asynccontextmanager
async def lifespan(application: FastAPI):
    session = Session()
    redis = RedisClient()
    yield
    session.close()
    redis.close()


app = FastAPI(
    lifespan=lifespan,
    title='marketplace'
)

app.mount(
    '/static',
    StaticFiles(directory=os.path.join(ROOT_PATH, r"frontend\static")),
    name='static'
)
app.mount(
    '/images',
    StaticFiles(directory=os.path.join(ROOT_PATH, "images")),
    name='images'
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(comments_router)
app.include_router(users_router)
app.include_router(orders_router)


templates = Jinja2Templates(
    directory=os.path.join(ROOT_PATH, r"frontend\templates")
)


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        name='index.html',
        request=request
    )
