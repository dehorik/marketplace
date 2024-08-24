from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from core.database import Session
from routes import product_router, comment_router, order_router, role_router, user_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    session = Session()
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

app.include_router(product_router)
app.include_router(comment_router)
app.include_router(user_router)
app.include_router(order_router)
app.include_router(role_router)


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        name='index.html',
        request=request
    )
