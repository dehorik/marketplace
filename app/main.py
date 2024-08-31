from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from auth import RedisClient, auth_router
from core.database import Session
from entities import (
    products_router,
    comments_router,
    users_router,
    orders_router,
    roles_router
)


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
    StaticFiles(directory='../frontend/static'),
    name='static'
)
app.mount(
    '/database_data',
    StaticFiles(directory='../database_data'),
    name='database_data'
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(comments_router)
app.include_router(users_router)
app.include_router(orders_router)
app.include_router(roles_router)


templates = Jinja2Templates(
    directory='../frontend/templates'
)


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        name='index.html',
        request=request
    )
