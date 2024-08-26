from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

import entities
from auth.redis_client import RedisClient
from core.database import Session


@asynccontextmanager
async def lifespan(application: FastAPI):
    session = Session()
    redis = RedisClient()
    yield
    session.close_connection()


app = FastAPI(
    lifespan=lifespan,
    title='marketplace'
)

templates = Jinja2Templates(
    directory='../frontend/templates'
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

app.include_router(entities.products_router)
app.include_router(entities.comments_router)
app.include_router(entities.users_router)
app.include_router(entities.orders_router)
app.include_router(entities.roles_router)


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        name='index.html',
        request=request
    )
